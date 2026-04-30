
from mcp.tools.inventario_tools import api_get, api_post, ok, error

def registrar_venta_tool(arguments: dict):
    try:
        metodo = arguments["metodo_pago"]
        items = arguments["items"]
        payload = {"metodo_pago": metodo, "items": items}
        data = api_post("/vender", payload)
        return ok(f"Venta Registrada Exitosamente:\n{data}")
    except Exception as e:
        return error(str(e))

def consultar_ventas_tool(arguments: dict):
    try:
        data = api_get("/ventas")
        return ok(f"HISTORIAL DE VENTAS:\n{data}")
    except Exception as e:
        return error(str(e))

def consultar_detalle_venta_tool(arguments: dict):
    try:
        id_venta = arguments["id_venta"]
        data = api_get(f"/ventas/{id_venta}")
        return ok(f"DETALLE VENTA {id_venta}:\n{data}")
    except Exception as e:
        return error(str(e))

def resumen_negocio_tool(arguments: dict):
    try:
        inv = api_get("/inventario")
        vts = api_get("/ventas")
        return ok(f"RESUMEN EJECUTIVO:\nInventario: {len(inv.get('inventario',[]))} items.\nVentas: {len(vts.get('ventas',[]))} transacciones.")
    except Exception as e:
        return error(str(e))
