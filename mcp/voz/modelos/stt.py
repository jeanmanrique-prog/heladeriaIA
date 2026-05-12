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

¿POR QUÉ USAMOS EL MODELO BASE EN VEZ DEL TINY?
Es normal que haya errores de reconocimiento. Los robots tienen una pronunciación "perfecta" que el modelo de IA tiny (el más pequeño y rápido) entiende fácil. Los humanos, en cambio, arrastramos palabras, hablamos más lento o tenemos acentos que el modelo pequeño no alcanza a procesar bien.

He diseñado un Plan de Mejora de Precisión de Voz para que Urban sea mucho más inteligente al escucharte.
Los 3 pilares del plan son:
1. Subir de nivel el modelo: Cambiar el motor de tiny a base. Es un poco más pesado, pero mucho más capaz de entender a una persona real.
2. Darle pistas (Contexto): Vamos a inyectar un "prompt inicial" en Whisper con palabras como helado, chocolate, fresa, efectivo. Así, cuando escuche algo parecido a "colate", la IA sabrá que lo más probable es que hayas dicho "chocolate".
3. Búsqueda profunda: Aumentaremos el esfuerzo que hace la IA por evaluar diferentes opciones de palabras antes de decidirse por una, lo que ayuda mucho con las personas que hablan despacio.
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
    beam_size: int = 5,
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
            initial_prompt="Helado, heladería, Urban, chocolate, fresa, vainilla, ron pasas, macadamia, efectivo, tarjeta, datáfono, pedir, comprar, menú, catálogo, nequi, daviplata.",
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

