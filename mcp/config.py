import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
API_URL = "http://127.0.0.1:8000"
MODELO = "llama3.2:1b"
VOZ_MODELO = str(BASE_DIR / "voz_es.onnx")
VOZ_CONFIG = str(BASE_DIR / "voz_es.onnx.json")
ASR_MODELO = "tiny"
MENSAJE_BIENVENIDA = "Ey parcero bienvenido a Gelateria Urban los mejores helados de Colombia, que se te antoja hoy?"
MENSAJE_BIENVENIDA_CLIENTE = (
    '{"accion":"saludo","mensaje":"Ey parcero bienvenido a Gelateria Urban los mejores helados de Colombia, que se te antoja hoy?"}'
)

# Configuraciones específicas para el sistema de voz
SAMPLE_RATE = 16000
BLOCK_SIZE = 1024
CHANNELS = 1
DTYPE = "int16"
SILENCE_THRESHOLD = 500
MIN_AUDIO_LEN_FOR_STT = 8000 # aprox 0.5s

# Prompts exportados para conveniencia
from .prompts.prompt_base import SYSTEM_PROMPT, SYSTEM_PROMPT_VENDEDOR
from .prompts.prompt_sugerencias import PROMPT_SUGERENCIAS

