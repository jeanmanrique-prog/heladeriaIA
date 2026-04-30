"""
app/admin/gestion_manual/ventas.py
──────────────────────────────────
Visualización de ingresos, tendencias y detalles de ventas.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.peticiones import APIClient
from estilos.tema import fig_layout
from utils.formatters import formatear_precio

def render_ventas(api_ok: bool, theme: dict):
    """Renderiza la página de análisis de ventas."""
    st.markdown("<h1>Ventas 📈</h1>", unsafe_allow_html=True)

    if not api_ok:
        st.error("⚠️ Servidor API desconectado.")
        return

    data = APIClient.obtener_ventas()
    if not data or not data["ventas"]:
        st.info("🍦 No hay ventas para mostrar hoy.")
        return

    df = pd.DataFrame(data["ventas"])
    df["fecha"] = pd.to_datetime(df["fecha"]).dt.strftime("%d/%m")

    # KPIs
    _render_kpis(df)
    st.markdown("---")

    # Gráfica de tendencia
    _render_trend_chart(df, theme)

    # Listado detallado
    _render_sales_list(df)

def _render_kpis(df):
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("🛒 Pedidos", len(df))
    with col2: st.metric("💰 Total", formatear_precio(df["total"].sum()))
    with col3: st.metric("🎯 Ticket Promedio", formatear_precio(df["total"].mean()))

def _render_trend_chart(df, t):
    st.markdown('<div class="section-title">Tendencia de Ingresos</div>', unsafe_allow_html=True)
    df_day = df.groupby("fecha")["total"].sum().reset_index()
    fig = px.line(df_day, x="fecha", y="total", markers=True, color_discrete_sequence=[t['COLOR_LINE']])
    fig.update_traces(line_width=3, marker_size=8)
    st.plotly_chart(fig_layout(fig, t, height=300), use_container_width=True)

def _render_sales_list(df):
    st.markdown('<div class="section-title">Historial de Ventas</div>', unsafe_allow_html=True)
    disp = df[["id_venta", "fecha", "total", "metodo_pago"]].copy()
    disp.columns = ["ID", "Fecha", "Monto", "Pago"]
    st.dataframe(disp, use_container_width=True, hide_index=True)
