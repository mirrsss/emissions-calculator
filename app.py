# app.py
import streamlit as st
import pandas as pd
import shared_state
import general_info
import agri

st.set_page_config(page_title="CAFI Mitigation Tool", layout="wide")
shared_state.init_state()

tabs = st.tabs([
    "0 Start", 
    "1 Energy", 
    "2 Afforestation & Reforestation", 
    "3 Agriculture", 
    "4 Forestry & Conservation", 
    "Results"
])

with tabs[0]:
    general_info.render_general_info()
    st.sidebar.title("Settings")
    soil_years = st.sidebar.number_input(
        "Soil Calculation Period (Years)", 
        min_value=1, value=int(shared_state.get("soil_divisor")), step=1,
        help="Time period for soil carbon changes (default 20)."
    )
    shared_state.set("soil_divisor", soil_years)

with tabs[1]:
    st.header("1. Energy")
    st.info("Coming soon...")

with tabs[2]:
    st.header("2. Afforestation & Reforestation")
    st.info("Coming soon...")

with tabs[3]:
    agri.render_agri_module()

with tabs[4]:
    st.header("4. Forestry & Conservation")
    st.info("Coming soon...")

with tabs[5]:
    st.header("Results Summary")
    
    # Detailed Breakdown Table (The "Missing Info" fix)
    results_data = shared_state.get("agri_results_table")
    grand_total = shared_state.get("agri_grand_total")
    
    col_metric, col_dummy = st.columns([1,3])
    col_metric.metric("Grand Total (tCO2e)", f"{grand_total:,.2f}")

    if results_data:
        st.subheader("Detailed Breakdown per Activity")
        df_res = pd.DataFrame(results_data)
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
        fig = px.bar(df_res, x="Section", y="Emission Reduction", color="Crop", title="Reductions by Crop System")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No calculations performed yet. Go to the Agriculture tab and click 'Calculate'.")