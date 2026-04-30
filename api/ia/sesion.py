from fastapi import APIRouter
from api.services.ia_service import IAService

router = APIRouter()

@router.post("/sesion/limpiar", summary="Limpia la sesión actual de la IA")
def limpiar_sesion(session_id: str):
    if session_id in IAService._sesiones:
        del IAService._sesiones[session_id]
        return {"mensaje": "Sesión limpia"}
    return {"mensaje": "Sesión no encontrada"}

@router.post("/sesion/limpiar-todo", summary="Limpia todas las sesiones expiradas")
def limpiar_todas():
    IAService.limpiar_sesiones_antiguas()
    return {"mensaje": "Limpieza completada"}
