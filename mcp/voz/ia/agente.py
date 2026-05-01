import json
import re
import requests
import ollama
from typing import Optional, Dict, List, Any

from mcp.config import MODELO, API_URL
from mcp.prompts.prompt_base import SYSTEM_PROMPT
from mcp.prompts.prompt_ventas import PROMPT_VENDEDOR as SYSTEM_PROMPT_VENDEDOR
from mcp.prompts.prompt_estado import PROMPT_ESTADO
from mcp.prompts.prompt_pagos import PROMPT_PAGOS
from mcp.prompts.prompt_sugerencias import PROMPT_SUGERENCIAS

from ..procesamiento.normalizacion import normalizar_texto_base

# Recursos (Resources) - Capa de datos de solo lectura
from mcp.resources.catalog_resource import CatalogResource
from mcp.resources.contexto_resource import ContextoResource

# Herramientas (Tools) - Capa de acciones reales
from mcp.tools.catalog_tools import obtener_catalogo_real
from api.ia.estado import GestorEstado
from .intencion import detectar_intencion

# ─────────────────────────────────────────────
# CONSTANTES DE FILTRADO
# ─────────────────────────────────────────────

_PATRON_TECNICO = re.compile(
    r'(get_catalog|create_sale|tool_call|"accion"\s*:|"function"|"name"\s*:|'
    r'"arguments"|<tool_call>|<tool_response>)',
    re.IGNORECASE
)

# ─────────────────────────────────────────────
# NORMALIZACIÓN
# ─────────────────────────────────────────────

PALABRAS_CANTIDAD = {
    "un": 1, "una": 1, "uno": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5,
    "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10
}

PALABRAS_GENERICAS_PRODUCTO = {
    "de", "del", "la", "el", "los", "las", "por", "favor", "quiero", "me",
    "das", "dame", "para", "pagar", "pago", "con", "helado", "helados",
    "tarro", "tarros", "litro", "litros", "uno", "una", "un", "dos",
    "pedir", "pedido", "quisiera", "solicito", "hola", "hey", "id", "producto"
}

import unicodedata

def normalizar_texto_usuario_voz(texto: str) -> str:
    """Normalización robusta de texto de voz/chat."""
    if not texto: return ""
    texto = texto.strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    reemplazos = [
        (r"\bquieto\b", "quiero"), (r"\bqiero\b", "quiero"), (r"\bkiero\b", "quiero"),
        (r"\belado\b", "helado"), (r"\be lado\b", "helado"), (r"\bhelao\b", "helado"),
        (r"\bpresa\b", "fresa")
    ]
    for patron, reemplazo in reemplazos:
        texto = re.sub(patron, reemplazo, texto)
    return re.sub(r"\s+", " ", texto).strip()

# ─────────────────────────────────────────────
# ELIMINADAS FUNCIONES REDUNDANTES (Se usa intencion.py)
# ─────────────────────────────────────────────

_RESPUESTA_FALLBACK_CONEXION = "Uy bro, no me puedo conectar ahora. ¿Está Ollama abierto?"
_RESPUESTA_FALLBACK = "Uy, ahí se enredó la cosa. ¿Me repites?"

# ─────────────────────────────────────────────
# VERIFICACIÓN DE OLLAMA
# ─────────────────────────────────────────────

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

# ─────────────────────────────────────────────
# CATÁLOGO (para compatibilidad interna)
# ─────────────────────────────────────────────

def cargar_catalogo_productos() -> list:
    return obtener_catalogo_real()

def _construir_catalogo_texto(catalogo: list) -> str:
    if not catalogo:
        return "⚠️ No hay productos disponibles en este momento."
    lineas = []
    for p in catalogo:
        nombre = str(p.get('nombre_producto') or p.get('nombre') or 'Producto sin nombre')
        sabor = str(p.get('sabor') or '?')
        try:
            precio = float(p.get('precio_unitario') or p.get('precio') or 0)
        except:
            precio = 0.0
        try:
            stock = int(p.get('stock') or p.get('cantidad_unidades') or 0)
        except:
            stock = 0
        stock_txt = f"{stock} uds" if stock > 0 else "AGOTADO"
        id_prod = p.get('id_producto', '?')
        lineas.append(
            f"• {nombre} | Sabor: {sabor} | "
            f"Precio: {precio:,.0f} pesos COP | Stock: {stock_txt} | ID: {id_prod}"
        )
    return "\n".join(lineas)

