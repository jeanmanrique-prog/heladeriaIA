"""
app/main.py
───────────
Router principal de la aplicación Gelateria Urbana.
"""

import streamlit as st
import base64
import sys
from pathlib import Path

# Agregar el directorio raíz al path para que reconozca los módulos de mcp/
root_path = str(Path(__file__).resolve().parent.parent)
if root_path not in sys.path:
    sys.path.append(root_path)

import importlib
try:
    import mcp.config
    import mcp.prompts.prompt_ventas
    import mcp.voz.ia.agente
    import mcp.voz.pipeline.pipeline_voz
    importlib.reload(mcp.config)
    importlib.reload(mcp.prompts.prompt_ventas)
    importlib.reload(mcp.voz.ia.agente)
    importlib.reload(mcp.voz.pipeline.pipeline_voz)
except Exception:
    pass

# Utilidades y Gestión de Estado (Rutas locales para Streamlit)

from utilidades.gestor_sesion import GestorSesion
from utilidades.peticiones import ClienteAPI
from utilidades.formateadores import corregir_codificacion

# Estilos y Tema
from estilos.tema import get_tema, aplicar_css_global

# Componentes Globales
from componentes.barra_lateral import render_sidebar

# Páginas de Administrador
from admin.gestion_manual.dashboard import render_dashboard
from admin.gestion_manual.inventario import render_inventario
from admin.gestion_manual.ventas import render_ventas
from admin.gestion_manual.movimientos import render_movimientos

# Páginas de Cliente
from cliente.compra_manual.comprar import render_comprar

# ──────────────────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Gelateria Urbana | Street Style",
    page_icon="🍦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ──────────────────────────────────────────────────────────
# FUNCIONES DE DESPACHO DE IA (CENTRALIZADAS)
# ──────────────────────────────────────────────────────────
def render_ia_admin(pagina: str, api_ok: bool, theme: dict):
    if pagina == "💬 Chat con IA":
        from ia.chat.interfaz.interfaz_admin import render_pagina_chat_admin
        render_pagina_chat_admin(api_ok, theme)
    elif pagina == "📞 Llamada con IA":
        from ia.llamada.interfaz.interfaz_admin import render_pagina_llamada_admin
        render_pagina_llamada_admin(theme)

def render_ia_cliente(pagina: str, api_ok: bool, theme: dict):
    if pagina == "💬 Chat con IA":
        from ia.chat.interfaz.interfaz_cliente import render_pagina_chat_cliente
        render_pagina_chat_cliente(api_ok, theme)
    elif pagina == "📞 Llamada con IA":
        from ia.llamada.interfaz.interfaz_cliente import render_pagina_llamada_cliente
        render_pagina_llamada_cliente(theme)

def render_conocenos(theme):
    """Página especial 'Conócenos' con imagen inmersiva."""
    img_path = Path(__file__).resolve().parent.parent / "imagenes" / "sobre_nosotros.png"
    if img_path.exists():
        with open(img_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(f"""
            <style>
            [data-testid="stMain"] {{ padding: 0 !important; }}
            .about-wrapper {{ width: 100%; background: {theme['BG']}; }}
            .about-image {{ width: 100%; display: block; }}
            </style>
            <div class="about-wrapper">
                <img src="data:image/png;base64,{b64}" class="about-image">
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Nuestra historia se está escribiendo... 🍦")

# ──────────────────────────────────────────────────────────
# PUNTO DE ENTRADA (ROUTER)
# ──────────────────────────────────────────────────────────

def main():
    # 1. Inicializar Estado Global
    GestorSesion.inicializar()
    
    # 2. Determinar Tema (Admin: Dark / Cliente: Light)
    is_admin = st.session_state.role == "admin"
    theme = get_tema(is_admin)
    st.session_state["theme_accent"] = theme['ACCENT']
    
    # 3. Aplicar Estilos Globales (CSS)
    aplicar_css_global(theme)
    
    # 4. Verificar Conectividad API
    api_ok = ClienteAPI.verificar_api()

    
    # 5. Refrescar servicios IA si es necesario (Voz/ASR)
    if st.session_state.pagina_actual == "📞 Llamada con IA":
        GestorSesion.refrescar_servicios(modo="call")

    
    # 6. Renderizar Barra Lateral
    render_sidebar(api_ok, theme)
    
    pagina = st.session_state.pagina_actual
    
    if is_admin:
        if pagina == "📊 Dashboard":
            render_dashboard(api_ok, theme)
        elif pagina == "📦 Inventario":
            render_inventario(api_ok, theme)
        elif pagina == "📈 Ventas":
            render_ventas(api_ok, theme)
        elif pagina == "📋 Movimientos":
            render_movimientos(api_ok, theme)
        elif pagina in ["💬 Chat con IA", "📞 Llamada con IA"]:
            render_ia_admin(pagina, api_ok, theme)
        else:
            render_dashboard(api_ok, theme)
    else:
        if pagina in ["🛒 Comprar", "🛍️ Comprar"]:
            render_comprar(pagina, api_ok, theme)
        elif pagina in ["💬 Chat con IA", "📞 Llamada con IA"]:
            render_ia_cliente(pagina, api_ok, theme)
        elif pagina == "✨ Conócenos":
            render_conocenos(theme)
        else:
            render_comprar("🛒 Comprar", api_ok, theme)

if __name__ == "__main__":
    main()
