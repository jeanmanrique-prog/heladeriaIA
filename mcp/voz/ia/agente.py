import json
import re
import requests
import ollama

from mcp.config import MODELO, API_URL
from mcp.prompts.prompt_base import SYSTEM_PROMPT, SYSTEM_PROMPT_VENDEDOR
from mcp.prompts.prompt_estado import PROMPT_ESTADO
from ..procesamiento.normalizacion import normalizar_texto_base

# catalog.py es un módulo aislado: SIN dependencia de mcp.types ni inventario_tools
# Esto evita el ImportError al iniciar la app Streamlit
from mcp.tools.catalog import get_catalog

# ─────────────────────────────────────────────
# CONSTANTES DE FILTRADO
# ─────────────────────────────────────────────

_PATRON_TECNICO = re.compile(
    r'(get_catalog|create_sale|tool_call|"accion"\s*:|"function"|"name"\s*:|'
    r'"arguments"|<tool_call>|<tool_response>)',
    re.IGNORECASE
)

# Fallback contextual — reemplaza el mensaje de "error técnico"
def _fallback_inteligente(estado: dict) -> str:
    """Genera una respuesta de fallback útil según el estado actual del pedido."""
    if estado.get("producto") and not estado.get("pago"):
        precio = estado.get("precio")
        precio_txt = f"{precio:,} pesos".replace(",", ".") if precio else "el precio del catálogo"
        return f"¿Vas con efectivo o tarjeta? 💳 Son {precio_txt}."
    if not estado.get("producto"):
        return "¿Qué sabor te provoca? 🍦"
    return "¿Me confirmas el pedido? 🙌"

# Fallback genérico (solo para errores de conexión)
_RESPUESTA_FALLBACK_CONEXION = "Uy bro, no me puedo conectar ahora. ¿Está Ollama abierto?"


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
# CATÁLOGO DE PRODUCTOS — usa get_catalog() con fallback SQLite
# ─────────────────────────────────────────────

def cargar_catalogo_productos() -> list:
    """
    Carga el catálogo real.
    Prioridad: API REST → SQLite directo (via get_catalog).
    NUNCA retorna lista vacía si hay datos en la BD.
    """
    return get_catalog()


def _construir_catalogo_texto(catalogo: list) -> str:
    """Formatea el catálogo en texto claro para inyectar al prompt.
    Garantiza que precio y stock nunca sean None."""
    if not catalogo:
        return "⚠️ No hay productos disponibles en este momento."
    lineas = []
    for p in catalogo:
        # Normalizar campos — nunca None
        nombre = str(p.get('nombre_producto') or p.get('nombre') or 'Producto sin nombre')
        sabor = str(p.get('sabor') or '?')
        precio_raw = p.get('precio_unitario') or p.get('precio') or 0
        try:
            precio = float(precio_raw)
        except (TypeError, ValueError):
            precio = 0.0
        stock_raw = p.get('stock') or p.get('cantidad_unidades') or 0
        try:
            stock = int(stock_raw)
        except (TypeError, ValueError):
            stock = 0
        stock_txt = f"{stock} uds" if stock > 0 else "AGOTADO"
        id_prod = p.get('id_producto', '?')
        lineas.append(
            f"• {nombre} | Sabor: {sabor} | "
            f"Precio: {precio:,.0f} pesos COP | Stock: {stock_txt} | ID: {id_prod}"
        )
    return "\n".join(lineas)


# ─────────────────────────────────────────────
# FILTRO DE RESPUESTA — BLOQUEA CONTENIDO TÉCNICO
# ─────────────────────────────────────────────

def _limpiar_respuesta(texto: str) -> str:
    """Devuelve fallback si la respuesta contiene leaks técnicos."""
    if not texto or not texto.strip():
        return _RESPUESTA_FALLBACK
    if _PATRON_TECNICO.search(texto):
        return _RESPUESTA_FALLBACK
    # Quitar bloques de código
    limpio = re.sub(r'```[\w]*\n?', '', texto)
    limpio = re.sub(r'```', '', limpio)
    limpio = limpio.strip()
    return limpio if limpio else _RESPUESTA_FALLBACK


