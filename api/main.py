"""
Módulo API (api/main.py)
-------------------------
Este archivo contiene el servidor FastAPI principal.
Expone los endpoints para interactuar con la base de datos y manejar el flujo de voz.
Forma parte de la nueva arquitectura modular recomendada.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Importar routers modulares
from api.admin.gestion_manual.inventario import router as inventario_router
from api.admin.gestion_manual.ventas import router as ventas_router
from api.ia.llamada import router as llamada_router

app = FastAPI(title="API Heladería", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(inventario_router, tags=["Inventario & Catálogo"])
app.include_router(ventas_router, tags=["Ventas"])
app.include_router(llamada_router, tags=["Llamada IA"])

@app.get("/", summary="Estado de la API")
def read_root():
    return {
        "mensaje": "API Heladería funcionando correctamente 🍦",
        "version": "1.0.0",
        "endpoints": [
            "/sabores", "/productos", "/inventario",
            "/inventario/alertas", "/inventario/entrada",
            "/vender", "/ventas", "/movimientos", "/voz-stream"
        ]
    }
