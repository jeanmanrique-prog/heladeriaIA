"""
app/ia/voz/controller.py
──────────────────────────
Controlador para la lógica de voz.
"""

import streamlit as st
import time
from utils.session_manager import SessionManager
from utils.peticiones import APIClient

class VozController:
    @staticmethod
    def iniciar_llamada():
        """Inicializa una nueva sesión de llamada."""
        st.session_state["_voz_session_id"] = str(int(time.time()))
        st.session_state["call_greeted"] = False

    @staticmethod
    def finalizar_llamada():
        """Limpia el estado al colgar."""
        st.session_state["_voz_session_id"] = ""
        st.session_state["call_greeted"] = False
