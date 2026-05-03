"""
app/estilos/tema.py
────────────────────
Paletas de colores, CSS global y helpers de gráficas.
"""

import streamlit as st
from estilos.estilos_globales import obtener_estilos_globales, obtener_script_forzar_light

def get_tema(dark: bool = False) -> dict:
    """SIEMPRE devuelve el tema CLARO para cumplir con el requerimiento del usuario."""
    ACCENT = "#a8124a"
    ACCENT2 = "#d94f7a"
    return dict(
        BG="#FFFFFF", BG2="#fdeef4", BG3="#fad5e0",
        BORDER="#ff1493", TEXT="#2a1a1a", TEXT2="#6b1a35", TEXT3="#a8124a",
        ACCENT=ACCENT, ACCENT2=ACCENT2,
        SIDEBAR_BG="#FFFFFF", SIDEBAR_BDR=ACCENT, SIDEBAR_BDR_ALT=ACCENT,
        SIDEBAR_GLOW_SOFT="rgba(168, 18, 74, 0.22)",
        SIDEBAR_GLOW_STRONG="rgba(168, 18, 74, 0.44)",
        METRIC_BG="linear-gradient(135deg,#fdeef4 0%,#fad5e0 100%)",
        METRIC_LBL="#6b1a35", METRIC_VAL="#a8124a",
        SECT_BG="linear-gradient(90deg,#fad5e0 0%,transparent 100%)",
        ALERTA_BG="#fff5f5", ALERTA_BDR="#feb2b2",
        ALERTA_NOM="#c53030", ALERTA_TXT="#2a1a1a",
        STATUS_ON_BG="#f0fff4", STATUS_ON_BDR="#48bb78", STATUS_ON_TXT="#22543d",
        STATUS_OFF_BG="#fff5f5", STATUS_OFF_BDR="#f56565", STATUS_OFF_TXT="#742a2a",
        INPUT_BG="#FFFFFF", INPUT_BDR="#fad5e0",
        DD_BG="#FFFFFF", DD_HOVER="#fdeef4", DD_TXT="#2a1a1a",
        PLOT_BG="rgba(0,0,0,0)", PLOT_FONT="#2a1a1a", PLOT_GRID="#fdeef4",
        BTN_FROM="#a8124a", BTN_TO="#d94f7a",
        BTN_HOV_F="#8a0f3d", BTN_HOV_T="#c0456a",
        TAB_COLOR="#6b1a35", TAB_SEL="#a8124a",
        HR="#fad5e0", CAPTION="#6b1a35",
        TEMA_ICON="🌙", TEMA_TXT="Tema Oscuro",
        SIDEBAR_LABEL_COLOR="#6b1a35",
        TABLE_BG="#FFFFFF", TABLE_BG_ALT="#fdeef4",
        TABLE_HDR_BG="#fad5e0", TABLE_BDR="#fad5e0", TABLE_TXT="#2a1a1a",
        BOT_BG="#fdeef4", BOT_TEXT="#2a1a1a",
        COLOR_OK="#2ecc71", COLOR_ALERTA="#e74c3c",
        COLOR_BAR1="#a8124a", COLOR_BAR2="#d94f7a", COLOR_LINE="#a8124a",
        COLORES_PIE=["#a8124a", "#2ecc71", "#ffb347", "#74b9ff", "#a29bfe"],
        IS_REPO_ADMIN=False
    )

def aplicar_css_global(t: dict) -> None:
    """Fuerza modo claro y oculta la barra superior de Streamlit."""
    
    # Forzar tema light mediante JS
    st.components.v1.html(obtener_script_forzar_light(), height=0)

    # Inyectar estilos globales
    st.markdown(obtener_estilos_globales(), unsafe_allow_html=True)

def fig_layout(fig, t: dict, height: int = 300):
    """Aplica el layout Plotly correcto según el tema activo."""
    fig.update_layout(
        paper_bgcolor=t.get('PLOT_BG', 'rgba(0,0,0,0)'),
        plot_bgcolor=t.get('PLOT_BG', 'rgba(0,0,0,0)'),
        font=dict(color=t.get('PLOT_FONT', '#31333F'), family="Nunito", size=13),
        height=height,
        xaxis=dict(gridcolor=t.get('PLOT_GRID', '#f0f0f0')),
        yaxis=dict(gridcolor=t.get('PLOT_GRID', '#f0f0f0')),
    )
    return fig
