# parameters.py

# --- Agriculture Parameters ---

RESIDUE_MULTIPLIER_BY_REGION = {
    "Central Africa": 0.47, 
    "Indonesia": 0.47, 
    "Brazil": 0.47
}

DEFAULT_AGB_BGB_SOIL_BY_REGION = {
    region: {
        "Alley cropping": (2.75, 0.59, 27.3),
        "Hedgerow": (0.47, 0.11, 27.3),
        "Multistrata": (2.98, 0.72, 27.3),
        "Parkland": (0.59, 0.21, 27.3),
        "Perennial fallow": (5.3, 1.27, 27.3),
        "Shaded perennial": (1.82, 0.44, 27.3),
        "Silvopasture": (2.91, 0.79, 27.3),
        "Silvoarable": (5.09, 1.22, 27.3),
    }
    for region in ["Central Africa", "Indonesia", "Brazil"]
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