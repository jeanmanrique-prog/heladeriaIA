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
    modelo_display = MODELO if ollama_ok else "Sin conexión"
    dot_color = "#2ecc71" if ollama_ok else "#e74c3c"
    
    st.markdown(f"""
        <style>
        .helio-badge {{
            display: inline-flex; align-items: center; gap: 7px;
            background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.14);
            border-radius: 20px; padding: 5px 14px; font-size: 0.78rem; font-weight: 700;
        }}
        .helio-badge .dot {{
            width: 9px; height: 9px; border-radius: 50%;
            background: {dot_color}; box-shadow: 0 0 6px {dot_color};
        }}
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f'<div class="helio-badge"><span class="dot"></span><span>{modelo_display}</span></div>', unsafe_allow_html=True)
    with col2:
        if st.button("🔄 Nuevo", key=f"reset_{mode}", use_container_width=True):
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
    
    ollama_ok = st.session_state.get("helio_ollama_ok", False)
    accent = theme.get("ACCENT", "#a8124a") if theme else "#a8124a"
    
    render_header_chat(mode, ollama_ok, accent)
    st.divider()
    
    # Saludo por voz inicial
    if not st.session_state.get(SessionManager.state_key(mode, "saludo_enviado"), False):
        if st.session_state.get("helio_voz_activa", False):
            audio = sintetizar_audio_wav(texto_visible_asistente(MENSAJE_BIENVENIDA_CLIENTE))
            render_audio_invisible(audio)
            st.session_state[SessionManager.state_key(mode, "saludo_enviado")] = True

    # Historial
    m_key = SessionManager.state_key(mode, "mensajes")
    for m in st.session_state[m_key]:
        with st.chat_message(m["role"]):
            if m["role"] == "assistant":
                render_message_assistant(m)
            else:
                st.write(m["display"])

    # Audio respuesta pendiente
    audio_resp = st.session_state.get(SessionManager.state_key(mode, "audio_respuesta"))
    if audio_resp and st.session_state.get(SessionManager.state_key(mode, "audio_autoplay"), False):
        render_audio_invisible(audio_resp)
        st.session_state[SessionManager.state_key(mode, "audio_autoplay")] = False

    # Input
    if prompt := st.chat_input("Dime qué deseas pedir...", disabled=not ollama_ok or not api_ok):
        ChatController.enviar_mensaje(prompt, mode)
        st.rerun()
