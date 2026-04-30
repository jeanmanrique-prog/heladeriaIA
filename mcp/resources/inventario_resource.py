import requests
from mcp.config import API_URL

class InventarioResource:
    @staticmethod
    def get_context():
        """Obtiene el contexto del inventario para la IA en formato de solo lectura."""
        try:
            r = requests.get(f"{API_URL}/inventario", timeout=5)
            r.raise_for_status()
            data = r.json()
            items = data.get("inventario", [])
            
            contexto = "SABORES Y STOCK ACTUAL:\n"
            for item in items:
                contexto += f"- {item['sabor']}: {item['stock']} unidades disponibles.\n"
            return contexto
        except Exception:
            return "No se pudo cargar el contexto del inventario."
