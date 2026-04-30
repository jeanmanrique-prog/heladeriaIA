
from mcp.tools.inventario_tools import api_get, ok, error

def consultar_productos_tool(arguments: dict):
    try:
        data = api_get("/productos")
        return ok(f"CATÁLOGO PRODUCTOS:\n{data}")
    except Exception as e:
        return error(str(e))

def consultar_sabores_tool(arguments: dict):
    try:
        data = api_get("/sabores")
        return ok(f"SABORES ACTIVOS:\n{data}")
    except Exception as e:
        return error(str(e))