# ─────────────────────────────────────────────
# FILTRO DE RESPUESTA
# ─────────────────────────────────────────────

def _limpiar_respuesta(texto: str) -> str:
    if not texto or not texto.strip():
        return _RESPUESTA_FALLBACK
    if _PATRON_TECNICO.search(texto):
        return _RESPUESTA_FALLBACK
    limpio = re.sub(r'```[\w]*\n?', '', texto)
    limpio = re.sub(r'```', '', limpio).strip()
    return limpio if limpio else _RESPUESTA_FALLBACK

# ─────────────────────────────────────────────
# FORMATEO DE TEXTO
# ─────────────────────────────────────────────

def _corregir_mojibake(texto: str) -> str:
    if not texto: return ""
    try:
        return texto.encode('latin1').decode('utf-8')
    except:
        return texto

def _relajar_texto_urbano(texto: str) -> str:
    t = _corregir_mojibake(texto or "").strip()
    if not t: return t
    reemplazos = {
        "Con que metodo de pago deseas pagar? (efectivo o tarjeta)": "¿Vas con efectivo o tarjeta, bro?",
        "Venta realizada con exito.": "¡Listo, ya te lo tengo 🎉",
        "No pude procesar la respuesta.": "Uy, ahí se enredó la respuesta.",
    }
    for origen, destino in reemplazos.items():
        t = t.replace(origen, destino)
    t = re.sub(r"(?i)\b(brother|mano|parcero)\b", "bro", t)
    return t

def texto_voz_respuesta_vendedor(texto: str) -> str:
    """Convierte la respuesta JSON del vendedor en una frase natural para voz."""
    try:
        data = json.loads(texto)
    except:
        return _relajar_texto_urbano(texto)

    accion = data.get("accion")
    mensaje = str(data.get("mensaje", "")).strip()

    if accion in {"saludo", "sin_stock", "confirmar_pago", "informacion"}:
        return _relajar_texto_urbano(mensaje or "No pude procesar la respuesta.")

    if accion == "mostrar_productos":
        productos = data.get("productos", [])
        if not productos:
            return "En este momento no tengo helados disponibles."
        resumen = [p.get("sabor") or p.get("nombre") or "helado" for p in productos[:3]]
        return f"{mensaje} Tengo " + ", ".join(resumen) + " y otros más."

    if accion in {"pedir_pago", "crear_venta"}:
        # El campo 'mensaje' ya contiene el texto completo con precio y pregunta de pago
        # Devolvemos directamente sin duplicar items ni total
        return _relajar_texto_urbano(mensaje) if mensaje else "\u00bfPagas con efectivo o tarjeta?"

    if accion == "venta_exitosa":
        return _relajar_texto_urbano(mensaje)

    return _relajar_texto_urbano(mensaje or texto)


# ─────────────────────────────────────────────
# CREAR VENTA — TOOL REAL (llama a la API)
# ─────────────────────────────────────────────

def crear_venta_api(items: list, metodo_pago: str) -> dict:
    """Llama al endpoint /vender de la API REST. Retorna resultado o error."""
    # Normalizar método de pago: el endpoint solo acepta 'efectivo' o 'tarjeta'
    _mapa_pago = {
        "nequi": "efectivo",
        "daviplata": "efectivo",
        "efectivo": "efectivo",
        "tarjeta": "tarjeta",
    }
    metodo_normalizado = _mapa_pago.get(metodo_pago.lower(), "efectivo")
    try:
        payload = {"metodo_pago": metodo_normalizado, "items": items}
        r = requests.post(f"{API_URL}/vender", json=payload, timeout=6)
        return r.json()
    except Exception as e:
        return {"error": str(e)}


# ─────────────────────────────────────────────
# MÁQUINA DE ESTADOS — MEMORIA DE LA CONVERSACIÓN
# Flujo: inicio → esperando_pago → completado
# ─────────────────────────────────────────────

_METODOS_PAGO   = ["efectivo", "tarjeta", "nequi", "daviplata"]
_CONFIRMACIONES = ["si", "sí", "dale", "ok", "listo", "de una", "hágale", "hagale", "claro", "perfecto", "bueno"]


