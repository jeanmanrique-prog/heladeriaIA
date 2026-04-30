"""
app/admin/gestion_manual/movimientos.py
───────────────────────────────────────
Kardex y registro histórico de movimientos de inventario.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.peticiones import APIClient
from estilos.tema import fig_layout

def render_movimientos(api_ok: bool, theme: dict):
    """Renderiza el historial de movimientos de inventario."""
    st.markdown("<h1>Movimientos 📋</h1>", unsafe_allow_html=True)

    if not api_ok:
        st.error("⚠️ Servidor API desconectado.")
        return

    data = APIClient.obtener_movimientos()
    if not data or not data["movimientos"]:
        st.info("No hay movimientos registrados.")
        return

    df = pd.DataFrame(data["movimientos"])
    df["fecha"] = pd.to_datetime(df["fecha"]).dt.strftime("%d/%m %H:%M")

    # Filtros
    _render_filters_and_chart(df, theme)
    
    # Tabla
    _render_moves_table(df)

def _render_filters_and_chart(df, t):
    st.markdown('<div class="section-title">Análisis de Movimientos</div>', unsafe_allow_html=True)
    
    resumen = df.groupby(["nombre_producto", "tipo"])["cantidad"].sum().reset_index()
    fig = px.bar(resumen, x="nombre_producto", y="cantidad", color="tipo",
                 barmode="group", color_discrete_map={"entrada": t['COLOR_OK'], "salida": t['COLOR_ALERTA']})
    
    st.plotly_chart(fig_layout(fig, t, height=300), use_container_width=True)

def _render_moves_table(df):
    st.markdown('<div class="section-title">Registro Histórico</div>', unsafe_allow_html=True)
    disp = df[["fecha", "nombre_producto", "tipo", "cantidad", "motivo"]].copy()
    disp.columns = ["Fecha", "Producto", "Tipo", "Cant", "Motivo"]
    st.dataframe(disp, use_container_width=True, hide_index=True)
