import json
import re
import requests
import ollama
import time
from typing import Optional, Dict, List, Any

from mcp.config import MODELO, API_URL
from mcp.prompts.prompt_base import SYSTEM_PROMPT
from mcp.prompts.prompt_ventas import PROMPT_VENDEDOR as SYSTEM_PROMPT_VENDEDOR
from mcp.prompts.prompt_estado import PROMPT_ESTADO
from mcp.prompts.prompt_pagos import PROMPT_PAGOS
from mcp.prompts.prompt_sugerencias import PROMPT_SUGERENCIAS

from ..procesamiento.normalizacion import normalizar_texto_base
from mcp.tools.catalog_tools import obtener_catalogo_real
from api.ia.estado import GestorEstado
from .intencion import detectar_intencion

# ──────────────────────────────────────────────────────────
# CONSTANTES Y RECURSOS
# ──────────────────────────────────────────────────────────

_METODOS_PAGO = ["efectivo", "tarjeta", "nequi", "daviplata"]
_CONFIRMACIONES = ["si", "sí", "dale", "ok", "listo", "de una", "hágale", "claro", "perfecto"]

# ──────────────────────────────────────────────────────────
# NORMALIZACIÓN ROBUSTA
# ──────────────────────────────────────────────────────────

def normalizar_texto_usuario_voz(texto: str) -> str:
    """Normalización fonética y de limpieza para el transcriptor."""
    if not texto: return ""
    t = texto.lower().strip()
    # Reemplazos fonéticos comunes
    reemplazos = [
        (r"quieto|qiero|kiero|quisira|quisera|quera|ero|y ero|y era", "quiero"),
        (r"elado|helao|elao|lado|celado|celados", "helado"),
        (r"efecto|perfecto|festivo|efectiva", "efectivo"),
        (r"targeta|tarjera|targueta", "tarjeta"),
        (r"comienda|remienda|recomiendo", "recomienda"),
        (r"choclate|choclati|colate|olate", "chocolate"),
        (r"presa|fresa", "fresa"),
        (r"vainilla|vainia|vainilla", "vainilla"),
        (r"brownie|broni|brauni", "brownie"),
        (r"limon|limn|imin|limones", "limón"),
        (r"y me|dame|ver|manda", "mostrar")
    ]
    for p, r in reemplazos:
        t = re.sub(p, r, t)
    return t

# ──────────────────────────────────────────────────────────
# LÓGICA DE ESTADO (BACKEND-DRIVEN)
# ──────────────────────────────────────────────────────────

def _obtener_catalogo_map():
    catalogo = obtener_catalogo_real()
    cmap = {}
    for p in catalogo:
        sabor = normalizar_texto_usuario_voz(p.get("sabor") or "").strip()
        if sabor:
            cmap[sabor] = {
                "id": p.get("id_producto"),
                "precio": int(float(p.get("precio_unitario") or 0)),
                "stock": int(p.get("stock") or 0)
            }
    return cmap

