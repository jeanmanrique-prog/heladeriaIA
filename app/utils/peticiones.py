"""
app/utils/peticiones.py
────────────────────────
Cliente centralizado para todas las peticiones a la API del backend.
"""

import requests
import streamlit as st

# Intentar obtener la URL de la API desde el estado o usar default
API_URL = "http://127.0.0.1:8000"

class APIClient:
    @staticmethod
    def _fetch(endpoint: str):
        try:
            r = requests.get(f"{API_URL}{endpoint}", timeout=5)
            if r.status_code == 200:
                return r.json()
            return None
        except Exception:
            return None

    @staticmethod
    def _post(endpoint: str, payload: dict):
        try:
            r = requests.post(f"{API_URL}{endpoint}", json=payload, timeout=8)
            if r.status_code in (200, 201):
                return True, r.json()
            
            # Intentar obtener el error del detalle de FastAPI
            try:
                error_msg = r.json().get("detail", "Error desconocido")
            except:
                error_msg = f"Error servidor ({r.status_code})"
            return False, error_msg
        except Exception as e:
            return False, str(e)

    @classmethod
    def check_api(cls):
        """Verifica si el servidor backend está online."""
        try:
            r = requests.get(f"{API_URL}/", timeout=2)
            return r.status_code == 200
        except Exception:
            return False

    @classmethod
    def obtener_inventario(cls):
        return cls._fetch("/inventario")

    @classmethod
    def obtener_alertas(cls):
        return cls._fetch("/inventario/alertas")

    @classmethod
    def obtener_ventas(cls):
        return cls._fetch("/ventas")

    @classmethod
    def obtener_movimientos(cls):
        return cls._fetch("/movimientos")

    @classmethod
    def obtener_productos(cls):
        return cls._fetch("/productos")

    @classmethod
    def obtener_sabores(cls):
        return cls._fetch("/sabores")

    @classmethod
    def crear_venta(cls, payload: dict):
        return cls._post("/vender", payload)

    @classmethod
    def entrada_inventario(cls, payload: dict):
        return cls._post("/inventario/entrada", payload)

    @classmethod
    def enviar_mensaje_chat(cls, payload: dict):
        return cls._post("/chat", payload)

    @classmethod
    def enviar_chunk_voz(cls, files, data):
        """Envía audio a voz-stream (usado en modo llamada)."""
        try:
            r = requests.post(f"{API_URL}/voz-stream", files=files, data=data, timeout=5)
            return r.json() if r.status_code == 200 else None
        except Exception:
            return None
