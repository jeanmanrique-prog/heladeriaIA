"""
app/componentes/sidebar.py
Componente lateral de navegación (Restaurado a la versión centrada y rosa).
"""

import streamlit as st
from pathlib import Path

def render_sidebar(api_ok: bool, theme: dict):
    """Renderiza el sidebar con el estilo anterior (fondo rosa, botones blancos centrados con letras rosas)."""
    
    with st.sidebar:
        _render_logo_centrado()
        
        # 1. SECCIÓN COMPRAS
        st.markdown('<p class="sidebar-label-centrada">#### COMPRAS</p>', unsafe_allow_html=True)
        if st.button("COMPRAR", key="nav_btn_comp_restaurado"):
            st.session_state.pagina_actual = "🛒 Comprar"; st.rerun()
        # (Sin divisor para agrupar compras)

        # 2. SECCIÓN IA
        st.markdown('<p class="sidebar-label-centrada">COMPRA CON IA</p>', unsafe_allow_html=True)
        if st.button("CHAT CON IA", key="nav_btn_chat_restaurado"):
            st.session_state.pagina_actual = "💬 Chat con IA"; st.rerun()
        if st.button("LLAMAR IA", key="nav_btn_call_restaurado"):
            st.session_state.pagina_actual = "📞 Llamada con IA"
            st.session_state.call_greeted = False; st.rerun()
        # (Sin divisor para agrupar imagen)

        # 3. IMAGEN COMPRE
        _render_imagen_compre_centrada()
        
        st.sidebar.divider()

        # 4. CONÓCENOS
        st.markdown('<p class="sidebar-label-centrada">#### GELATERÍA URBANA CONÓCENOS</p>', unsafe_allow_html=True)
        if st.button("✨ CONÓCENOS", key="nav_btn_abt_restaurado"):
            st.session_state.pagina_actual = "✨ Conócenos"; st.rerun()

        # 5. ADMIN
        st.sidebar.divider()
        with st.sidebar.expander("🔐 Administrador"):
            pwd = st.text_input("Password", type="password", key="pwd_restaurado")
            if st.button("Ingresar", key="btn_login_restaurado"):
                if pwd == "admin":
                    st.session_state.role = "admin"
                    st.session_state.pagina_actual = "📊 Dashboard"; st.rerun()
                else: st.error("Incorrecta")
        
        _render_api_status(api_ok)

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