def procesar_logica_ventas(msg_usuario: str, session_id: str) -> Optional[dict]:
    """
    INTERCEPTOR DE BACKEND: Decide si responder directamente sin LLM.
    Implementa la máquina de estados estricta.
    """
    cmap = _obtener_catalogo_map()
    estado = GestorEstado.obtener_estado(session_id)
    t = normalizar_texto_usuario_voz(msg_usuario)
    
    # 1. DETECTAR PRODUCTO Y CANTIDAD
    # Buscar números o palabras clave de "todo"
    es_todo = any(word in t for word in ["todo", "todos", "lo que tenga", "lo que quede", "lo que queda", "completos"])
    numeros = re.findall(r'\d+', t)
    cantidad_detectada = int(numeros[0]) if numeros else None

    for sabor, datos in cmap.items():
        if sabor in t and len(sabor) > 3:
            # Si pidió "todo", la cantidad es el stock disponible
            cantidad = datos["stock"] if es_todo else (cantidad_detectada or 1)

            # VALIDACIÓN DE STOCK REAL PARA LA CANTIDAD PEDIDA
            if datos["stock"] < cantidad or cantidad <= 0:
                mensaje_agotado = f"Ay bro, me vas a matar pero de {sabor.capitalize()} solo me quedan {datos['stock']} unidades. ¿Te empaco esas o prefieres ver otro sabor?"
                if datos["stock"] <= 0:
                    mensaje_agotado = f"Ay bro, el de {sabor.capitalize()} se me acaba de agotar totalmente. ¿No te provoca otro o miramos el catálogo?"
                
                return {
                    "accion": "informacion",
                    "mensaje": mensaje_agotado
                }
            
            estado.update({
                "producto": sabor,
                "cantidad": cantidad,
                "precio_total": datos["precio"] * cantidad,
                "paso": "esperando_pago"
            })
            GestorEstado.actualizar_estado(session_id, estado)
            
            total_fmt = f"{datos['precio'] * cantidad:,}".replace(",", ".")
            msj_vendedor = f"¡De una! Te empaco los {cantidad} de {sabor.capitalize()} que me quedan. 🍦" if es_todo else f"¡Listo! {cantidad} de {sabor.capitalize()} 🍦."
            
            return {
                "accion": "pedir_pago",
                "mensaje": f"{msj_vendedor} El total serían {total_fmt} pesos. ¿Pagas con efectivo o tarjeta?",
                "total": datos["precio"] * cantidad,
                "items": [{"id_producto": datos["id"], "sabor": sabor, "cantidad": cantidad}]
            }

    # 2. DETECTAR PAGO
    if estado.get("paso") == "esperando_pago" and estado.get("producto"):
        pago_detectado = next((m for m in _METODOS_PAGO if m in t), None)
        if pago_detectado:
            producto_sabor = estado["producto"]
            cantidad = estado.get("cantidad", 1)
            producto_id = cmap.get(producto_sabor, {}).get("id")
            
            # EJECUTAR VENTA REAL
            venta_ok = False
            if producto_id:
                res = crear_venta_api([{"id_producto": producto_id, "cantidad": cantidad}], pago_detectado)
                venta_ok = "error" not in res
            
            if venta_ok:
                GestorEstado.limpiar_estado(session_id)
                return {
                    "accion": "venta_exitosa",
                    "mensaje": f"¡Listo bro! Ahí te mando los {cantidad} de {producto_sabor.capitalize()}. 🎉 ¡Disfrútalos!",
                    "detalle": {"producto": producto_sabor, "cantidad": cantidad, "pago": pago_detectado}
                }
            else:
                return {
                    "accion": "informacion",
                    "mensaje": "Uy bro, tuve un problemita técnico registrando la venta. ¿Intentamos de nuevo?"
                }

    return None # Si no hay lógica de venta clara, usar LLM

def verificar_ollama() -> tuple[bool, str]:
    """Comprueba si Ollama está corriendo y el modelo está disponible."""
    try:
        ollama.list()
        return True, f"Ollama está listo ({MODELO})."
    except Exception as e:
        err = str(e).lower()
        if "connect" in err or "unreachable" in err or "refused" in err:
            msg = "No se pudo conectar con Ollama. ¿Está el servidor iniciado?"
        elif "not found" in err:
            msg = f"El modelo '{MODELO}' no está descargado en Ollama."
        else:
            msg = "Ollama no responde. Asegúrate de que la aplicación esté abierta."
        return False, msg

# ──────────────────────────────────────────────────────────
# INTEGRACIÓN LLM (ESTILO Y CHARLA)
# ──────────────────────────────────────────────────────────

def _enriquecer_historial(historial: list, session_id: str) -> list:
    """Añade contexto mínimo para que el LLM mantenga el tono."""
    estado = GestorEstado.obtener_estado(session_id)
    estado_txt = f"Estado actual del pedido: {json.dumps(estado, ensure_ascii=False)}"
    
    extra = f"\n\nInstrucciones: Eres Urban, un vendedor de helados relajado de Medellín. " \
            f"No inventes precios. Si el usuario pregunta qué hay, dile que mire el catálogo. " \
            f"IMPORTANTE: Responde SOLO con texto natural, NUNCA uses formato JSON ni llaves {{}} en tu respuesta. " \
            f"Mantén la charla corta.\n{estado_txt}"
    
    enriquecido = []
    found_system = False
    for m in historial:
        if m.get('role') == 'system':
            enriquecido.append({'role': 'system', 'content': m['content'] + extra})
            found_system = True
        else:
            enriquecido.append(m)
    if not found_system:
        enriquecido.insert(0, {'role': 'system', 'content': extra})
    return enriquecido