def _extraer_sabor_de_mensaje_asistente(historial: list, catalogo_map: dict) -> Optional[str]:
    """
    Busca el sabor mencionado por el ASISTENTE en el historial.
    Prioriza el ÚLTIMO sabor mencionado en el último mensaje para evitar ambigüedades.
    """
    for m in reversed(historial):
        if m.get("role") in ("assistant", "model"):
            texto_asistente = normalizar_texto_usuario_voz(m.get("content", ""))
            # Encontrar todas las ocurrencias de sabores y su posición
            encontrados = []
            for sabor in catalogo_map:
                if len(sabor) > 3:
                    pos = texto_asistente.rfind(sabor) # Buscar la última ocurrencia
                    if pos != -1:
                        encontrados.append((pos, sabor))
            
            if encontrados:
                # Retornar el sabor que aparece más al final del texto
                encontrados.sort(key=lambda x: x[0], reverse=True)
                return encontrados[0][1]
    return None


def _extraer_estado_pedido(historial: list, catalogo: list, session_id: Optional[str] = None) -> dict:
    """
    Máquina de estados estricta: inicio → esperando_pago → completado.
    El estado persistente (GestorEstado) es la fuente de verdad.
    Solo el ÚLTIMO mensaje del usuario puede avanzar el estado — nunca retrocede.
    """
    # 1. Fuente de verdad: estado guardado en la sesión
    estado = {"producto": None, "precio": None, "pago": None, "confirmado": False, "paso": "inicio"}
    if session_id:
        estado = GestorEstado.obtener_estado(session_id)

    # Mapa sabor → {id, precio, stock} para búsqueda O(1)
    catalogo_map = {}
    for p in catalogo:
        sabor_norm = normalizar_texto_usuario_voz(str(p.get("sabor") or ""))
        if sabor_norm:
            catalogo_map[sabor_norm] = {
                "id":     p.get("id_producto"),
                "precio": int(float(p.get("precio_unitario") or p.get("precio") or 0)),
                "stock":  int(p.get("stock") or p.get("cantidad_unidades") or 0)
            }

    # 2. Analizar el ÚLTIMO mensaje del usuario
    msg_usuario = ""
    for m in reversed(historial):
        if m.get("role") == "user":
            msg_usuario = normalizar_texto_usuario_voz(m.get("content", ""))
            break

    if msg_usuario:
        paso_actual = estado.get("paso", "inicio")

        # PASO INICIO / COMPLETADO → buscar nuevo sabor en el mensaje del usuario
        if paso_actual in ("inicio", "completado"):
            sabor_encontrado = None
            for sabor, datos in catalogo_map.items():
                if sabor in msg_usuario and len(sabor) > 3:
                    sabor_encontrado = sabor
                    estado["producto"]   = sabor
                    estado["precio"]     = datos["precio"]
                    estado["pago"]       = None
                    estado["confirmado"] = False
                    estado["paso"]       = "esperando_pago"
                    break

            # 🆕 FIX: Si el usuario confirmó ("si", "dale", "ok") sin mencionar sabor
            # → buscar el sabor recomendado en el último mensaje del ASISTENTE
            if not sabor_encontrado:
                es_confirmacion = any(conf == msg_usuario or conf in msg_usuario.split()
                                      for conf in _CONFIRMACIONES)
                if es_confirmacion:
                    sabor_asistente = _extraer_sabor_de_mensaje_asistente(historial, catalogo_map)
                    if sabor_asistente and sabor_asistente in catalogo_map:
                        datos = catalogo_map[sabor_asistente]
                        estado["producto"]   = sabor_asistente
                        estado["precio"]     = datos["precio"]
                        estado["pago"]       = None
                        estado["confirmado"] = False
                        estado["paso"]       = "esperando_pago"

        # PASO ESPERANDO_PAGO → buscar método de pago SOLAMENTE
        elif paso_actual == "esperando_pago":
            pago_encontrado = False
            for metodo in _METODOS_PAGO:
                if metodo in msg_usuario:
                    estado["pago"]  = metodo
                    estado["paso"]  = "completado"
                    pago_encontrado = True
                    break
            # Si dijo "sí"/"dale" sin especificar método → marcar confirmado para el prompt
            if not pago_encontrado:
                for conf in _CONFIRMACIONES:
                    if conf in msg_usuario:
                        estado["confirmado"] = True
                        break

    # 3. Persistir estado actualizado
    if session_id:
        GestorEstado.actualizar_estado(session_id, estado)

    return estado


# ─────────────────────────────────────────────
# ENRIQUECIMIENTO DE HISTORIAL (inyecta resources + prompts)
# ─────────────────────────────────────────────

