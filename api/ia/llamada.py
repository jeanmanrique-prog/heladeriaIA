"""
api/ia/llamada.py
─────────────────
Endpoint /voz-stream: procesa chunks de audio en tiempo real.

Flujo por chunk:
  1. Recibe blob de audio del frontend JS
  2. Transcribe con Faster-Whisper (STT) en un executor no bloqueante
  3. Acumula texto del usuario en la sesión
  4. Cuando el frontend señala silencio (force_reply=True) → genera respuesta LLM + TTS
  5. Devuelve JSON con texto transcrito + texto de IA + audio en base64

El frontend JS ya maneja VAD, silencio y reproducción de audio.
"""

from fastapi import APIRouter, Form, UploadFile, File
from pathlib import Path
import sys
from typing import Optional
import base64
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
import json
import threading
import time
import uuid

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from mcp.voz.pipeline.pipeline_voz import (  # noqa: E402
    MENSAJE_BIENVENIDA_CLIENTE,
    SYSTEM_PROMPT_VENDEDOR,
    inicializar_transcriptor,
    inicializar_voz,
    normalizar_texto_usuario_voz,
    responder_vendedor_json,
    sintetizar_audio_wav,
    texto_voz_respuesta_vendedor,
    transcribir_audio,
)

# ──────────────────────────────────────────────────────────
# CONSTANTES DE CONFIGURACIÓN
# ──────────────────────────────────────────────────────────

MAX_TURNOS_VOZ = 16                # Máximos turnos en historial de voz
VOICE_SESSION_TTL_SEC = 1800       # 30 min — sesiones sin actividad expiradas
VOICE_REPLY_TIMEOUT_SEC = 25       # Timeout para LLM
VOICE_STT_TIMEOUT_SEC = 6          # Timeout para STT (Whisper puede ser lento)
VOICE_TTS_TIMEOUT_SEC = 8          # Timeout para TTS
VOICE_SILENCE_CHUNKS_TO_REPLY = 3  # Chunks de silencio antes de forzar respuesta

# Executors dedicados para no bloquear el event loop de FastAPI
_EXECUTOR_LLM = ThreadPoolExecutor(max_workers=4, thread_name_prefix="llm")
_EXECUTOR_STT = ThreadPoolExecutor(max_workers=4, thread_name_prefix="stt")
_EXECUTOR_TTS = ThreadPoolExecutor(max_workers=2, thread_name_prefix="tts")

_SESIONES: dict[str, dict] = {}
_SESIONES_LOCK = threading.Lock()


# ──────────────────────────────────────────────────────────
# GESTIÓN DE SESIONES
# ──────────────────────────────────────────────────────────

def _historial_base() -> list[dict]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT_VENDEDOR},
        {"role": "assistant", "content": MENSAJE_BIENVENIDA_CLIENTE},
    ]


def _recortar_historial(historial: list[dict]) -> list[dict]:
    max_len = 2 + MAX_TURNOS_VOZ * 2
    if len(historial) <= max_len:
        return historial
    return historial[:2] + historial[-(MAX_TURNOS_VOZ * 2):]


def _limpiar_sesiones_expiradas(now_ts: float) -> None:
    expiradas = [
        sid for sid, s in _SESIONES.items()
        if (now_ts - float(s.get("last_seen", 0))) > VOICE_SESSION_TTL_SEC
    ]
    for sid in expiradas:
        _SESIONES.pop(sid, None)
        print(f"[voz-stream][sesion] expirada: {sid[:8]}...")


def _obtener_sesion(session_id: Optional[str], reset: bool) -> tuple[str, dict]:
    now_ts = time.time()
    sid = (session_id or "").strip() or str(uuid.uuid4())
    with _SESIONES_LOCK:
        _limpiar_sesiones_expiradas(now_ts)
        sesion = _SESIONES.get(sid)
        if reset or sesion is None:
            sesion = {
                "historial": _historial_base(),
                "buffer_usuario": "",
                "silence_chunks": 0,
                "last_seen": now_ts,
            }
            _SESIONES[sid] = sesion
            print(f"[voz-stream][sesion] nueva: {sid[:8]}... (reset={reset})")
        else:
            sesion["last_seen"] = now_ts
    return sid, sesion


