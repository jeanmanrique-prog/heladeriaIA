"""
mcp/tools/catalog.py
─────────────────────
Módulo aislado para obtener el catálogo real de productos.
NO depende de mcp.types ni del SDK de MCP — sólo usa sqlite3 y requests.
Esto evita el conflicto de nombres entre el paquete local mcp/ y el SDK mcp.
"""

import sqlite3
import requests
from pathlib import Path

# Ruta directa a la BD
_DB_PATH = Path(__file__).resolve().parent.parent.parent / "db" / "heladeria.db"

_API_URL = "http://127.0.0.1:8000"


def _get_catalog_from_db() -> list:
    """
    Lee el catálogo directamente de SQLite.
    Fallback robusto — no depende de la API ni del SDK MCP.
    """
    try:
        con = sqlite3.connect(str(_DB_PATH))
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("""
            SELECT
                p.id_producto,
                p.nombre_producto,
                p.precio_unitario,
                s.nombre AS sabor,
                COALESCE(i.cantidad_unidades, 0) AS stock
            FROM productos p
            JOIN sabores s ON s.id_sabor = p.id_sabor
            LEFT JOIN inventario i ON i.id_producto = p.id_producto
            WHERE p.activo = 1
            ORDER BY p.id_producto
        """)
        rows = cur.fetchall()
        con.close()
        return [dict(r) for r in rows]
    except Exception:
        return []


def get_catalog() -> list:
    """
    Retorna lista real de productos con nombre, precio y stock.
    Prioridad: API REST → SQLite directo.
    NUNCA devuelve lista vacía si hay datos en la BD.
    """
    # 1. Intentar via API REST
    try:
        r = requests.get(f"{_API_URL}/productos", timeout=2)
        if r.status_code == 200:
            productos = r.json().get("productos", [])
            if productos:
                return productos
    except Exception:
        pass

    # 2. Fallback directo a SQLite
    return _get_catalog_from_db()
