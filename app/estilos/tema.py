"""
app/estilos/tema.py
────────────────────
Paletas de colores, CSS global y helpers de gráficas.

Funciones públicas:
  get_tema(dark: bool) -> dict   — devuelve todas las variables de color del tema
  aplicar_css_global(t: dict)    — inyecta el CSS completo en Streamlit
  fig_layout(fig, t, height)     — aplica tema a un gráfico Plotly
"""

import streamlit as st


# ──────────────────────────────────────────────────────────
# PALETAS
# ──────────────────────────────────────────────────────────

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
            SIDEBAR_GLOW_STRONG="rgba(168, 18, 74, 0.38)",
            METRIC_BG="linear-gradient(135deg,#fdeef4 0%,#fad5e0 100%)",
            METRIC_LBL="#6b1a35", METRIC_VAL=ACCENT,
            SECT_BG="linear-gradient(90deg,#fad5e0 0%,transparent 100%)",
            ALERTA_BG="#ffeaea", ALERTA_BDR="#cc2222",
            ALERTA_NOM="#aa1111", ALERTA_TXT="#2a1a1a",
            STATUS_ON_BG="#d4f5e2", STATUS_ON_BDR="#1a8a4a", STATUS_ON_TXT="#0d5c30",
            STATUS_OFF_BG="#ffd5d5", STATUS_OFF_BDR="#cc2222", STATUS_OFF_TXT="#8a0000",
            INPUT_BG="#fff8f2", INPUT_BDR="#d9638a",
            DD_BG="#fff8f2", DD_HOVER="#fad5e0", DD_TXT="#2a1a1a",
            PLOT_BG="rgba(0,0,0,0)", PLOT_FONT="#2a1a1a", PLOT_GRID="#f4d0da",
            BTN_FROM=ACCENT, BTN_TO=ACCENT2,
            BTN_HOV_F="#8a0d3c", BTN_HOV_T="#c0436c",
            TAB_COLOR="#6b1a35", TAB_SEL=ACCENT,
            HR="#d9638a", CAPTION="#5a3a3a",
            TEMA_ICON="🌙", TEMA_TXT="Tema Oscuro",
            SIDEBAR_LABEL_COLOR=ACCENT,
            TABLE_BG="#ffffff", TABLE_BG_ALT="#fff8f2",
            TABLE_HDR_BG="#fdeef4", TABLE_BDR="#f2c7d6", TABLE_TXT="#2a1a1a",
            BOT_BG="#fdeef4", BOT_TEXT="#2a1a1a",
            COLOR_OK="#1a8a4a", COLOR_ALERTA="#e74c3c",
            COLOR_BAR1="#d94f7a", COLOR_BAR2="#ffb347", COLOR_LINE=ACCENT,
            COLORES_PIE=["#f06090", "#2ecc71", "#ffb347", "#74b9ff", "#a29bfe"],
        )


# ──────────────────────────────────────────────────────────
# CSS GLOBAL
# ──────────────────────────────────────────────────────────

def aplicar_css_global(t: dict) -> None:
    """Inyecta el CSS completo del tema en la app Streamlit."""
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Permanent+Marker&family=Sedgwick+Ave+Display&family=Nunito:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {{
    font-family: 'Nunito', sans-serif;
    color: {t['TEXT']};
}}
[data-testid="stHeader"] {{ display: none !important; }}
[data-testid="stToolbar"] {{ display: none !important; }}
#MainMenu {{ visibility: hidden; }}
footer {{ visibility: hidden; }}

.stApp {{ background-color: {t['BG']}; color: {t['TEXT']}; }}
p, span, li, td, th {{ color: {t['TEXT']} !important; }}

h1 {{ font-family:'Permanent Marker',cursive !important; color:{t['ACCENT']} !important; font-size:3rem !important; text-shadow: 2px 2px 0px rgba(0,0,0,0.1); letter-spacing: 2px; }}
h2 {{ font-family:'Permanent Marker',cursive !important; color:{t['ACCENT']} !important; font-size:2rem !important; }}
h3 {{ font-family:'Permanent Marker',cursive !important; color:{t['TEXT']} !important; font-weight:400 !important; }}

