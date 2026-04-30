"""
app/ia/chat/controller.py
──────────────────────────
Controlador para la lógica de chat con la IA.
"""

import streamlit as st
from mcp.voz.pipeline.pipeline_voz import responder_vendedor_json, sintetizar_audio_wav
from utils.session_manager import SessionManager
from utils.formatters import texto_visible_asistente

class ChatController:
    @staticmethod
    def enviar_mensaje(prompt: str, mode: str = "chat"):
        """Procesa un mensaje del usuario y obtiene respuesta de la IA."""
        h_key = SessionManager.state_key(mode, "historial")
        m_key = SessionManager.state_key(mode, "mensajes")
        
        # 1. Agregar mensaje del usuario
        st.session_state[m_key].append(
            SessionManager.create_ui_message("user", prompt)
        )
        st.session_state[h_key].append({"role": "user", "content": prompt})
        
        # 2. Obtener respuesta de la IA
        try:
            respuesta_raw = responder_vendedor_json(
                st.session_state[h_key],
                verbose=False
            )
        except Exception:
            respuesta_raw = '{"accion":"error","mensaje":"No pude procesar tu mensaje. Intenta de nuevo."}'

        # 3. Guardar respuesta en el estado
        st.session_state[h_key].append({"role": "assistant", "content": respuesta_raw})
        msg_ui = SessionManager.create_ui_message("assistant", respuesta_raw)
        st.session_state[m_key].append(msg_ui)
        
        # 4. Mantenimiento de historial
        SessionManager.trim_history(mode)
        
        # 5. Generar audio si la voz está activa
        if st.session_state.get("helio_voz_activa", False):
            ChatController.generar_audio_respuesta(respuesta_raw, mode)

    @staticmethod
    def generar_audio_respuesta(respuesta_raw: str, mode: str):
        """Sintetiza audio para la respuesta de la IA."""
        texto_voz = texto_visible_asistente(respuesta_raw)
        audio = sintetizar_audio_wav(texto_voz)
        if audio:
            st.session_state[SessionManager.state_key(mode, "audio_respuesta")] = audio
            st.session_state[SessionManager.state_key(mode, "audio_autoplay")] = True
