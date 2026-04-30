"""
ia_gui.py — Módulo de Chat IA para Streamlit
─────────────────────────────────────────────
render_chat_page() → usado desde app/cliente/ia.py y app/admin/ia.py.
"""

import streamlit as st
import streamlit.components.v1 as components
import time
import json
import base64
from pathlib import Path

from mcp.voz.pipeline.pipeline_voz import (
    verificar_ollama,
    inicializar_voz,
    inicializar_transcriptor,
    texto_voz_respuesta_vendedor,
    sintetizar_audio_wav,
    transcribir_audio,
    responder_vendedor_json,
    SYSTEM_PROMPT_VENDEDOR,
    MENSAJE_BIENVENIDA_CLIENTE,
    MODELO,
)

MAX_TURNOS_UI = 20
PROMPT_VERSION = "ventas-2026-04-23-v11"

# ──────────────────────────────────────────────────────────
# AUDIO INVISIBLE (sin reproductores visibles)
# ──────────────────────────────────────────────────────────

def _audio_autoplay_invisible(audio_bytes: bytes) -> None:
    """Reproduce audio WAV automáticamente SIN mostrar controles visuales."""
    if not audio_bytes:
        return
    b64 = base64.b64encode(audio_bytes).decode()
    components.html(
        f"""
        <audio autoplay style="display:none">
            <source src="data:audio/wav;base64,{b64}" type="audio/wav">
        </audio>
        """,
        height=0,
    )


# ──────────────────────────────────────────────────────────
# HELPERS DE ESTADO
# ──────────────────────────────────────────────────────────

def _state_key(mode: str, suffix: str) -> str:
    role_scope = str(st.session_state.get("role", "client")).strip().lower()
    role_scope = "admin" if role_scope == "admin" else "client"
    return f"helio_{role_scope}_{mode}_{suffix}"


def _copiar_historial_base() -> list[dict]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT_VENDEDOR},
        {"role": "assistant", "content": MENSAJE_BIENVENIDA_CLIENTE},
    ]


def _cargar_json(texto: str) -> dict | None:
    try:
        data = json.loads(texto)
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def _corregir_mojibake(texto: str) -> str:
    if not texto:
        return texto
    reemplazos = {
        "Â¿": "?", "Â¡": "!", "Ã¡": "á", "Ã©": "é",
        "Ã­": "í", "Ã³": "ó", "Ãº": "ú", "Ã±": "ñ",
    }
    limpio = texto
    for origen, destino in reemplazos.items():
        limpio = limpio.replace(origen, destino)
    return limpio.replace("¿", "?").replace("¡", "!")


def _texto_visible_asistente(texto: str) -> str:
    texto_natural = _corregir_mojibake(texto_voz_respuesta_vendedor(texto)).strip()
    return texto_natural if texto_natural else _corregir_mojibake(texto.strip()) or "Sin respuesta."


def _crear_mensaje_ui(role: str, contenido: str, source: str = "text") -> dict:
    payload = _cargar_json(contenido) if role == "assistant" else None
    display = _texto_visible_asistente(contenido) if role == "assistant" else contenido.strip()
    return {
        "role": role,
        "raw": contenido,
        "display": display or contenido,
        "payload": payload,
        "source": source,
    }


# ──────────────────────────────────────────────────────────
# SERVICIOS
# ──────────────────────────────────────────────────────────

def _refrescar_servicios(mode: str = "chat") -> None:
    ok, mensaje = verificar_ollama()
    st.session_state["helio_ollama_ok"] = ok
    st.session_state["helio_ollama_msg"] = mensaje
    if mode == "call":
        if not st.session_state.get("helio_voz_activa"):
            st.session_state["helio_voz_activa"] = inicializar_voz()
        if not st.session_state.get("helio_asr_activo"):
            st.session_state["helio_asr_activo"] = inicializar_transcriptor()


def _inicializar_estado_global(mode: str = "chat") -> None:
    if "helio_ollama_ok" not in st.session_state:
        _refrescar_servicios(mode)
    elif mode == "call" and not st.session_state.get("helio_asr_activo"):
        _refrescar_servicios(mode)


