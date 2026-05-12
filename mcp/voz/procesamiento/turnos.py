"""
🚦 GESTOR DE TURNOS — EL SEMÁFORO DE LA CHARLA
----------------------------------------------
En una conversación real, la gente se interrumpe. Este archivo controla que 
Urban sepa callarse si el usuario empieza a hablar mientras él responde.

¿QUÉ HACE EXACTAMENTE?
1. CONTROL DE ESTADO: Sabe si la IA está hablando o si el usuario está hablando.
2. INTERRUPCIÓN (Barge-in): Si tú hablas mientras Urban te responde, este archivo 
   activa una señal para detener el sonido de la IA inmediatamente.
3. FLUIDEZ: Asegura que el micrófono no intente grabar lo que la propia IA 
   está diciendo por los parlantes.

FLUJO DETALLADO POR ARCHIVO:
1. DETECTAR: 'pipeline_voz.py' detecta que el usuario empezó a hablar.
2. NOTIFICAR: El pipeline llama a este archivo ('turnos.py') para marcar el turno del usuario.
3. INTERRUMPIR: Si la IA estaba hablando mediante 'tts.py', este archivo le envía una 
   señal de cancelación inmediata para que Urban guarde silencio.
4. LIBERAR: Cuando el usuario termina, el pipeline avisa a este archivo para que la 
   IA pueda volver a pensar y responder.
"""
import threading

class GestorTurnos:
    def __init__(self):
        self._ia_hablando = False
        self._usuario_hablando = False
        self._cancelar_tts = threading.Event()

    def ia_comienza_hablar(self):
        self._ia_hablando = True
        self._cancelar_tts.clear()

    def ia_termina_hablar(self):
        self._ia_hablando = False

    def usuario_comienza_hablar(self):
        self._usuario_hablando = True
        if self._ia_hablando:
            # BARGE-IN: El usuario interrumpió a la IA
            self.interrumpir_ia()

    def usuario_termina_hablar(self):
        self._usuario_hablando = False

    def interrumpir_ia(self):
        """Activa la señal para cancelar el TTS actual."""
        print("⚠️ Interrupción detectada: Cancelando respuesta de la IA.")
        self._cancelar_tts.set()
        self._ia_hablando = False

    def debe_cancelar_tts(self) -> bool:
        return self._cancelar_tts.is_set()

    @property
    def hay_interrupcion(self) -> bool:
        return self._cancelar_tts.is_set()
