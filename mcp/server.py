"""
Servidor MCP — Heladería
Expone las herramientas de la heladería como un servidor MCP estándar
para que cualquier agente compatible (IA de Gelateria Urbana u otros) las consuma.

Uso:
    python mcp/server.py

Requiere:
    - API corriendo en http://127.0.0.1:8000
    - pip install mcp requests
"""

import sys
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

from mcp.config import API_URL
from mcp.tools.inventario_tools import consultar_inventario_tool, consultar_alertas_tool, agregar_stock_tool, consultar_movimientos_tool
from mcp.tools.productos_tools import consultar_productos_tool, consultar_sabores_tool
from mcp.tools.ventas_tools import registrar_venta_tool, consultar_ventas_tool, consultar_detalle_venta_tool, resumen_negocio_tool

server = Server("heladeria-mcp")

# ==========================================
# REGISTRO DE HERRAMIENTAS
# ==========================================

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="consultar_inventario",
            description="Obtiene el inventario completo, niveles de stock y alertas.",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="consultar_alertas",
            description="Muestra solo los productos que están por debajo del stock mínimo.",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="consultar_productos",
            description="Muestra el catálogo con IDs y precios. Usar SIEMPRE antes de vender si el usuario no dice el ID.",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="consultar_sabores",
            description="Lista de sabores de helado que vende el negocio.",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="registrar_venta",
            description="Registra una venta. Requiere método de pago ('efectivo' o 'tarjeta') y lista de items.",
            inputSchema={
                "type": "object",
                "properties": {
                    "metodo_pago": {"type": "string", "enum": ["efectivo", "tarjeta"]},
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id_producto": {"type": "integer"},
                                "cantidad": {"type": "integer"}
                            },
                            "required": ["id_producto", "cantidad"]
                        }
                    }
                },
                "required": ["metodo_pago", "items"]
            }
        ),
        types.Tool(
            name="agregar_stock",
            description="Agrega unidades al inventario de un producto específico por su ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "id_producto": {"type": "integer", "description": "ID del producto en la BD"},
                    "cantidad": {"type": "integer", "description": "Unidades a sumar al stock"},
                    "motivo": {"type": "string", "description": "Motivo (ej. 'Reposición')"}
                },
                "required": ["id_producto", "cantidad"]
            }
        ),
        types.Tool(
            name="consultar_ventas",
            description="Devuelve el historial general de ventas.",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="consultar_detalle_venta",
            description="Busca qué productos específicos se vendieron en una venta concreta.",
            inputSchema={
                "type": "object",
                "properties": {
                    "id_venta": {"type": "integer", "description": "El ID numérico de la venta a consultar."}
                },
                "required": ["id_venta"]
            }
        ),
        types.Tool(
            name="consultar_movimientos",
            description="Muestra el registro de entradas y salidas del inventario con fechas y motivos.",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="resumen_negocio",
            description="Da una métrica ejecutiva rápida de total de inventario y ventas globales.",
            inputSchema={"type": "object", "properties": {}}
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    if arguments is None:
        arguments = {}

    if name == "consultar_inventario":
        return consultar_inventario_tool(arguments)
    elif name == "consultar_alertas":
        return consultar_alertas_tool(arguments)
    elif name == "consultar_productos":
        return consultar_productos_tool(arguments)
    elif name == "consultar_sabores":
        return consultar_sabores_tool(arguments)
    elif name == "registrar_venta":
        return registrar_venta_tool(arguments)
    elif name == "agregar_stock":
        return agregar_stock_tool(arguments)
    elif name == "consultar_ventas":
        return consultar_ventas_tool(arguments)
    elif name == "consultar_detalle_venta":
        return consultar_detalle_venta_tool(arguments)
    elif name == "consultar_movimientos":
        return consultar_movimientos_tool(arguments)
    elif name == "resumen_negocio":
        return resumen_negocio_tool(arguments)
    else:
        raise ValueError(f"Herramienta desconocida: {name}")

async def main():
    import requests
    try:
        r = requests.get(f"{API_URL}/", timeout=2)
        if r.status_code == 200:
            print("   ✅ API Backend detectada. Conexión exitosa.", file=sys.stderr)
    except Exception:
        print("   ❌ No se pudo conectar con la API.", file=sys.stderr)
        print("   Inicia el servidor antes de usar el MCP.", file=sys.stderr)

    print("   ✅ Servidor MCP listo.\n", file=sys.stderr)

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())