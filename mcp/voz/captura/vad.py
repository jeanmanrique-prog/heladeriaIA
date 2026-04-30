import numpy as np
import collections

class VAD:
    def __init__(self, sample_rate=16000, frame_duration_ms=30, threshold=0.5):
        self.sample_rate = sample_rate
        self.frame_duration_ms = frame_duration_ms
        self.frame_size = int(sample_rate * frame_duration_ms / 1000)
        self.threshold = threshold
        self.buffer = collections.deque(maxlen=10) # Para suavizado
        
        # Intentar cargar Silero VAD si está disponible
        self.model = None
        try:
            # Este es un placeholder. En una implementación real, se cargaría el modelo de Silero.
            # import torch
            # model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad')
            # self.model = model
            pass
        except Exception:
            pass

    def is_speech(self, audio_chunk: bytes) -> bool:
        """Determina si hay voz en el chunk de audio."""
        if not audio_chunk:
            return False
            
        audio_data = np.frombuffer(audio_chunk, dtype=np.int16)
        
        if self.model:
            # Lógica para Silero VAD (requiere torch)
            # audio_float = audio_data.astype(np.float32) / 32768.0
            # prob = self.model(torch.from_numpy(audio_float), self.sample_rate).item()
            # return prob > self.threshold
            pass
            
        # Fallback: Energía RMS con suavizado
        energy = np.sqrt(np.mean(audio_data.astype(np.float32)**2))
        self.buffer.append(energy)
        avg_energy = sum(self.buffer) / len(self.buffer)
        
        return avg_energy > 500 # Umbral empírico mejorado
