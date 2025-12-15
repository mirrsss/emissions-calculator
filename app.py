# app.py
import streamlit as st
import shared_state
import agri

# 1. Page Config
st.set_page_config(page_title="Emissions Calculator", layout="wide")

# 2. Initialize Shared State
shared_state.init_state()

# 3. Sidebar (Global Inputs)
st.sidebar.title("Settings")

# --- Step 1: Select Region ---
region_options = ["Indonesia", "Brazil", "Central Africa"]
current_region_state = shared_state.get("gi_region")

# Default to Indonesia if state is empty/invalid
if current_region_state not in region_options:
    current_region_state = "Indonesia"

selected_region = st.sidebar.selectbox(
    "Region", 
    region_options,
    index=region_options.index(current_region_state),
    key="region_selector"
)

# --- Step 2: Select Country (Based on Region) ---
if selected_region == "Central Africa":
    country_options = [
        "Cameroon", 
        "Central African Republic", 
        "Republic of Congo", 
        "Democratic Republic of the Congo", 
        "Equatorial Guinea", 
        "Gabon"
    ]
else:
    # If Indonesia or Brazil is selected, the country is just the region name
    country_options = [selected_region]

# Helper to keep country selection stable if switching regions
current_country_state = shared_state.get("gi_country")
if current_country_state not in country_options:
    current_country_state = country_options[0]

selected_country = st.sidebar.selectbox(
    "Country", 
    country_options,
    index=country_options.index(current_country_state)
)

# Update Shared State
shared_state.set("gi_region", selected_region)
shared_state.set("gi_country", selected_country)

# --- Soil Inputs ---
soil_years = st.sidebar.number_input(
    "Soil Calculation Period (Years)", 
    min_value=1, 
    value=shared_state.get("soil_divisor")
)
shared_state.set("soil_divisor", soil_years)

# 4. Main App Logic
st.title("Emissions Reduction Calculator")
st.caption(f"Calculating for: {selected_country} ({selected_region})")

# Render Agriculture Module
agri.render_agri_module()