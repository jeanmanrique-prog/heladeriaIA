"""
app/utils/session_manager.py
─────────────────────────────
Gestión centralizada del estado de sesión (st.session_state).
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
from utils.formatters import texto_visible_asistente, cargar_json_seguro


MAX_TURNOS_UI = 24
PROMPT_VERSION = "ventas-2026-04-23-v12"

class SessionManager:
    @staticmethod
    def initialize():
        """Inicializa las variables globales de sesión."""
        if "role" not in st.session_state:
            st.session_state.role = "client"
            
        if "pagina_actual" not in st.session_state:
            st.session_state.pagina_actual = "🛒 Comprar" if st.session_state.role == "client" else "📊 Dashboard"
            
        if "helio_ollama_ok" not in st.session_state:
            SessionManager.refresh_services()

    @staticmethod
    def state_key(mode: str, suffix: str) -> str:
        """Genera una llave de estado basada en el rol y el modo (chat/call)."""
        role = str(st.session_state.get("role", "client")).strip().lower()
        role = "admin" if role == "admin" else "client"
        return f"helio_{role}_{mode}_{suffix}"

    @staticmethod
    def refresh_services(mode: str = "chat"):
        """Verifica y refresca el estado de los servicios (Ollama, STT, TTS)."""
        ok, mensaje = verificar_ollama()
        st.session_state["helio_ollama_ok"] = ok
        st.session_state["helio_ollama_msg"] = mensaje
        
        if mode == "call":
            if not st.session_state.get("helio_voz_activa"):
                st.session_state["helio_voz_activa"] = inicializar_voz()
            if not st.session_state.get("helio_asr_activo"):
                st.session_state["helio_asr_activo"] = inicializar_transcriptor()

    @staticmethod
    def initialize_mode(mode: str):
        """Inicializa el estado específico para un modo (chat o call)."""
        historial_key = SessionManager.state_key(mode, "historial")
        mensajes_key = SessionManager.state_key(mode, "mensajes")
        prompt_version_key = SessionManager.state_key(mode, "prompt_version")

        # Cargar historial base si no existe
        if historial_key not in st.session_state:
            st.session_state[historial_key] = SessionManager.get_base_history()
            st.session_state["primera_vez_voz"] = True

        # Cargar mensajes UI si no existe
        if mensajes_key not in st.session_state:
            st.session_state[mensajes_key] = [
                SessionManager.create_ui_message("assistant", MENSAJE_BIENVENIDA_CLIENTE, source="system")
            ]

        # Reset si la versión del prompt cambió
        if st.session_state.get(prompt_version_key) != PROMPT_VERSION:
            SessionManager.reset_conversation(mode)
            st.session_state[prompt_version_key] = PROMPT_VERSION

        # Otros defaults
        defaults = {
            SessionManager.state_key(mode, "audio_respuesta"): None,
            SessionManager.state_key(mode, "audio_autoplay"): False,
            SessionManager.state_key(mode, "saludo_enviado"): False,
            SessionManager.state_key(mode, "respuesta_en_curso"): False,
            "urban_brand": "Urban"
        }
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    @staticmethod
    def get_base_history():
        return [
            {"role": "system", "content": SYSTEM_PROMPT_VENDEDOR},
            {"role": "assistant", "content": MENSAJE_BIENVENIDA_CLIENTE},
        ]

    @staticmethod
    def create_ui_message(role: str, contenido: str, source: str = "text") -> dict:
        payload = cargar_json_seguro(contenido) if role == "assistant" else None
        display = texto_visible_asistente(contenido) if role == "assistant" else contenido.strip()
        return {
            "role": role,
            "raw": contenido,
            "display": display or contenido,
            "payload": payload,
            "source": source,
        }

    @staticmethod
    def reset_conversation(mode: str):
        """Limpia el historial y mensajes de un modo específico."""
        st.session_state[SessionManager.state_key(mode, "historial")] = SessionManager.get_base_history()
        st.session_state[SessionManager.state_key(mode, "mensajes")] = [
            SessionManager.create_ui_message("assistant", MENSAJE_BIENVENIDA_CLIENTE, source="system")
        ]
        st.session_state[SessionManager.state_key(mode, "audio_respuesta")] = None
        st.session_state[SessionManager.state_key(mode, "audio_autoplay")] = False
        st.session_state[SessionManager.state_key(mode, "saludo_enviado")] = False
        st.session_state[SessionManager.state_key(mode, "respuesta_en_curso")] = False

    @staticmethod
    def trim_history(mode: str):
        """Mantiene el historial dentro de los límites de memoria."""
        h_key = SessionManager.state_key(mode, "historial")
        m_key = SessionManager.state_key(mode, "mensajes")
        
        historial = st.session_state[h_key]
        if len(historial) > (2 + MAX_TURNOS_UI * 2):
            st.session_state[h_key] = historial[:2] + historial[-(MAX_TURNOS_UI * 2):]
            
        mensajes = st.session_state[m_key]
        if len(mensajes) > (1 + MAX_TURNOS_UI * 2):
            st.session_state[m_key] = mensajes[:1] + mensajes[-(MAX_TURNOS_UI * 2):]