# ─────────────────────────────────────────────
# FORMATEO DE TEXTO PARA VOZ / DISPLAY
# ─────────────────────────────────────────────

def _corregir_mojibake(texto: str) -> str:
    if not texto:
        return ""
    try:
        return texto.encode('latin1').decode('utf-8')
    except Exception:
        return texto


def _relajar_texto_urbano(texto: str) -> str:
    t = _corregir_mojibake(texto or "").strip()
    if not t:
        return t
    reemplazos = {
        "Con que metodo de pago deseas pagar? (efectivo o tarjeta)": "¿Vas con efectivo o tarjeta, bro?",
        "Venta realizada con exito.": "¡Listo bro, pedido confirmado!",
        "No pude procesar la respuesta.": "Uy bro, ahí se enredó la respuesta.",
    }
    for origen, destino in reemplazos.items():
        t = t.replace(origen, destino)
    t = re.sub(r"(?i)\b(brother|mano|parcero)\b", "bro", t)
    return t


def texto_voz_respuesta_vendedor(texto: str) -> str:
    """Convierte cualquier respuesta (JSON o texto) en frase natural para voz/display."""
    # Si el texto parece JSON, intentar extraer el campo mensaje
    if texto and texto.strip().startswith("{"):
        try:
            data = json.loads(texto)
            if isinstance(data, dict):
                mensaje = str(data.get("mensaje", "")).strip()
                if mensaje:
                    return _relajar_texto_urbano(mensaje)
        except Exception:
            pass
    # Si no es JSON o no tiene mensaje, devolver el texto limpio
    limpio = _limpiar_respuesta(texto)
    return _relajar_texto_urbano(limpio)


# ─────────────────────────────────────────────
# CREAR VENTA (Llamada directa a la API — sin tool del LLM)
# ─────────────────────────────────────────────

def crear_venta_api(items: list, metodo_pago: str) -> dict:
    """Llama a la API REST para crear la venta. Devuelve el resultado o error."""
    try:
        payload = {"items": items, "metodo_pago": metodo_pago}
        r = requests.post(f"{API_URL}/ventas", json=payload, timeout=6)
        return r.json()
    except Exception as e:
        return {"error": str(e)}


# ─────────────────────────────────────────────
# DETECTOR DE ESTADO DE PEDIDO — MEMORIA EXPLÍCITA
# ─────────────────────────────────────────────

_SABORES = ["fresa", "chocolate", "vainilla", "mango", "limon", "limón"]
_METODOS_PAGO = ["efectivo", "tarjeta", "nequi", "daviplata"]
_CONFIRMACIONES = ["si", "sí", "dale", "ok", "listo", "de una", "hágale", "hagale", "claro", "perfecto", "bueno"]

def _extraer_estado_pedido(historial: list, catalogo: list) -> dict:
    """
    Recorre el historial para detectar el último producto, método de pago
    y si el usuario confirmó el pedido.
    Esto se inyecta en el system prompt para que el LLM nunca pierda contexto.
    """
    estado = {"producto": None, "precio": None, "pago": None, "confirmado": False}

    # Construir mapa sabor → precio desde catálogo real
    precio_por_sabor = {}
    for p in catalogo:
        sabor = str(p.get("sabor") or "").lower().strip()
        precio_raw = p.get("precio_unitario") or p.get("precio") or 0
        try:
            precio_por_sabor[sabor] = int(float(precio_raw))
        except (TypeError, ValueError):
            precio_por_sabor[sabor] = 0

    # Recorrer solo mensajes del usuario (role=user)
    for msg in historial:
        if msg.get("role") != "user":
            continue
        texto = str(msg.get("content", "")).lower().strip()

        # Detectar producto / sabor
        for sabor in _SABORES:
            if sabor in texto:
                estado["producto"] = sabor
                estado["precio"] = precio_por_sabor.get(sabor)
                # Si cambia de sabor, resetear pago y confirmación
                estado["pago"] = None
                estado["confirmado"] = False
                break

        # Detectar método de pago
        for metodo in _METODOS_PAGO:
            if metodo in texto:
                estado["pago"] = metodo
                break

        # Detectar confirmaciones simples ("sí", "dale", "ok"...)
        # Solo si el mensaje es corto (≤ 4 palabras) — evita falsos positivos
        palabras = texto.split()
        if len(palabras) <= 4:
            for confirmacion in _CONFIRMACIONES:
                if confirmacion in palabras or texto == confirmacion:
                    estado["confirmado"] = True
                    break

    return estado


