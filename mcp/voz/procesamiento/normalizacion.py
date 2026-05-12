"""
🧹 NORMALIZACIÓN — EL LIMPIADOR DE TEXTO
----------------------------------------
Whisper no es perfecto. A veces escucha "presa" cuando dijiste "fresa". 
Este archivo se encarga de corregir esos errores para que la IA no se confunda.

FLUJO DESDE LA PERSPECTIVA DE LA NORMALIZACIÓN:
1. RECIBIR: Toma el texto crudo enviado por 'stt.py'.
2. LIMPIAR: Quita tildes, mayúsculas y puntos.
3. CORREGIR: Usa REGLAS_CORRECCION para errores comunes.
4. REFINAR: Usa el catálogo para corregir sabores mal escuchados.
5. ENTREGAR: Envía la frase limpia a 'pipeline_voz.py' para ir al 'agente.py'.
"""
import re
import unicodedata
from rapidfuzz import fuzz

REGLAS_CORRECCION = {
    "efecto": "efectivo",
    "presa": "fresa",
    "tarjetaa": "tarjeta",
    "elado": "helado",
    "helao": "helado",
    "aunidades": "unidades",
    "anador": "añadir",
}

def normalizar_texto_base(texto: str) -> str:
    """Limpieza básica de texto."""
    if not texto:
        return ""
    texto = texto.strip().lower()
    # Eliminar acentos
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    # Limpiar caracteres especiales
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto

def corregir_palabras_comunes(texto: str) -> str:
    """Aplica reglas fijas de corrección."""
    palabras = texto.split()
    for i, p in enumerate(palabras):
        if p in REGLAS_CORRECCION:
            palabras[i] = REGLAS_CORRECCION[p]
    return " ".join(palabras)

def normalizar_para_ia(texto: str, catalogo_sabores: list[str] = None) -> str:
    """Normalización completa incluyendo corrección de sabores si se provee el catálogo."""
    t = normalizar_texto_base(texto)
    if not t:
        return ""

    t = corregir_palabras_comunes(t)

    if catalogo_sabores:
        palabras = t.split()
        for i, palabra in enumerate(palabras):
            if len(palabra) < 4 or palabra.isdigit():
                continue
            
            # Busqueda difusa en el catálogo de sabores
            for sabor in catalogo_sabores:
                if fuzz.ratio(palabra, sabor) > 85:
                    palabras[i] = sabor
                    break
        t = " ".join(palabras)

    return t
