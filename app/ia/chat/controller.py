"""
app/ia/chat/controller.py
──────────────────────────
Controlador para la lógica de chat con la IA.
"""

import streamlit as st
from mcp.voz.pipeline.pipeline_voz import responder_vendedor_json, sintetizar_audio_wav
from utilidades.gestor_sesion import GestorSesion
from utilidades.formateadores import obtener_texto_visible

class ChatController:
    @staticmethod
    def enviar_mensaje(prompt: str, mode: str = "chat"):
        """Procesa un mensaje del usuario y obtiene respuesta de la IA."""
        h_key = GestorSesion.obtener_llave_estado(mode, "historial")
        m_key = GestorSesion.obtener_llave_estado(mode, "mensajes")
        
        # 1. Agregar mensaje del usuario
        st.session_state[m_key].append(
            GestorSesion.crear_mensaje_ui("user", prompt)
        )
        st.session_state[h_key].append({"role": "user", "content": prompt})
        
        # 2. Obtener respuesta de la IA — con session_id para memoria persistente
        session_id = GestorSesion.obtener_id_sesion(mode)
        try:
            respuesta_raw = responder_vendedor_json(
                st.session_state[h_key],
                verbose=False,
                session_id=session_id
            )
        except Exception as e:
            print(f"[ChatController] Error: {e}")
            respuesta_raw = '{"accion":"informacion","mensaje":"Uy, algo salió mal. ¿Me repites el pedido?"}'

        # 3. Guardar respuesta en el estado
        st.session_state[h_key].append({"role": "assistant", "content": respuesta_raw})
        msg_ui = GestorSesion.crear_mensaje_ui("assistant", respuesta_raw)
        st.session_state[m_key].append(msg_ui)
        
        # 4. Mantenimiento de historial
        GestorSesion.recortar_historial(mode)
        
        # 5. Generar audio si la voz está activa
        if st.session_state.get("helio_voz_activa", False):
            ChatController.generar_audio_respuesta(respuesta_raw, mode)

    @staticmethod
    def generar_audio_respuesta(respuesta_raw: str, mode: str):
        """Sintetiza audio para la respuesta de la IA."""
        texto_voz = obtener_texto_visible(respuesta_raw)
        audio = sintetizar_audio_wav(texto_voz)
        if audio:
            st.session_state[GestorSesion.obtener_llave_estado(mode, "audio_respuesta")] = audio
            st.session_state[GestorSesion.obtener_llave_estado(mode, "audio_autoplay")] = True
