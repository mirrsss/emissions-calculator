# app.py
import streamlit as st
import shared_state
import general_info  # The new dashboard file
import agri          # The agriculture module

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
    # We load the Agri module we already built
    agri.render_agri_module()

# --- TAB 4: Forestry ---
with tabs[4]:
    st.header("4. Forestry & Conservation")
    st.info("Forestry module coming soon...")

# --- TAB 5: Results ---
with tabs[5]:
    st.header("Results Summary")
    # Simple summary for now
    total_agri = shared_state.get("agri_3_1_total") + shared_state.get("agri_3_2_total") + shared_state.get("agri_3_3_total")
    st.metric("Total Agriculture Reduction", f"{total_agri:,.2f} tCO2e")