import json
import uuid
import time
from typing import Optional
from api.ia.estado import GestorEstado
from mcp.voz.pipeline.pipeline_voz import responder_vendedor_json, SYSTEM_PROMPT_VENDEDOR, MENSAJE_BIENVENIDA_CLIENTE

class IAService:
    _sesiones = {}

    @classmethod
    def obtener_sesion(cls, session_id: str):
        if session_id not in cls._sesiones:
            cls._sesiones[session_id] = {
                "historial": [
                    {"role": "system", "content": SYSTEM_PROMPT_VENDEDOR},
                    {"role": "assistant", "content": MENSAJE_BIENVENIDA_CLIENTE},
                ],
                "last_seen": time.time()
            }
        return cls._sesiones[session_id]

    @classmethod
    def procesar_mensaje(cls, mensaje: str, session_id: str):
        sesion = cls.obtener_sesion(session_id)
        sesion["historial"].append({"role": "user", "content": mensaje})
        sesion["last_seen"] = time.time()

        try:
            # Llamada al core de la IA con el session_id para manejar el estado
            # Pasamos el session_id para que el agente pueda recuperar el estado persistente
            respuesta_raw = responder_vendedor_json(sesion["historial"], session_id=session_id)
            
            # Intentar parsear si es JSON
            try:
                respuesta_data = json.loads(respuesta_raw)
            except:
                respuesta_data = {"mensaje": respuesta_raw, "accion": "informacion"}
                
            sesion["historial"].append({"role": "assistant", "content": respuesta_raw})
            return respuesta_data
        except Exception as e:
            print(f"Error en IAService: {e}")
            return {"mensaje": "Uy bro, ahí se enredó el proceso.", "accion": "informacion"}
            
    @classmethod
    def limpiar_sesiones_antiguas(cls, ttl_segundos: int = 3600):
        now = time.time()
        expiradas = [sid for sid, s in cls._sesiones.items() if (now - s["last_seen"]) > ttl_segundos]
        for sid in expiradas:
            del cls._sesiones[sid]
