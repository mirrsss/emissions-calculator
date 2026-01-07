# shared_state.py
import streamlit as st
from datetime import date

def init_state():
    """
    Initializes the session state variables if they don't exist.
    """
    defaults = {
        # General Info - Project Details
        "gi_user_name": "",
        "gi_date": date.today(),
        "gi_project_name": "",
        "gi_project_cost": 0,
        "gi_funding_agency": "CAFI",
        "gi_executing_agency": "",
        
        # General Info - Site Details
        "gi_region": "Central Africa",
        "gi_country": "Cameroon", 
        "gi_climate": "Tropical montane",
        "gi_moisture": "Moist",
        "gi_soil": "Spodic soils",
        "gi_impl_phase": 4,
        "gi_cap_phase": 10,

        # Activity Checkboxes
        "check_energy": False,
        "check_arr": False,
        "check_agri": True,
        "check_forest": False,
        
        # Agri Logic State
        "soil_divisor": 20,
        "agri_grand_total": 0.0,      # <--- ADDED THIS (Fixes the crash)
        "agri_results_table": [],     # <--- ADDED THIS
        
        # Keep individual totals just in case
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