"""
app/ia/voz/controller.py
──────────────────────────
Controlador para la lógica de voz.
"""

import streamlit as st
import time
from utilidades.gestor_sesion import GestorSesion
from utilidades.peticiones import ClienteAPI

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
