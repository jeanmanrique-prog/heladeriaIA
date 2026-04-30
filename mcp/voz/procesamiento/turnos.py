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
