"""
app/ia/estilos/admin.py
───────────────────────
Estilos CSS para la página de IA del Administrador.
"""

def obtener_estilos_admin():
    return """
    <style>
    [data-testid="stMain"] { padding: 0 !important; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    </style>
    """
