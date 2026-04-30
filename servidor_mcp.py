"""
Punto de entrada seguro para el servidor MCP del proyecto.

El repositorio usa la carpeta local `mcp/` para su propio codigo y tambien
depende de la libreria externa `mcp`. Ejecutar `python -m mcp.server`
resuelve primero al modulo local y termina en un import circular.

Este archivo importa la libreria externa temporalmente, restaura el path
del proyecto y luego carga la configuracion y herramientas locales.
"""

from __future__ import annotations

import asyncio
import importlib
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent


def _cargar_runtime_mcp():
    """Carga la libreria externa `mcp` sin mezclarla con el paquete local."""
    removidos: list[str] = []
    for candidato in ("", str(ROOT_DIR)):
        while candidato in sys.path:
            sys.path.remove(candidato)
            removidos.append(candidato)

    try:
        server_mod = importlib.import_module("mcp.server")
        stdio_mod = importlib.import_module("mcp.server.stdio")
        types_mod = importlib.import_module("mcp.types")
    finally:
        # Limpiar los modulos externos para poder importar despues el paquete local.
        for nombre in list(sys.modules):
            if nombre == "mcp" or nombre.startswith("mcp."):
                sys.modules.pop(nombre, None)
        for entrada in reversed(removidos):
            sys.path.insert(0, entrada)

    return server_mod.Server, stdio_mod.stdio_server, types_mod


Server, stdio_server, mcp_types = _cargar_runtime_mcp()

from mcp.config import API_URL  # noqa: E402
from mcp.tools.inventario_tools import (  # noqa: E402
    agregar_stock_tool,
    consultar_alertas_tool,
    consultar_inventario_tool,
    consultar_movimientos_tool,
)
from mcp.tools.productos_tools import (  # noqa: E402
    consultar_productos_tool,
    consultar_sabores_tool,
)
from mcp.tools.ventas_tools import (  # noqa: E402
    consultar_detalle_venta_tool,
    consultar_ventas_tool,
    registrar_venta_tool,
    resumen_negocio_tool,
)


server = Server("heladeria-mcp")


@server.list_tools()
async def handle_list_tools() -> list[mcp_types.Tool]:
    return [
        mcp_types.Tool(
            name="consultar_inventario",
            description="Obtiene el inventario completo, niveles de stock y alertas.",
            inputSchema={"type": "object", "properties": {}},
        ),
        mcp_types.Tool(
            name="consultar_alertas",
            description="Muestra solo los productos que estan por debajo del stock minimo.",
            inputSchema={"type": "object", "properties": {}},
        ),
        mcp_types.Tool(
            name="consultar_productos",
            description="Muestra el catalogo con IDs y precios. Usar siempre antes de vender si el usuario no dice el ID.",
            inputSchema={"type": "object", "properties": {}},
        ),
        mcp_types.Tool(
            name="consultar_sabores",
            description="Lista de sabores de helado que vende el negocio.",
            inputSchema={"type": "object", "properties": {}},
        ),
        mcp_types.Tool(
            name="registrar_venta",
            description="Registra una venta. Requiere metodo de pago ('efectivo' o 'tarjeta') y lista de items.",
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
                                "cantidad": {"type": "integer"},
                            },
                            "required": ["id_producto", "cantidad"],
                        },
                    },
                },
                "required": ["metodo_pago", "items"],
            },
        ),
        mcp_types.Tool(
            name="agregar_stock",
            description="Agrega unidades al inventario de un producto especifico por su ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "id_producto": {"type": "integer", "description": "ID del producto en la BD"},
                    "cantidad": {"type": "integer", "description": "Unidades a sumar al stock"},
                    "motivo": {"type": "string", "description": "Motivo (ej. 'Reposicion')"},
                },
                "required": ["id_producto", "cantidad"],
            },
        ),
        mcp_types.Tool(
            name="consultar_ventas",
            description="Devuelve el historial general de ventas.",
            inputSchema={"type": "object", "properties": {}},
        ),
        mcp_types.Tool(
            name="consultar_detalle_venta",
            description="Busca que productos especificos se vendieron en una venta concreta.",
            inputSchema={
                "type": "object",
                "properties": {
                    "id_venta": {
                        "type": "integer",
                        "description": "El ID numerico de la venta a consultar.",
                    }
                },
                "required": ["id_venta"],
            },
        ),
        mcp_types.Tool(
            name="consultar_movimientos",
            description="Muestra el registro de entradas y salidas del inventario con fechas y motivos.",
            inputSchema={"type": "object", "properties": {}},
        ),
        mcp_types.Tool(
            name="resumen_negocio",
            description="Da una metrica ejecutiva rapida de total de inventario y ventas globales.",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[mcp_types.TextContent]:
    arguments = arguments or {}

    if name == "consultar_inventario":
        return consultar_inventario_tool(arguments)
    if name == "consultar_alertas":
        return consultar_alertas_tool(arguments)
    if name == "consultar_productos":
        return consultar_productos_tool(arguments)
    if name == "consultar_sabores":
        return consultar_sabores_tool(arguments)
    if name == "registrar_venta":
        return registrar_venta_tool(arguments)
    if name == "agregar_stock":
        return agregar_stock_tool(arguments)
    if name == "consultar_ventas":
        return consultar_ventas_tool(arguments)
    if name == "consultar_detalle_venta":
        return consultar_detalle_venta_tool(arguments)
    if name == "consultar_movimientos":
        return consultar_movimientos_tool(arguments)
    if name == "resumen_negocio":
        return resumen_negocio_tool(arguments)
    raise ValueError(f"Herramienta desconocida: {name}")


async def main():
    import requests

    try:
        respuesta = requests.get(f"{API_URL}/", timeout=2)
        if respuesta.status_code == 200:
            print("   API Backend detectada. Conexion exitosa.", file=sys.stderr)
    except Exception:
        print("   No se pudo conectar con la API.", file=sys.stderr)
        print("   Inicia el servidor antes de usar el MCP.", file=sys.stderr)

    print("   Servidor MCP listo.\n", file=sys.stderr)

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
