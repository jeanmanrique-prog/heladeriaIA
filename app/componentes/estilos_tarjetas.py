"""
app/componentes/estilos_tarjetas.py
───────────────────────────────────
Estilos CSS para las tarjetas de productos y métricas.
"""

def obtener_estilo_tarjeta_metrica(bg_color, label_color, val_color):
    """Retorna el estilo CSS para una tarjeta de métrica."""
    return f"""
    <div style="background-color: {bg_color}; padding: 20px; border-radius: 15px; border: 1px solid rgba(0,0,0,0.05); text-align: center;">
    """

def obtener_estilo_tarjeta_producto(input_bg, border_color):
    """Retorna el estilo CSS para una tarjeta de producto."""
    return f"""
    <div style="background-color: {input_bg}; border-radius: 15px; padding: 20px; text-align: center; border: 1px solid {border_color}; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 20px;">
    """
