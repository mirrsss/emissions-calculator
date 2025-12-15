# agri.py
import pandas as pd
import streamlit as st
import plotly.express as px
from parameters import (
    DEFAULT_AGB_BGB_SOIL_BY_REGION, 
    REMOVAL_FACTORS_BY_REGION, 
    RESIDUE_MULTIPLIER_BY_REGION
)
import shared_state

# -----------------------------
# 1. HELPER FUNCTIONS & LOGIC
# -----------------------------

CENTRAL_AFRICA_COUNTRIES = [
    "Cameroon", 
    "Central African Republic", 
    "Republic of Congo", 
    "Democratic Republic of the Congo", 
    "Equatorial Guinea", 
    "Gabon"
]

def resolve_region(country):
    """
    Maps a specific country to its broader region parameters.
    """
    if country in ["Indonesia", "Brazil"]:
        return country
    # If it's one of the CA countries, return the region key
    if country in CENTRAL_AFRICA_COUNTRIES:
        return "Central Africa"
    # Default fallback
    return "Central Africa"

def get_region_params(country):
    region_key = resolve_region(country)
    return {
        "agb_bgb_soil": DEFAULT_AGB_BGB_SOIL_BY_REGION[region_key],
        "removal_factors": REMOVAL_FACTORS_BY_REGION[region_key],
        "residue_multiplier": RESIDUE_MULTIPLIER_BY_REGION[region_key]
    }

def safe_get(value):
    """
    Safety function: The data editor sometimes returns values as a list [val] 
    instead of just val. This extracts the actual item.
    """
    if isinstance(value, list):
        return value[0] if len(value) > 0 else None
    return value

def safe_float(value):
    """
    Converts input to float, handling lists, None, or strings safely.
    Fixes the TypeError: '>' not supported between instances of 'list' and 'int'
    """
    val = safe_get(value)
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0

def compute_row_ghg(row, params, soil_divisor):
    """Calculates GHG for a single row of data."""
    agb_bgb_soil = params["agb_bgb_soil"]
    removal_factors = params["removal_factors"]
    residue_multiplier = params["residue_multiplier"]

    # 1. Clean up Text Inputs
    crop = safe_get(row["Crop System"])
    tillage_opt = safe_get(row["Tillage"])
    inputs_opt = safe_get(row["Inputs"])
    residue_opt = safe_get(row["Residue"])

    # 2. Clean up Numeric Inputs (The fix for your error)
    area = safe_float(row["Area (ha)"])
    local_agb = safe_float(row["Local AGB"])
    local_bgb = safe_float(row["Local BGB"])
    local_soil = safe_float(row["Local Soil"])
    local_tillage = safe_float(row["Local Tillage Factor"])
    local_input = safe_float(row["Local Input Factor"])
    local_residue = safe_float(row["Local Residue Factor"])

    # Defaults from Parameters
    agb_default, bgb_default, soil_default = agb_bgb_soil.get(crop, (0,0,0))
    
    # Logic: Use Local override if > 0, else Default
    agb = local_agb if local_agb > 0 else agb_default
    bgb = local_bgb if local_bgb > 0 else bgb_default
    soil = local_soil if local_soil > 0 else soil_default
    
    # Get Factor values
    tillage_val = local_tillage if local_tillage > 0 else removal_factors["tillage"].get(tillage_opt, 0)
    input_val = local_input if local_input > 0 else removal_factors["input"].get(inputs_opt, 0)
    residue_val = local_residue if local_residue > 0 else removal_factors["residue"].get(residue_opt, 0)

    # Math Formula
    carbon_biomass = (agb * 3.664 + bgb * 3.664) * area
    soil_term = (soil / soil_divisor) * tillage_val * input_val
    residue_term = residue_val * residue_multiplier * 3.664
    
    return round(carbon_biomass + soil_term - residue_term, 2)

# -----------------------------
# 2. STREAMLIT UI COMPONENT
# -----------------------------

