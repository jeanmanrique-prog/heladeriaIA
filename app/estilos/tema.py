"""
app/estilos/tema.py
────────────────────
Paletas de colores, CSS global y helpers de gráficas.
"""

import streamlit as st

def get_tema(dark: bool) -> dict:
    """Devuelve el diccionario completo de tokens de color según el modo."""
    if dark:
        return dict(
            BG="#1a0d10", BG2="#2a1520", BG3="#3a1f2a",
            BORDER="#7a2a45", TEXT="#f5e6ea", TEXT2="#d4a0b0", TEXT3="#c07090",
            ACCENT="#f06090", ACCENT2="#c0365a",
            SIDEBAR_BG="#11080b", SIDEBAR_BDR="#ff1493", SIDEBAR_BDR_ALT="#ff69b4",
            SIDEBAR_GLOW_SOFT="rgba(255, 20, 147, 0.2)",
            SIDEBAR_GLOW_STRONG="rgba(255, 20, 147, 0.4)",
            METRIC_BG="linear-gradient(135deg,#2a1520 0%,#3a1f2a 100%)",
            METRIC_LBL="#d4a0b0", METRIC_VAL="#f06090",
            SECT_BG="linear-gradient(90deg,#3a0d1e 0%,transparent 100%)",
            ALERTA_BG="#2a0d0d", ALERTA_BDR="#cc2222",
            ALERTA_NOM="#ff8080", ALERTA_TXT="#f5e6ea",
            STATUS_ON_BG="#0d2a18", STATUS_ON_BDR="#1a8a4a", STATUS_ON_TXT="#6deba0",
            STATUS_OFF_BG="#2a0d0d", STATUS_OFF_BDR="#cc2222", STATUS_OFF_TXT="#ff8080",
            INPUT_BG="#2a1520", INPUT_BDR="#7a2a45",
            DD_BG="#2a1520", DD_HOVER="#3a1f2a", DD_TXT="#f5e6ea",
            PLOT_BG="rgba(0,0,0,0)", PLOT_FONT="#f5e6ea", PLOT_GRID="#4a2535",
            BTN_FROM="#c0365a", BTN_TO="#f06090",
            BTN_HOV_F="#a02848", BTN_HOV_T="#d05070",
            TAB_COLOR="#d4a0b0", TAB_SEL="#f06090",
            HR="#7a2a45", CAPTION="#c07090",
            TEMA_ICON="☀️", TEMA_TXT="Tema Claro",
            SIDEBAR_LABEL_COLOR="#ff9fc1",
            TABLE_BG="#1c1017", TABLE_BG_ALT="#261520",
            TABLE_HDR_BG="#351b29", TABLE_BDR="#7a2a45", TABLE_TXT="#ffffff",
            BOT_BG="#2a1520", BOT_TEXT="#f5e6ea",
            COLOR_OK="#2ecc71", COLOR_ALERTA="#e74c3c",
            COLOR_BAR1="#f06090", COLOR_BAR2="#ffb347", COLOR_LINE="#f06090",
            COLORES_PIE=["#f06090", "#2ecc71", "#ffb347", "#74b9ff", "#a29bfe"],
            IS_REPO_ADMIN=True
        )
    else:
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
    """Inyecta el CSS según si es administrador (oscuro) o cliente (claro/mockup)."""
    
    # Intentar forzar el tema de Streamlit mediante JS (si el navegador lo permite)
    tema_js = "dark" if t.get('IS_REPO_ADMIN') else "light"
    st.components.v1.html(f"""
        <script>
            window.parent.document.documentElement.setAttribute('data-theme', '{tema_js}');
            window.parent.document.body.setAttribute('data-theme', '{tema_js}');
        </script>
    """, height=0)

    if t.get('IS_REPO_ADMIN', False):
        # MODO ADMIN: ESTILO OSCURO DE AYER
        st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Permanent+Marker&display=swap');

:root {{
    --background-color: {t['BG']};
    --secondary-background-color: {t['BG2']};
    --text-color: {t['TEXT']};
    --primary-color: {t['ACCENT']};
}}

html, body, [data-testid="stAppViewContainer"] {{ background-color: {t['BG']} !important; font-family: 'Nunito', sans-serif !important; }}
[data-testid="stSidebar"] {{ background-color: {t['SIDEBAR_BG']} !important; border-right: 2px solid {t['SIDEBAR_BDR']} !important; }}

h1, h2, h3, h4, h5, h6, p, span, label, div {{ font-family: 'Nunito', sans-serif; color: {t['TEXT']} !important; }}

[data-testid="stMetric"] {{
    background: {t['METRIC_BG']}; border: 2px solid {t['BORDER']}; border-radius: 20px; padding: 15px 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2); transition: all 0.3s ease;
}}
[data-testid="stMetric"]:hover {{ transform: translateY(-3px); box-shadow: 0 8px 25px rgba(0,0,0,0.25); }}
div[data-testid="metric-container"] label {{ color: {t['METRIC_LBL']} !important; font-size: 0.75rem !important; font-weight: 800 !important; text-transform: uppercase; }}
div[data-testid="metric-container"] div[data-testid="metric-value"] {{ color: {t['METRIC_VAL']} !important; font-weight: 900 !important; font-size: 2.1rem !important; }}

