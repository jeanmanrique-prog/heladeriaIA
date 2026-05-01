from api.ia.estado import GestorEstado

class ContextoResource:
    """
    Recurso de solo lectura para proveer el estado actual del pedido a la IA.
    Garantiza que el modelo recuerde qué producto y pago se han discutido.
    """
    @staticmethod
    def get_context_text(session_id: str) -> str:
        estado = GestorEstado.obtener_estado(session_id)
        producto = estado.get("producto")
        pago = estado.get("pago")
        precio = estado.get("precio")
        
        if not producto and not pago:
            return ""

        txt = "\n═══ CONTEXTO DE LA VENTA ACTUAL ═══\n"
        if producto:
            txt += f"PRODUCTO: {producto.upper()}\n"
            if precio:
                txt += f"PRECIO: {precio:,} pesos\n".replace(",", ".")
        if pago:
            txt += f"PAGO: {pago.upper()}\n"
        
        # Lógica de sugerencia de acción para el backend/modelo
        if producto and pago:
            txt += "ESTADO: COMPLETO. Proceder a cerrar la venta.\n"
        elif producto:
            txt += "ESTADO: PENDIENTE PAGO. Preguntar método de pago.\n"
            
        txt += "═══════════════════════════════════\n"
        return txt
