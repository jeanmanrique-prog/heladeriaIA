import streamlit as st

def render_header(titulo, subtitulo, text_color):
    st.markdown(f"""
        <div style="text-align: left; margin-bottom: 2rem;">
            <h1 style="color: {text_color}; margin-bottom: 0;">{titulo}</h1>
            <p style="color: {text_color}; opacity: 0.8; font-size: 1.2rem;">{subtitulo}</p>
        </div>
    """, unsafe_allow_html=True)
