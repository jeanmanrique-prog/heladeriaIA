"""
app/cliente/compra_manual/comprar.py
────────────────────────────────────
Catálogo Urbano (Versión Diseño Ligero/Mockup).
"""

import streamlit as st
import base64
from pathlib import Path
from utilidades.peticiones import ClienteAPI

def render_comprar(pagina: str, api_ok: bool, theme: dict):
    """Renderiza el catálogo imitando el diseño limpio de la imagen de referencia."""
    
    if st.session_state.get("compra_exitosa"):
        st.balloons()
        st.toast("¡Pedido confirmado con éxito! 🎉", icon="✅")
        st.session_state.compra_exitosa = False

    # LAYOUT PRINCIPAL [Catálogo | Carrito]
    col_cat, col_cart = st.columns([2.8, 1.2], gap="large") 
    
    with col_cat:
        # TÍTULOS ALINEADOS A LA IZQUIERDA (Como en la imagen)
        st.markdown("<h1 class='main-title'>Catálogo Urbano 🍨</h1>", unsafe_allow_html=True)
        st.markdown("<p class='sub-title'>Pide tu helado artesanal en segundos 🤍</p>", unsafe_allow_html=True)
        
        # BUSCADOR
        busqueda = st.text_input("", placeholder="🔍 Buscar sabor...", label_visibility="collapsed", key="search_mockup")
        st.markdown("<br>", unsafe_allow_html=True)

        # Obtener productos
        res = ClienteAPI.obtener_productos()
        if isinstance(res, dict): productos = res.get("productos", [])
        elif isinstance(res, list): productos = res
        else: productos = []

        if busqueda:
            productos = [p for p in productos if busqueda.lower() in p['nombre_producto'].lower()]

        if not productos:
            st.warning("No se encontraron productos.")
        else:
            # GRID DE PRODUCTOS
            c1, c2, c3 = st.columns(3)
            cols = [c1, c2, c3]
            for idx, p in enumerate(productos):
                with cols[idx % 3]:
                    with st.container(border=True):
                        _render_card_mockup(p)

    with col_cart:
        # TARJETA DEL CARRITO (Todo envuelto en un contenedor sombreado)
        with st.container(border=True):
            st.markdown("<h3 style='text-align:center; color:#FF3366; font-weight:800;'>🛒 Carrito</h3>", unsafe_allow_html=True)
            st.markdown("<div class='dotted-divider'></div>", unsafe_allow_html=True)
            
            _render_carrito_mockup(theme)
            
            # Footer de Seguridad integrado en el carrito
            st.markdown("""
                <div style="background-color: #FFF8F1; border-radius: 12px; padding: 15px; text-align: center; margin-top: 20px;">
                    <p style="color: #FF3366; font-weight: 800; font-size: 0.9rem; margin-bottom: 2px;">🔒 Compra 100% segura</p>
                    <p style="color: #9CA3AF; font-size: 0.75rem; margin-bottom: 0;">Tus datos están protegidos.</p>
                </div>
            """, unsafe_allow_html=True)

    # FOOTER CENTRAL INFERIOR
    st.markdown("<br><br><p style='text-align:center; color:#FF3366; font-weight:700; font-size:0.8rem; letter-spacing:1px;'>— HECHO CON ❤️ Y MUCHO SABOR —</p>", unsafe_allow_html=True)

