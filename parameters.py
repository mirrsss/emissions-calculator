# parameters.py
import imported_data  # <--- Loads the data extracted from Excel

# --- Agriculture Parameters ---

RESIDUE_MULTIPLIER_BY_REGION = {
    "Central Africa": 0.47, 
    "Indonesia": 0.47, 
    "Brazil": 0.47
}

# Use the exact list from the Excel file
DEFAULT_AGB_BGB_SOIL_BY_REGION = {
    "Central Africa": imported_data.AGRI_CROP_DATA,
    "Indonesia": imported_data.AGRI_CROP_DATA,
    "Brazil": imported_data.AGRI_CROP_DATA
}

REMOVAL_FACTORS_BY_REGION = {
    region: {
        "tillage": {"Full tillage": 1, "Reduced tillage": 1.04, "No tillage": 1.1},
        "input": {
            "Low C input": 0.92,
            "Medium C input": 1,
            "High C input, no manure": 1.11,
            "High C input, with manure": 1.44,
        },
        "residue": {"Burned": 2.26, "Retained": 2.26, "Exported": 2.26},
    }
    for region in ["Central Africa", "Indonesia", "Brazil"]
}
