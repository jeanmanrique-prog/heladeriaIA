"""
Orquestador Principal de Voz — Heladería Urban
----------------------------------------------
Este módulo coordina la captura, procesamiento, transcripción,
intención y respuesta del sistema de voz.
"""

import os
import sys
import threading
import time

# Re-exportación de funciones para compatibilidad con el resto del proyecto
from ..modelos.stt import transcribir_audio, inicializar_transcriptor
from ..procesamiento.normalizacion import normalizar_para_ia as normalizar_texto_usuario_voz
from ..procesamiento.normalizacion import normalizar_para_ia
from ..modelos.tts import hablar, sintetizar_audio_wav, inicializar_voz
from ..ia.agente import responder, responder_vendedor_json, texto_voz_respuesta_vendedor, verificar_ollama
from ..ia.intencion import detectar_intencion

# Módulos para el orquestador
from ..captura.microfono import CapturadorAudio
from ..captura.vad import VAD
from ..captura.buffer import AudioBuffer
from ..procesamiento.turnos import GestorTurnos

# Re-exportación de constantes para compatibilidad
from mcp.config import MENSAJE_BIENVENIDA, MENSAJE_BIENVENIDA_CLIENTE, MODELO, PROMPT_SISTEMA_VOZ_COMPLETO
from mcp.prompts.prompt_base import SYSTEM_PROMPT
SYSTEM_PROMPT_VENDEDOR = PROMPT_SISTEMA_VOZ_COMPLETO

# Instancias globales para el orquestador
gestor_turnos = GestorTurnos()
buffer_audio = AudioBuffer()
detector_vad = VAD()

def ejecutar_pipeline_voz():
    """
    Función de orquestación principal (Ejemplo solicitado).
    Coordina el flujo desde el audio hasta la respuesta.
    """
    capturador = CapturadorAudio()
    
    def procesar_bloque(chunk):
        # 1. Detección de Voz (VAD) e Interrupción
        if detector_vad.is_speech(chunk):
            gestor_turnos.usuario_comienza_hablar()
            buffer_audio.add_chunks(chunk)
        else:
            gestor_turnos.usuario_termina_hablar()
            
            # 2. Si hay audio acumulado y el usuario dejó de hablar -> Transcribir
            if len(buffer_audio) > 8000: # aprox 0.5s de audio
                audio_wav = buffer_audio.get_wav_bytes()
                buffer_audio.clear()
                
                # 3. STT (Transcripción)
                ok, texto = transcribir_audio(audio_wav)
                if ok and texto:
                    # 4. Normalización y Corrección
                    texto_corregido = normalizar_para_ia(texto)
                    print(f"🎙️ Usuario: {texto_corregido}")
                    
                    # 5. Intención y Respuesta
                    intencion = detectar_intencion(texto_corregido)
                    # (Aquí se llamaría al agente de IA con el historial)
                    # ... lógica de respuesta ...

    # capturador.iniciar(callback=procesar_bloque)

# --- Funciones de Fachada para el resto del proyecto ---

def procesar_audio_y_responder(audio_bytes: bytes, historial: list, modo_vendedor: bool = False):
    """
    Fachada para ser llamada desde la API o el Frontend.
    """
    ok, texto = transcribir_audio(audio_bytes)
    if not ok or not texto:
        return None, None

    texto_norm = normalizar_para_ia(texto)
    
    if modo_vendedor:
        resp_json = responder_vendedor_json(historial)
        resp_voz = texto_voz_respuesta_vendedor(resp_json)
        return texto_norm, resp_voz
    else:
        resp_texto = responder(historial)
        return texto_norm, resp_texto

# --- Bucle Principal CLI (Simulación de llamada) ---

def main():
    print("=" * 55)
    print("  🍦 HELIO — Orquestador de Voz Refactorizado 🍦")
    print("=" * 55)
    
    historial = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # En modo CLI, por ahora usamos input de texto para probar la lógica de respuesta
    # ya que la captura de audio real depende del hardware.
    
    while True:
        try:
            entrada = input("👤 Tú: ").strip()
            if entrada.lower() in ("salir", "exit"): break
            
            # Normalizar
            texto_norm = normalizar_para_ia(entrada)
            
            # Responder
            respuesta = responder(historial + [{"role": "user", "content": texto_norm}])
            print(f"🤖 Helio: {respuesta}")
            
            # Hablar con soporte para interrupciones
            hablar(respuesta, gestor_turnos=gestor_turnos)
            
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
