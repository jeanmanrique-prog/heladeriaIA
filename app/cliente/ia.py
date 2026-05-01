"""
app/cliente/ia.py
──────────────────
Módulo de cliente para interacción con IA.
"""

import streamlit as st
from pathlib import Path
from ia.chat.ui import render_chat_interface
from componentes.llamada import mostrar_llamada_ia

def render_ia_cliente(pagina: str, api_ok: bool, theme: dict):
    """Renderiza las páginas de IA para el cliente (Chat y Llamada)."""
    if pagina == "💬 Chat con IA":
        _render_chat_page(api_ok, theme)
    elif pagina == "📞 Llamada con IA":
        _render_call_page(api_ok, theme)

def _render_chat_page(api_ok: bool, theme: dict):
    # CSS para el chat
    st.markdown(f"""
        <style>
        [data-testid="stMain"] {{ padding: 0 !important; }}
        .block-container {{ padding: 0 !important; max-width: 100% !important; }}
        /* Imagen lateral alineada al fondo de la tarjeta */
        .img-bottom-align {{
            display: flex;
            align-items: flex-end;
            height: 100%;
            padding-bottom: 0;
        }}
        .img-bottom-align img {{
            width: 100%;
            display: block;
            border-radius: 0 0 16px 0;
        }}
        </style>
    """, unsafe_allow_html=True)

    col_chat, col_img = st.columns([1.2, 0.8])

    with col_chat:
        st.markdown('<div style="padding: 40px 10% 40px 10%;">', unsafe_allow_html=True)
        render_chat_interface(api_ok=api_ok, theme=theme)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_img:
        _render_urban_image_bottom("urban_chateando.png", theme['BG'])

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


def _render_urban_image_bottom(img_name: str, bg_color: str):
    """Imagen alineada al fondo — su base coincide con el final de la tarjeta del chat."""
    root_dir = Path(__file__).resolve().parent.parent.parent
    img_path = root_dir / "imagenes" / img_name
    if not img_path.exists():
        img_path = root_dir / "imagenes" / "urban_comiendo.png"
    
    if img_path.exists():
        import base64
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
