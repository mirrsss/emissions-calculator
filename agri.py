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
# 1. HELPER FUNCTIONS
# -----------------------------

CENTRAL_AFRICA_COUNTRIES = [
    "Cameroon", "Central African Republic", "Republic of Congo", 
    "Democratic Republic of the Congo", "Equatorial Guinea", "Gabon"
]

def resolve_region(country):
    if country in ["Indonesia", "Brazil"]: return country
    if country in CENTRAL_AFRICA_COUNTRIES: return "Central Africa"
    return "Central Africa"

def get_region_params(country):
    region_key = resolve_region(country)
    return {
        "agb_bgb_soil": DEFAULT_AGB_BGB_SOIL_BY_REGION[region_key],
        "removal_factors": REMOVAL_FACTORS_BY_REGION[region_key],
        "residue_multiplier": RESIDUE_MULTIPLIER_BY_REGION[region_key]
    }

def safe_get(value):
    if isinstance(value, list):
        return value[0] if len(value) > 0 else None
    return value

def safe_float(value):
    val = safe_get(value)
    try: return float(val)
    except: return 0.0

def compute_row_ghg(row, params, soil_divisor):
    """Calculates GHG and returns dictionary with details for results."""
    agb_bgb_soil = params["agb_bgb_soil"]
    removal_factors = params["removal_factors"]
    residue_multiplier = params["residue_multiplier"]

    # 1. Clean Inputs
    crop = safe_get(row["Crop System"])
    tillage_opt = safe_get(row["Tillage"])
    inputs_opt = safe_get(row["Inputs"])
    residue_opt = safe_get(row["Residue"])
    area = safe_float(row["Area (ha)"])

    # 2. Defaults
    agb_def, bgb_def, soil_def = agb_bgb_soil.get(crop, (0,0,0))
    
    # 3. Local Overrides
    agb = safe_float(row["Local AGB"]) if safe_float(row["Local AGB"]) > 0 else agb_def
    bgb = safe_float(row["Local BGB"]) if safe_float(row["Local BGB"]) > 0 else bgb_def
    soil = safe_float(row["Local Soil"]) if safe_float(row["Local Soil"]) > 0 else soil_def
    
    # 4. Factors
    tillage_val = safe_float(row["Local Tillage Factor"]) if safe_float(row["Local Tillage Factor"]) > 0 else removal_factors["tillage"].get(tillage_opt, 0)
    input_val = safe_float(row["Local Input Factor"]) if safe_float(row["Local Input Factor"]) > 0 else removal_factors["input"].get(inputs_opt, 0)
    residue_val = safe_float(row["Local Residue Factor"]) if safe_float(row["Local Residue Factor"]) > 0 else removal_factors["residue"].get(residue_opt, 0)

    # 5. Calculation
    carbon_biomass = (agb * 3.664 + bgb * 3.664) * area
    soil_term = (soil / soil_divisor) * tillage_val * input_val
    residue_term = residue_val * residue_multiplier * 3.664
    
    total = round(carbon_biomass + soil_term - residue_term, 2)
    
    return total, {
        "agb_used": agb, "bgb_used": bgb, "soil_used": soil,
        "tillage_factor": tillage_val, "input_factor": input_val
    }

# -----------------------------
# 2. UI RENDER
# -----------------------------

def render_agri_module():
    st.header("3. Agriculture Emissions")
    
    country = shared_state.get("gi_country")
    soil_divisor = shared_state.get("soil_divisor")
    params = get_region_params(country)

    crop_options = list(params["agb_bgb_soil"].keys()) # "Tea" is now here
    tillage_options = list(params["removal_factors"]["tillage"].keys())
    input_options = list(params["removal_factors"]["input"].keys())
    residue_options = list(params["removal_factors"]["residue"].keys())

    st.info("ℹ️ **Defaults:** Columns starting with 'Ref' show the default CAFI factor for the selected crop. Enter values in 'Local' columns to override them.")

    # UPDATED TABS TO MATCH CAFI TITLES
    tab1, tab2, tab3 = st.tabs([
        "3.1 Deforestation-free Outgrower", 
        "3.2 Agro-industrial", 
        "3.3 Sustainable Intensification"
    ])

    def render_data_editor(key_name):
        if key_name not in st.session_state:
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
                "Crop System": st.column_config.SelectboxColumn("Crop System", options=crop_options, required=True),
                "Area (ha)": st.column_config.NumberColumn("Area (ha)", min_value=0.0, step=0.1, required=True),
                "Tillage": st.column_config.SelectboxColumn("Tillage Practice", options=tillage_options, required=True),
                "Inputs": st.column_config.SelectboxColumn("Input Level", options=input_options, required=True),
                "Residue": st.column_config.SelectboxColumn("Residue Mgmt", options=residue_options, required=True),
                
                # EXPLICIT LOCAL DATA COLUMNS
                "Local AGB": st.column_config.NumberColumn("Local AGB (tC/ha)", default=0.0, help="Override default AGB"),
                "Local BGB": st.column_config.NumberColumn("Local BGB (tC/ha)", default=0.0, help="Override default BGB"),
                "Local Soil": st.column_config.NumberColumn("Local Soil (tC/ha)", default=0.0, help="Override default Soil Carbon"),
            },
            use_container_width=True
        )

    with tab1:
        st.caption("Deforestation-free outgrower schemes")
        df_3_1 = render_data_editor("df_3_1")
    with tab2:
        st.caption("Agro-industrial plantations")
        df_3_2 = render_data_editor("df_3_2")
    with tab3:
        st.caption("Sustainable intensification")
        df_3_3 = render_data_editor("df_3_3")

    st.divider()

    if st.button("Calculate Agriculture Emissions", type="primary"):
        chart_rows = []
        
        def process_section(df, section_name):
            total = 0
            for _, row in df.iterrows():
                if safe_get(row["Crop System"]):
                    val, details = compute_row_ghg(row, params, soil_divisor)
                    total += val
                    # Add row to results table
                    chart_rows.append({
                        "Section": section_name,
                        "Crop": safe_get(row["Crop System"]),
                        "Area": safe_float(row["Area (ha)"]),
                        "Ref AGB": details["agb_used"], # Showing the factor used
                        "Ref Soil": details["soil_used"],
                        "Emission Reduction": val
                    })
            return total

        t1 = process_section(df_3_1, "3.1 Outgrower")
        t2 = process_section(df_3_2, "3.2 Agro-industrial")
        t3 = process_section(df_3_3, "3.3 Intensification")
        
        grand_total = t1 + t2 + t3
        shared_state.set("agri_grand_total", grand_total)
        shared_state.set("agri_results_table", chart_rows) # Save detailed results for the Results Tab
        
        st.success("Calculations updated!")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("3.1 Outgrower", f"{t1:,.2f}")
        c2.metric("3.2 Agro-ind", f"{t2:,.2f}")
        c3.metric("3.3 Intensif", f"{t3:,.2f}")
        c4.metric("TOTAL", f"{grand_total:,.2f}")