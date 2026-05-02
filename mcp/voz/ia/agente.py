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
        (r"quieto|qiero|kiero|quisira|quisera|quera", "quiero"),
        (r"elado|helao|elao|lado", "helado"),
        (r"efecto|perfecto|festivo|efectiva", "efectivo"),
        (r"targeta|tarjera|targueta", "tarjeta"),
        (r"comienda|remienda|recomiendo", "recomienda"),
        (r"choclate|choclati|colate|olate", "chocolate"),
        (r"presa|fresa", "fresa"),
        (r"vainilla|vainia|vainilla", "vainilla"),
        (r"brownie|broni|brauni", "brownie")
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

    # 1. DETECTAR PRODUCTO (Avanza a esperando_pago)
    for sabor, datos in cmap.items():
        if sabor in t and len(sabor) > 3:
            estado.update({
                "producto": sabor,
                "precio": datos["precio"],
                "pago": None,
                "paso": "esperando_pago"
            })
            GestorEstado.actualizar_estado(session_id, estado)
            precio_fmt = f"{datos['precio']:,}".replace(",", ".")
            return {
                "accion": "pedir_pago",
                "mensaje": f"Listo, un helado de {sabor.capitalize()} 🍦. Son {precio_fmt} pesos. ¿Pagas con efectivo o tarjeta?",
                "total": datos["precio"],
                "items": [{"id_producto": datos["id"], "sabor": sabor, "cantidad": 1}]
            }

    # 2. DETECTAR PAGO (Avanza a completado y cierra venta)
    if estado.get("paso") == "esperando_pago" and estado.get("producto"):
        pago_detectado = next((m for m in _METODOS_PAGO if m in t), None)
        if pago_detectado:
            producto_sabor = estado["producto"]
            producto_id = cmap.get(producto_sabor, {}).get("id")
            
            # EJECUTAR VENTA REAL EN BACKEND
            if producto_id:
                crear_venta_api([{"id_producto": producto_id, "cantidad": 1}], pago_detectado)
            
            GestorEstado.limpiar_estado(session_id)
            return {
                "accion": "venta_exitosa",
                "mensaje": "¡Listo bro, ya te lo tengo! 🎉 Disfruta tu helado.",
                "detalle": {"producto": producto_sabor, "pago": pago_detectado}
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
        return json.dumps({
            "accion": "mostrar_productos",
            "mensaje": "Mirá lo que tengo hoy, todo melo:",
            "productos": obtener_catalogo_real()
        }, ensure_ascii=False)

    # 4. FALLBACK AL LLM (Charla general)
    texto_ia = responder(historial, session_id)
    return json.dumps({"accion": "informacion", "mensaje": texto_ia}, ensure_ascii=False)

def crear_venta_api(items: list, metodo_pago: str) -> dict:
    """Llamada directa al backend con normalización de método de pago."""
    _mapa = {"nequi": "efectivo", "daviplata": "efectivo", "efectivo": "efectivo", "tarjeta": "tarjeta"}
    pago_final = _mapa.get(metodo_pago.lower(), "efectivo")
    try:
        payload = {"metodo_pago": pago_final, "items": items}
        r = requests.post(f"{API_URL}/vender", json=payload, timeout=5)
        return r.json()
    except:
        return {"error": "Conexión fallida"}

def texto_voz_respuesta_vendedor(texto_json: str) -> str:
    """Limpia el JSON para la síntesis de voz."""
    try:
        data = json.loads(texto_json)
        return data.get("mensaje", "")
    except:
        return texto_json
