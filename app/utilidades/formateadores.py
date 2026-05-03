"""
app/utils/formateadores.py
───────────────────────────
Utilidades para formateo de texto, moneda y mensajes de IA con nombres en español.
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

def corregir_codificacion(texto: str) -> str:
    """Corrige errores comunes de codificación (mojibake)."""
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

def obtener_texto_visible(texto: str) -> str:
    """Extrae el texto natural de una respuesta JSON del vendedor y lo corrige."""
    if not texto:
        return ""
    
    # 1. Intentar decodificar si es un JSON completo
    try:
        data = json.loads(texto)
        if isinstance(data, dict):
            # Si es el formato del vendedor, sacar 'mensaje'
            msg = data.get("mensaje", "")
            # Si el mensaje mismo es un JSON (sopa), intentar decodificarlo otra vez
            try:
                inner_data = json.loads(msg)
                if isinstance(inner_data, dict):
                    msg = inner_data.get("mensaje", msg)
            except:
                pass
            return corregir_codificacion(msg)
    except:
        pass

    # 2. Si no es JSON, intentar extraer el mensaje natural vía pipeline de voz
    texto_natural = corregir_codificacion(texto_voz_respuesta_vendedor(texto)).strip()
    
    if texto_natural and not (texto_natural.startswith("{") and texto_natural.endswith("}")):
        return texto_natural
        
    # 3. Limpieza de emergencia: quitar llaves si quedaron restos
    limpio = re.sub(r'\{.*?"mensaje":\s*"(.*?)"\}', r'\1', texto, flags=re.DOTALL)
    limpio = limpio.replace("{", "").replace("}", "").replace('"', '').strip()
    
    return corregir_codificacion(limpio) or "Sin respuesta."

def cargar_json_seguro(texto: str) -> dict or None:
    """Intenta cargar un JSON de forma segura extrayendo el objeto entre llaves."""
    if not texto:
        return None
    try:
        # Buscar el primer '{' y el último '}' para extraer JSON
        inicio = texto.find('{')
        fin = texto.rfind('}') + 1
        if inicio != -1 and fin != 0:
            json_str = texto[inicio:fin]
            data = json.loads(json_str)
            return data if isinstance(data, dict) else None
    except Exception:
        pass
    return None