# ─────────────────────────────────────────────
# MOTOR DEL AGENTE — SIN TOOLS (catálogo + estado inyectados)
# ─────────────────────────────────────────────

def _enriquecer_historial(historial: list) -> list:
    """
    Inyecta en el system prompt:
    1. El PROMPT_ESTADO (reglas de memoria)
    2. El catálogo REAL de productos
    3. El estado actual del pedido (producto + pago detectados en el historial)
    Esto garantiza que el LLM NUNCA pierda contexto entre turnos.
    """
    catalogo = cargar_catalogo_productos()

    if not catalogo:
        regla = (
            "\n\n⚠️ CATÁLOGO NO DISPONIBLE. "
            "Di al cliente: 'Uy bro, en este momento no me carga el menú, dame un segundo.' "
            "NO inventes precios ni productos."
        )
        enriquecido = []
        for m in historial:
            if m.get('role') == 'system':
                enriquecido.append({'role': 'system', 'content': m['content'] + regla})
            else:
                enriquecido.append(m)
        return enriquecido

    # Catálogo formateado
    catalogo_txt = _construir_catalogo_texto(catalogo)
    bloque_catalogo = (
        f"\n\n═══ CATÁLOGO ACTUAL (DATOS REALES DE LA BD) ═══\n"
        f"{catalogo_txt}\n"
        f"═══════════════════════════════════════════════\n"
        f"REGLA CRÍTICA: USA SOLO ESTOS PRECIOS Y STOCKS. "
        f"NUNCA inventes precios, nombres ni disponibilidad."
    )

    # Estado actual del pedido extraído del historial
    estado = _extraer_estado_pedido(historial, catalogo)
    producto    = estado["producto"]
    precio      = estado["precio"]
    pago        = estado["pago"]
    confirmado  = estado["confirmado"]

    precio_txt = f"{precio:,} pesos".replace(",", ".") if precio else "(ver catálogo)"

    if producto and pago:
        # ─ CASO 3: Pedido COMPLETO — producto + pago confirmados
        bloque_estado = (
            f"\n\n═══ ESTADO DEL PEDIDO: COMPLETO ═══\n"
            f"producto: {producto}\n"
            f"precio:   {precio_txt}\n"
            f"pago:     {pago}\n"
            f"════════════════════════════════════\n"
            f"✅ TODO LISTO. RESPONDE SOLO:\n"
            f"'Listo, ya te lo tengo 🎉'\n"
            f"NO hagas más preguntas."
        )
    elif producto and confirmado and not pago:
        # ─ CASO 2b: Cliente confirmó ("sí", "dale"...) pero no ha dicho cómo paga
        bloque_estado = (
            f"\n\n═══ ESTADO DEL PEDIDO: CONFIRMADO, PENDIENTE PAGO ═══\n"
            f"producto:   {producto}\n"
            f"precio:     {precio_txt}\n"
            f"confirmado: SÍ\n"
            f"pago:       (AÚN NO INDICADO)\n"
            f"═══════════════════════════════════════════════════════\n"
            f"⚠️ El cliente YA confirmó el pedido.\n"
            f"SIGUIENTE PASO: preguntar SOLO el método de pago.\n"
            f"Ejemplo: 'De una 🍦 Son {precio_txt}. ¿Pagas con efectivo o tarjeta?'"
        )
    elif producto and not pago:
        # ─ CASO 2: Tiene producto, sin confirmar ni pagar
        bloque_estado = (
            f"\n\n═══ ESTADO DEL PEDIDO: PENDIENTE PAGO ═══\n"
            f"producto: {producto}\n"
            f"precio:   {precio_txt}\n"
            f"pago:     (AÚN NO INDICADO)\n"
            f"══════════════════════════════════════════\n"
            f"⚠️ SIGUIENTE PASO OBLIGATORIO:\n"
            f"Confirma precio y pregunta método de pago.\n"
            f"Ejemplo: 'Listo, te dejo el de {producto} 🍦 Son {precio_txt}. ¿Pagas con efectivo o tarjeta?'\n"
            f"❌ NO digas 'Listo ya te lo tengo' hasta que el cliente diga cómo paga."
        )
    else:
        # ─ CASO 1: Sin estado — primera interacción
        bloque_estado = ""

    # Combinar: reglas de estado + catálogo + estado actual
    extra = PROMPT_ESTADO + bloque_catalogo + bloque_estado

    enriquecido = []
    for m in historial:
        if m.get('role') == 'system':
            enriquecido.append({'role': 'system', 'content': m['content'] + extra})
        else:
            enriquecido.append(m)
    return enriquecido


