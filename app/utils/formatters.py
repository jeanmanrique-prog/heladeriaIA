"""
app/utils/formatters.py
────────────────────────
Utilidades para formateo de texto, moneda y mensajes de IA.
"""

import re
import json
from mcp.voz.pipeline.pipeline_voz import texto_voz_respuesta_vendedor

def formatear_precio(valor) -> str:
    """Formatea un valor a moneda COP: $ 10.000"""
    try:
        if valor is None or valor == "" or valor == "None":
            return "$ 0"
        
        # Limpiar caracteres no numéricos excepto el punto si es decimal
        num_str = re.sub(r'[^\d.]', '', str(valor))
        if not num_str:
            return "$ 0"
            
        n = float(num_str)
        return f"$ {n:,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return "$ 0"

def corregir_mojibake(texto: str) -> str:
    """Corrige errores comunes de codificación (UTF-8 mal interpretado)."""
    if not texto:
        return texto
    reemplazos = {
        "Â¿": "?", "Â¡": "!", "Ã¡": "á", "Ã©": "é",
        "Ã­": "í", "Ã³": "ó", "Ãº": "ú", "Ã±": "ñ",
        "Ã ": "Á", "Ã‰": "É", "Ã ": "Í", "Ã“": "Ó",
        "Ãš": "Ú", "Ã‘": "Ñ",
    }
    limpio = texto
    for origen, destino in reemplazos.items():
        limpio = limpio.replace(origen, destino)
    
    # Limpieza final de duplicados y caracteres raros
    limpio = limpio.replace("¿", "?").replace("¡", "!")
    while "??" in limpio:
        limpio = limpio.replace("??", "?")
    return limpio

def texto_visible_asistente(texto: str) -> str:
    """Extrae el texto natural de una respuesta JSON del vendedor y lo corrige."""
    if not texto:
        return ""
        
    # Intentar limpiar como si fuera un JSON del vendedor
    texto_natural = corregir_mojibake(texto_voz_respuesta_vendedor(texto)).strip()
    
    if texto_natural:
        return texto_natural
        
    # Si no es JSON o falló la extracción, devolver el texto limpio
    return corregir_mojibake(texto.strip()) or "Sin respuesta."

def cargar_json_seguro(texto: str) -> dict | None:
    """Intenta cargar un JSON de forma segura."""
    if not texto:
        return None
    try:
        # Buscar el primer '{' y el último '}' para extraer JSON si hay basura alrededor
        start = texto.find('{')
        end = texto.rfind('}') + 1
        if start != -1 and end != 0:
            json_str = texto[start:end]
            data = json.loads(json_str)
            return data if isinstance(data, dict) else None
    except Exception:
        pass
    return None
