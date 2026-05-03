"""
app/ia/llamada/interfaz/interfaz_cliente.py
───────────────────────────────────────────
Orquestador de vista para la Llamada de IA en el panel de Cliente.
"""

import streamlit as st
from ia.llamada.interfaz.interfaz_llamada import render_realtime_call
from ia.llamada.estilos.estilos_cliente import obtener_estilos_cliente

def render_pagina_llamada_cliente(theme: dict):
    """Renderiza la página completa de llamada para el cliente."""
    # Inyectar estilos específicos del cliente
    st.markdown(obtener_estilos_cliente(), unsafe_allow_html=True)
    
    # Renderizar la interfaz de llamada
    render_realtime_call(theme)
