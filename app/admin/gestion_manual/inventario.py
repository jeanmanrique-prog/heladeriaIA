"""
app/admin/gestion_manual/inventario.py
──────────────────────────────────────
Gestión de stock y registro de entradas de inventario (Versión Compacta).
"""

import streamlit as st
from pathlib import Path
from utils.peticiones import APIClient

def render_inventario(api_ok: bool, theme: dict):
    """Renderiza la página de inventario con pestañas para ver y agregar stock."""
    # Estilos para uniformidad de tarjetas de inventario COMPACTO
    st.markdown(f"""
        <style>
        .inventory-card {{
            background: {theme['BG2']};
            border-radius: 12px;
            padding: 10px;
            border: 1px solid rgba(255,255,255,0.05);
            height: 280px; /* Reducido de 420px */
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            margin-bottom: 15px;
        }}
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1>Inventario 📦</h1>", unsafe_allow_html=True)

    if not api_ok:
        st.error("⚠️ Servidor API desconectado.")
        return

    tab_ver, tab_entrada = st.tabs(["📋 Estado Actual", "➕ Agregar Stock"])

    with tab_ver:
        _render_stock_grid(theme)

    with tab_entrada:
        _render_entrada_stock()

def _render_stock_grid(t):
    inv_data = APIClient.obtener_inventario()
    if not inv_data:
        st.info("Cargando inventario...")
        return
        
    st.markdown('<div class="section-title">Niveles de Stock</div>', unsafe_allow_html=True)
    # 4 columnas para modo compacto
    grid = st.columns(4)
    for idx, item in enumerate(inv_data["inventario"]):
        with grid[idx % 4]:
            _render_item_card(item, t)

def _render_item_card(item, t):
    sabor = str(item.get('sabor', '')).strip().lower()
    
    st.markdown('<div class="inventory-card">', unsafe_allow_html=True)
    
    # Imagen de producto (más pequeña)
    _render_producto_img(sabor, t)
    
    # Detalles
    st.markdown(f"""
        <div style="text-align: center;">
            <h5 style="margin: 5px 0; font-size: 0.95rem;">{item['nombre_producto']}</h5>
        </div>
    """, unsafe_allow_html=True)
    
    color = t['COLOR_OK'] if not item['alerta_stock'] else t['COLOR_ALERTA']
    st.markdown(f"""
        <div style="text-align: center; margin-bottom: 5px;">
            <span style='color:{color}; font-size:1.4rem; font-weight:900;'>{item['stock']} L</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def _render_producto_img(sabor, t):
    root_dir = Path(__file__).resolve().parent.parent.parent.parent
    path = root_dir / "imagenes" / f"{sabor}-oscuro.png"
    if path.exists():
        # Imagen compacta
        st.image(str(path), use_container_width=True)
    else:
        st.markdown(f"<div style='height:80px; display:flex; align-items:center; justify-content:center; background:{t['BG']}; border-radius:12px; font-size:1.5rem;'>🍨</div>", unsafe_allow_html=True)

def _render_entrada_stock():
    st.markdown("### ➕ Registrar Entrada")
    prod_data = APIClient.obtener_productos()
    if prod_data:
        prods = {p["nombre_producto"]: p["id_producto"] for p in prod_data["productos"]}
        sel = st.selectbox("Producto", list(prods.keys()))
        cant = st.number_input("Litros a ingresar", min_value=1, value=10)
        motivo = st.text_input("Motivo", value="Reposición de stock")
        
        if st.button("📥 Registrar"):
            res = APIClient.entrada_inventario({"id_producto": prods[sel], "cantidad": cant, "motivo": motivo})
            if res:
                st.success("Stock actualizado correctamente")
                st.rerun()
