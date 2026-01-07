# app.py
import streamlit as st
import pandas as pd
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
    
    st.sidebar.title("Settings")
    # Soil Input
    soil_years = st.sidebar.number_input(
        "Soil Calculation Period (Years)", 
        min_value=1, 
        value=int(shared_state.get("soil_divisor") or 20), 
        step=1,
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
    agri.render_agri_module()

# --- TAB 4: Forestry ---
with tabs[4]:
    st.header("4. Forestry & Conservation")
    st.info("Forestry module coming soon...")

# --- TAB 5: Results ---
with tabs[5]:
    st.header("Results Summary")
    
    # Retrieve data safely. If it returns None, default to 0.0
    grand_total = shared_state.get("agri_grand_total") or 0.0
    results_data = shared_state.get("agri_results_table") or []
    
    # Display Metric
    col_metric, col_dummy = st.columns([1,3])
    col_metric.metric("Grand Total (tCO2e)", f"{grand_total:,.2f}")

    if results_data:
        st.subheader("Detailed Breakdown per Activity")
        df_res = pd.DataFrame(results_data)
        
        # Display Table
        st.dataframe(
            df_res, 
            column_config={
                "Emission Reduction": st.column_config.NumberColumn(format="%.2f"),
                "Ref AGB": st.column_config.NumberColumn(format="%.2f"),
                "Ref Soil": st.column_config.NumberColumn(format="%.2f"),
            },
            use_container_width=True
        )
        
        # Stacked Chart
        import plotly.express as px
        if "Section" in df_res.columns and "Emission Reduction" in df_res.columns:
            fig = px.bar(
                df_res, 
                x="Section", 
                y="Emission Reduction", 
                color="Crop", 
                title="Reductions by Crop System"
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No calculations performed yet. Go to the Agriculture tab and click 'Calculate Agriculture Emissions' to see results here.")