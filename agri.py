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
    if country in ["Indonesia", "Brazil"]:
        return country
    if country in CENTRAL_AFRICA_COUNTRIES:
        return "Central Africa"
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
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0

def compute_row_ghg(row, params, soil_divisor):
    """Calculates GHG for a single row of data."""
    agb_bgb_soil = params["agb_bgb_soil"]
    removal_factors = params["removal_factors"]
    residue_multiplier = params["residue_multiplier"]

    # 1. Clean Inputs
    crop = safe_get(row["Crop System"])
    tillage_opt = safe_get(row["Tillage"])
    inputs_opt = safe_get(row["Inputs"])
    residue_opt = safe_get(row["Residue"])
    
    # 2. Clean Numerics
    area = safe_float(row["Area (ha)"])
    local_agb = safe_float(row["Local AGB"])
    local_bgb = safe_float(row["Local BGB"])
    local_soil = safe_float(row["Local Soil"])
    local_tillage = safe_float(row["Local Tillage Factor"])
    local_input = safe_float(row["Local Input Factor"])
    local_residue = safe_float(row["Local Residue Factor"])

    # Defaults
    agb_default, bgb_default, soil_default = agb_bgb_soil.get(crop, (0,0,0))
    
    # Logic: Use Local override if > 0, else Default
    agb = local_agb if local_agb > 0 else agb_default
    bgb = local_bgb if local_bgb > 0 else bgb_default
    soil = local_soil if local_soil > 0 else soil_default
    
    tillage_val = local_tillage if local_tillage > 0 else removal_factors["tillage"].get(tillage_opt, 0)
    input_val = local_input if local_input > 0 else removal_factors["input"].get(inputs_opt, 0)
    residue_val = local_residue if local_residue > 0 else removal_factors["residue"].get(residue_opt, 0)

    # Formula
    carbon_biomass = (agb * 3.664 + bgb * 3.664) * area
    soil_term = (soil / soil_divisor) * tillage_val * input_val
    residue_term = residue_val * residue_multiplier * 3.664
    
    return round(carbon_biomass + soil_term - residue_term, 2)

# -----------------------------
# 2. STREAMLIT UI COMPONENT
# -----------------------------

def render_agri_module():
    st.header("3. Agriculture Emissions")
    
    # Inputs
    country = shared_state.get("gi_country")
    soil_divisor = shared_state.get("soil_divisor")
    params = get_region_params(country)

    crop_options = list(params["agb_bgb_soil"].keys())
    tillage_options = list(params["removal_factors"]["tillage"].keys())
    input_options = list(params["removal_factors"]["input"].keys())
    residue_options = list(params["removal_factors"]["residue"].keys())

    # Explain optional values
    st.info("ℹ️ **Note on Defaults:** Columns labeled **'(Optional Override)'** are for advanced users. Leave them as **0** to use the standard default values for your selected Region and Crop System.")

    tab1, tab2, tab3 = st.tabs(["3.1 Outgrower", "3.2 Agro-industrial", "3.3 Intensification"])

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
                "Crop System": st.column_config.SelectboxColumn(
                    label="Crop System (Action)",
                    options=crop_options, 
                    required=True,
                    help="Select the type of agricultural activity."
                ),
                "Area (ha)": st.column_config.NumberColumn(
                    label="Area (ha)",
                    min_value=0.0, step=0.1, required=True,
                    help="Total land area for this activity."
                ),
                "Tillage": st.column_config.SelectboxColumn(
                    label="Tillage Practice",
                    options=tillage_options, required=True,
                    help="Select the intensity of soil tillage."
                ),
                "Inputs": st.column_config.SelectboxColumn(
                    label="Input Level",
                    options=input_options, required=True,
                    help="Level of organic/inorganic inputs."
                ),
                "Residue": st.column_config.SelectboxColumn(
                    label="Residue Mgmt",
                    options=residue_options, required=True,
                    help="How crop residues are handled (Burned, Retained, etc.)"
                ),
                # OPTIONAL OVERRIDES
                "Local AGB": st.column_config.NumberColumn(
                    label="AGB Override (tC/ha)", default=0.0,
                    help="Optional: Above Ground Biomass. Leave 0 to use default."
                ),
                "Local BGB": st.column_config.NumberColumn(
                    label="BGB Override (tC/ha)", default=0.0,
                    help="Optional: Below Ground Biomass. Leave 0 to use default."
                ),
                "Local Soil": st.column_config.NumberColumn(
                    label="Soil Override (tC/ha)", default=0.0,
                    help="Optional: Soil Organic Carbon. Leave 0 to use default."
                ),
                "Local Tillage Factor": st.column_config.NumberColumn(label="Tillage Factor (Override)", default=0.0),
                "Local Input Factor": st.column_config.NumberColumn(label="Input Factor (Override)", default=0.0),
                "Local Residue Factor": st.column_config.NumberColumn(label="Residue Factor (Override)", default=0.0),
            },
            use_container_width=True
        )

    with tab1:
        st.caption("Enter data for Outgrower Schemes")
        df_3_1 = render_data_editor("df_3_1")
    with tab2:
        st.caption("Enter data for Agro-industrial Plantations")
        df_3_2 = render_data_editor("df_3_2")
    with tab3:
        st.caption("Enter data for Intensification")
        df_3_3 = render_data_editor("df_3_3")

    st.divider()

    if st.button("Calculate Agriculture Emissions", type="primary"):
        # Helper to process rows and prepare stack chart data
        chart_rows = []
        
        def process_section(df, section_name):
            total = 0
            for _, row in df.iterrows():
                if safe_get(row["Crop System"]): # Only if crop selected
                    val = compute_row_ghg(row, params, soil_divisor)
                    total += val
                    # Add to chart data
                    chart_rows.append({
                        "Section": section_name,
                        "Action (Crop System)": safe_get(row["Crop System"]),
                        "Emissions Reduction (tCO2e)": val
                    })
            return total

        total_3_1 = process_section(df_3_1, "3.1 Outgrower")
        total_3_2 = process_section(df_3_2, "3.2 Agro-industrial")
        total_3_3 = process_section(df_3_3, "3.3 Intensification")
        
        # Save totals
        shared_state.set("agri_3_1_total", total_3_1)
        shared_state.set("agri_3_2_total", total_3_2)
        shared_state.set("agri_3_3_total", total_3_3)
        
        grand_total = total_3_1 + total_3_2 + total_3_3
        st.success("Calculations updated!")

        # --- RESULTS & STACKED CHART ---
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("3.1 Outgrower", f"{total_3_1:,.2f}")
        c2.metric("3.2 Agro-industrial", f"{total_3_2:,.2f}")
        c3.metric("3.3 Intensification", f"{total_3_3:,.2f}")
        c4.metric("TOTAL (tCO2e)", f"{grand_total:,.2f}")

        if chart_rows:
            chart_df = pd.DataFrame(chart_rows)
            
            # STACKED BAR CHART
            fig = px.bar(
                chart_df, 
                x="Section", 
                y="Emissions Reduction (tCO2e)", 
                color="Action (Crop System)", # <--- THIS CREATES THE STACKS
                title="Emissions Reduction Breakdown by Intervention & Action",
                text_auto='.2s'
            )
            fig.update_layout(xaxis_title="", yaxis_title="tCO2e Reduction")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Add data to see the breakdown chart.")