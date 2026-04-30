
import requests
from mcp import types
from mcp.config import API_URL

def api_get(endpoint: str) -> dict:
    r = requests.get(f"{API_URL}{endpoint}", timeout=5)
    r.raise_for_status()
    return r.json()

def api_post(endpoint: str, payload: dict) -> dict:
    r = requests.post(f"{API_URL}{endpoint}", json=payload, timeout=5)
    r.raise_for_status()
    return r.json()

def ok(texto: str) -> list[types.TextContent]:
    return [types.TextContent(type="text", text=texto)]

def error(texto: str) -> list[types.TextContent]:
    return [types.TextContent(type="text", text=f"❌ Error: {texto}")]

def consultar_inventario_tool(arguments: dict):
    try:
        data = api_get("/inventario")
        return ok(f"INVENTARIO ACTUAL:\n{data}")
    except Exception as e:
        return error(str(e))

def consultar_alertas_tool(arguments: dict):
    try:
        data = api_get("/inventario/alertas")
        return ok(f"ALERTAS DE STOCK:\n{data}")
    except Exception as e:
        return error(str(e))

def agregar_stock_tool(arguments: dict):
    try:
        id_prod = arguments["id_producto"]
        cant = arguments["cantidad"]
        motivo = arguments.get("motivo", "Reposición")
        payload = {"id_producto": id_prod, "cantidad": cant, "motivo": motivo}
        data = api_post("/inventario/entrada", payload)
        return ok(f"Stock agregado:\n{data}")
    except Exception as e:
        return error(str(e))

def consultar_movimientos_tool(arguments: dict):
    try:
        data = api_get("/movimientos")
        return ok(f"HISTORIAL MOVIMIENTOS:\n{data}")
    except Exception as e:
        return error(str(e))