def responder(historial: list, session_id: Optional[str] = None) -> str:
    """Usa el LLM solo para 'decorar' o charlar."""
    if not session_id: session_id = "temp_chat"
    try:
        h = _enriquecer_historial(historial, session_id)
        resp = ollama.chat(model=MODELO, messages=h, options={"temperature": 0.4, "num_predict": 100})
        return str(resp.message.content).strip()
    except:
        return "¡Ey bro! Qué más, ¿qué heladito te provoca?"

# ──────────────────────────────────────────────────────────
# PUNTO DE ENTRADA CENTRAL
# ──────────────────────────────────────────────────────────

def responder_vendedor_json(historial: list, verbose: bool = False, session_id: Optional[str] = None) -> str:
    """
    MOTOR CENTRAL: Backend Controlado.
    """
    if not session_id: session_id = "temp_default"
    
    # 1. Obtener último mensaje
    msg_usuario = ""
    for m in reversed(historial):
        if m.get("role") == "user":
            msg_usuario = m.get("content", "")
            break
    
    if not msg_usuario:
        return json.dumps({"accion": "saludo", "mensaje": "¡Qué onda bro! ¿Qué sabor te empaco?"})

    # 2. INTERCEPTAR CON LÓGICA DE BACKEND (DETERMINÍSTICO)
    respuesta_backend = procesar_logica_ventas(msg_usuario, session_id)
    if respuesta_backend:
        return json.dumps(respuesta_backend, ensure_ascii=False)

    # 3. OTROS ATAJOS (Catálogo, Recomendación)
    intencion = detectar_intencion(msg_usuario)
    if intencion == "catalogo":
        productos = obtener_catalogo_real()
        sabores_disponibles = [p["sabor"] for p in productos if p.get("stock", 0) > 0]
        lista_sabores = ", ".join(sabores_disponibles[:-1]) + " y " + sabores_disponibles[-1] if len(sabores_disponibles) > 1 else (sabores_disponibles[0] if sabores_disponibles else "nada por ahora")
        
        return json.dumps({
            "accion": "mostrar_productos",
            "mensaje": f"¡Claro bro! Mirá, hoy tengo helado de {lista_sabores}. Todo está bien melo. ¿Cuál te provoca?",
            "productos": productos
        }, ensure_ascii=False)

    # 4. FALLBACK AL LLM (Charla general)
    texto_ia = responder(historial, session_id)
    return json.dumps({"accion": "informacion", "mensaje": texto_ia}, ensure_ascii=False)

from .db_heladeria import registrar_venta as registrar_venta_directo

def crear_venta_api(items: list, metodo_pago: str) -> dict:
    """Llamada al backend con fallback directo a SQLite si la API falla."""
    _mapa = {"nequi": "efectivo", "daviplata": "efectivo", "efectivo": "efectivo", "tarjeta": "tarjeta"}
    pago_final = _mapa.get(metodo_pago.lower(), "efectivo")
    
    # 1. Intentar vía API
    try:
        payload = {"metodo_pago": pago_final, "items": items}
        r = requests.post(f"{API_URL}/vender", json=payload, timeout=5)
        if r.status_code in (200, 201):
            return r.json()
    except Exception as e:
        print(f"[Agente] Error API Ventas: {e}. Intentando fallback directo...")

    # 2. Fallback Directo a SQLite (Garantiza que la venta se registre)
    try:
        res_directo = registrar_venta_directo(items, pago_final)
        if res_directo.get("ok"):
            return res_directo
        return {"error": res_directo.get("error", "Error en DB")}
    except Exception as e:
        print(f"[Agente] Error Crítico en Fallback de Ventas: {e}")
        return {"error": "Conexión fallida total"}

def texto_voz_respuesta_vendedor(texto_json: str) -> str:
    """Limpia el JSON para la síntesis de voz usando el formateador robusto de la app."""
    try:
        from app.utilidades.formateadores import obtener_texto_visible
        return obtener_texto_visible(texto_json)
    except Exception as e:
        print(f"[Agente] Error importando formateador: {e}")
        try:
            import json
            data = json.loads(texto_json)
            return data.get("mensaje", texto_json)
        except:
            return texto_json
