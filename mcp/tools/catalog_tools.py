import sqlite3
import requests
from pathlib import Path
from mcp.config import API_URL

_DB_PATH = Path(__file__).resolve().parent.parent.parent / "db" / "heladeria.db"

def obtener_catalogo_real() -> list:
    """
    TOOL: Obtiene el catálogo completo de productos con stock y precios.
    Prioriza API, con fallback a SQLite.
    """
    # 1. Intentar via API
    try:
        r = requests.get(f"{API_URL}/productos", timeout=2)
        if r.status_code == 200:
            productos = r.json().get("productos", [])
            if productos: return productos
    except:
        pass

    # 2. Fallback a SQLite
    try:
        con = sqlite3.connect(str(_DB_PATH))
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("""
            SELECT p.id_producto, p.nombre_producto, p.precio_unitario, 
                   s.nombre AS sabor, COALESCE(i.cantidad_unidades, 0) AS stock
            FROM productos p
            JOIN sabores s ON s.id_sabor = p.id_sabor
            LEFT JOIN inventario i ON i.id_producto = p.id_producto
            WHERE p.activo = 1
        """)
        rows = [dict(r) for r in cur.fetchall()]
        con.close()
        return rows
    except:
        return []
