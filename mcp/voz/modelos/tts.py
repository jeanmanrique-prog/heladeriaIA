import io
import os
import re
import tempfile
import threading
import wave
from mcp.config import VOZ_MODELO, VOZ_CONFIG

_voz = None  # instancia global de PiperVoice

def inicializar_voz() -> bool:
    """Carga el modelo de voz. Retorna True si tuvo éxito."""
    global _voz
    if _voz is not None:
        return True
    try:
        from piper import PiperVoice
        if not os.path.exists(VOZ_MODELO):
            print(f"  ⚠️  Archivo de voz no encontrado: {VOZ_MODELO}")
            return False
        if not os.path.exists(VOZ_CONFIG):
            print(f"  ⚠️  Configuracion de voz no encontrada: {VOZ_CONFIG}")
            return False
        _voz = PiperVoice.load(VOZ_MODELO, config_path=VOZ_CONFIG)
        return True
    except ImportError:
        print("  ⚠️  piper-tts no instalado. Ejecuta: pip install piper-tts")
        return False
    except Exception as e:
        print(f"  ⚠️  Error al cargar voz: {e}")
        return False

def limpiar_texto_para_voz(texto: str) -> str:
    """Limpia el texto para que suene natural: elimina emojis, markdown y simbolos."""
    texto = re.sub(r'[^\x00-\x7FáéíóúÁÉÍÓÚñÑüÜ¿¡.,;:!?()\-\s]', '', texto)
    texto = re.sub(r'[\*\_\#\`]', '', texto)
    texto = re.sub(r'^[\-=]{3,}$', '', texto, flags=re.MULTILINE)
    texto = re.sub(r'\n{2,}', '. ', texto)
    texto = re.sub(r'\n', ', ', texto)
    texto = re.sub(r'\s{2,}', ' ', texto).strip()
    if len(texto) > 400:
        texto = texto[:400] + "..."
    return texto

def sintetizar_audio_wav(texto: str) -> bytes | None:
    """Genera un WAV en memoria para reproducirlo en web o escritorio."""
    global _voz
    if _voz is None and not inicializar_voz():
        return None

    texto_limpio = limpiar_texto_para_voz(texto)
    if not texto_limpio.strip():
        return None

    try:
        buffer = io.BytesIO()
        syn_config = None
        try:
            from piper.config import SynthesisConfig
            # voz masculina cuando el modelo tiene varios speakers (M=0, F=1)
            speaker_id = 0 if getattr(_voz.config, "num_speakers", 1) > 1 else None
            syn_config = SynthesisConfig(
                speaker_id=speaker_id,
                length_scale=1.05,
                noise_scale=0.72,
                noise_w_scale=0.88,
                volume=1.02,
            )
        except Exception:
            syn_config = None

        with wave.open(buffer, "wb") as wav_file:
            if syn_config is not None:
                _voz.synthesize_wav(texto_limpio, wav_file, syn_config=syn_config)
            else:
                _voz.synthesize_wav(texto_limpio, wav_file)
        return buffer.getvalue()
    except Exception:
        return None

def hablar(texto: str, gestor_turnos=None):
    """Sintetiza el texto y lo reproduce en un hilo separado para no bloquear la consola."""
    if _voz is None and not inicializar_voz():
        return

    def _reproducir():
        try:
            if gestor_turnos:
                gestor_turnos.ia_comienza_hablar()
                
            audio_wav = sintetizar_audio_wav(texto)
            if not audio_wav:
                if gestor_turnos: gestor_turnos.ia_termina_hablar()
                return
                
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            tmp.write(audio_wav)
            tmp.close()
            
            if os.name == 'nt':  # Windows
                import winsound
                # Nota: winsound.PlaySound no es fácilmente interrumpible desde otro hilo
                # a menos que se use SND_ASYNC y se llame con NULL.
                if gestor_turnos and gestor_turnos.debe_cancelar_tts():
                    os.unlink(tmp.name)
                    return
                winsound.PlaySound(tmp.name, winsound.SND_FILENAME)
            else:  # Linux / Raspberry Pi
                import subprocess
                proc = subprocess.Popen(["aplay", "-q", tmp.name])
                while proc.poll() is None:
                    if gestor_turnos and gestor_turnos.debe_cancelar_tts():
                        proc.terminate()
                        break
                    import time
                    time.sleep(0.1)
                    
            os.unlink(tmp.name)
        except Exception:
            pass
        finally:
            if gestor_turnos:
                gestor_turnos.ia_termina_hablar()

    threading.Thread(target=_reproducir, daemon=True).start()