# ──────────────────────────────────────────────────────────
# STT — Transcripción de audio
# ──────────────────────────────────────────────────────────

def _transcribir(audio_bytes: bytes) -> tuple[bool, str]:
    """Transcribe audio WAV/WebM a texto. No bloqueante via executor."""
    t0 = time.monotonic()
    try:
        fut = _EXECUTOR_STT.submit(transcribir_audio, audio_bytes)
        ok, texto = fut.result(timeout=VOICE_STT_TIMEOUT_SEC)
        elapsed = time.monotonic() - t0
        if ok and texto:
            print(f"📝 STT ok ({elapsed:.2f}s): '{texto[:60]}'")
        else:
            print(f"[voz-stream][STT] sin texto ({elapsed:.2f}s): {texto}")
        return ok, texto
    except FuturesTimeoutError:
        print(f"[voz-stream][STT] timeout ({time.monotonic()-t0:.2f}s)")
        return False, "timeout"
    except Exception as e:
        print(f"[voz-stream][STT] error: {e}")
        return False, str(e)


# ──────────────────────────────────────────────────────────
# LLM — Generación de respuesta
# ──────────────────────────────────────────────────────────

def _generar_respuesta(sesion: dict) -> dict:
    """Llama al LLM con el buffer acumulado y obtiene respuesta + audio TTS."""
    texto_usuario = str(sesion.get("buffer_usuario", "")).strip()
    if not texto_usuario:
        return {}

    historial = sesion.get("historial", _historial_base())
    print(f"🧠 LLM procesando: '{texto_usuario[:80]}'")

    historial.append({"role": "user", "content": texto_usuario})
    sesion["buffer_usuario"] = ""   # limpiar ANTES del LLM para no perder mensajes concurrentes
    sesion["silence_chunks"] = 0

    try:
        fut = _EXECUTOR_LLM.submit(responder_vendedor_json, historial, False)
        respuesta_raw = fut.result(timeout=VOICE_REPLY_TIMEOUT_SEC)
    except FuturesTimeoutError:
        respuesta_raw = json.dumps(
            {"accion": "informacion", "mensaje": "Mmm... me quedé pensando. Qué me decías?"},
            ensure_ascii=False,
        )
    except Exception as e:
        print(f"[voz-stream][LLM] error: {e}")
        respuesta_raw = json.dumps(
            {"accion": "error", "mensaje": "No pude responder ahora. Inténtalo de nuevo."},
            ensure_ascii=False,
        )

    historial.append({"role": "assistant", "content": respuesta_raw})
    sesion["historial"] = _recortar_historial(historial)

    texto_asistente = texto_voz_respuesta_vendedor(respuesta_raw).strip() or "Entendido."
    # Limitar longitud para TTS rápido
    if len(texto_asistente) > 500:
        texto_asistente = texto_asistente[:500].rsplit(" ", 1)[0].strip() + "."

    print(f"🤖 Respuesta generada: '{texto_asistente[:80]}'")
    audio = _sintetizar_tts(texto_asistente)

    return {
        "assistant_text": texto_asistente,
        "assistant_audio_b64": base64.b64encode(audio).decode("ascii") if audio else "",
        "assistant_audio_mime": "audio/wav",
    }


# ──────────────────────────────────────────────────────────
# TTS — Síntesis de voz
# ──────────────────────────────────────────────────────────

def _sintetizar_tts(texto: str) -> bytes:
    t0 = time.monotonic()
    try:
        fut = _EXECUTOR_TTS.submit(sintetizar_audio_wav, texto)
        audio = fut.result(timeout=VOICE_TTS_TIMEOUT_SEC) or b""
        elapsed = time.monotonic() - t0
        if audio:
            print(f"🔊 TTS ok ({elapsed:.2f}s, {len(audio)} bytes)")
        else:
            print(f"[voz-stream][TTS] vacío ({elapsed:.2f}s)")
        return audio
    except FuturesTimeoutError:
        print(f"[voz-stream][TTS] timeout ({time.monotonic()-t0:.2f}s)")
        return b""
    except Exception as e:
        print(f"[voz-stream][TTS] error: {e}")
        return b""


