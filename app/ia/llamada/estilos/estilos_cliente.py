"""
app/ia/estilos/cliente.py
─────────────────────────
Estilos CSS para la página de IA del Cliente.
"""

def obtener_estilos_cliente():
    return """
    <style>
    [data-testid="stMain"] { padding: 0 !important; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    
    /* Imagen lateral alineada al fondo de la tarjeta */
    .img-bottom-align {
        display: flex;
        align-items: flex-end;
        height: 100%;
        padding-bottom: 0;
    }
    .img-bottom-align img {
        width: 100%;
        display: block;
        border-radius: 0 0 16px 0;
    }
    </style>
    """
