"""
app/utils/gestor_sesion.py
───────────────────────────
Gestión centralizada del estado de sesión (st.session_state) con nombres en español.
"""

import streamlit as st
import time
from mcp.voz.pipeline.pipeline_voz import (
    verificar_ollama, 
    inicializar_voz, 
    inicializar_transcriptor,
    SYSTEM_PROMPT_VENDEDOR,
    MENSAJE_BIENVENIDA_CLIENTE
)
from utilidades.formateadores import obtener_texto_visible, cargar_json_seguro


MAX_TURNOS_UI = 24
VERSION_PROMPT = "ventas-2026-04-23-v12"

class GestorSesion:
    @staticmethod
    def inicializar():
        """Inicializa las variables globales de sesión."""
        if "role" not in st.session_state:
            st.session_state.role = "client"
            
        if "pagina_actual" not in st.session_state:
            st.session_state.pagina_actual = "🛒 Comprar" if st.session_state.role == "client" else "📊 Dashboard"
            
        if "helio_ollama_ok" not in st.session_state:
            GestorSesion.refrescar_servicios()

    @staticmethod
    def obtener_llave_estado(modo: str, sufijo: str) -> str:
        """Genera una llave de estado basada en el rol y el modo (chat/call)."""
        rol = str(st.session_state.get("role", "client")).strip().lower()
        rol = "admin" if rol == "admin" else "client"
        return f"helio_{rol}_{modo}_{sufijo}"

    @staticmethod
    def refrescar_servicios(modo: str = "chat"):
        """Verifica y refresca el estado de los servicios (Ollama, STT, TTS)."""
        ok, mensaje = verificar_ollama()
        st.session_state["helio_ollama_ok"] = ok
        st.session_state["helio_ollama_msg"] = mensaje
        
        if modo == "call":
            if not st.session_state.get("helio_voz_activa"):
                st.session_state["helio_voz_activa"] = inicializar_voz()
            if not st.session_state.get("helio_asr_activo"):
                st.session_state["helio_asr_activo"] = inicializar_transcriptor()

    @staticmethod
    def inicializar_modo(modo: str):
        """Inicializa el estado específico para un modo (chat o call)."""
        historial_llave = GestorSesion.obtener_llave_estado(modo, "historial")
        mensajes_llave = GestorSesion.obtener_llave_estado(modo, "mensajes")
        version_prompt_llave = GestorSesion.obtener_llave_estado(modo, "prompt_version")

        # Cargar historial base si no existe
        if historial_llave not in st.session_state:
            st.session_state[historial_llave] = GestorSesion.obtener_historial_base()
            st.session_state["primera_vez_voz"] = True

        # Cargar mensajes UI si no existe
        if mensajes_llave not in st.session_state:
            st.session_state[mensajes_llave] = [
                GestorSesion.crear_mensaje_ui("assistant", MENSAJE_BIENVENIDA_CLIENTE, fuente="system")
            ]

        # Reiniciar si la versión del prompt cambió
        if st.session_state.get(version_prompt_llave) != VERSION_PROMPT:
            GestorSesion.reiniciar_conversacion(modo)
            st.session_state[version_prompt_llave] = VERSION_PROMPT

        # Otros valores por defecto
        valores_defecto = {
            GestorSesion.obtener_llave_estado(modo, "audio_respuesta"): None,
            GestorSesion.obtener_llave_estado(modo, "audio_autoplay"): False,
            GestorSesion.obtener_llave_estado(modo, "saludo_enviado"): False,
            GestorSesion.obtener_llave_estado(modo, "respuesta_en_curso"): False,
            "urban_brand": "Urban"
        }
        for llave, valor in valores_defecto.items():
            if llave not in st.session_state:
                st.session_state[llave] = valor

    @staticmethod
    def obtener_historial_base():
        return [
            {"role": "system", "content": SYSTEM_PROMPT_VENDEDOR},
            {"role": "assistant", "content": MENSAJE_BIENVENIDA_CLIENTE},
        ]

    @staticmethod
    def crear_mensaje_ui(rol: str, contenido: str, fuente: str = "text") -> dict:
        payload = cargar_json_seguro(contenido) if rol == "assistant" else None
        display = obtener_texto_visible(contenido) if rol == "assistant" else contenido.strip()
        return {
            "role": rol,
            "raw": contenido,
            "display": display or contenido,
            "payload": payload,
            "source": fuente,
        }

    @staticmethod
    def reiniciar_conversacion(modo: str):
        """Limpia el historial y mensajes de un modo específico."""
        st.session_state[GestorSesion.obtener_llave_estado(modo, "historial")] = GestorSesion.obtener_historial_base()
        st.session_state[GestorSesion.obtener_llave_estado(modo, "mensajes")] = [
            GestorSesion.crear_mensaje_ui("assistant", MENSAJE_BIENVENIDA_CLIENTE, fuente="system")
        ]
        st.session_state[GestorSesion.obtener_llave_estado(modo, "audio_respuesta")] = None
        st.session_state[GestorSesion.obtener_llave_estado(modo, "audio_autoplay")] = False
        st.session_state[GestorSesion.obtener_llave_estado(modo, "saludo_enviado")] = False
        st.session_state[GestorSesion.obtener_llave_estado(modo, "respuesta_en_curso")] = False

    @staticmethod
    def recortar_historial(modo: str):
        """Mantiene el historial dentro de los límites de memoria."""
        h_llave = GestorSesion.obtener_llave_estado(modo, "historial")
        m_llave = GestorSesion.obtener_llave_estado(modo, "mensajes")
        
        historial = st.session_state[h_llave]
        if len(historial) > (2 + MAX_TURNOS_UI * 2):
            st.session_state[h_llave] = historial[:2] + historial[-(MAX_TURNOS_UI * 2):]
            
        mensajes = st.session_state[m_llave]
        if len(mensajes) > (1 + MAX_TURNOS_UI * 2):
            st.session_state[m_llave] = mensajes[:1] + mensajes[-(MAX_TURNOS_UI * 2):]

    @staticmethod
    def obtener_id_sesion(modo: str) -> str:
        """
        Devuelve un ID de sesión estable y único por usuario/modo.
        """
        id_llave = GestorSesion.obtener_llave_estado(modo, "session_id")
        if id_llave not in st.session_state:
            import uuid
            st.session_state[id_llave] = str(uuid.uuid4())
        return st.session_state[id_llave]
