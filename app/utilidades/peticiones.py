"""
app/utilidades/peticiones.py
─────────────────────────────
Cliente centralizado para todas las peticiones a la API del backend.
"""

import requests
import streamlit as st

# URL de la API del backend
URL_API = "http://127.0.0.1:8000"

class ClienteAPI:
    @staticmethod
    def _obtener(endpoint: str):
        """Realiza una petición GET al endpoint especificado."""
        try:
            r = requests.get(f"{URL_API}{endpoint}", timeout=5)
            if r.status_code == 200:
                return r.json()
            return None
        except Exception:
            return None

    @staticmethod
    def _enviar(endpoint: str, payload: dict):
        """Realiza una petición POST con un cuerpo JSON."""
        try:
            r = requests.post(f"{URL_API}{endpoint}", json=payload, timeout=8)
            if r.status_code in (200, 201):
                return True, r.json()
            
            # Intentar obtener el mensaje de error del detalle de FastAPI
            try:
                mensaje_error = r.json().get("detail", "Error desconocido")
            except:
                mensaje_error = f"Error del servidor ({r.status_code})"
            return False, mensaje_error
        except Exception as e:
            return False, str(e)

    @classmethod
    def verificar_api(cls):
        """Verifica si el servidor backend está en línea."""
        try:
            r = requests.get(f"{URL_API}/", timeout=2)
            return r.status_code == 200
        except Exception:
            return False

    @classmethod
    def obtener_inventario(cls):
        return cls._obtener("/inventario")

    @classmethod
    def obtener_alertas(cls):
        return cls._obtener("/inventario/alertas")

    @classmethod
    def obtener_ventas(cls):
        return cls._obtener("/ventas")

    @classmethod
    def obtener_movimientos(cls):
        return cls._obtener("/movimientos")

    @classmethod
    def obtener_productos(cls):
        return cls._obtener("/productos")

    @classmethod
    def obtener_sabores(cls):
        return cls._obtener("/sabores")

    @classmethod
    def crear_venta(cls, datos: dict):
        return cls._enviar("/vender", datos)

    @classmethod
    def registrar_entrada_inventario(cls, datos: dict):
        return cls._enviar("/inventario/entrada", datos)

    @classmethod
    def enviar_mensaje_chat(cls, datos: dict):
        return cls._enviar("/chat", datos)

    @classmethod
    def enviar_audio_voz(cls, archivos, datos):
        """Envía audio al endpoint de streaming de voz."""
        try:
            r = requests.post(f"{URL_API}/voz-stream", files=archivos, data=datos, timeout=5)
            return r.json() if r.status_code == 200 else None
        except Exception:
            return None
