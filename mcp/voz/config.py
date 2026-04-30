from mcp.config import *

# Configuraciones específicas para el sistema de voz
SAMPLE_RATE = 16000
BLOCK_SIZE = 1024
CHANNELS = 1
DTYPE = "int16"

# Umbrales de silencio y detección
SILENCE_THRESHOLD = 500
MIN_AUDIO_LEN_FOR_STT = 8000 # aprox 0.5s
