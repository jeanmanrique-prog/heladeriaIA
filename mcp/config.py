import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
API_URL = "http://127.0.0.1:8000"
MODELO = "llama3.2:1b"
VOZ_MODELO = str(BASE_DIR / "voz_es.onnx")
VOZ_CONFIG = str(BASE_DIR / "voz_es.onnx.json")
ASR_MODELO = "tiny"
MENSAJE_BIENVENIDA = "Ey parcero bienvenido a Gelateria Urban los mejores helados de Colombia, bro. Que se te antoja hoy?"
MENSAJE_BIENVENIDA_CLIENTE = (
    '{"accion":"saludo","mensaje":"Ey parcero bienvenido a Gelateria Urban los mejores helados de Colombia, bro. Que se te antoja hoy?"}'
)
