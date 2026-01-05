# general_info.py
import streamlit as st
import shared_state
from datetime import date

def render_general_info():
    # --- Header Section ---
    st.markdown("""
        <div style='background-color: white; padding: 15px; border-radius: 5px; border: 1px solid #ddd; margin-bottom: 20px;'>
            <h1 style='color: #E87722; text-align: center; font-size: 30px; margin:0;'>CAFI Mitigation Tool</h1>
            <p style='color: grey; text-align: center; margin:0; font-style: italic;'>
                A tool for ex-ante and post-ante estimation of the mitigation potential of projects funded by CAFI
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 0. Start / General Description")

    # --- Top Section: Two Columns (Project Info & Site Info) ---
    col1, col2 = st.columns(2)

    # LEFT COLUMN: Project Name & Details
    with col1:
        with st.container(border=True):
            st.markdown("#### 📘 Project Description")
            
            # Using session state callbacks to save data immediately
            st.text_input("User Name", key="gi_user_name")
            st.date_input("Date", key="gi_date")
            st.text_input("Project Name", key="gi_project_name")
            st.number_input("Project Cost (USD)", key="gi_project_cost", min_value=0, step=1000)
            st.text_input("Funding Agency", key="gi_funding_agency")
            st.text_input("Executing Agency", key="gi_executing_agency")

    # RIGHT COLUMN: Site & Duration
    with col2:
        with st.container(border=True):
            st.markdown("#### 🌍 Project Site and Duration")
            
            # Region/Country Selection
            region_opts = ["Central Africa", "Indonesia", "Brazil"]
            
            # Ensure valid index for region
            curr_reg = shared_state.get("gi_region")
            reg_idx = region_opts.index(curr_reg) if curr_reg in region_opts else 0
            
            region = st.selectbox("Region", region_opts, index=reg_idx, key="region_selector")
            # Update state manually if changed
            if region != shared_state.get("gi_region"):
                shared_state.set("gi_region", region)
            
            # Country Logic based on Region
            if region == "Central Africa":
                c_options = ["Cameroon", "Central African Republic", "Republic of Congo", "Democratic Republic of the Congo", "Equatorial Guinea", "Gabon"]
            else:
                c_options = [region]
            
            # Ensure valid index for country
            curr_country = shared_state.get("gi_country")
            c_idx = c_options.index(curr_country) if curr_country in c_options else 0

            country = st.selectbox("Country", c_options, index=c_idx, key="country_selector")
            if country != shared_state.get("gi_country"):
                shared_state.set("gi_country", country)

            # Other Inputs
            st.selectbox("Climate", ["Tropical montane", "Tropical wet", "Tropical dry"], key="gi_climate")
            st.selectbox("Moisture", ["Moist", "Wet", "Dry"], key="gi_moisture")
            st.selectbox("Soil Type", ["Spodic soils", "Volcanic soils", "Clay soils", "Sandy soils"], key="gi_soil")

            st.divider()
            
            # Durations
            c1, c2 = st.columns(2)
            impl = c1.number_input("Implementation (yrs)", min_value=0, value=4, key="gi_impl_phase")
            cap = c2.number_input("Capitalization (yrs)", min_value=0, value=10, key="gi_cap_phase")
            st.info(f"**Total Duration:** {impl + cap} years")

    # --- Bottom Section: Activities & Summary ---
    col3, col4 = st.columns(2)

    # LEFT: Activities Reported (Checkboxes)
    with col3:
        with st.container(border=True):
            st.markdown("#### ✅ Activities Reported")
            st.caption("Select the sectors involved in this project:")
            
            st.checkbox("1. Energy (Cookstoves, Fuel substitution)", key="check_energy")
            st.checkbox("2. Afforestation & Reforestation", key="check_arr")
            st.checkbox("3. Agriculture (Outgrower, Intensification)", value=True, key="check_agri") 
            st.checkbox("4. Forestry & Conservation", key="check_forest")

    # RIGHT: Summary
    with col4:
        with st.container(border=True):
            st.markdown("#### 📊 Summary")
            st.write("Mitigation potential for the following sectors:")
            
            if st.session_state.get("check_energy"):
                st.markdown("- (i) Energy")
            if st.session_state.get("check_arr"):
                st.markdown("- (ii) Afforestation & Reforestation")
            if st.session_state.get("check_agri"):
                st.markdown("- (iii) Agriculture")
            if st.session_state.get("check_forest"):
                st.markdown("- (iv) Forestry & Conservation")
                
            st.divider()
            agri_total = shared_state.get("agri_3_1_total") + shared_state.get("agri_3_2_total") + shared_state.get("agri_3_3_total")
            st.metric("Total Emissions Reduction (So Far)", f"{agri_total:,.2f} tCO2e")