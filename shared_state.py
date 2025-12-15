# shared_state.py
import streamlit as st

def init_state():
    """
    Initializes the session state variables if they don't exist.
    """
    defaults = {
        # General Settings
        "gi_region": "Indonesia",   # <--- ADDED THIS LINE
        "gi_country": "Indonesia", 
        "soil_divisor": 20,
        
        # Agri Logic State
        "agri_3_1_total": 0.0,
        "agri_3_2_total": 0.0,
        "agri_3_3_total": 0.0,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def get(key):
    return st.session_state.get(key)

def set(key, value):
    st.session_state[key] = value