"""
app/ia/chat/interfaz/interfaz_cliente.py
────────────────────────────────────────
Orquestador de vista para el Chat de IA en el panel de Cliente.
"""

import streamlit as st
import base64
from pathlib import Path
from ia.chat.interfaz.interfaz_chat import render_chat_interface
from ia.chat.estilos.estilos_cliente import obtener_estilos_cliente

def render_pagina_chat_cliente(api_ok: bool, theme: dict):
    """Renderiza la página completa de chat para el cliente."""
    # Inyectar estilos específicos del cliente
    st.markdown(obtener_estilos_cliente(), unsafe_allow_html=True)

    col_chat, col_img = st.columns([1.2, 0.8])

    with col_chat:
        st.markdown('<div style="padding: 40px 10% 40px 10%;">', unsafe_allow_html=True)
        render_chat_interface(api_ok=api_ok, theme=theme)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_img:
        _render_urban_image_bottom("urban_chateando.png", theme['BG'])

def _render_urban_image_bottom(img_name: str, bg_color: str):
    """Imagen alineada al fondo para el chat del cliente."""
    root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
    img_path = root_dir / "imagenes" / img_name
    if not img_path.exists():
        img_path = root_dir / "imagenes" / "urban_comiendo.png"
    
    if img_path.exists():
        with open(str(img_path), "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(f"""
            <div style="
                display: flex;
                align-items: flex-end;
                height: 100%;
                min-height: 620px;
                padding: 40px 0 0 0;
            ">
                <img src="data:image/png;base64,{b64}"
                     style="width:100%; display:block; object-fit: contain; object-position: bottom;"
                />
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='background: {bg_color}; height: 100%;'></div>", unsafe_allow_html=True)
