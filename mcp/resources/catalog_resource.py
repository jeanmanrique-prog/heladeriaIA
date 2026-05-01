import requests
import json
from mcp.config import API_URL

class CatalogResource:
    """
    Recurso de solo lectura para proveer el catálogo de productos a la IA.
    Evita que el modelo invente precios o sabores.
    """
    @staticmethod
    def get_catalog_text() -> str:
        try:
            r = requests.get(f"{API_URL}/inventario", timeout=5)
            r.raise_for_status()
            items = r.json().get("inventario", [])
            
            if not items:
                return "CATÁLOGO: No hay productos disponibles en este momento."
            
            txt = "═══ CATÁLOGO REAL DE PRODUCTOS ═══\n"
            for p in items:
                stock = p.get("stock", 0)
                if stock > 0:
                    txt += f"- {p['sabor']}: {p['precio_unitario']:,} pesos (Stock: {stock})\n"
            txt += "══════════════════════════════════"
            return txt.replace(",", ".")
        except Exception as e:
            return f"Error al cargar catálogo: {str(e)}"