@keyframes sidebar-glow {{
    0%   {{ border-right: 3px solid {t['SIDEBAR_BDR']}; box-shadow: 10px 0 20px {t['SIDEBAR_GLOW_SOFT']}; }}
    50%  {{ border-right: 3px solid {t['SIDEBAR_BDR_ALT']}; box-shadow: 15px 0 30px {t['SIDEBAR_GLOW_STRONG']}; }}
    100% {{ border-right: 3px solid {t['SIDEBAR_BDR']}; box-shadow: 10px 0 20px {t['SIDEBAR_GLOW_SOFT']}; }}
}}
section[data-testid="stSidebar"] {{
    background: {t['SIDEBAR_BG']} !important;
    border-right: 3px solid {t['SIDEBAR_BDR']} !important;
    animation: sidebar-glow 3s infinite ease-in-out;
}}
section[data-testid="stSidebar"] div {{ color: {t['TEXT']} !important; }}
section[data-testid="stSidebar"] h2 {{
    font-family:'Permanent Marker',cursive !important;
    color:#ff1493 !important;
    transform: rotate(-3deg) translateY(10px);
    text-shadow: 3px 3px 0px rgba(0,0,0,0.15);
    font-size: 2.5rem !important;
    margin-bottom: 30px !important;
}}
div[data-testid="stSidebar"] label {{
    font-family: 'Permanent Marker', cursive !important;
    font-size:1.1rem !important;
    color:{t['TEXT']} !important;
    letter-spacing: 1px;
}}

div[data-testid="metric-container"] {{
    background: {t['METRIC_BG']};
    border: 2px solid {t['BORDER']};
    border-radius: 20px;
    padding: 18px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    transition: transform 0.2s, box-shadow 0.2s;
}}
div[data-testid="metric-container"]:hover {{
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.25);
}}
div[data-testid="metric-container"] label {{ color: {t['METRIC_LBL']} !important; font-size: 0.75rem !important; font-weight: 800 !important; text-transform: uppercase; letter-spacing: 0.1em; }}
div[data-testid="metric-container"] div[data-testid="metric-value"] {{ color: {t['METRIC_VAL']} !important; font-family: 'Nunito', sans-serif !important; font-weight: 900 !important; font-size: 2.1rem !important; }}
div[data-testid="metric-container"] div[data-testid="metric-delta"] {{ color: {t['TEXT']} !important; font-weight: 700 !important; }}

.stButton > button {{
    background: linear-gradient(135deg, {t['BTN_FROM']} 0%, {t['BTN_TO']} 100%) !important;
    color: #ffffff !important;
    font-family: 'Permanent Marker', cursive !important;
    font-size: 1.15rem !important;
    border: 3px solid #ffffff !important;
    border-radius: 12px !important;
    padding: 8px 16px !important;
    box-shadow: 6px 6px 0px rgba(0,0,0,0.2) !important;
    transition: all 0.1s ease !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    width: 100% !important;
}}
.stButton > button:hover {{
    transform: translate(-3px, -3px) !important;
    box-shadow: 10px 10px 0px rgba(0,0,0,0.3) !important;
    filter: brightness(1.1) !important;
    color: #ffffff !important;
}}
.stButton > button:active {{
    transform: translate(2px, 2px) !important;
    box-shadow: 2px 2px 0px rgba(0,0,0,0.2) !important;
    color: #ffffff !important;
}}

button[data-baseweb="tab"] {{ font-family: 'Nunito', sans-serif !important; font-weight: 700 !important; color: {t['TAB_COLOR']} !important; background: transparent !important; }}
button[data-baseweb="tab"][aria-selected="true"] {{ color: {t['TAB_SEL']} !important; border-bottom-color: {t['TAB_SEL']} !important; }}

