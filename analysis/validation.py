"""
validation.py - Validates Berg model against experimental data.
"""

import numpy as np
import pandas as pd
from sklearn.metrics import r2_score
from core.berg_model import BergModel

def load_sproul_tin():
    """Load TiN experimental data from Sproul et al."""
    return pd.DataFrame({
        'pressure': [0.002, 0.005, 0.008, 0.01, 0.015, 0.02],
        'rate': [115, 110, 95, 75, 35, 20],
        'theta': [0.05, 0.10, 0.20, 0.35, 0.70, 0.85]
    })

def validate_model(material='TiN'):
    """Validate Berg model against experimental data."""
    exp = load_sproul_tin()
    model = BergModel(material)
    
    pred_rate = []
    pred_theta = []
    
    for p in exp['pressure']:
        theta = model.compute_poisoning_fraction(p)
        rate = model.compute_deposition_rate(theta)
        pred_rate.append(rate)
        pred_theta.append(theta)
    
    r2_rate = r2_score(exp['rate'], pred_rate)
    r2_theta = r2_score(exp['theta'], pred_theta)
    
    print(f"Validation R² for {material}: Rate={r2_rate:.4f}, Theta={r2_theta:.4f}")
    
    return {'r2_rate': r2_rate, 'r2_theta': r2_theta}