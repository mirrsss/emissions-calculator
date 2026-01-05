# app.py
import streamlit as st
import shared_state
import general_info
import agri

# 1. Page Config
st.set_page_config(page_title="CAFI Mitigation Tool", layout="wide")

# 2. Initialize Shared State
shared_state.init_state()

# 3. Create Top Navigation Tabs
tabs = st.tabs([
    "0 Start", 
    "1 Energy", 
    "2 Afforestation & Reforestation", 
    "3 Agriculture", 
    "4 Forestry & Conservation", 
    "Results"
])

# --- TAB 0: Start / Landing Page ---
with tabs[0]:
    general_info.render_general_info()

    # Move Soil Input here or keep in Sidebar? 
    # Based on your previous setup, it was in the sidebar, but we can put it here or generally available.
    # Let's keep a global settings expander or sidebar for this specific math param if you prefer.
    # For now, I will keep the sidebar logic here as it persists across tabs.
    
    st.sidebar.title("Settings")
    
    # Soil Input - FIXED with step=1 to prevent erratic behavior
    soil_years = st.sidebar.number_input(
        "Soil Calculation Period (Years)", 
        min_value=1, 
        value=int(shared_state.get("soil_divisor")), 
        step=1,  # <--- THIS FIXES THE +/- ISSUE
        help="The time period over which soil carbon changes are calculated (default 20 years)."
    )
    shared_state.set("soil_divisor", soil_years)

# --- TAB 1: Energy ---
with tabs[1]:
    st.header("1. Energy")
    st.info("Energy module coming soon...")

# --- TAB 2: ARR ---
with tabs[2]:
    st.header("2. Afforestation & Reforestation")
    st.info("ARR module coming soon...")

# --- TAB 3: Agriculture ---
with tabs[3]:
    # We load the Agri module
    agri.render_agri_module()

# --- TAB 4: Forestry ---
with tabs[4]:
    st.header("4. Forestry & Conservation")
    st.info("Forestry module coming soon...")

# --- TAB 5: Results ---
with tabs[5]:
    st.header("Results Summary")
    
    # Recalculate totals to be safe
    t1 = shared_state.get("agri_3_1_total")
    t2 = shared_state.get("agri_3_2_total")
    t3 = shared_state.get("agri_3_3_total")
    total_agri = t1 + t2 + t3
    
    st.metric("Total Agriculture Reduction", f"{total_agri:,.2f} tCO2e")