.stButton > button {{
    background: linear-gradient(135deg, {t['BTN_FROM']} 0%, {t['BTN_TO']} 100%) !important;
    color: #ffffff !important;
    font-family: 'Permanent Marker', cursive !important;
    font-size: 1.15rem !important;
    border: 3px solid #ffffff !important; border-radius: 12px !important; padding: 8px 16px !important;
    box-shadow: 6px 6px 0px rgba(0,0,0,0.2) !important; text-transform: uppercase !important;
}}
.alerta-card {{ background: {t['ALERTA_BG']}; border: 2px solid {t['ALERTA_BDR']}; border-radius: 16px; padding: 14px 18px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }}
.section-title {{ font-family: 'Permanent Marker', cursive; font-size: 1.5rem; color: {t['ACCENT']}; border-left: 8px solid {t['BORDER']}; background: {t['SECT_BG']}; padding: 8px 12px 8px 16px; border-radius: 0 15px 15px 0; margin: 1.8rem 0 1rem 0; text-transform: uppercase; }}

div[data-testid="stDataFrame"] {{
    --gdg-bg-cell: {t['TABLE_BG_ALT']}; --gdg-bg-cell-medium: {t['TABLE_BG']}; --gdg-bg-header: {t['TABLE_HDR_BG']};
    --gdg-text-dark: {t['TABLE_TXT']}; --gdg-border-color: {t['TABLE_BDR']};
    border: 1px solid {t['TABLE_BDR']} !important; border-radius: 16px !important; background: {t['TABLE_BG']} !important;
}}
hr {{ border-color:{t['HR']} !important; border-width:1.5px !important; }}
</style>
""", unsafe_allow_html=True)
    else:
        # MODO CLIENTE: ESTILO MOCKUP BLANCO Y ROSA
        st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');

    :root {{
        --background-color: #FFFFFF;
        --secondary-background-color: #FFF5F7;
        --text-color: #31333F;
        --primary-color: #FF3366;
    }}

    html, body, [data-testid="stAppViewContainer"] {{ background-color: #FFFFFF !important; font-family: 'Nunito', sans-serif !important; }}
    h1, h2, h3, h4, h5, h6, p, span, label, div {{ font-family: 'Nunito', sans-serif; color: #31333F !important; }}

    [data-testid="stSidebar"] {{ background-color: #FFF5F7 !important; border-right: 1px solid #FFE6EB !important; }}
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {{ display: flex !important; justify-content: center !important; width: 100% !important; }}

    .sidebar-label-centrada {{ color: #555555 !important; font-size: 0.8rem !important; font-weight: 700 !important; text-transform: uppercase; width: 100% !important; text-align: center !important; margin-top: 15px !important; margin-bottom: 5px !important; }}

    [data-testid="stSidebar"] .stButton > button {{
        background-color: #FFFFFF !important; color: #FF3366 !important; border: 2px solid #FF3366 !important;
        border-radius: 12px !important; font-weight: 800 !important; width: 95% !important; margin: 5px auto !important;
        height: 45px !important; display: block !important; text-align: center !important;
    }}
    [data-testid="stSidebar"] .stButton > button p {{ color: #FF3366 !important; font-weight: 800 !important; text-align: center !important; }}

    .main-title {{ color: #1F2937 !important; font-weight: 900 !important; font-size: 2.5rem !important; }}
    .sub-title {{ color: #6B7280 !important; font-weight: 600 !important; font-size: 1rem !important; }}

    [data-testid="stVerticalBlockBordered"] {{ background-color: #FFFFFF !important; border: none !important; border-radius: 20px !important; box-shadow: 0 8px 24px rgba(0,0,0,0.06) !important; padding: 20px !important; }}

    button[kind="primary"], [data-testid="baseButton-primary"] {{ background-color: #FF3366 !important; color: #FFFFFF !important; border-radius: 12px !important; border: none !important; font-weight: 800 !important; width: 100% !important; height: 45px !important; }}
    button[kind="primary"] p, [data-testid="baseButton-primary"] p {{ color: #FFFFFF !important; }}
    
    .dotted-divider {{ border-top: 2px dotted #FFE6EB; margin: 15px 0; }}
    .card-title {{ color: #1F2937 !important; font-weight: 800 !important; font-size: 1.1rem !important; text-align: center !important; }}
    .card-flavor {{ color: #6B7280 !important; font-size: 0.85rem !important; text-align: center !important; }}
    .card-price {{ color: #FF3366 !important; font-weight: 900 !important; font-size: 1.4rem !important; text-align: center !important; }}

    div[data-testid="column"]:nth-child(2) {{ border-left: 1px solid #F3F4F6 !important; padding-left: 20px !important; box-shadow: -10px 0px 15px -10px rgba(0,0,0,0.03) !important; }}
</style>
""", unsafe_allow_html=True)

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
