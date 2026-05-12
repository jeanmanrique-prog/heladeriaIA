"""
🛠️ CATALOG TOOLS — EL BUSCADOR DE PRODUCTOS
-------------------------------------------
Este archivo permite a la IA consultar qué hay disponible. 
Está integrado con db_heladeria.py para garantizar que, si el servidor 
principal falla (por mantenimiento o red), Urban siempre tenga acceso al catálogo 
real. Esto es posible porque db_heladeria.py lee directamente el archivo de la 
base de datos (.db) sin necesidad de internet ni de que el servidor esté encendido.
"""
import requests
from mcp.config import API_URL
from mcp.voz.ia.db_heladeria import obtener_catalogo

def obtener_catalogo_real() -> list:
    """
    TOOL: Obtiene el catálogo completo de productos con stock y precios.
    Prioriza API, con fallback centralizado a db_heladeria.py.
    """
    # 1. Intentar via API
    try:
        r = requests.get(f"{API_URL}/productos", timeout=2)
        if r.status_code == 200:
            productos = r.json().get("productos", [])
            if productos: return productos
    except:
        pass

    # 2. Fallback Centralizado (Usa db_heladeria.py)
    return obtener_catalogo()
