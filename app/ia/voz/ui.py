"""
app/ia/voz/ui.py
─────────────────
Interfaz de usuario para la llamada en tiempo real con soporte de temas.
"""

import streamlit as st
import streamlit.components.v1 as components
from componentes.ai_ui_lib import get_ai_call_html
from utils.session_manager import SessionManager
import base64
from pathlib import Path

def render_realtime_call(theme: dict):
    """Renderiza la interfaz de llamada con soporte completo de colores del tema."""
    SessionManager.initialize_mode("call")
    
    # Colores del tema
    accent = theme.get("ACCENT", "#ff1493")
    bg = theme.get("BG", "#ffffff")
    text = theme.get("TEXT", "#1a1a1a")
    card = theme.get("BG2", "#ffffff")
    border = theme.get("ACCENT", "#ff1493")

    # Cargar recursos visuales desde la raíz del proyecto
    root_dir = Path(__file__).resolve().parent.parent.parent.parent
    images_dir = root_dir / "imagenes"
    
    # Avatar
    avatar_path = images_dir / "perfil_ia.png"
    avatar_src = "🍦"
    if avatar_path.exists():
        with open(avatar_path, "rb") as f:
            b64_av = base64.b64encode(f.read()).decode()
        avatar_src = f'data:image/png;base64,{b64_av}'

    # Imagen lateral (Urban Comiendo)
    urban_path = images_dir / "urban_comiendo.png"
    urban_src = ""
    if urban_path.exists():
        with open(urban_path, "rb") as f:
            b64_u = base64.b64encode(f.read()).decode()
        urban_src = f'data:image/png;base64,{b64_u}'

    saved_sid = st.session_state.get("_voz_session_id") or ""
    is_fresh = not st.session_state.get("call_greeted", False)
    
    if is_fresh:
        st.session_state["call_greeted"] = True
        st.session_state["_voz_session_id"] = ""
        saved_sid = ""

    # Pasar todos los parámetros requeridos por ai_ui_lib.py, incluyendo colores del tema
    html_code = get_ai_call_html(
        api_url="http://127.0.0.1:8000",
        saved_sid=saved_sid,
        is_fresh=is_fresh,
        avatar_src=avatar_src,
        urban_src=urban_src,
        accent_color=accent,
        bg_color=bg,
        text_color=text,
        card_bg=card,
        border_color=border
    )
    
    components.html(html_code, height=900, scrolling=False)
