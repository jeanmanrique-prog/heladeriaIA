import streamlit as st
from componentes.estilos_tarjetas import obtener_estilo_tarjeta_metrica, obtener_estilo_tarjeta_producto

def renderizar_tarjeta_metrica(titulo, valor, icono, bg_color, text_color, label_color, val_color):
    st.markdown(f"""
        {obtener_estilo_tarjeta_metrica(bg_color, label_color, val_color)}
            <div style="font-size: 2rem; margin-bottom: 10px;">{icono}</div>
            <div style="color: {label_color}; font-size: 0.9rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">{titulo}</div>
            <div style="color: {val_color}; font-size: 1.8rem; font-weight: 800; margin-top: 5px;">{valor}</div>
        </div>
    """, unsafe_allow_html=True)

def renderizar_tarjeta_producto(nombre, sabor, precio, stock, accent_color, text_color, text2_color, input_bg, border_color):
    st.markdown(f"""
        {obtener_estilo_tarjeta_producto(input_bg, border_color)}
            <div style="font-size: 3rem; margin-bottom: 15px;">🍨</div>
            <h3 style="color: {text_color}; margin: 0;">{nombre}</h3>
            <p style="color: {text2_color}; font-size: 1.1rem; margin-bottom: 15px;">{sabor}</p>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <span style="font-weight: bold; font-size: 1.2rem; color: {accent_color};">${precio}</span>
                <span style="color: {text2_color};">Stock: {stock}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
