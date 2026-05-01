from typing import Dict, Optional

class GestorEstado:
    """
    Gestiona el estado persistente de la conversación para la IA.
    Evita que el modelo pierda contexto de qué producto se está vendiendo.
    """
    _estados: Dict[str, dict] = {}

    @classmethod
    def obtener_estado(cls, session_id: str) -> dict:
        if session_id not in cls._estados:
            cls._estados[session_id] = {
                "producto": None,
                "precio": None,
                "pago": None,
                "confirmado": False,
                "paso": "inicio"
            }
        return cls._estados[session_id]

    @classmethod
    def actualizar_estado(cls, session_id: str, data: dict):
        estado = cls.obtener_estado(session_id)
        for key, value in data.items():
            if value is not None:
                estado[key] = value
        
        # Lógica de transición de pasos
        if estado["producto"] and not estado["pago"]:
            estado["paso"] = "esperando_pago"
        elif estado["producto"] and estado["pago"]:
            estado["paso"] = "completado"
        
        cls._estados[session_id] = estado

    @classmethod
    def limpiar_estado(cls, session_id: str):
        if session_id in cls._estados:
            del cls._estados[session_id]
