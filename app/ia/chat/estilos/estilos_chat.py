"""
app/ia/chat/estilos_chat.py
───────────────────────────
Estilos CSS para la interfaz de chat.
"""

def obtener_estilos_chat(dot_color):
    """Retorna los estilos CSS para la interfaz de chat."""
    return f"""
<style>
/* Fondo Integral (Blanco) */
[data-testid="stAppViewContainer"], [data-testid="stHeader"], .stApp, [data-testid="stMain"] {{
    background-color: #FFFFFF !important;
}}

/* Estilo de la Tarjeta del Chat (Blanca con Sombra) */
[data-testid="stVerticalBlockBorderWrapper"] {{
    border: 1px solid #F0F0F0 !important;
    border-radius: 20px !important;
    padding: 10px 15px !important;
    background-color: #FFFFFF !important;
    box-shadow: 0 10px 30px rgba(0,0,0,0.05) !important;
}}

/* CONTENEDOR DE MENSAJES (Rosa muy claro) */
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlockBorderWrapper"] {{
    border: 1px solid #FFE6EB !important;
    border-radius: 15px !important;
    padding: 15px !important;
    background-color: #FFF5F7 !important;
}}

/* Forzar que el chat_input se quede abajo de la tarjeta */
.stChatInput {{
    margin-top: 2px !important;
}}

/* Cambiar el fondo de la burbuja del usuario a rosa */
[data-testid="stChatMessageUser"] {{
    background-color: #FF3366 !important;
    color: white !important;
    flex-direction: row-reverse;
    border: none !important;
}}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {{
    background-color: #FF3366 !important;
    color: white !important;
    flex-direction: row-reverse;
    border: none !important;
}}

/* Redondear las burbujas */
[data-testid="stChatMessage"] {{
    border-radius: 18px;
    margin-bottom: 8px;
    padding: 4px 12px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    border: 1px solid #eee;
}}

/* Mensajes de IA: fondo gris muy claro */
[data-testid="stChatMessage"]:not(:has([data-testid="chatAvatarIcon-user"])):not([data-testid="stChatMessageUser"]) {{
    background-color: #f8f9fa !important;
}}

/* Compactar el perfil en el header */
.chat-profile img {{ width: 45px !important; height: 45px !important; }}
.chat-profile-info h3 {{ font-size: 1.1rem !important; }}

/* Estilos del Header del Chat */
.chat-header-container {{
    display: flex; align-items: center; justify-content: space-between;
    padding-bottom: 10px; margin-bottom: 5px;
}}
.chat-profile {{
    display: flex; align-items: center; gap: 15px;
}}
.chat-profile img {{
    width: 55px; height: 55px; border-radius: 50%; object-fit: cover;
    border: 2px solid #FF3366;
}}
.chat-profile-info h3 {{
    margin: 0; padding: 0; font-size: 1.3rem; font-weight: 800; color: #333;
}}
.chat-status {{
    font-size: 0.8rem; color: #666; display: flex; align-items: center; gap: 6px; margin-top: 2px;
}}
.dot-online {{
    width: 8px; height: 8px; background-color: {dot_color}; border-radius: 50%;
    display: inline-block; box-shadow: 0 0 5px {dot_color};
}}
</style>
"""
