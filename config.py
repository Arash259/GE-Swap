"""
config.py - Global configuration and material parameters.
"""

PHYSICAL_CONSTANTS = {
    'e': 1.602e-19,
    'k_B': 1.380649e-23,
    'N_A': 6.02214076e23,
    'T': 300.0,
}

MATERIAL_PARAMS = {
    'TiN': {
        'Y_M': 1.5, 'Y_C': 0.3,
        'alpha_t': 1.0, 'alpha_c': 1.0,
        'R_M': 120.0, 'R_C': 22.0,
        'A_t': 127e-4, 'A_c': 10 * 127e-4,
        'J': 1.4e3, 'S_p': 85e-3, 'M_g': 28.014e-3,
    },
    'TiO2': {
        'Y_M': 1.5, 'Y_C': 0.2,
        'alpha_t': 0.8, 'alpha_c': 0.8,
        'R_M': 100.0, 'R_C': 15.0,
        'A_t': 127e-4, 'A_c': 10 * 127e-4,
        'J': 1.4e3, 'S_p': 85e-3, 'M_g': 32.0e-3,
    },
    'Al2O3': {
        'Y_M': 1.2, 'Y_C': 0.15,
        'alpha_t': 0.7, 'alpha_c': 0.7,
        'R_M': 80.0, 'R_C': 10.0,
        'A_t': 127e-4, 'A_c': 10 * 127e-4,
        'J': 1.4e3, 'S_p': 85e-3, 'M_g': 32.0e-3,
    }
}

def get_material_params(material):
    if material not in MATERIAL_PARAMS:
        raise ValueError(f"Material {material} not found.")
    return {**PHYSICAL_CONSTANTS, **MATERIAL_PARAMS[material]}