# ──────────────────────────────────────────────────────────
# ENDPOINT PRINCIPAL
# ──────────────────────────────────────────────────────────

@router.post("/voz-stream", summary="Procesar chunks de voz en modo llamada continua")
def voz_stream(
    session_id: Optional[str] = Form(default=None),
    reset: bool = Form(default=False),
    force_reply: bool = Form(default=False),
    mime_type: Optional[str] = Form(default=None),
    audio_chunk: Optional[UploadFile] = File(default=None),
):
    """
    Endpoint llamado por el frontend JS cada ~300ms con un blob de audio.

    Parámetros:
    - session_id: ID de sesión persistente por llamada
    - reset: True → nueva sesión + enviar saludo
    - force_reply: True → procesar buffer y generar respuesta inmediatamente
    - mime_type: MIME del audio (audio/webm, audio/ogg, audio/wav)
    - audio_chunk: Blob de audio del MediaRecorder
    """
    sid, sesion = _obtener_sesion(session_id, reset=reset)

    respuesta = {
        "ok": True,
        "session_id": sid,
        "transcription_ok": False,
        "transcript_chunk": "",
        "transcript_live": "",
        "assistant_text": "",
        "assistant_audio_b64": "",
        "assistant_audio_mime": "audio/wav",
    }

    # ── 1. SALUDO INICIAL (reset sin audio) ──
    if reset and audio_chunk is None:
        saludo_txt = texto_voz_respuesta_vendedor(MENSAJE_BIENVENIDA_CLIENTE).strip()
        if not saludo_txt:
            saludo_txt = "Ey bro, bienvenido a Gelateria Urbana. Que se te antoja hoy?"
        print(f"[voz-stream] saludo: '{saludo_txt[:60]}'")
        saludo_audio = _sintetizar_tts(saludo_txt)
        respuesta["assistant_text"] = saludo_txt
        respuesta["assistant_audio_b64"] = (
            base64.b64encode(saludo_audio).decode("ascii") if saludo_audio else ""
        )
        return respuesta

    # ── 2. TRANSCRIPCIÓN DEL CHUNK ──
    if audio_chunk is not None:
        audio_bytes = audio_chunk.file.read()
        if audio_bytes and len(audio_bytes) > 500:  # ignorar blobs vacíos/cabeceras
            print(f"🎤 Chunk recibido: {len(audio_bytes)} bytes")
            ok, texto = _transcribir(audio_bytes)
            if ok and texto and texto.strip():
                texto_limpio = normalizar_texto_usuario_voz(texto).strip()
                if texto_limpio:
                    sesion["buffer_usuario"] = texto_limpio   # sobreescribir con el acumulado más reciente
                    sesion["silence_chunks"] = 0
                    respuesta["transcription_ok"] = True
                    respuesta["transcript_chunk"] = texto_limpio
            else:
                # Sin transcripción → incrementar contador de silencio
                if str(sesion.get("buffer_usuario", "")).strip():
                    sesion["silence_chunks"] = int(sesion.get("silence_chunks", 0)) + 1

    # ── 3. DECIDIR SI RESPONDER ──
    buffer_actual = str(sesion.get("buffer_usuario", "")).strip()
    respuesta["transcript_live"] = buffer_actual

    should_reply = bool(buffer_actual) and (
        force_reply
        or int(sesion.get("silence_chunks", 0)) >= VOICE_SILENCE_CHUNKS_TO_REPLY
    )

    # ── 4. GENERAR RESPUESTA LLM + TTS ──
    if should_reply:
        print(f"🧠 Generando respuesta (force={force_reply})...")
        update = _generar_respuesta(sesion)
        respuesta.update(update)
        respuesta["transcript_live"] = str(sesion.get("buffer_usuario", "")).strip()

    return respuesta
