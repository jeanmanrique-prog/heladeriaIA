"""
🔊 STT (Speech-To-Text) — EL TRADUCTOR DE SONIDO
-----------------------------------------------
Este archivo es el "traductor" que convierte las ondas de audio en palabras escritas.
Utiliza **Whisper** (específicamente la versión optimizada 'faster-whisper').

¿QUÉ ES WHISPER?
Es una inteligencia artificial de OpenAI entrenada para entender el habla humana 
en muchos idiomas. Aquí lo usamos para que Urban pueda "leer" lo que el cliente dice.

FLUJO DESDE LA PERSPECTIVA DEL STT:
1. RECIBIR: El 'pipeline_voz.py' le entrega el archivo de audio (.wav) desde 'buffer.py'.
2. CARGAR: El motor Whisper se carga en memoria.
3. TRANSCRIBIR: Convierte el audio en texto palabra por palabra.
4. NORMALIZAR: Se envía el texto a 'normalizacion.py' para limpiar errores.
5. ENTREGAR: Devuelve la frase limpia a 'pipeline_voz.py' para enviarla al 'agente.py'.
"""
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

    except Exception:
        return False

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

