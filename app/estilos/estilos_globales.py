"""
app/estilos/estilos_globales.py
───────────────────────────────
Estilos CSS globales para la aplicación.
"""

def obtener_estilos_globales():
    """Retorna el bloque de estilos CSS globales."""
    return """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');

    /* OCULTAR BARRA SUPERIOR Y MENÚS */
    header[data-testid="stHeader"] { visibility: hidden; height: 0; }
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    .stAppDeployButton { display:none; }
    [data-testid="stDecoration"] { display:none; }

    :root {
        --background-color: #FFFFFF;
        --secondary-background-color: #FFF5F7;
        --text-color: #31333F;
        --primary-color: #FF3366;
    }

    html, body, [data-testid="stAppViewContainer"] { background-color: #FFFFFF !important; font-family: 'Nunito', sans-serif !important; }
    h1, h2, h3, h4, h5, h6, p, span, label, div { font-family: 'Nunito', sans-serif; color: #31333F !important; }

    [data-testid="stSidebar"] { background-color: #FFF5F7 !important; border-right: 1px solid #FFE6EB !important; }
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div { display: flex !important; justify-content: center !important; width: 100% !important; }

    .sidebar-label-centrada { color: #555555 !important; font-size: 0.8rem !important; font-weight: 700 !important; text-transform: uppercase; width: 100% !important; text-align: center !important; margin-top: 15px !important; margin-bottom: 5px !important; }

    [data-testid="stSidebar"] .stButton > button {
        background-color: #FFFFFF !important; color: #FF3366 !important; border: 2px solid #FF3366 !important;
        border-radius: 12px !important; font-weight: 800 !important; width: 95% !important; margin: 5px auto !important;
        height: 45px !important; display: block !important; text-align: center !important;
    }
    [data-testid="stSidebar"] .stButton > button p { color: #FF3366 !important; font-weight: 800 !important; text-align: center !important; }

    .main-title { color: #1F2937 !important; font-weight: 900 !important; font-size: 2.5rem !important; }
    .sub-title { color: #6B7280 !important; font-weight: 600 !important; font-size: 1rem !important; }

    [data-testid="stVerticalBlockBordered"] { background-color: #FFFFFF !important; border: none !important; border-radius: 20px !important; box-shadow: 0 8px 24px rgba(0,0,0,0.06) !important; padding: 20px !important; }

    button[kind="primary"], [data-testid="baseButton-primary"] { background-color: #FF3366 !important; color: #FFFFFF !important; border-radius: 12px !important; border: none !important; font-weight: 800 !important; width: 100% !important; height: 45px !important; }
    button[kind="primary"] p, [data-testid="baseButton-primary"] p { color: #FFFFFF !important; }
    
    .dotted-divider { border-top: 2px dotted #FFE6EB; margin: 15px 0; }
    .card-title { color: #1F2937 !important; font-weight: 800 !important; font-size: 1.1rem !important; text-align: center !important; }
    .card-flavor { color: #6B7280 !important; font-size: 0.85rem !important; text-align: center !important; }
    .card-price { color: #FF3366 !important; font-weight: 900 !important; font-size: 1.4rem !important; text-align: center !important; }

    div[data-testid="column"]:nth-child(2) { border-left: 1px solid #F3F4F6 !important; padding-left: 20px !important; box-shadow: -10px 0px 15px -10px rgba(0,0,0,0.03) !important; }
</style>
"""

def obtener_script_forzar_light():
    """Retorna el script JS para forzar el tema claro."""
    return """
    <script>
        window.parent.document.documentElement.setAttribute('data-theme', 'light');
        window.parent.document.body.setAttribute('data-theme', 'light');
    </script>
    """