input, textarea {{ border-radius: 12px !important; border-color: {t['INPUT_BDR']} !important; background-color: {t['INPUT_BG']} !important; color: {t['TEXT']} !important; }}
div[data-testid="stTextInput"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stRadio"] label {{ color: {t['TEXT']} !important; font-weight: 700 !important; }}

div[data-testid="stSelectbox"] > div > div,
div[data-baseweb="select"] > div,
div[data-baseweb="select"] {{ background-color: {t['INPUT_BG']} !important; border-color: {t['INPUT_BDR']} !important; border-radius: 12px !important; }}
div[data-baseweb="select"] span,
div[data-baseweb="select"] div,
div[data-testid="stSelectbox"] span {{ color: {t['TEXT']} !important; background-color: transparent !important; }}
ul[data-testid="stSelectboxVirtualDropdown"],
div[role="listbox"],
div[data-baseweb="popover"] ul {{ background-color: {t['DD_BG']} !important; border: 1.5px solid {t['INPUT_BDR']} !important; border-radius: 12px !important; }}
li[role="option"],
div[data-baseweb="menu"] li {{ background-color: {t['DD_BG']} !important; color: {t['DD_TXT']} !important; font-weight: 600 !important; }}
li[role="option"]:hover,
div[data-baseweb="menu"] li:hover {{ background-color: {t['DD_HOVER']} !important; color: {t['ACCENT']} !important; }}

.alerta-card {{ background: {t['ALERTA_BG']}; border: 2px solid {t['ALERTA_BDR']}; border-radius: 16px; padding: 14px 18px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 3px 10px rgba(0,0,0,0.15); }}
.alerta-nombre {{ font-family: 'Nunito', sans-serif; font-weight: 800; color: {t['ALERTA_NOM']}; font-size: 1rem; }}
.alerta-stock {{ color: {t['ALERTA_TXT']}; font-size: 0.85rem; font-weight: 600; }}

.section-title {{ font-family: 'Permanent Marker', cursive; font-size: 1.5rem; color: {t['ACCENT']}; border-left: 8px solid {t['BORDER']}; background: {t['SECT_BG']}; padding: 8px 12px 8px 16px; border-radius: 0 15px 15px 0; margin: 1.8rem 0 1rem 0; text-transform: uppercase; }}

.status-online {{ display: inline-flex; align-items: center; gap: 8px; background: {t['STATUS_ON_BG']}; border: 2px solid {t['STATUS_ON_BDR']}; border-radius: 50px; padding: 6px 16px; font-weight: 800; color: {t['STATUS_ON_TXT']}; font-size: 0.85rem; }}
.status-offline {{ display: inline-flex; align-items: center; gap: 8px; background: {t['STATUS_OFF_BG']}; border: 2px solid {t['STATUS_OFF_BDR']}; border-radius: 50px; padding: 6px 16px; font-weight: 800; color: {t['STATUS_OFF_TXT']}; font-size: 0.85rem; }}
.dot-online {{ width:10px; height:10px; background:{t['STATUS_ON_BDR']}; border-radius:50%; animation:pulse-green 1.5s infinite; }}
.dot-offline {{ width:10px; height:10px; background:{t['STATUS_OFF_BDR']}; border-radius:50%; }}
@keyframes pulse-green {{ 0%,100% {{ opacity:1; transform:scale(1); }} 50% {{ opacity:0.5; transform:scale(1.3); }} }}

.sabor-badge {{ display: inline-block; padding: 4px 11px; border-radius: 20px; font-size: 0.78rem; font-weight: 800; margin: 2px; color: #1a0a0a !important; border: 1.5px solid rgba(0,0,0,0.18); }}
.sidebar-sub  {{ color:{t['TEXT2']} !important; font-size:0.85rem; margin-top:-10px; font-weight:600; }}
.sidebar-label{{ font-family: 'Permanent Marker', sans-serif !important; font-size:1.1rem !important; color:{t['SIDEBAR_LABEL_COLOR']} !important; text-transform:uppercase; letter-spacing:0.1em; }}
section[data-testid="stSidebar"] .sidebar-label,
section[data-testid="stSidebar"] .sidebar-label p,
section[data-testid="stSidebar"] .sidebar-label span {{ color:{t['SIDEBAR_LABEL_COLOR']} !important; }}

div[data-testid="stCaptionContainer"] p, small {{ color: {t['CAPTION']} !important; font-weight: 600 !important; }}

.stDataFrame {{ border-radius:16px; overflow:hidden; }}
div[data-testid="stDataFrame"] {{
    --gdg-bg-cell: {t['TABLE_BG_ALT']};
    --gdg-bg-cell-medium: {t['TABLE_BG']};
    --gdg-bg-header: {t['TABLE_HDR_BG']};
    --gdg-bg-header-hovered: {t['TABLE_HDR_BG']};
    --gdg-text-dark: {t['TABLE_TXT']};
    --gdg-text-medium: {t['TABLE_TXT']};
    --gdg-border-color: {t['TABLE_BDR']};
    border: 1px solid {t['TABLE_BDR']} !important;
    border-radius: 16px !important;
    overflow: hidden !important;
    background: {t['TABLE_BG']} !important;
}}
div[data-testid="stDataFrame"] [role="columnheader"] {{ background: {t['TABLE_HDR_BG']} !important; color: {t['TABLE_TXT']} !important; font-weight: 800 !important; }}
div[data-testid="stDataFrame"] [role="gridcell"] {{ background: {t['TABLE_BG_ALT']} !important; color: {t['TABLE_TXT']} !important; }}
div[data-testid="stDataFrame"] div,
div[data-testid="stDataFrame"] span,
div[data-testid="stDataFrame"] p {{ color: {t['TABLE_TXT']} !important; }}

div[data-testid="stAlert"] {{ border-radius:16px !important; }}
div[data-testid="stAlert"] p {{ font-weight:700 !important; }}
hr {{ border-color:{t['HR']} !important; border-width:1.5px !important; }}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────
# GRÁFICAS
# ──────────────────────────────────────────────────────────

def fig_layout(fig, t: dict, height: int = 300):
    """Aplica el layout Plotly correcto según el tema activo."""
    fig.update_layout(
        paper_bgcolor=t['PLOT_BG'],
        plot_bgcolor=t['PLOT_BG'],
        font=dict(color=t['PLOT_FONT'], family="Nunito", size=13),
        height=height,
        margin=dict(t=30, b=20, l=10, r=10),
        xaxis=dict(
            gridcolor=t['PLOT_GRID'],
            tickfont=dict(color=t['PLOT_FONT'], size=12),
            title_font=dict(color=t['PLOT_FONT']),
            linecolor=t['PLOT_GRID'],
        ),
        yaxis=dict(
            gridcolor=t['PLOT_GRID'],
            tickfont=dict(color=t['PLOT_FONT'], size=12),
            title_font=dict(color=t['PLOT_FONT']),
            linecolor=t['PLOT_GRID'],
        ),
        legend=dict(
            font=dict(color=t['PLOT_FONT'], size=12),
            bgcolor="rgba(0,0,0,0)",
        ),
    )
    return figdef aplicar_css_global(t: dict) -> None:
    if t.get('IS_REPO_ADMIN', False):

    else:
    st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');

    /* 1. RESET Y FONDO GLOBAL (BLANCO) */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF !important; /* Fondo blanco puro */
        font-family: 'Nunito', sans-serif !important;
    }
    
    /* TODAS las letras oscuras para que se vean bien sobre blanco */
    h1, h2, h3, h4, h5, h6, p, span, label, div {
        font-family: 'Nunito', sans-serif;
        color: #31333F !important; /* Gris muy oscuro, casi negro */
    }

    /* 2. SIDEBAR RESTAURADO (Fondo Rosa Pálido + Centrado) */
    [data-testid="stSidebar"] {
        background-color: #FFF5F7 !important;
        border-right: 1px solid #FFE6EB !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }

    /* Etiquetas del Sidebar */
    .sidebar-label-centrada {
        color: #555555 !important;
        font-size: 0.8rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        width: 100% !important;
        text-align: center !important;
        margin-top: 15px !important;
        margin-bottom: 5px !important;
    }

    /* Botones Sidebar: Muy anchos, fondo blanco, letras y borde rosas */
    [data-testid="stSidebar"] .stButton > button {
        background-color: #FFFFFF !important;
        color: #FF3366 !important;
        border: 2px solid #FF3366 !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
        width: 95% !important;
        margin: 5px auto !important;
        height: 45px !important;
        display: block !important;
        text-align: center !important;
        box-shadow: 0 4px 6px rgba(255, 51, 102, 0.05) !important;
    }
    [data-testid="stSidebar"] .stButton > button p {
        color: #FF3366 !important;
        font-weight: 800 !important;
        text-align: center !important;
    }

    /* 3. CATÁLOGO PRINCIPAL */
    .main-title {
        color: #1F2937 !important;
        font-weight: 900 !important;
        font-size: 2.5rem !important;
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }
    .sub-title {
        color: #6B7280 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        margin-top: 5px !important;
        margin-bottom: 25px !important;
    }

    /* 4. BUSCADOR */
    .stTextInput { max-width: 450px !important; }
    .stTextInput input {
        background-color: #FFFFFF !important;
        border: 1.5px solid #E5E7EB !important;
        border-radius: 12px !important;
        padding: 10px 15px !important;
        color: #31333F !important;
    }
    .stTextInput input:focus { border-color: #FF3366 !important; }

    /* 5. TARJETAS DE PRODUCTO Y CARRITO (Sombreadas) */
    [data-testid="stVerticalBlockBordered"] {
        background-color: #FFFFFF !important;
        border: none !important;
        border-radius: 20px !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.06) !important;
        padding: 20px !important;
    }

    /* Botones de +PEDIR en el catálogo: Forzosamente ROSA SÓLIDO (#FF3366) */
    button[kind="primary"], [data-testid="baseButton-primary"] {
        background-color: #FF3366 !important;
        color: #FFFFFF !important;
        border-radius: 12px !important;
        border: none !important;
        font-weight: 800 !important;
        width: 100% !important;
        height: 45px !important;
    }
    button[kind="primary"] p, [data-testid="baseButton-primary"] p { color: #FFFFFF !important; }
    
    /* Separador punteado */
    .dotted-divider { border-top: 2px dotted #FFE6EB; margin: 15px 0; }

    /* Textos dentro de la tarjeta */
    .card-title { color: #1F2937 !important; font-weight: 800 !important; font-size: 1.1rem !important; margin-bottom: 2px !important; text-align: center !important; }
    .card-flavor { color: #6B7280 !important; font-size: 0.85rem !important; font-weight: 600 !important; text-align: center !important; margin-bottom: 15px !important; }
    .card-price { color: #FF3366 !important; font-weight: 900 !important; font-size: 1.4rem !important; text-align: center !important; margin-bottom: 15px !important; }

    /* 6. SOMBRITA/SEPARADOR ENTRE CATÁLOGO Y CARRITO */
    /* Añadimos un borde izquierdo suave con sombra a la columna del carrito (la segunda columna) */
    div[data-testid="column"]:nth-child(2) {
        border-left: 1px solid #F3F4F6 !important;
        padding-left: 20px !important;
        box-shadow: -10px 0px 15px -10px rgba(0,0,0,0.03) !important;
    }

    /* 7. TOAST VERDE */
    [data-testid="stToast"] { background-color: #22c55e !important; border: none !important; }
    [data-testid="stToast"] p { color: #FFFFFF !important; font-weight: 700 !important; }

    /* Ocultar elementos de Streamlit */
    [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
</style>
""", unsafe_allow_html=True)



# ──────────────────────────────────────────────────────────
# GRÁFICAS
# ──────────────────────────────────────────────────────────

def fig_layout(fig, t: dict, height: int = 300):
    """Aplica el layout Plotly correcto según el tema activo."""
    fig.update_layout(
        paper_bgcolor=t['PLOT_BG'],
        plot_bgcolor=t['PLOT_BG'],
        font=dict(color=t['PLOT_FONT'], family="Nunito", size=13),
        height=height,
        margin=dict(t=30, b=20, l=10, r=10),
        xaxis=dict(
            gridcolor=t['PLOT_GRID'],
            tickfont=dict(color=t['PLOT_FONT'], size=12),
            title_font=dict(color=t['PLOT_FONT']),
            linecolor=t['PLOT_GRID'],
        ),
        yaxis=dict(
            gridcolor=t['PLOT_GRID'],
            tickfont=dict(color=t['PLOT_FONT'], size=12),
            title_font=dict(color=t['PLOT_FONT']),
            linecolor=t['PLOT_GRID'],
        ),
        legend=dict(
            font=dict(color=t['PLOT_FONT'], size=12),
            bgcolor="rgba(0,0,0,0)",
        ),
    )
    return fig