# ──────────────────────────────────────────────────────────
# RESET DE CONVERSACIÓN
# ──────────────────────────────────────────────────────────

def _reiniciar_conversacion(mode: str) -> None:
    """Limpia historial, mensajes, audio y saludo — reinicio completo."""
    st.session_state[_state_key(mode, "historial")] = _copiar_historial_base()
    st.session_state[_state_key(mode, "mensajes")] = [
        _crear_mensaje_ui("assistant", MENSAJE_BIENVENIDA_CLIENTE, source="system")
    ]
    st.session_state[_state_key(mode, "audio_respuesta")] = None
    st.session_state[_state_key(mode, "audio_autoplay")] = False
    st.session_state[_state_key(mode, "saludo_enviado")] = False


def _inicializar_estado_modo(mode: str) -> None:
    historial_key = _state_key(mode, "historial")
    mensajes_key = _state_key(mode, "mensajes")
    prompt_version_key = _state_key(mode, "prompt_version")

    if historial_key not in st.session_state:
        st.session_state[historial_key] = _copiar_historial_base()
        st.session_state["primera_vez_voz"] = True

    if mensajes_key not in st.session_state:
        st.session_state[mensajes_key] = [
            _crear_mensaje_ui("assistant", MENSAJE_BIENVENIDA_CLIENTE, source="system")
        ]

    if st.session_state.get(prompt_version_key) != PROMPT_VERSION:
        _reiniciar_conversacion(mode)
        st.session_state[prompt_version_key] = PROMPT_VERSION

    defaults = {
        _state_key(mode, "audio_respuesta"): None,
        _state_key(mode, "audio_autoplay"): False,
        _state_key(mode, "saludo_enviado"): False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _recortar_historial(mode: str) -> None:
    historial_key = _state_key(mode, "historial")
    mensajes_key = _state_key(mode, "mensajes")
    historial = st.session_state[historial_key]
    if len(historial) > (2 + MAX_TURNOS_UI * 2):
        st.session_state[historial_key] = historial[:2] + historial[-(MAX_TURNOS_UI * 2):]
    mensajes = st.session_state[mensajes_key]
    if len(mensajes) > (1 + MAX_TURNOS_UI * 2):
        st.session_state[mensajes_key] = mensajes[:1] + mensajes[-(MAX_TURNOS_UI * 2):]


# ──────────────────────────────────────────────────────────
# AUDIO (invisible)
# ──────────────────────────────────────────────────────────

def _guardar_y_reproducir_audio(mode: str, respuesta_raw: str, voz_activa: bool) -> None:
    """Sintetiza y reproduce audio de la respuesta de forma invisible."""
    if not voz_activa:
        return
    texto_voz = _texto_visible_asistente(respuesta_raw)
    audio = sintetizar_audio_wav(texto_voz)
    if audio:
        st.session_state[_state_key(mode, "audio_respuesta")] = audio
        st.session_state[_state_key(mode, "audio_autoplay")] = True


def _reproducir_saludo_voz(mode: str, voz_activa: bool) -> None:
    """Reproduce el saludo de bienvenida UNA sola vez, sin mostrar controles."""
    saludo_key = _state_key(mode, "saludo_enviado")
    if st.session_state.get(saludo_key, False) or not voz_activa:
        return
    texto_saludo = _texto_visible_asistente(MENSAJE_BIENVENIDA_CLIENTE)
    audio = sintetizar_audio_wav(texto_saludo)
    if audio:
        _audio_autoplay_invisible(audio)
    st.session_state[saludo_key] = True


# ──────────────────────────────────────────────────────────
# RENDERIZADO DE MENSAJES
# ──────────────────────────────────────────────────────────

def _renderizar_items(items: list[dict]) -> None:
    filas = [
        {
            "Producto": i.get("nombre_producto") or i.get("producto") or i.get("nombre") or "Producto",
            "Cantidad": i.get("cantidad", 1),
            "Precio": i.get("precio_unitario") or i.get("precio") or "-",
            "Subtotal": i.get("subtotal", "-"),
        }
        for i in items
    ]
    if filas:
        st.dataframe(filas, use_container_width=True, hide_index=True)


def _renderizar_mensaje_asistente(mensaje: dict) -> None:
    """Siempre muestra texto natural. Nunca JSON crudo."""
    display = mensaje.get("display", "")
    payload = mensaje.get("payload")

    if not payload or not isinstance(payload, dict):
        st.write(display or "...")
        return

    accion = payload.get("accion", "informacion")

    if accion == "mostrar_productos":
        st.write(display)
        prods = [
            {
                "Producto": p.get("nombre") or p.get("nombre_producto") or p.get("sabor") or "?",
                "Sabor": p.get("sabor", "-"),
                "Precio": p.get("precio", "-"),
                "Stock": p.get("stock", "-"),
            }
            for p in payload.get("productos", [])
        ]
        if prods:
            st.dataframe(prods, use_container_width=True, hide_index=True)

    elif accion in {"pedir_pago", "crear_venta"}:
        st.write(display)
        _renderizar_items(payload.get("items", []))
        if payload.get("total"):
            st.caption(f"Total: {payload.get('total')}")

    elif accion == "venta_exitosa":
        st.success(display)
        detalle = payload.get("detalle", {})
        _renderizar_items(detalle.get("productos", []))
        extras = []
        if detalle.get("id_venta"):
            extras.append(f"Venta #{detalle['id_venta']}")
        total = detalle.get("total", payload.get("total"))
        if total:
            extras.append(f"Total: {total}")
        metodo = detalle.get("metodo_pago", payload.get("metodo_pago"))
        if metodo:
            extras.append(f"Pago: {metodo}")
        if extras:
            st.caption(" | ".join(extras))

    elif accion in {"error", "sin_stock"}:
        st.warning(display)

    else:
        st.write(display)


# ──────────────────────────────────────────────────────────
# HEADER DEL CHAT — badge modelo + botón nueva conversación
# ──────────────────────────────────────────────────────────

def _renderizar_header_chat(mode: str, ollama_ok: bool, accent: str = "#a8124a") -> None:
    """
    Header moderno con:
    - Badge del modelo activo (punto verde/rojo)
    - Botón estilizado "Nueva conversación"
    Sin título (el título lo pone el componente padre en cliente/ia.py).
    """
    modelo_display = MODELO if ollama_ok else "Sin conexión"
    dot_color = "#2ecc71" if ollama_ok else "#e74c3c"
    estado_txt = "Conectado" if ollama_ok else "Desconectado"

    # CSS una sola vez por sesión
    st.markdown(
        f"""
        <style>
        .helio-badge {{
            display: inline-flex;
            align-items: center;
            gap: 7px;
            background: rgba(255,255,255,0.07);
            border: 1px solid rgba(255,255,255,0.14);
            border-radius: 20px;
            padding: 5px 14px 5px 10px;
            font-size: 0.78rem;
            font-weight: 700;
            white-space: nowrap;
        }}
        .helio-badge .dot {{
            width: 9px; height: 9px;
            border-radius: 50%;
            background: {dot_color};
            flex-shrink: 0;
            box-shadow: 0 0 6px {dot_color};
        }}
        .helio-badge .model-name {{
            font-family: 'Nunito', monospace;
            letter-spacing: 0.02em;
        }}
        .helio-badge .status-txt {{
            opacity: 0.65;
            font-size: 0.70rem;
        }}
        /* Botón nueva conversación: override del sticker urbano para este key */
        div[data-testid="stButton"][data-key="btn_nueva_{mode}"] > button,
        [data-testid="column"] button[kind="secondary"] {{
            background: linear-gradient(135deg, {accent} 0%, #e05080 100%) !important;
            color: #fff !important;
            border-radius: 14px !important;
            border: none !important;
            padding: 7px 16px !important;
            font-size: 0.88rem !important;
            font-weight: 800 !important;
            letter-spacing: 0.03em !important;
            box-shadow: 0 4px 14px rgba(168,18,74,0.28) !important;
            transition: transform 0.15s ease, box-shadow 0.15s ease !important;
            text-transform: none !important;
        }}
        div[data-testid="stButton"][data-key="btn_nueva_{mode}"] > button:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 7px 18px rgba(168,18,74,0.38) !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    col_badge, col_btn = st.columns([3, 2])

    with col_badge:
        st.markdown(
            f"""
            <div class="helio-badge">
                <span class="dot"></span>
                <span class="model-name">{modelo_display}</span>
                <span class="status-txt">· {estado_txt}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_btn:
        if st.button(
            "🔄 Nueva conversación",
            key=f"btn_nueva_{mode}",
            use_container_width=True,
            type="secondary",
        ):
            _reiniciar_conversacion(mode)
            st.rerun()


# ──────────────────────────────────────────────────────────
# PÁGINA PRINCIPAL DE CHAT
# ──────────────────────────────────────────────────────────

def render_chat_page(api_ok: bool = True, page_mode: str = "chat", accent: str = "#a8124a") -> None:
    """
    Renderiza la página de chat completa.
    El título debe ponerse en el componente padre (cliente/ia.py o admin/ia.py).
    """
    mode = "call" if page_mode == "call" else "chat"

    _inicializar_estado_global(mode)
    _inicializar_estado_modo(mode)

    ollama_ok = st.session_state.get("helio_ollama_ok", False)
    voz_activa = st.session_state.get("helio_voz_activa", False)

    if mode != "chat":
        return  # El modo call se delega al componente de voz en main.py

    # ── Header (badge + botón) ──
    _renderizar_header_chat(mode, ollama_ok, accent=accent)
    st.divider()

    # ── Alerta si Ollama no responde ──
    if not ollama_ok:
        st.error(
            f"⚠️ {st.session_state.get('helio_ollama_msg', 'Ollama no disponible.')} "
            "— Verifica que esté abierto.",
            icon="🔌",
        )

    # ── Saludo por voz (una sola vez, sin UI visible) ──
    _reproducir_saludo_voz(mode, voz_activa)

    # ── Historial de mensajes ──
    for m in st.session_state[_state_key(mode, "mensajes")]:
        with st.chat_message(m["role"]):
            if m["role"] == "assistant":
                _renderizar_mensaje_asistente(m)
            else:
                st.write(m["display"])

    # ── Reproducir audio de la última respuesta (invisible) ──
    audio_resp = st.session_state.get(_state_key(mode, "audio_respuesta"))
    autoplay = st.session_state.get(_state_key(mode, "audio_autoplay"), False)
    if audio_resp and autoplay:
        _audio_autoplay_invisible(audio_resp)
        st.session_state[_state_key(mode, "audio_autoplay")] = False

    # ── Input del chat ──
    if prompt := st.chat_input(
        "Escribe tu pedido...",
        disabled=(not ollama_ok or not api_ok),
    ):
        with st.chat_message("user"):
            st.write(prompt)

        msg_user = _crear_mensaje_ui("user", prompt)
        st.session_state[_state_key(mode, "mensajes")].append(msg_user)
        st.session_state[_state_key(mode, "historial")].append(
            {"role": "user", "content": prompt}
        )

        with st.chat_message("assistant"):
            with st.spinner("Urban está pensando... 🍦"):
                try:
                    res = responder_vendedor_json(
                        st.session_state[_state_key(mode, "historial")],
                        verbose=False,
                    )
                except Exception:
                    res = '{"accion":"error","mensaje":"No pude responder. Intenta de nuevo."}'

        st.session_state[_state_key(mode, "historial")].append(
            {"role": "assistant", "content": res}
        )
        msg_ui = _crear_mensaje_ui("assistant", res)
        st.session_state[_state_key(mode, "mensajes")].append(msg_ui)

        _recortar_historial(mode)
        _guardar_y_reproducir_audio(mode, res, voz_activa)
        st.rerun()
