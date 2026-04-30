"""
app/admin/gestion_manual/inventario.py
Gestion de stock y registro de entradas de inventario.
"""

import base64
import html
from pathlib import Path

import streamlit as st

from utils.peticiones import APIClient


def render_inventario(api_ok: bool, theme: dict):
    """Renderiza la pagina de inventario con pestanas para ver y agregar stock."""
    st.markdown(
        f"""
        <style>
        .inventory-card {{
            background: {theme['BG2']};
            border-radius: 12px;
            padding: 14px 12px;
            border: 1px solid rgba(255,255,255,0.05);
            min-height: 280px;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
        }}
        .inventory-card__media {{
            width: 100%;
            height: 150px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .inventory-card__media img {{
            display: block;
            max-width: 100%;
            max-height: 150px;
            margin: 0 auto;
            object-fit: contain;
        }}
        .inventory-card__title {{
            min-height: 2.8em;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
        }}
        .inventory-card__title h5 {{
            margin: 0;
            font-size: 0.95rem;
            line-height: 1.35;
        }}
        .inventory-card__stock {{
            margin-top: auto;
            text-align: center;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<h1>Inventario 📦</h1>", unsafe_allow_html=True)

    if not api_ok:
        st.error("⚠️ Servidor API desconectado.")
        return

    tab_ver, tab_entrada = st.tabs(["📋 Estado Actual", "➕ Agregar Stock"])

    with tab_ver:
        _render_stock_grid(theme)

    with tab_entrada:
        _render_entrada_stock()


def _render_stock_grid(theme: dict):
    inv_data = APIClient.obtener_inventario()
    if not inv_data:
        st.info("Cargando inventario...")
        return

    st.markdown('<div class="section-title">Niveles de Stock</div>', unsafe_allow_html=True)
    grid = st.columns(4)
    for idx, item in enumerate(inv_data["inventario"]):
        with grid[idx % 4]:
            _render_item_card(item, theme)


def _render_item_card(item: dict, theme: dict):
    sabor = str(item.get("sabor", "")).strip().lower()
    nombre = html.escape(str(item["nombre_producto"]))
    color = theme["COLOR_OK"] if not item["alerta_stock"] else theme["COLOR_ALERTA"]

    st.markdown(
        f"""
        <div class="inventory-card">
            {_render_producto_img_markup(sabor, theme)}
            <div class="inventory-card__title">
                <h5>{nombre}</h5>
            </div>
            <div class="inventory-card__stock">
                <span style="color:{color}; font-size:1.4rem; font-weight:900;">{item['stock']} L</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_producto_img_markup(sabor: str, theme: dict) -> str:
    root_dir = Path(__file__).resolve().parent.parent.parent.parent
    path = root_dir / "imagenes" / f"{sabor}-oscuro.png"

    if path.exists():
        img_b64 = base64.b64encode(path.read_bytes()).decode()
        return (
            '<div class="inventory-card__media">'
            f'<img src="data:image/png;base64,{img_b64}" alt="{html.escape(sabor)}">'
            "</div>"
        )

    return (
        '<div class="inventory-card__media">'
        f"<div style='height:100%; width:100%; display:flex; align-items:center; justify-content:center; "
        f"background:{theme['BG']}; border-radius:12px; font-size:1.5rem;'>🍨</div>"
        "</div>"
    )


def _render_entrada_stock():
    st.markdown("### ➕ Registrar Entrada")
    prod_data = APIClient.obtener_productos()
    if prod_data:
        prods = {p["nombre_producto"]: p["id_producto"] for p in prod_data["productos"]}
        sel = st.selectbox("Producto", list(prods.keys()))
        cant = st.number_input("Litros a ingresar", min_value=1, value=10)
        motivo = st.text_input("Motivo", value="Reposición de stock")

        if st.button("📥 Registrar"):
            res = APIClient.entrada_inventario(
                {"id_producto": prods[sel], "cantidad": cant, "motivo": motivo}
            )
            if res:
                st.success("Stock actualizado correctamente")
                st.rerun()
