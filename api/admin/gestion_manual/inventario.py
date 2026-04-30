from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from api.services.inventario_service import InventarioService

router = APIRouter()

class EntradaInventario(BaseModel):
    id_producto: int
    cantidad: int
    motivo: str = "Reposición"

@router.get("/sabores", summary="Listar todos los sabores activos")
def listar_sabores():
    return {"sabores": InventarioService.listar_sabores()}

@router.get("/sabores/{id_sabor}", summary="Obtener un sabor por ID")
def obtener_sabor(id_sabor: int):
    sabor = InventarioService.obtener_sabor(id_sabor)
    if not sabor:
        raise HTTPException(status_code=404, detail="Sabor no encontrado")
    return sabor

@router.get("/productos", summary="Listar todos los productos con stock")
def listar_productos():
    return {"productos": InventarioService.listar_productos()}

@router.get("/productos/{id_producto}", summary="Obtener un producto por ID")
def obtener_producto(id_producto: int):
    producto = InventarioService.obtener_producto(id_producto)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

@router.get("/inventario", summary="Ver estado del inventario completo")
def ver_inventario():
    return {"inventario": InventarioService.ver_inventario()}

@router.get("/inventario/alertas", summary="Productos con stock bajo")
def alertas_stock():
    return {"alertas": InventarioService.alertas_stock()}

@router.post("/inventario/entrada", summary="Agregar stock a un producto")
def entrada_inventario(entrada: EntradaInventario):
    ok, msg = InventarioService.entrada_inventario(entrada.id_producto, entrada.cantidad, entrada.motivo)
    if not ok:
        raise HTTPException(status_code=404, detail=msg)
    return {"mensaje": msg}

@router.get("/movimientos", summary="Ver historial de movimientos de inventario")
def listar_movimientos():
    return {"movimientos": InventarioService.listar_movimientos()}
