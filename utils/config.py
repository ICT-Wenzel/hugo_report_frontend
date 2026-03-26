import os
import streamlit as st

def get_config(key: str, default=None):
    # 1. Versuche, aus Umgebungsvariablen zu lesen
    value = os.getenv(key)
    if value is not None:
        return value
    # 2. Versuche, aus streamlit secrets zu lesen
    if hasattr(st, "secrets") and key in st.secrets:
        return st.secrets[key]
    # 3. Fallback
    return default