def _enriquecer_historial(historial: list, session_id: Optional[str] = None) -> list:
    """
    ARQUITECTURA MCP: Inyecta RESOURCES y PROMPTS en el contexto del modelo.
    """
    # 1. Resources (datos reales de solo lectura)
    catalogo_txt = CatalogResource.get_catalog_text()
    contexto_txt = ContextoResource.get_context_text(session_id) if session_id else ""

    # 2. Prompts (cerebro conversacional completo)
    prompts_ia = (
        SYSTEM_PROMPT + "\n" + 
        SYSTEM_PROMPT_VENDEDOR + "\n" + 
        PROMPT_ESTADO + "\n" + 
        PROMPT_PAGOS + "\n" + 
        PROMPT_SUGERENCIAS
    )

    # 3. Bloque de contexto completo
    extra = f"\n\n{prompts_ia}\n\n{catalogo_txt}\n\n{contexto_txt}"

    enriquecido = []
    for m in historial:
        if m.get('role') == 'system':
            enriquecido.append({'role': 'system', 'content': m['content'] + extra})
        else:
            enriquecido.append(m)
    return enriquecido


def responder(historial: list, verbose: bool = False, session_id: Optional[str] = None) -> str:
    """Genera respuesta en texto natural usando el estado de sesión."""
    try:
        historial_enriquecido = _enriquecer_historial(historial, session_id=session_id)
        response = ollama.chat(
            model=MODELO,
            messages=historial_enriquecido,
            options={"num_predict": 200, "temperature": 0.6}
        )
        contenido = response.message.content or ""
        return _limpiar_respuesta(contenido)
    except Exception as e:
        if verbose: print(f"[agente] Error: {e}")
        return _RESPUESTA_FALLBACK_CONEXION


# ─────────────────────────────────────────────
# MOTOR PRINCIPAL — MÁQUINA DE ESTADOS JSON
# ─────────────────────────────────────────────

