try:
    import sounddevice as sd
except ImportError:
    sd = None
import numpy as np
import io
import wave
import os
import tempfile

class CapturadorAudio:
    def __init__(self, sample_rate=16000, block_size=1024):
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.stream = None

    def iniciar(self, callback):
        """Inicia la captura de audio con un callback para procesar cada bloque."""
        if sd is None:
            print("Error: sounddevice no está disponible o no está instalado.")
            return
            
        def sd_callback(indata, frames, time, status):
            if status:
                print(f"Error en stream de audio: {status}")
            callback(indata.copy())

        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype=np.int16,
            blocksize=self.block_size,
            callback=sd_callback
        )
        self.stream.start()

    def detener(self):
        """Detiene la captura."""
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

def guardar_audio_temporal(audio_bytes: bytes, audio_format: str | None = None) -> str:
    """Guarda bytes de audio en un archivo temporal y devuelve la ruta."""
    # Suffix logic moved here to avoid circular imports
    formato = (audio_format or "").strip().lower()
    suffix = ".wav"
    if "webm" in formato: suffix = ".webm"
    elif "ogg" in formato: suffix = ".ogg"
    elif "mp3" in formato: suffix = ".mp3"
    
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(audio_bytes)
    tmp.close()
    return tmp.name

def obtener_info_wav(audio_bytes: bytes):
    """Extrae información básica de un buffer WAV."""
    try:
        with wave.open(io.BytesIO(audio_bytes), 'rb') as wav:
            params = wav.getparams()
            return {
                "nchannels": params.nchannels,
                "sampwidth": params.sampwidth,
                "framerate": params.framerate,
                "nframes": params.nframes
            }
    except Exception:
        return None
