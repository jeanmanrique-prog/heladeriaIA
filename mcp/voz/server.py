"""
Servidor de Voz — Heladería Urban
---------------------------------
Este servidor gestiona las conexiones persistentes para llamadas en tiempo real,
utilizando WebSockets o streaming de audio continuo.
"""

from fastapi import APIRouter, WebSocket
from .pipeline.pipeline_voz import gestor_turnos, buffer_audio, detector_vad

router = APIRouter()

@router.websocket("/ws/voz")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_bytes()
            # Lógica de procesamiento de audio en tiempo real
            pass
    except Exception:
        await websocket.close()
