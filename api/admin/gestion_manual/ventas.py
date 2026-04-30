from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from api.services.ventas_service import VentasService

router = APIRouter()

class ItemVenta(BaseModel):
    id_producto: int
    cantidad: int

class VentaRequest(BaseModel):
    metodo_pago: str
    items: List[ItemVenta]

@router.post("/vender", summary="Registrar una venta con uno o varios productos")
def vender(venta: VentaRequest):
    if venta.metodo_pago not in ("efectivo", "tarjeta"):
        raise HTTPException(status_code=400, detail="Método de pago inválido. Use 'efectivo' o 'tarjeta'")

    ok, msg, data = VentasService.realizar_venta(venta.metodo_pago, venta.items)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    
    return {
        "mensaje": msg,
        "id_venta": data["id_venta"],
        "total": data["total"],
        "metodo_pago": venta.metodo_pago,
        "items": data["items"]
    }

@router.get("/ventas", summary="Listar todas las ventas")
def listar_ventas():
    return {"ventas": VentasService.listar_ventas()}

@router.get("/ventas/{id_venta}", summary="Detalle de una venta")
def detalle_venta(id_venta: int):
    venta, detalles = VentasService.obtener_detalle_venta(id_venta)
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return {"venta": venta, "detalles": detalles}
