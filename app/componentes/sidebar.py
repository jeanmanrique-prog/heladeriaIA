"""
app/componentes/sidebar.py
Componente lateral de navegación (Soporte Admin/Cliente con Estilo Centrado Rosa).
"""

import streamlit as st
from pathlib import Path

def render_sidebar(api_ok: bool, theme: dict):
    """Renderiza el sidebar dinámicamente según el rol del usuario."""
    
    with st.sidebar:
        _render_logo_centrado()
        
        is_admin = st.session_state.get("role") == "admin"

        if is_admin:
            _render_admin_nav()
        else:
            _render_client_nav()

        # Opciones inferiores (Login o Logout)
        st.sidebar.divider()
        if is_admin:
            if st.button("Cerrar Sesión", key="btn_logout_restaurado"):
                st.session_state.role = "client"
                st.session_state.pagina_actual = "🛒 Comprar"; st.rerun()
        else:
            with st.sidebar.expander("🔐 Administrador"):
                pwd = st.text_input("Password", type="password", key="pwd_restaurado")
                if st.button("Ingresar", key="btn_login_restaurado"):
                    if pwd == "admin":
                        st.session_state.role = "admin"
                        st.session_state.pagina_actual = "📊 Dashboard"; st.rerun()
                    else: st.error("Incorrecta")
        
        _render_api_status(api_ok)

def _render_client_nav():
    # 1. SECCIÓN COMPRAS
    st.markdown('<p class="sidebar-label-centrada">#### COMPRAS</p>', unsafe_allow_html=True)
    if st.button("COMPRAR", key="nav_btn_comp_restaurado"):
        st.session_state.pagina_actual = "🛒 Comprar"; st.rerun()
    
    # 2. SECCIÓN IA
    st.markdown('<p class="sidebar-label-centrada">COMPRA CON IA</p>', unsafe_allow_html=True)
    if st.button("CHAT CON IA", key="nav_btn_chat_restaurado"):
        st.session_state.pagina_actual = "💬 Chat con IA"; st.rerun()
    if st.button("LLAMAR IA", key="nav_btn_call_restaurado"):
        st.session_state.pagina_actual = "📞 Llamada con IA"
        st.session_state.call_greeted = False; st.rerun()

    # 3. IMAGEN COMPRE
    _render_imagen_compre_centrada()
    
    st.sidebar.divider()

    # 4. CONÓCENOS
    st.markdown('<p class="sidebar-label-centrada">#### GELATERÍA URBANA CONÓCENOS</p>', unsafe_allow_html=True)
    if st.button("✨ CONÓCENOS", key="nav_btn_abt_restaurado"):
        st.session_state.pagina_actual = "✨ Conócenos"; st.rerun()

def _render_admin_nav():
    st.markdown('<p class="sidebar-label-centrada">GESTIÓN DE NEGOCIO</p>', unsafe_allow_html=True)
    if st.button("Dashboard", key="btn_dash_adm"):
        st.session_state.pagina_actual = "📊 Dashboard"; st.rerun()
    if st.button("Inventario", key="btn_inv_adm"):
        st.session_state.pagina_actual = "📦 Inventario"; st.rerun()
    if st.button("Ventas", key="btn_ventas_adm"):
        st.session_state.pagina_actual = "📈 Ventas"; st.rerun()
    if st.button("Movimientos", key="btn_mov_adm"):
        st.session_state.pagina_actual = "📋 Movimientos"; st.rerun()

    st.markdown('<p class="sidebar-label-centrada">GESTIÓN CON IA</p>', unsafe_allow_html=True)
    if st.button("Chat con IA", key="btn_chat_adm"):
        st.session_state.pagina_actual = "💬 Chat con IA"; st.rerun()
    if st.button("Llamar IA", key="btn_call_adm"):
        st.session_state.pagina_actual = "📞 Llamada con IA"
        st.session_state.call_greeted = False; st.rerun()

def _render_logo_centrado():
    logo_path = Path(__file__).resolve().parent.parent.parent / "imagenes" / "logo-claro.png"
    if logo_path.exists():
        st.sidebar.image(str(logo_path), use_container_width=True)

def _render_imagen_compre_centrada():
    img_path = Path(__file__).resolve().parent.parent.parent / "imagenes" / "urban_compre.png"
    if img_path.exists():
        st.sidebar.image(str(img_path), use_container_width=True)

def _render_api_status(api_ok: bool):
    color = "#2ecc71" if api_ok else "#e74c3c"
    st.sidebar.markdown(f"<p style='text-align:center; font-size:0.5rem; color:#bbb; margin-top:20px;'>SISTEMA ONLINE <span style='color:{color};'>●</span></p>", unsafe_allow_html=True)