def responder_vendedor_json(historial: list, verbose: bool = False, session_id: Optional[str] = None) -> str:
    """
    Motor DETERMINÍSTICO basado en MÁQUINA DE ESTADOS estricta.
    Flujo: inicio → esperando_pago → completado
    Cada paso produce UN SOLO tipo de respuesta — nunca se mezclan.
    """
    catalogo = obtener_catalogo_real()

    # Último mensaje del usuario
    msg_usuario = ""
    for m in reversed(historial):
        if m.get("role") == "user":
            msg_usuario = normalizar_texto_usuario_voz(m.get("content", ""))
            break

    # ── CORTOCIRCUITOS INMEDIATOS ──────────────────────────────────────────────
    if not msg_usuario:
        return json.dumps({"accion": "saludo", "mensaje": "¡Hola! ¿Qué helado te provoca hoy? 🍦"})

    # Usar el motor centralizado de intenciones
    intencion = detectar_intencion(msg_usuario)

    if intencion == "saludo":
        return json.dumps({"accion": "saludo", "mensaje": "Bienvenido a Gelateria Urbana, bro. ¿Qué sabor te empaco hoy? 😎"})

    if intencion == "catalogo":
        productos = [
            {"id_producto": p.get("id_producto"), "sabor": p.get("sabor"), "precio": p.get("precio_unitario")}
            for p in catalogo if int(p.get("stock") or 0) > 0
        ]
        return json.dumps({
            "accion": "mostrar_productos",
            "mensaje": "Aquí tienes lo que tengo disponible ahora:",
            "productos": productos
        }, ensure_ascii=False)

    if intencion == "recomendacion":
        # Lógica de variedad: no recomendar lo mismo que ya se recomendó
        sabores_vistos = set()
        for m in historial:
            if m.get("role") in ("assistant", "model"):
                t_low = m.get("content", "").lower()
                for p in catalogo:
                    s_low = str(p.get("sabor", "")).lower()
                    if s_low and s_low in t_low:
                        sabores_vistos.add(s_low)
        
        # Prioridad: Chocolate -> Fresa -> Otros
        prioridad = ["chocolate", "fresa"]
        seleccionado = None
        
        # 1. Intentar con prioridad que no se haya visto
        for p_sabor in prioridad:
            if p_sabor not in sabores_vistos:
                for p in catalogo:
                    if str(p.get("sabor", "")).lower() == p_sabor and int(p.get("stock") or 0) > 0:
                        seleccionado = p.get("sabor")
                        break
            if seleccionado: break
            
        # 2. Si no, cualquier otro con stock que no se haya visto
        if not seleccionado:
            for p in catalogo:
                s_cand = str(p.get("sabor", "")).lower()
                if int(p.get("stock") or 0) > 0 and s_cand not in sabores_vistos:
                    seleccionado = p.get("sabor")
                    break
                    
        # 3. Si ya se recomendaron todos, repetir el primero de prioridad que tenga stock
        if not seleccionado:
            for p_sabor in prioridad:
                for p in catalogo:
                    if str(p.get("sabor", "")).lower() == p_sabor and int(p.get("stock") or 0) > 0:
                        seleccionado = p.get("sabor")
                        break
                if seleccionado: break

        if seleccionado:
            return json.dumps({
                "accion": "informacion",
                "mensaje": f"¡Te recomiendo el de {seleccionado}! Es el que más están llevando hoy. ¿Te va bien? 🍦"
            }, ensure_ascii=False)

    # ── ESTADO PERSISTENTE (fuente de verdad) ─────────────────────────────────
    estado = _extraer_estado_pedido(historial, catalogo, session_id=session_id)
    paso           = estado.get("paso", "inicio")
    producto_sabor = estado.get("producto")
    pago           = estado.get("pago")

    # Datos reales del catálogo para el sabor guardado
    producto_id = None
    precio_real = 0
    stock_real  = 0
    if producto_sabor:
        for p in catalogo:
            if normalizar_texto_usuario_voz(str(p.get("sabor", ""))) == producto_sabor:
                producto_id = p.get("id_producto")
                precio_real = int(float(p.get("precio_unitario") or p.get("precio") or 0))
                stock_real  = int(p.get("stock") or p.get("cantidad_unidades") or 0)
                break

    precio_txt = f"{precio_real:,.0f}".replace(",", ".") + " pesos" if precio_real else ""

    # ── MÁQUINA DE ESTADOS — cada caso es EXCLUSIVO ───────────────────────────

    # CASO 1: COMPLETADO → producto + pago listos → EJECUTAR VENTA → confirmar
    if paso == "completado" and producto_id and pago:
        crear_venta_api([{"id_producto": producto_id, "cantidad": 1}], pago)
        if session_id:
            GestorEstado.limpiar_estado(session_id)
        return json.dumps({
            "accion": "venta_exitosa",
            "mensaje": "Listo, ya te lo tengo 🎉",
            "detalle": {"producto": producto_sabor, "pago": pago, "total": precio_real}
        }, ensure_ascii=False)

    # CASO 2: ESPERANDO_PAGO → tenemos producto, falta pago
    if paso == "esperando_pago" and producto_id:
        # Sin stock: sugerir alternativa y resetear
        if stock_real == 0:
            alternativa = next(
                (p.get("sabor") for p in catalogo
                 if int(p.get("stock") or 0) > 0 and
                 normalizar_texto_usuario_voz(str(p.get("sabor", ""))) != producto_sabor),
                None
            )
            alt_txt = f" Te recomiendo el de {alternativa} 🍦" if alternativa else ""
            if session_id:
                GestorEstado.limpiar_estado(session_id)
            return json.dumps({
                "accion": "sin_stock",
                "mensaje": f"Uy, el de {producto_sabor} está agotado 😔 ¿Quieres otro?{alt_txt}"
            }, ensure_ascii=False)

        # Con stock: pedir método de pago (UN SOLO mensaje, sin confirmar todavía)
        return json.dumps({
            "accion": "pedir_pago",
            "mensaje": f"Listo, te dejo el de {producto_sabor} 🍦 Son {precio_txt}. ¿Pagas con efectivo o tarjeta?",
            "items": [{"id_producto": producto_id, "producto": producto_sabor, "cantidad": 1}],
            "total": precio_real
        }, ensure_ascii=False)

    # ── FALLBACK AL LLM — solo para charla general ────────────────────────────
    texto_llm = responder(historial, verbose=verbose, session_id=session_id)

    # Blindaje: si el LLM genera JSON, extraer solo el mensaje
    if "{" in texto_llm and "}" in texto_llm:
        try:
            temp = json.loads(re.search(r'\{.*\}', texto_llm, re.DOTALL).group())
            texto_llm = temp.get("mensaje") or temp.get("content") or texto_llm
        except:
            texto_llm = re.sub(r'\{.*\}', '', texto_llm).strip()

    return json.dumps({
        "accion": "informacion",
        "mensaje": _relajar_texto_urbano(texto_llm)
    }, ensure_ascii=False)
