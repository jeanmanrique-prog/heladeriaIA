"""
app/admin/ia.py
────────────────
Módulo de administrador para interacción con IA.
"""

import streamlit as st
from pathlib import Path
from ia.chat.ui import render_chat_interface
from componentes.llamada import mostrar_llamada_ia

def render_ia_admin(pagina: str, api_ok: bool, theme: dict):
    """Renderiza las páginas de IA para el administrador (Chat y Llamada)."""
    if pagina == "💬 Chat con IA":
        _render_chat_page(api_ok, theme)
    elif pagina == "📞 Llamada con IA":
        _render_call_page(api_ok, theme)

def _render_chat_page(api_ok: bool, theme: dict):
    st.markdown("<style>[data-testid='stMain'] { padding: 0 !important; } .block-container { padding: 0 !important; }</style>", unsafe_allow_html=True)
    
    col_chat, col_img = st.columns([1.2, 0.8])

    with col_chat:
        st.markdown('<div style="padding: 40px 10% 40px 10%;">', unsafe_allow_html=True)
        render_chat_interface(api_ok=api_ok, theme=theme)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_img:
        _render_urban_image("urban_stock.png", theme['BG'])

def _render_call_page(api_ok: bool, theme: dict):
    st.markdown("<style>[data-testid='stMain'] { padding: 0 !important; }</style>", unsafe_allow_html=True)
    mostrar_llamada_ia(
        api_ok,
        st.session_state.get("helio_ollama_ok", False),
        st.session_state.get("helio_asr_activo", False),
        theme
    )

def _render_urban_image(img_name: str, bg_color: str):
    root_dir = Path(__file__).resolve().parent.parent.parent
    img_path = root_dir / "imagenes" / img_name
    if not img_path.exists():
        img_path = root_dir / "imagenes" / "urban_comiendo.png"
    
    if img_path.exists():
        st.image(str(img_path), use_container_width=True)
    else:
        st.markdown(f"<div style='background: {bg_color}; height: 100vh;'></div>", unsafe_allow_html=True)
