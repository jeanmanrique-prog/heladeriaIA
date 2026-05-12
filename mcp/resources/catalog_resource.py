import requests
import json
from mcp.config import API_URL
from mcp.voz.ia.db_heladeria import obtener_catalogo

class CatalogResource:
    """
    📖 CATALOG RESOURCE — LA "HOJA DE PRECIOS" INSTANTÁNEA
    -----------------------------------------------------
    Este recurso es fundamental para la velocidad del Chat y la Llamada con IA.
    
    ¿POR QUÉ ES MEJOR QUE LAS TOOLS PARA CONSULTAR EL CATÁLOGO?
    1. VELOCIDAD (Latencia Cero): Las Tools requieren que la IA "piense" y decida llamar a una función. 
       El Resource ya está inyectado en el contexto; la IA responde de inmediato porque "ya lo está viendo".
    2. REDUCCIÓN DE ERRORES: Al tener el catálogo frente a sus ojos, la IA no tiene que recordar 
       precios de una llamada anterior, evitando confusiones.
    
    ¿POR QUÉ ES SEGURO QUE ENTREGA DATOS REALES?
    Este archivo NO guarda una lista estática. Cada vez que se solicita el texto del catálogo, 
    el método realiza una petición HTTP en vivo a nuestra propia API de inventario.
    
    FLUJO DE DATOS:
    [IA] -> [CatalogResource] -> [GET /inventario] -> [Base de Datos SQLite]
    
    Esto garantiza que si cambias un precio o se agota un helado en la base de datos, 
    la IA lo sabrá en el siguiente mensaje sin necesidad de reiniciar nada.

    INTEGRACIÓN CON DB_HELADERIA:
    Si la API de inventario no está disponible (ej. servidor caído o sin red), 
    este recurso usa automáticamente 'db_heladeria.py'. Como este último lee 
    el archivo SQLite directamente del disco, la IA nunca se queda "muda" 
    aunque el sistema principal esté en mantenimiento.
    """
    @staticmethod
    def get_catalog_text() -> str:
        items = []
        # 1. Intentar via API
        try:
            r = requests.get(f"{API_URL}/inventario", timeout=2)
            r.raise_for_status()
            items = r.json().get("inventario", [])
        except Exception:
            # 2. Fallback a DB Directa si la API falla
            items = obtener_catalogo()
            
        if not items:
            return "CATÁLOGO: No hay productos disponibles en este momento."
        
        txt = "═══ CATÁLOGO REAL DE PRODUCTOS ═══\n"
        for p in items:
            stock = p.get("stock", 0)
            if stock > 0:
                txt += f"- {p['sabor']}: {p['precio_unitario']:,} pesos (Stock: {stock})\n"
        txt += "══════════════════════════════════"
        return txt.replace(",", ".")
