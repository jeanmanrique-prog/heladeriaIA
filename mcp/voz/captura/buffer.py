import io
import wave

class AudioBuffer:
    def __init__(self, sample_rate=16000):
        self.buffer = io.BytesIO()
        self.sample_rate = sample_rate
        self.n_frames = 0

    def add_chunks(self, chunks: bytes):
        """Agrega chunks de audio al buffer."""
        self.buffer.write(chunks)
        # Asumiendo 16-bit PCM (2 bytes por frame)
        self.n_frames += len(chunks) // 2

    def get_wav_bytes(self) -> bytes:
        """Retorna el contenido actual del buffer como un archivo WAV válido en bytes."""
        output = io.BytesIO()
        with wave.open(output, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2) # 16-bit
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(self.buffer.getvalue())
        return output.getvalue()

    def clear(self):
        """Limpia el buffer."""
        self.buffer = io.BytesIO()
        self.n_frames = 0

    def __len__(self):
        return self.n_frames
