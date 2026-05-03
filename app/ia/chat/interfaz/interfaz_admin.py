"""
app/ia/chat/interfaz/interfaz_admin.py
───────────────────────────────────────
Orquestador de vista para el Chat de IA en el panel de Administrador.
"""

import streamlit as st
from pathlib import Path
from ia.chat.interfaz.interfaz_chat import render_chat_interface
from ia.chat.estilos.estilos_admin import obtener_estilos_admin

def render_pagina_chat_admin(api_ok: bool, theme: dict):
    """Renderiza la página completa de chat para el administrador."""
    # Inyectar estilos de página específicos del admin
    st.markdown(obtener_estilos_admin(), unsafe_allow_html=True)
    
    col_chat, col_img = st.columns([1.2, 0.8])

    with col_chat:
        st.markdown('<div style="padding: 40px 10% 40px 10%;">', unsafe_allow_html=True)
        render_chat_interface(api_ok=api_ok, theme=theme)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_img:
        _render_urban_image("urban_stock.png", theme['BG'])

def _render_urban_image(img_name: str, bg_color: str):
    root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
    img_path = root_dir / "imagenes" / img_name
    if not img_path.exists():
        img_path = root_dir / "imagenes" / "urban_comiendo.png"
    
    if img_path.exists():
        st.image(str(img_path), use_container_width=True)
    else:
        st.markdown(f"<div style='background: {bg_color}; height: 100vh;'></div>", unsafe_allow_html=True)
