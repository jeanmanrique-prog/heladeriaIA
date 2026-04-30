"""
app/estilos/tema.py
────────────────────
Tema UI (Sidebar Restaurado + Catálogo Mockup con Letras Oscuras).
"""

import streamlit as st

def get_tema(dark: bool) -> dict:
    return dict(BG="#FFFFFF", TEXT="#31333F", ACCENT="#FF3366", IS_REPO_ADMIN=dark)

def aplicar_css_global(t: dict) -> None:
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

def fig_layout(fig, t: dict, height: int = 300):
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family="Nunito, sans-serif", color="#31333F"))
    return fig
