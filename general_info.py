# general_info.py
import streamlit as st
import shared_state
import imported_data # <--- Loads Excel lists
from datetime import date

def render_general_info():
    # --- Header Section ---
    st.markdown("""
        <div style='background-color: white; padding: 15px; border-radius: 5px; border: 1px solid #ddd; margin-bottom: 20px;'>
            <h1 style='color: #E87722; text-align: center; font-size: 30px; margin:0;'>CAFI Mitigation Tool</h1>
            <p style='color: grey; text-align: center; margin:0; font-style: italic;'>
                Mirror of CMT v1.1 Excel Tool
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 0. Start / General Description")

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown("#### 📘 Project Description")
            st.text_input("User Name", key="gi_user_name", value=shared_state.get("gi_user_name") or "")
            st.date_input("Date", key="gi_date", value=date.today())
            st.text_input("Project Name", key="gi_project_name", value=shared_state.get("gi_project_name") or "")
            st.number_input("Project Cost (USD)", key="gi_project_cost", min_value=0, step=1000)
            st.text_input("Funding Agency", key="gi_funding_agency", value="CAFI")
            st.text_input("Executing Agency", key="gi_executing_agency")

    with col2:
        with st.container(border=True):
            st.markdown("#### 🌍 Project Site and Duration")
            
            # Region
            region_opts = ["Central Africa", "Indonesia", "Brazil"]
            curr_reg = shared_state.get("gi_region") or "Central Africa"
            region = st.selectbox("Region", region_opts, index=region_opts.index(curr_reg) if curr_reg in region_opts else 0)
            if region != shared_state.get("gi_region"): shared_state.set("gi_region", region)
            
            # Country
            if region == "Central Africa":
                c_options = ["Cameroon", "Central African Republic", "Republic of Congo", "Democratic Republic of the Congo", "Equatorial Guinea", "Gabon"]
            else:
                c_options = [region]
            
            country = st.selectbox("Country", c_options, key="gi_country_select")
            shared_state.set("gi_country", country)

            # DYNAMIC LISTS FROM EXCEL
            # We use the lists extracted by sync_excel.py
            st.selectbox("Climate", imported_data.CLIMATES, key="gi_climate")
            st.selectbox("Moisture", imported_data.MOISTURES, key="gi_moisture")
            st.selectbox("Soil Type", imported_data.SOIL_TYPES, key="gi_soil")

            st.divider()
            
            c1, c2 = st.columns(2)
            impl = c1.number_input("Implementation (yrs)", min_value=0, value=4, key="gi_impl_phase")
            cap = c2.number_input("Capitalization (yrs)", min_value=0, value=10, key="gi_cap_phase")
            st.info(f"**Total Duration:** {impl + cap} years")

    # Bottom Section (Activities)
    col3, col4 = st.columns(2)
    with col3:
        with st.container(border=True):
            st.markdown("#### ✅ Activities Reported")
            st.checkbox("1. Energy (Cookstoves, Fuel substitution)", key="check_energy")
            st.checkbox("2. Afforestation & Reforestation", key="check_arr")
            
            st.markdown("**3. Agriculture**")
            st.checkbox("3.1 Deforestation-free outgrower schemes", value=True, key="check_agri_3_1")
            st.checkbox("3.2 Agro-industrial plantations", value=True, key="check_agri_3_2")
            st.checkbox("3.3 Sustainable intensification", value=True, key="check_agri_3_3")
            
            st.checkbox("4. Forestry & Conservation", key="check_forest")

    with col4:
        with st.container(border=True):
            st.markdown("#### 📊 Summary")
            st.write("Mitigation potential for the following sectors:")
            
            if st.session_state.get("check_energy"): st.markdown("- Energy")
            if st.session_state.get("check_arr"): st.markdown("- Afforestation & Reforestation")
            if st.session_state.get("check_agri_3_1") or st.session_state.get("check_agri_3_2") or st.session_state.get("check_agri_3_3"):
                st.markdown("- Agriculture")
            if st.session_state.get("check_forest"): st.markdown("- Forestry & Conservation")
                
            st.divider()
            agri_total = shared_state.get("agri_grand_total") or 0.0
            st.metric("Total Emissions Reduction", f"{agri_total:,.2f} tCO2e")