def render_agri_module():
    """Renders the Agriculture calculator interface."""
    
    st.header("3. Agriculture Emissions")
    
    # Get Shared State inputs
    country = shared_state.get("gi_country")
    soil_divisor = shared_state.get("soil_divisor")
    
    # Lookup parameters based on the specific country -> region mapping
    params = get_region_params(country)

    # Setup Dropdown Options
    crop_options = list(params["agb_bgb_soil"].keys())
    tillage_options = list(params["removal_factors"]["tillage"].keys())
    input_options = list(params["removal_factors"]["input"].keys())
    residue_options = list(params["removal_factors"]["residue"].keys())

    # Tabs
    tab1, tab2, tab3 = st.tabs(["3.1 Outgrower", "3.2 Agro-industrial", "3.3 Intensification"])

    def render_data_editor(key_name):
        # Helper to create the input grid
        if key_name not in st.session_state:
            # Initialize empty DF with columns
            st.session_state[key_name] = pd.DataFrame(columns=[
                "Crop System", "Area (ha)", "Tillage", "Inputs", "Residue",
                "Local AGB", "Local BGB", "Local Soil", 
                "Local Tillage Factor", "Local Input Factor", "Local Residue Factor"
            ])
            
        return st.data_editor(
            st.session_state[key_name],
            key=f"editor_{key_name}",
            num_rows="dynamic",
            column_config={
                "Crop System": st.column_config.SelectboxColumn(options=crop_options, required=True),
                "Tillage": st.column_config.SelectboxColumn(options=tillage_options, required=True),
                "Inputs": st.column_config.SelectboxColumn(options=input_options, required=True),
                "Residue": st.column_config.SelectboxColumn(options=residue_options, required=True),
                "Area (ha)": st.column_config.NumberColumn(min_value=0.0, step=0.1),
                "Local AGB": st.column_config.NumberColumn(default=0.0),
                "Local BGB": st.column_config.NumberColumn(default=0.0),
                "Local Soil": st.column_config.NumberColumn(default=0.0),
            },
            use_container_width=True
        )

    # Render grids
    with tab1:
        st.caption("Enter data for Outgrower Schemes")
        df_3_1 = render_data_editor("df_3_1")
    with tab2:
        st.caption("Enter data for Agro-industrial Plantations")
        df_3_2 = render_data_editor("df_3_2")
    with tab3:
        st.caption("Enter data for Intensification")
        df_3_3 = render_data_editor("df_3_3")

    # --- Calculation Trigger ---
    if st.button("Calculate Agriculture Emissions", type="primary"):
        # We add a check 'if row["Crop System"]' to ensure we don't calculate empty rows
        total_3_1 = sum(compute_row_ghg(row, params, soil_divisor) for _, row in df_3_1.iterrows() if safe_get(row["Crop System"]))
        total_3_2 = sum(compute_row_ghg(row, params, soil_divisor) for _, row in df_3_2.iterrows() if safe_get(row["Crop System"]))
        total_3_3 = sum(compute_row_ghg(row, params, soil_divisor) for _, row in df_3_3.iterrows() if safe_get(row["Crop System"]))
        
        # Save to shared state
        shared_state.set("agri_3_1_total", total_3_1)
        shared_state.set("agri_3_2_total", total_3_2)
        shared_state.set("agri_3_3_total", total_3_3)
        
        st.success("Calculations updated!")

    # --- Results Display ---
    t1 = shared_state.get("agri_3_1_total")
    t2 = shared_state.get("agri_3_2_total")
    t3 = shared_state.get("agri_3_3_total")
    grand_total = t1 + t2 + t3

    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("3.1 Outgrower", f"{t1:,.2f}")
    c2.metric("3.2 Agro-industrial", f"{t2:,.2f}")
    c3.metric("3.3 Intensification", f"{t3:,.2f}")
    c4.metric("TOTAL (tCO2e)", f"{grand_total:,.2f}")

    # Plot
    if grand_total > 0:
        chart_data = pd.DataFrame({
            "Source": ["Outgrower", "Agro-industrial", "Intensification"],
            "Value": [t1, t2, t3]
        })
        fig = px.bar(chart_data, x="Source", y="Value", title="Emissions Reduction by Sub-module")
        st.plotly_chart(fig, use_container_width=True)