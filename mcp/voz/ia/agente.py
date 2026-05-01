import json
import re
import requests
import ollama

from mcp.config import MODELO, API_URL
from mcp.prompts.prompt_base import SYSTEM_PROMPT, SYSTEM_PROMPT_VENDEDOR
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

_RESPUESTA_FALLBACK = "Uy bro, tuve un problema técnico. ¿Puedes repetirme qué quieres?"


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
# MOTOR DEL AGENTE — SIN TOOLS (catálogo inyectado en sistema)
# ─────────────────────────────────────────────

def _enriquecer_historial(historial: list) -> list:
    """
    Inyecta el catálogo REAL en cada mensaje de sistema.
    Si no hay catálogo, bloquea la respuesta con un error controlado.
    """
    catalogo = cargar_catalogo_productos()

    if not catalogo:
        # Sin datos reales → no responder con datos inventados
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

    catalogo_txt = _construir_catalogo_texto(catalogo)
    contexto = (
        f"\n\n═══ CATÁLOGO ACTUAL (DATOS REALES DE LA BD) ═══\n"
        f"{catalogo_txt}\n"
        f"═══════════════════════════════════════════════\n"
        f"REGLA CRÍTICA: USA SOLO ESTOS PRECIOS Y STOCKS. "
        f"NUNCA inventes precios, nombres ni disponibilidad."
    )

    enriquecido = []
    for m in historial:
        if m.get('role') == 'system':
            enriquecido.append({'role': 'system', 'content': m['content'] + contexto})
        else:
            enriquecido.append(m)
    return enriquecido


def responder(historial: list, verbose: bool = False) -> str:
    """
    Envía el historial a Ollama.
    NUNCA usa tools — el catálogo está inyectado en el prompt de sistema.
    Siempre devuelve texto natural, nunca JSON crudo ni leaks técnicos.
    """
    try:
        historial_enriquecido = _enriquecer_historial(historial)

        response = ollama.chat(
            model=MODELO,
            messages=historial_enriquecido,
            options={
                "num_predict": 300,
                "temperature": 0.75,
                "top_p": 0.9,
                "repeat_penalty": 1.1,
            }
        )

        contenido = response.message.content or ""

        # Bloquear cualquier leak técnico
        return _limpiar_respuesta(contenido)

    except Exception as e:
        err = str(e).lower()
        if verbose:
            print(f"[agente] Error en Ollama: {e}")
        if "connect" in err or "refused" in err:
            return "Uy bro, no me puedo conectar ahora. ¿Está Ollama abierto?"
        return _RESPUESTA_FALLBACK


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