def _render_card_mockup(p):
    """Tarjeta de producto ultra limpia."""
    sabor = str(p.get('sabor', 'vainilla')).strip().lower()
    root_dir = Path(__file__).resolve().parent.parent.parent.parent
    img_path = root_dir / "imagenes" / f"{sabor}.png"
    
    img_tag = "<div style='font-size: 3.5rem; text-align:center; height:120px;'>🍨</div>"
    if img_path.exists():
        b64 = base64.b64encode(img_path.read_bytes()).decode()
        img_tag = f'<div style="text-align:center; height:150px; margin-bottom:10px;"><img src="data:image/png;base64,{b64}" style="max-height:150px; width:auto;"></div>'
    
    stock = p.get('stock', 0)
    stock_txt = f"<p class='card-price'>$ {p['precio_unitario']:,}</p>"
    if stock <= 0:
        stock_txt = "<p style='color:#EF4444; font-weight:800; font-size:1rem; margin:10px 0;'>⚠️ AGOTADO</p>"

    st.markdown(f"""
        {img_tag}
        <p class='card-title'>Tarro 1L {sabor.capitalize()}</p>
        <p class='card-flavor'>{sabor.capitalize()}</p>
        {stock_txt}
    """, unsafe_allow_html=True)
    
    # Botón deshabilitado si no hay stock
    if st.button(f"+ PEDIR", type="primary", key=f"btn_p_mock_{p['id_producto']}", use_container_width=True, disabled=stock <= 0):
        _agregar_al_carrito(p)
        st.toast(f"¡{p['nombre_producto']} añadido!")

def _render_carrito_mockup(theme):
    if "carrito" not in st.session_state: st.session_state.carrito = []
    
    if not st.session_state.carrito:
        # ESTADO VACÍO (Como en la imagen)
        st.markdown("""
            <div style="text-align: center; padding: 20px 0;">
                <div style="font-size: 4rem; color: #FFE6EB; margin-bottom: 10px;">🍦</div>
                <p style="color: #1F2937; font-weight: 800; font-size: 1.1rem; margin-bottom: 5px;">Tu carrito está vacío 🍨</p>
                <p style="color: #9CA3AF; font-size: 0.85rem; line-height: 1.4;">Agrega productos para<br>comenzar tu pedido</p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<div class='dotted-divider'></div>", unsafe_allow_html=True)
        return

    # PRODUCTOS EN EL CARRITO
    total = 0
    for idx, item in enumerate(st.session_state.carrito):
        st.markdown(f"<p style='color:#1F2937; font-weight:700; font-size:0.9rem; margin-bottom:2px;'>{item['nombre']}</p>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns([1.2, 0.6, 0.6, 0.6])
        c1.markdown(f"<span style='color:#FF3366; font-weight:800;'>${item['precio_unitario']:,}</span>", unsafe_allow_html=True)
        if c2.button("−", key=f"m_mock_{idx}"): _modificar_cantidad(idx, -1)
        c3.markdown(f"<p style='text-align:center; padding-top:4px; font-weight:700; color:#31333F;'>{item['cantidad']}</p>", unsafe_allow_html=True)
        if c4.button("+", key=f"p_mock_{idx}"): _modificar_cantidad(idx, 1)
        total += item['subtotal']
        st.markdown("<div class='dotted-divider'></div>", unsafe_allow_html=True)

    st.markdown(f"<h3 style='text-align:center; color:#1F2937; font-weight:900;'>Total: ${total:,}</h3>", unsafe_allow_html=True)
    metodo = st.radio("Pago", ["Efectivo", "Tarjeta"], key="pay_mock", horizontal=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("CONFIRMAR", type="primary", key="btn_confirm_mock", use_container_width=True):
        items_api = [{"id_producto": i["id_producto"], "cantidad": i["cantidad"]} for i in st.session_state.carrito]
        payload = {"metodo_pago": metodo.lower(), "items": items_api}
        
        ok, res = ClienteAPI.crear_venta(payload)
        if ok:
            st.session_state.carrito = []
            st.session_state.compra_exitosa = True
            st.rerun()
        else:
            st.error(f"Error: {res}")

def _modificar_cantidad(idx, delta):
    item = st.session_state.carrito[idx]
    item["cantidad"] += delta
    if item["cantidad"] <= 0: st.session_state.carrito.pop(idx)
    else: item["subtotal"] = item["cantidad"] * item["precio_unitario"]
    st.rerun()

def _agregar_al_carrito(p):
    if "carrito" not in st.session_state: st.session_state.carrito = []
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
