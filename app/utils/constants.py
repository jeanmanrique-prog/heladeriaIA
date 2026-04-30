# Colores fijos de gráficas (funcionan en ambos temas)
COLOR_OK_DARK     = "#2ecc71"
COLOR_OK_LIGHT    = "#1a8a4a"
COLOR_ALERTA      = "#e74c3c"
COLOR_BAR1_DARK   = "#f06090"
COLOR_BAR1_LIGHT  = "#d94f7a"
COLOR_BAR2        = "#ffb347"
COLOR_LINE_DARK   = "#f06090"
COLOR_LINE_LIGHT  = "#a8124a"
COLORES_PIE       = ["#f06090", "#2ecc71", "#ffb347", "#74b9ff", "#a29bfe"]

def get_graph_colors(dark: bool):
    return {
        "OK": COLOR_OK_DARK if dark else COLOR_OK_LIGHT,
        "ALERTA": COLOR_ALERTA,
        "BAR1": COLOR_BAR1_DARK if dark else COLOR_BAR1_LIGHT,
        "LINE": COLOR_LINE_DARK if dark else COLOR_LINE_LIGHT,
        "PIE": COLORES_PIE
    }
