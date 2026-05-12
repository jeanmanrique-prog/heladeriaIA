"""
⚙️ CONFIG — EL PANEL DE CONTROL DEL PROYECTO
-------------------------------------------
Este archivo centraliza todas las variables "mágicas" del sistema. Si quieres 
cambiar el modelo de IA, la voz de Urban o la URL de la base de datos, 
este es el único lugar donde debes hacerlo.

¿QUÉ HACE EXACTAMENTE?
1. DEFINE RUTAS: Localiza dónde están los modelos de voz (.onnx) y la BD.
2. CONFIGURA MODELOS: Elige qué IA usar (ej. Llama 3.2 o Whisper).
3. ESTABLECE PARÁMETROS: Ajusta qué tan sensible es el micrófono y cuánto 
   debe durar un silencio antes de que la IA responda.

EJEMPLO DE USO:
Si notas que Urban responde muy lento, podrías venir aquí y cambiar 
'MODELO' de uno pesado a uno más liviano. O si quieres que Urban sea más 
"paisa", cambiarías el 'MENSAJE_BIENVENIDA' aquí.
"""
import os
from pathlib import Path

MCP_DIR = Path(__file__).resolve().parent
API_URL = "http://127.0.0.1:8000"
MODELO = "llama3.2:1b"
VOZ_MODELO = str(MCP_DIR / "voz_es.onnx")
VOZ_CONFIG = str(MCP_DIR / "voz_es.onnx.json")
ASR_MODELO = "base"  # Usamos 'base' en lugar de 'tiny' para entender mejor el habla humana natural.
MENSAJE_BIENVENIDA = "Ey parcero bienvenido a Gelateria Urban los mejores helados de Colombia, que se te antoja hoy?"
MENSAJE_BIENVENIDA_CLIENTE = (
    '{"accion":"saludo","mensaje":"Ey parcero bienvenido a Gelateria Urban los mejores helados de Colombia, que se te antoja hoy?"}'
)

# Configuraciones específicas para el sistema de voz
SAMPLE_RATE = 16000
BLOCK_SIZE = 1024
CHANNELS = 1
DTYPE = "int16"
SILENCE_THRESHOLD = 700  # Aumentado de 500 a 700 para dar más tiempo a personas que hablan despacio.
MIN_AUDIO_LEN_FOR_STT = 8000 # aprox 0.5s

# Prompts exportados para conveniencia
from .prompts.prompt_base import SYSTEM_PROMPT, SYSTEM_PROMPT_VENDEDOR
from .prompts.prompt_sugerencias import PROMPT_SUGERENCIAS
from .prompts.prompt_voz_maestro import PROMPT_SISTEMA_VOZ_COMPLETO