def responder(historial: list, verbose: bool = False) -> str:
    """
    Responde al cliente con lógica determinística primero (cortocircuito),
    luego llama a Ollama solo cuando el estado es ambiguo.
    Esto compensa las limitaciones del modelo pequeño (1B).
    """
    # ── Lógica determinística ANTES del LLM ──────────────────────────────────
    # Precargamos catálogo y estado para cortocircuitar el modelo cuando sea
    # posible y evitar alucinaciones del modelo pequeño.
    try:
        catalogo = cargar_catalogo_productos()
        estado = _extraer_estado_pedido(historial, catalogo)
        producto   = estado["producto"]
        precio     = estado["precio"]
        pago       = estado["pago"]
        confirmado = estado["confirmado"]
        precio_txt = f"{precio:,} pesos".replace(",", ".") if precio else "el precio del catálogo"

        # CASO COMPLETO → respuesta directa sin LLM
        if producto and pago:
            return f"Listo bro, ya te lo tengo 🎉"

        # CASO CONFIRMACIÓN + PRODUCTO → preguntar pago directamente
        if producto and confirmado and not pago:
            return f"De una 🍦 Son {precio_txt}. ¿Pagas con efectivo o tarjeta?"

    except Exception as e:
        if verbose:
            print(f"[agente] Error en pre-procesado: {e}")
        estado = {}  # fallback seguro
        catalogo = []

    # ── Llamada al LLM (casos ambiguos o primera interacción) ─────────────────
    try:
        historial_enriquecido = _enriquecer_historial(historial)

        response = ollama.chat(
            model=MODELO,
            messages=historial_enriquecido,
            options={
                "num_predict": 200,
                "temperature": 0.6,
                "top_p": 0.85,
                "repeat_penalty": 1.15,
            }
        )

        contenido = response.message.content or ""
        resultado = _limpiar_respuesta(contenido)

        # Si el LLM aún devuelve algo técnico, usar fallback contextual
        if resultado == _RESPUESTA_FALLBACK_CONEXION or not resultado.strip():
            return _fallback_inteligente(estado)

        return resultado

    except Exception as e:
        err = str(e).lower()
        if verbose:
            print(f"[agente] Error en Ollama: {e}")
        if "connect" in err or "refused" in err:
            return _RESPUESTA_FALLBACK_CONEXION
        # Fallback contextual en lugar del mensaje de error técnico
        return _fallback_inteligente(estado)


# ─────────────────────────────────────────────
# RESPONDER VENDEDOR JSON
# Compatible con ia_gui.py que espera JSON válido para renderizar la UI
# ─────────────────────────────────────────────

def responder_vendedor_json(historial: list, verbose: bool = False) -> str:
    """
    Obtiene respuesta del LLM como texto natural.
    La envuelve en JSON compatible con la UI (accion + mensaje).
    NUNCA devuelve tools ni JSON crudo del LLM.
    """
    texto = responder(historial, verbose=verbose)
    texto_limpio = _relajar_texto_urbano(texto)

    return json.dumps({
        "accion": "informacion",
        "mensaje": texto_limpio
    }, ensure_ascii=False)
