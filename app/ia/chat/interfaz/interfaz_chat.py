"""
app/ia/chat/interfaz/interfaz_chat.py
───────────────────────────────────
Interfaz de usuario para el chat de IA.
"""

import streamlit as st
import streamlit.components.v1 as components
import base64
from mcp.voz.pipeline.pipeline_voz import MODELO, MENSAJE_BIENVENIDA_CLIENTE, sintetizar_audio_wav
from utilidades.gestor_sesion import GestorSesion
from utilidades.formateadores import obtener_texto_visible
from ia.chat.controller import ChatController
from ia.chat.estilos.estilos_chat import obtener_estilos_chat
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
    ia_avatar_path = Path(__file__).resolve().parent.parent.parent.parent.parent / "imagenes" / "perfil_ia.png"
    avatar_b64 = ""
    if ia_avatar_path.exists():
        with open(ia_avatar_path, "rb") as img_file:
            avatar_b64 = base64.b64encode(img_file.read()).decode()
            
    avatar_src = f"data:image/png;base64,{avatar_b64}" if avatar_b64 else "https://api.dicebear.com/7.x/bottts/svg?seed=Urban"
    
    modelo_display = "Ollama 3.2:1b"
    status_text = "En línea" if ollama_ok else "Sin conexión"
    dot_color = "#2ecc71" if ollama_ok else "#e74c3c"
    
    # Inyectar estilos específicos del chat
    st.markdown(obtener_estilos_chat(dot_color), unsafe_allow_html=True)
    
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
            GestorSesion.reiniciar_conversacion(mode)
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
    GestorSesion.inicializar_modo(mode)
    
    ollama_ok = st.session_state.get("helio_ollama_ok", False)
    accent = theme.get("ACCENT", "#a8124a") if theme else "#a8124a"
    
    # TARJETA EXTERIOR
    with st.container(border=True):
        
        # HEADER (Fijo dentro de la tarjeta)
        render_header_chat(mode, ollama_ok, accent)
        st.markdown("<hr style='margin-top: 5px; margin-bottom: 10px; border: 0; border-top: 1px solid #eee;'>", unsafe_allow_html=True)
        
        # CONTENEDOR CON SCROLL (Solo para los mensajes)
        with st.container(height=400):
            # Historial
            m_key = GestorSesion.obtener_llave_estado(mode, "mensajes")
            root_img = Path(__file__).resolve().parent.parent.parent.parent.parent / "imagenes"
            ia_avatar_path = str(root_img / "perfil_ia.png")
            client_avatar_path = str(root_img / "perfil_cliente.png")
            
            for m in st.session_state[m_key]:
                avatar = ia_avatar_path if m["role"] == "assistant" else client_avatar_path
                with st.chat_message(m["role"], avatar=avatar):
                    if m["role"] == "assistant":
                        render_message_assistant(m)
                    else:
                        st.write(m["display"])

        # Input (Dentro de la tarjeta exterior, debajo del historial)
        if prompt := st.chat_input("Escribe tu pedido...", disabled=not ollama_ok or not api_ok):
            ChatController.enviar_mensaje(prompt, mode)
            st.rerun()
