"""
app/componentes/llamada.py
───────────────────────────
Componente para gestionar la interfaz de llamada en tiempo real.
"""

import streamlit as st
from utils.session_manager import SessionManager
from ia.voz.ui import render_realtime_call

def mostrar_llamada_ia(api_ok: bool, ollama_ok: bool, asr_activo: bool, theme: dict):
    """Renderiza la interfaz de llamada directamente en el área principal."""
    if not (api_ok and ollama_ok and asr_activo):
        st.warning("⚠️ La llamada requiere que el Backend, Ollama y el Transcriptor estén activos.")
        return

    # Pasar el diccionario de tema completo para soportar modo oscuro/claro
    render_realtime_call(theme)
