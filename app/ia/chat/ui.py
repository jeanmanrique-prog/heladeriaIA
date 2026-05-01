"""
app/ia/chat/ui.py
──────────────────
Interfaz de usuario para el chat de IA.
"""

import streamlit as st
import streamlit.components.v1 as components
import base64
from mcp.voz.pipeline.pipeline_voz import MODELO, MENSAJE_BIENVENIDA_CLIENTE, sintetizar_audio_wav
from utils.session_manager import SessionManager
from utils.formatters import texto_visible_asistente
from ia.chat.controller import ChatController
from pathlib import Path

def render_audio_invisible(audio_bytes: bytes):
    """Reproduce audio automáticamente sin mostrar controles."""
    if not audio_bytes:
        return
    b64 = base64.b64encode(audio_bytes).decode()
    components.html(
        f'<audio autoplay style="display:none"><source src="data:audio/wav;base64,{b64}" type="audio/wav"></audio>',
        height=0,
    )

def render_header_chat(mode: str, ollama_ok: bool, accent: str):
    """Renderiza el header con el badge del modelo y el botón de reset."""
    ia_avatar_path = Path(__file__).resolve().parent.parent.parent.parent / "imagenes" / "perfil_ia.png"
    avatar_b64 = ""
    if ia_avatar_path.exists():
        with open(ia_avatar_path, "rb") as img_file:
            avatar_b64 = base64.b64encode(img_file.read()).decode()
            
    avatar_src = f"data:image/png;base64,{avatar_b64}" if avatar_b64 else "https://api.dicebear.com/7.x/bottts/svg?seed=Urban"
    
    modelo_display = "Ollama 3.2:1b"
    status_text = "En línea" if ollama_ok else "Sin conexión"
    dot_color = "#2ecc71" if ollama_ok else "#e74c3c"
    
    st.markdown(f"""
        <style>
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
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f'''
            <div class="chat-header-container" style="border:none; margin:0; padding:0;">
                <div class="chat-profile">
                    <img src="{avatar_src}">
                    <div class="chat-profile-info">
                        <h3>Chat con Urban</h3>
                        <div class="chat-status">{modelo_display} <span class="dot-online"></span> {status_text}</div>
                    </div>
                </div>
            </div>
        ''', unsafe_allow_html=True)
    with col2:
        if st.button("⊕ Nuevo chat", key=f"reset_{mode}", use_container_width=True):
            SessionManager.reset_conversation(mode)
            st.rerun()

def render_message_assistant(mensaje: dict):
    """Renderiza un mensaje de la IA de forma inteligente."""
    display = mensaje.get("display", "")
    payload = mensaje.get("payload")

    if not payload or not isinstance(payload, dict):
        st.write(display)
        return

    accion = payload.get("accion", "informacion")
    st.write(display)

    if accion == "mostrar_productos":
        prods = payload.get("productos", [])
        if prods:
            st.dataframe(prods, use_container_width=True, hide_index=True)
    elif accion in {"pedir_pago", "crear_venta", "venta_exitosa"}:
        items = payload.get("items", []) or payload.get("detalle", {}).get("productos", [])
        if items:
            st.dataframe(items, use_container_width=True, hide_index=True)
        total = payload.get("total") or payload.get("detalle", {}).get("total")
        if total:
            st.info(f"Total a pagar: {total}")
        
        if accion == "venta_exitosa":
            st.balloons()
            st.toast("¡Venta completada con éxito! 🤩")

def render_chat_interface(api_ok: bool = True, theme: dict = None):
    """Punto de entrada para la UI del chat."""
    mode = "chat"
    SessionManager.initialize_mode(mode)
    
    st.markdown("""
        <style>
        /* Estilo de la Tarjeta del Chat */
        [data-testid="stVerticalBlockBorderWrapper"] {
            border: 1px solid #F0F0F0 !important;
            border-radius: 20px !important;
            padding: 20px !important;
            background-color: #FFFFFF !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
        }

        /* Quitar el estilo de tarjeta al contenedor interno del scroll (height=500) para no duplicar cajas */
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlockBorderWrapper"] {
            border: none !important;
            box-shadow: none !important;
            padding: 0 5px 0 0 !important;
            background-color: transparent !important;
        }

        /* Forzar que el chat_input se quede abajo de la tarjeta */
        .stChatInput {
            margin-top: 10px !important;
        }

        /* Cambiar el fondo de la burbuja del usuario a rosa */
        [data-testid="stChatMessageUser"] {
            background-color: #FF3366 !important;
            color: white !important;
            flex-direction: row-reverse;
            border: none !important;
        }
        /* Compatibilidad con Streamlit moderno */
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
            background-color: #FF3366 !important;
            color: white !important;
            flex-direction: row-reverse;
            border: none !important;
        }
        
        /* Redondear las burbujas */
        [data-testid="stChatMessage"] {
            border-radius: 20px;
            margin-bottom: 15px;
            padding: 5px 15px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.03);
            border: 1px solid #eee;
        }

        /* Mensajes de IA: fondo gris muy claro */
        [data-testid="stChatMessage"]:not(:has([data-testid="chatAvatarIcon-user"])):not([data-testid="stChatMessageUser"]) {
            background-color: #f8f9fa !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    ollama_ok = st.session_state.get("helio_ollama_ok", False)
    accent = theme.get("ACCENT", "#a8124a") if theme else "#a8124a"
    
    # TARJETA EXTERIOR
    with st.container(border=True):
        
        # HEADER (Fijo dentro de la tarjeta)
        render_header_chat(mode, ollama_ok, accent)
        st.markdown("<hr style='margin-top: 15px; margin-bottom: 20px; border: 0; border-top: 1px solid #eee;'>", unsafe_allow_html=True)
        
        # CONTENEDOR CON SCROLL (Solo para los mensajes)
        with st.container(height=500):
            # Saludo por voz inicial
            if not st.session_state.get(SessionManager.state_key(mode, "saludo_enviado"), False):
                if st.session_state.get("helio_voz_activa", False):
                    audio = sintetizar_audio_wav(texto_visible_asistente(MENSAJE_BIENVENIDA_CLIENTE))
                    render_audio_invisible(audio)
                    st.session_state[SessionManager.state_key(mode, "saludo_enviado")] = True

            # Historial
            m_key = SessionManager.state_key(mode, "mensajes")
            root_img = Path(__file__).resolve().parent.parent.parent.parent / "imagenes"
            ia_avatar_path = str(root_img / "perfil_ia.png")
            client_avatar_path = str(root_img / "perfil_cliente.png")
            
            for m in st.session_state[m_key]:
                avatar = ia_avatar_path if m["role"] == "assistant" else client_avatar_path
                with st.chat_message(m["role"], avatar=avatar):
                    if m["role"] == "assistant":
                        render_message_assistant(m)
                    else:
                        st.write(m["display"])

            # Audio respuesta pendiente
            audio_resp = st.session_state.get(SessionManager.state_key(mode, "audio_respuesta"))
            if audio_resp and st.session_state.get(SessionManager.state_key(mode, "audio_autoplay"), False):
                render_audio_invisible(audio_resp)
                st.session_state[SessionManager.state_key(mode, "audio_autoplay")] = False

        # Input (Dentro de la tarjeta exterior, debajo del historial)
        if prompt := st.chat_input("Escribe tu pedido...", disabled=not ollama_ok or not api_ok):
            ChatController.enviar_mensaje(prompt, mode)
            st.rerun()
