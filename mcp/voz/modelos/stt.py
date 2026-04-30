import os
import tempfile
import unicodedata
import re
from mcp.config import ASR_MODELO

_transcriptor = None

def inicializar_transcriptor() -> bool:
    """Carga el modelo local de transcripcion."""
    global _transcriptor
    if _transcriptor is not None:
        return True

    try:
        from faster_whisper import WhisperModel
        _transcriptor = WhisperModel(ASR_MODELO, device="cpu", compute_type="int8")
        return True
    except ImportError:
        return False
    except Exception:
        return False

def normalizar_texto(texto: str) -> str:
    texto = (texto or "").strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    if "presa" in texto:
        texto = texto.replace("presa", "fresa")
    return texto

def _suffix_audio_desde_mime(audio_format: str | None) -> str:
    formato = normalizar_texto(audio_format or "")
    if "webm" in formato: return ".webm"
    if "ogg" in formato or "opus" in formato: return ".ogg"
    if "mpeg" in formato or "mp3" in formato: return ".mp3"
    if "mp4" in formato or "m4a" in formato: return ".m4a"
    if "wav" in formato: return ".wav"
    return ".wav"

def transcribir_audio(
    audio_bytes: bytes,
    language: str = "es",
    beam_size: int = 1,
) -> tuple[bool, str]:
    """Transcribe audio usando Faster-Whisper con parámetros optimizados."""
    global _transcriptor
    if not audio_bytes:
        return False, "No se recibio audio."

    if _transcriptor is None and not inicializar_transcriptor():
        return False, "No se pudo cargar el transcriptor local."

    # Usar un archivo temporal para Whisper
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    try:
        tmp.write(audio_bytes)
        tmp.close()

        segmentos, _ = _transcriptor.transcribe(
            tmp.name,
            language=language,
            beam_size=beam_size,
            vad_filter=True, # Usar VAD interno de Whisper también
            vad_parameters=dict(min_silence_duration_ms=500),
            condition_on_previous_text=False,
        )
        
        texto = " ".join(segment.text.strip() for segment in segmentos if segment.text.strip()).strip()
        
        if not texto:
            return False, ""
            
        return True, texto
    except Exception as e:
        return False, f"Error en STT: {e}"
    finally:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass

