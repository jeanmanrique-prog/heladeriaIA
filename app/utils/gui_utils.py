import streamlit as st

def _container(**kwargs):
    """Contenedor compatible con diferentes versiones de Streamlit."""
    try:
        return st.container(**kwargs)
    except TypeError:
        # Fallback para versiones antiguas que no soportan todos los kwargs
        fallback = {}
        if "border" in kwargs:
            fallback["border"] = kwargs["border"]
        if "height" in kwargs:
            fallback["height"] = kwargs["height"]
        return st.container(**fallback)
