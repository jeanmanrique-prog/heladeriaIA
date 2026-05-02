import re
from ..procesamiento.normalizacion import normalizar_texto_base

def detectar_intencion(texto: str) -> str:
    """Retorna la intención predominante del texto."""
    t = normalizar_texto_base(texto)
    if not t:
        return "desconocido"
    
    if es_intencion_pago(t):
        return "pago"
    if es_intencion_catalogo(t):
        return "catalogo"
    if es_intencion_pedido(t):
        return "pedido"
    if es_intencion_inventario(t):
        return "inventario"
    if es_intencion_alertas(t):
        return "alertas"
    if es_intencion_recomendacion(t):
         return "recomendacion"
    if es_intencion_ventas(t):
        return "ventas"
    if es_intencion_movimientos(t):
        return "movimientos"
    if es_intencion_resumen(t):
        return "resumen"
    if es_intencion_agregar_stock(t):
        return "agregar_stock"
    if es_saludo_simple(t):
        return "saludo"
        
    return "conversacion"

def es_intencion_catalogo(t: str) -> bool:
    patrones = ("que hay", "que tienen", "que sabores", "que productos", "menu", "catalogo", "lista de productos", "disponible", "que venden", "que helados", "que hay de bueno")
    return any(p in t for p in patrones)

def es_intencion_pago(t: str) -> bool:
    if any(m in t for m in ("efectivo", "tarjeta", "nequi", "daviplata")):
        return True
    prefijos_pago = ("pago con", "pago en", "pagar con", "pagar en", "quiero pagar", "voy con", "lo pago con", "con efectivo", "con tarjeta")
    if any(p in t for p in prefijos_pago):
        return True
    return bool(re.search(r"\b(pago|pagar|metodo|forma|cobrar|efectivo|tarjeta|nequi|daviplata)\b", t))

def es_intencion_pedido(t: str) -> bool:
    # Versión simplificada para el módulo, se puede expandir con la lógica compleja de pipeline.py
    palabras = t.split()
    sabores_clave = {"fresa", "chocolate", "vainilla", "mango", "limon"}
    if len(palabras) <= 3 and not any(sabor in t for sabor in sabores_clave):
        if not re.search(r"\b(un|una|uno|dos|tres|\d+)\s+(helado|helados|tarro|tarros)\b", t):
            return False
    claves_pedido = ("quiero", "quiere", "dame", "me das", "me da", "me vende", "pedido", "pedir", "vender", "vendeme", "helado", "helados", "tarro", "tarros")
    if any(k in t for k in claves_pedido):
        return True
    if re.search(r"\b(q(?:u)?ier\w*|kier\w*|dam\w*|ped\w*)\b", t):
        return True
    return False

def es_saludo_simple(t: str) -> bool:
    saludos = {"hola", "buenas", "buenos dias", "buenas tardes", "buenas noches", "que tal", "hey", "ey", "holi", "parcero", "bro"}
    return t in saludos

def es_intencion_inventario(t: str) -> bool:
    return any(p in t for p in ("inventario", "stock", "existencias", "cuanto hay"))

def es_intencion_alertas(t: str) -> bool:
    return any(p in t for p in ("alerta", "bajo stock", "agotado"))

def es_intencion_ventas(t: str) -> bool:
    return bool(re.search(r"\b(venta|ventas|vendido|vendida)\b", t))

def es_intencion_movimientos(t: str) -> bool:
    return any(p in t for p in ("movimientos", "movimiento", "entradas y salidas"))

def es_intencion_resumen(t: str) -> bool:
    return any(p in t for p in ("resumen", "reporte", "estado del negocio"))

def es_intencion_recomendacion(t: str) -> bool:
     patrones = ("recomienda", "recomiendas", "sugieres", "sugiere", "que me recomiendas", "que sabor es bueno", "cual es el mejor", "cual me llevo", "no se cual", "no me decido", "que me aconsejas", "que me sugieres")
     return any(p in t for p in patrones)
 
def es_intencion_agregar_stock(t: str) -> bool:
    patrones = ("agregar stock", "agrega stock", "anadir stock", "reponer", "abastecer")
    return any(p in t for p in patrones)
