from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from api.services.ia_service import IAService

router = APIRouter()

class ChatRequest(BaseModel):
    mensaje: str
    session_id: str = "default"

@router.post("/chat", summary="Chat con la IA")
def chat(request: ChatRequest):
    respuesta = IAService.procesar_mensaje(request.mensaje, request.session_id)
    if not respuesta:
        raise HTTPException(status_code=500, detail="Error al procesar el mensaje")
    return respuesta
