"""
app/ia/llamada/interfaz/interfaz_admin.py
──────────────────────────────────────────
Orquestador de vista para la Llamada de IA en el panel de Administrador.
"""

import streamlit as st
from ia.llamada.interfaz.interfaz_llamada import render_realtime_call
from ia.llamada.estilos.estilos_admin import obtener_estilos_admin

def render_pagina_llamada_admin(theme: dict):
    """Renderiza la página completa de llamada para el administrador."""
    # Inyectar estilos de página específicos del admin
    st.markdown(obtener_estilos_admin(), unsafe_allow_html=True)
    
    # En el admin, la llamada se renderiza directamente
    render_realtime_call(theme)
