"""
app/componentes/sidebar.py
───────────────────────────
Componente lateral de navegación y estado de servicios.
"""

import streamlit as st
import base64
from pathlib import Path
from utils.session_manager import SessionManager
from utils.formatters import texto_visible_asistente
from mcp.voz.pipeline.pipeline_voz import MENSAJE_BIENVENIDA_CLIENTE, sintetizar_audio_wav
import streamlit.components.v1 as components

def render_sidebar(api_ok: bool, theme: dict):
    """Renderiza el sidebar completo con navegación por roles (Estilo Original)."""
    with st.sidebar:
        # 1. Logo
        _render_logo()
        st.markdown("---")

        # 2. Saludo Inicial (Solo la primera vez que entra a la app)
        _render_greeting_audio()

        # 3. Navegación según rol
        if st.session_state.role == "client":
            _render_client_nav()
        else:
            _render_admin_nav()

        st.markdown("---")

        # 4. Acceso Admin / Cerrar Sesión
        if st.session_state.role == "client":
            _render_admin_access()
        else:
            if st.button("Cerrar Sesión", use_container_width=True):
                st.session_state.role = "client"
                st.session_state.pagina_actual = "🛒 Comprar"
                st.rerun()

        st.markdown("---")

        # 5. Status de API
        _render_api_status(api_ok, theme)

def _render_logo():
    # Encontrar la raíz desde el archivo actual (app/componentes/sidebar.py)
    root_dir = Path(__file__).resolve().parent.parent.parent
    images_dir = root_dir / "imagenes"
    
    is_admin = st.session_state.role == "admin"
    logo_width = 240 if is_admin else 180
    logo_name = "logo-oscuro.png" if is_admin else "logo-claro.png"
    logo_path = images_dir / logo_name
    
    if logo_path.exists():
        # Usar st.image es más confiable
        st.image(str(logo_path), width=logo_width)
    elif is_admin:
        st.markdown("<h2 style='text-align: center;'>Administrador</h2>", unsafe_allow_html=True)
    else:
        st.markdown("<h2 style='text-align: center;'>Gelateria Urbana</h2>", unsafe_allow_html=True)

def _render_greeting_audio():
    if st.session_state.get("primera_vez_voz", False):
        st.session_state["primera_vez_voz"] = False
        txt = texto_visible_asistente(MENSAJE_BIENVENIDA_CLIENTE)
        audio = sintetizar_audio_wav(txt)
        if audio:
            b64 = base64.b64encode(audio).decode()
            components.html(f'<audio autoplay style="display:none"><source src="data:audio/wav;base64,{b64}" type="audio/wav"></audio>', height=0)

def _render_client_nav():
    st.markdown('<div class="sidebar-label" style="text-align:center;">Compra manual</div>', unsafe_allow_html=True)
    if st.button("Comprar", key="btn_comprar_cli", use_container_width=True):
        st.session_state.pagina_actual = "🛒 Comprar"
        st.rerun()
        
    st.markdown('<br><div class="sidebar-label" style="text-align:center;">Compra con IA</div>', unsafe_allow_html=True)
    if st.button("Chat con IA", key="btn_chat_cli", use_container_width=True):
        st.session_state.pagina_actual = "💬 Chat con IA"
        st.rerun()
    if st.button("Llamar IA", key="btn_call_cli", use_container_width=True):
        st.session_state.pagina_actual = "📞 Llamada con IA"
        st.session_state.call_greeted = False
        st.rerun()

    st.markdown('<br><div class="sidebar-label" style="text-align:center;">Gelateria Urbana</div>', unsafe_allow_html=True)
    if st.button("Conócenos", key="btn_about_cli", use_container_width=True):
        st.session_state.pagina_actual = "✨ Conócenos"
        st.rerun()

def _render_admin_nav():
    st.markdown('<div class="sidebar-label" style="text-align:center;">Gestión de Negocio</div>', unsafe_allow_html=True)
    if st.button("Dashboard", key="btn_dash_adm", use_container_width=True):
        st.session_state.pagina_actual = "📊 Dashboard"
        st.rerun()
    if st.button("Inventario", key="btn_inv_adm", use_container_width=True):
        st.session_state.pagina_actual = "📦 Inventario"
        st.rerun()
    if st.button("Ventas", key="btn_ventas_adm", use_container_width=True):
        st.session_state.pagina_actual = "📈 Ventas"
        st.rerun()
    if st.button("Movimientos", key="btn_mov_adm", use_container_width=True):
        st.session_state.pagina_actual = "📋 Movimientos"
        st.rerun()
        
    st.markdown('<br><div class="sidebar-label" style="text-align:center;">Gestión con IA</div>', unsafe_allow_html=True)
    if st.button("Chat con IA", key="btn_chat_adm", use_container_width=True):
        st.session_state.pagina_actual = "💬 Chat con IA"
        st.rerun()
    if st.button("Llamar IA", key="btn_call_adm", use_container_width=True):
        st.session_state.pagina_actual = "📞 Llamada con IA"
        st.session_state.call_greeted = False
        st.rerun()

def _render_admin_access():
    if st.checkbox("🔐 Acceso Administrador", value=False):
        pwd = st.text_input("Contraseña", type="password")
        if st.button("Ingresar", use_container_width=True):
            if pwd == "admin":
                st.session_state.role = "admin"
                st.session_state.pagina_actual = "📊 Dashboard"
                st.rerun()
            else:
                st.error("Incorrecta")

def _render_api_status(api_ok: bool, t: dict):
    color = "#2ecc71" if api_ok else "#e74c3c"
    txt = "Conectada" if api_ok else "Desconectada"
    api_url = "http://127.0.0.1:8000"
    st.markdown(f"""
        <div style="text-align: center; margin-top: 10px; padding: 10px; border-top: 1px dashed #ddd;">
            <p style="font-weight: 700; color: {t['TEXT']}; margin-bottom: 5px;">
                <span style="width: 10px; height: 10px; border-radius: 50%; background-color: {color}; display: inline-block; margin-right: 5px;"></span>
                API {txt}
            </p>
            <p style="font-size: 0.8rem; color: {t['TEXT']}; opacity: 0.8; margin: 0;">
                📍 Servidor: <code style="color:{t['TEXT']}; background:transparent; font-family: 'Nunito', sans-serif;">{api_url}</code>
            </p>
        </div>
    """, unsafe_allow_html=True)
