import streamlit as st

def render_metric_card(titulo, valor, icono, bg_color, text_color, label_color, val_color):
    st.markdown(f"""
        <div style="background-color: {bg_color}; padding: 20px; border-radius: 15px; border: 1px solid rgba(0,0,0,0.05); text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 10px;">{icono}</div>
            <div style="color: {label_color}; font-size: 0.9rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">{titulo}</div>
            <div style="color: {val_color}; font-size: 1.8rem; font-weight: 800; margin-top: 5px;">{valor}</div>
        </div>
    """, unsafe_allow_html=True)

def render_product_card(nombre, sabor, precio, stock, accent_color, text_color, text2_color, input_bg, border_color):
    st.markdown(f"""
        <div style="background-color: {input_bg}; border-radius: 15px; padding: 20px; text-align: center; border: 1px solid {border_color}; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 20px;">
            <div style="font-size: 3rem; margin-bottom: 15px;">🍨</div>
            <h3 style="color: {text_color}; margin: 0;">{nombre}</h3>
            <p style="color: {text2_color}; font-size: 1.1rem; margin-bottom: 15px;">{sabor}</p>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <span style="font-weight: bold; font-size: 1.2rem; color: {accent_color};">${precio}</span>
                <span style="color: {text2_color};">Stock: {stock}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
