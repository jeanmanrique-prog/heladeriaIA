"""
app/admin/gestion_manual/dashboard.py
──────────────────────────────────────
Panel principal con métricas y gráficas para el administrador.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.peticiones import APIClient
from estilos.tema import fig_layout

def render_dashboard(api_ok: bool, theme: dict):
    """Renderiza el dashboard con KPIs y visualizaciones."""
    st.markdown("<h1>Dashboard 📊</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='sidebar-sub'>Resumen general de Gelateria Urbana</p>", unsafe_allow_html=True)

    if not api_ok:
        st.error("⚠️ Servidor API desconectado.")
        return

    # Cargar datos
    inv_data = APIClient.obtener_inventario()
    ventas_data = APIClient.obtener_ventas()
    alertas_data = APIClient.obtener_alertas()

    # Métricas principales
    _render_metrics(inv_data, ventas_data)
    st.markdown("---")

    col_izq, col_der = st.columns([3, 2])
    with col_izq:
        _render_stock_chart(inv_data, theme)
    with col_der:
        _render_alerts_list(alertas_data)

def _render_metrics(inv_data, ventas_data):
    col1, col2, col3, col4 = st.columns(4)
    total_stock = sum(i["stock"] for i in inv_data["inventario"]) if inv_data else 0
    alertas_count = sum(1 for i in inv_data["inventario"] if i["alerta_stock"]) if inv_data else 0
    total_ventas = len(ventas_data["ventas"]) if ventas_data else 0
    ingresos = sum(v["total"] for v in ventas_data["ventas"]) if ventas_data else 0

    with col1: st.metric("🍨 Stock Total", total_stock)
    with col2: st.metric("⚠️ En Alerta", alertas_count, delta=f"-{alertas_count}" if alertas_count > 0 else None, delta_color="inverse")
    with col3: st.metric("🛒 Ventas", total_ventas)
    with col4: st.metric("💰 Ingresos", f"${ingresos:,.0f}".replace(",", "."))

def _render_stock_chart(inv_data, t):
    st.markdown('<div class="section-title">Stock por Sabor</div>', unsafe_allow_html=True)
    if inv_data:
        df = pd.DataFrame(inv_data["inventario"])
        colors = [t['COLOR_ALERTA'] if r["alerta_stock"] else t['COLOR_OK'] for _, r in df.iterrows()]
        fig = go.Figure(go.Bar(
            x=df["nombre_producto"], y=df["stock"], marker_color=colors,
            text=df["stock"], textposition="outside"
        ))
        st.plotly_chart(fig_layout(fig, t, height=320), use_container_width=True)

def _render_alerts_list(alertas_data):
    st.markdown('<div class="section-title">⚠️ Reponer Stock</div>', unsafe_allow_html=True)
    if alertas_data and alertas_data["alertas"]:
        for a in alertas_data["alertas"]:
            st.markdown(f"""
                <div class="alerta-card">
                    <div>
                        <div class="alerta-nombre">🍨 {a['nombre_producto']}</div>
                        <div class="alerta-stock">Mínimo: {a['stock_minimo']} uds</div>
                    </div>
                    <div class="alerta-nombre">{a['stock']} uds</div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ Stock en niveles óptimos")
