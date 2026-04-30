"""
app/cliente/compra_manual/comprar.py
────────────────────────────────────
Módulo de catálogo y compra manual para el cliente (Versión Compacta Corregida).
"""

import streamlit as st
from pathlib import Path
from utils.peticiones import APIClient
from utils.formatters import formatear_precio

def render_comprar(pagina: str, api_ok: bool, theme: dict):
    """Renderiza el catálogo de productos y el carrito de compras."""
    if pagina != "🛒 Comprar" and pagina != "Comprar":
        return

    # Estilos para uniformidad de contenedores nativos
    st.markdown(f"""
        <style>
        [data-testid="stHeader"] {{ display: none !important; }}
        [data-testid="stToolbar"] {{ display: none !important; }}
        .stApp {{ background-color: {theme['BG']} !important; }}
        
        /* Forzar altura en contenedores con borde para uniformidad */
        [data-testid="stVerticalBlockBorderWrapper"] > div {{
            height: 380px !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: space-between !important;
            padding: 10px !important;
            background-color: {theme['BG2']} !important;
        }}
        
        /* Ajustar imágenes para que no se recorten */
        [data-testid="stImage"] img {{
            object-fit: contain !important;
            max-height: 140px !important;
        }}
        
        .compact-title {{
            font-size: 1.1rem !important;
            font-weight: 700 !important;
            margin: 5px 0 !important;
            text-align: center !important;
            height: 2.6em;
            overflow: hidden;
        }}
        
        .compact-price {{
            color: {theme['ACCENT']} !important;
            font-size: 1.3rem !important;
            font-weight: 900 !important;
            text-align: center !important;
            margin-bottom: 5px !important;
        }}
        </style>
    """, unsafe_allow_html=True)

    # 1. Imagen de Urban Compre (CENTRADA)
    _render_header_image()
    
    # 2. Título y Buscador (A LA IZQUIERDA)
    st.markdown("<h2 style='text-align:left; margin-bottom: 10px;'>Catálogo Urbano 🍨</h2>", unsafe_allow_html=True)

    if not api_ok:
        st.error("⚠️ API desconectada.")
        return

    res = APIClient.obtener_productos()
    if not res or "productos" not in res:
        st.info("Cargando catálogo...")
        return
        
    productos = res["productos"]
    if "carrito" not in st.session_state:
        st.session_state.carrito = []

    col_main, col_cart = st.columns([7.5, 2.5], gap="medium")

    with col_main:
        # Buscador pequeño a la izquierda
        col_q, _ = st.columns([0.4, 0.6])
        with col_q:
            q = st.text_input("🔍 Buscar sabor...", label_visibility="collapsed", placeholder="Buscar sabor...").lower()
        
        st.markdown("<br>", unsafe_allow_html=True)
        _render_catalogo(productos, q, theme)
    
    with col_cart:
        _render_carrito(theme)

def _render_header_image():
    root_dir = Path(__file__).resolve().parent.parent.parent.parent
    path = root_dir / "imagenes" / "urban_compre.png"
    if path.exists():
        c1, c2, c3 = st.columns([1, 1.5, 1])
        with c2:
            st.image(str(path), width=6500)

def _render_catalogo(productos, query, t):
    prods = [p for p in productos if query in p["nombre_producto"].lower() or query in p.get("sabor", "").lower()]
    
    if not prods:
        st.info("No hay resultados.")
        return

    cols = st.columns(3)
    for idx, p in enumerate(prods):
        with cols[idx % 3]:
            _render_producto_card(p, t)

def _render_producto_card(p, t):
    sabor = str(p.get('sabor', '')).strip().lower()
    root_dir = Path(__file__).resolve().parent.parent.parent.parent
    img_path = root_dir / "imagenes" / f"{sabor}.png"
    
    # Usar contenedor nativo con borde para evitar el desfase HTML/Streamlit
    with st.container(border=True):
        # Imagen
        if img_path.exists():
            st.image(str(img_path), use_container_width=True)
        else:
            st.markdown(f"<div style='height:140px; display:flex; align-items:center; justify-content:center; font-size:2.5rem;'>🍨</div>", unsafe_allow_html=True)

        # Info
        st.markdown(f"""
            <div class="compact-title">{p['nombre_producto']}</div>
            <div style='text-align:center; font-size:0.85rem; opacity:0.7; margin-bottom:5px;'>{sabor.capitalize()}</div>
            <div class="compact-price">{formatear_precio(p['precio_unitario'])}</div>
        """, unsafe_allow_html=True)
        
        # Botón
        stock = p.get('stock', 0)
        if stock > 0:
            if st.button("➕ Pedir", key=f"add_{p['id_producto']}", use_container_width=True):
                _agregar_al_carrito(p)
                st.rerun()
        else:
            st.error("Agotado")

def _agregar_al_carrito(p):
    existente = next((i for i in st.session_state.carrito if i["id_producto"] == p["id_producto"]), None)
    if existente:
        existente["cantidad"] += 1
        existente["subtotal"] = existente["cantidad"] * p["precio_unitario"]
    else:
        st.session_state.carrito.append({
            "id_producto": p["id_producto"],
            "nombre": p["nombre_producto"],
            "precio_unitario": p["precio_unitario"],
            "cantidad": 1,
            "subtotal": p["precio_unitario"]
        })

def _render_carrito(t):
    st.markdown('<div class="section-title">🛒 Carrito</div>', unsafe_allow_html=True)
    if not st.session_state.carrito:
        st.info("Vacío")
        return

    for idx, item in enumerate(st.session_state.carrito):
        with st.container(border=True):
            st.markdown(f"**{item['nombre']}**")
            st.markdown(f"{item['cantidad']} x {formatear_precio(item['precio_unitario'])}")
            if st.button("🗑️", key=f"del_{idx}"):
                st.session_state.carrito.pop(idx)
                st.rerun()

    total = sum(i["subtotal"] for i in st.session_state.carrito)
    st.markdown(f"<h3 style='color:{t['ACCENT']};'>Total: {formatear_precio(total)}</h3>", unsafe_allow_html=True)
    
    if st.button("🚀 Confirmar Compra", use_container_width=True):
        res = APIClient.crear_venta({"items": st.session_state.carrito, "metodo_pago": "efectivo"})
        if res:
            st.balloons()
            st.toast("¡Compra exitosa! 🤩")
            st.success("¡Listo! Disfruta tu helado.")
            st.session_state.carrito = []
            st.rerun()
