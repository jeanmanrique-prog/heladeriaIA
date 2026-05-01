"""
productos_tools.py
──────────────────
Herramientas MCP de productos.
IMPORTANTE: get_catalog() se importa desde catalog.py (módulo aislado sin mcp.types).
inventario_tools se importa de forma LAZY (dentro de funciones) para evitar
el ImportError: cannot import name 'types' from 'mcp' al iniciar la app.
"""

# get_catalog viene de un módulo SIN dependencia de mcp.types
from mcp.tools.catalog import get_catalog, _get_catalog_from_db


def consultar_productos_tool(arguments: dict):
    # Import lazy: solo se ejecuta cuando se llama la función (desde el MCP server)
    from mcp.tools.inventario_tools import ok, error
    try:
        productos = get_catalog()
        if not productos:
            return error("No hay productos disponibles en la base de datos.")
        lineas = []
        for p in productos:
            precio = p.get("precio_unitario") or p.get("precio") or 0
            stock = p.get("stock") or 0
            try:
                stock = int(stock)
            except (TypeError, ValueError):
                stock = 0
            stock_txt = f"{stock} uds" if stock > 0 else "AGOTADO"
            lineas.append(
                f"• {p.get('nombre_producto','?')} | Sabor: {p.get('sabor','?')} | "
                f"Precio: {int(precio):,} pesos | Stock: {stock_txt} | ID: {p.get('id_producto','?')}"
            )
        return ok("CATÁLOGO PRODUCTOS:\n" + "\n".join(lineas))
    except Exception as e:
        return error(str(e))


def consultar_sabores_tool(arguments: dict):
    from mcp.tools.inventario_tools import api_get, ok, error
    try:
        data = api_get("/sabores")
        return ok(f"SABORES ACTIVOS:\n{data}")
    except Exception as e:
        productos = _get_catalog_from_db()
        sabores = sorted({p["sabor"] for p in productos if p.get("sabor")})
        if sabores:
            return ok("SABORES ACTIVOS:\n" + ", ".join(sabores))
        return error(str(e))

