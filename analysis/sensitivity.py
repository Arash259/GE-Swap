"""
sensitivity.py - Monte Carlo and one-factor-at-a-time sensitivity.
"""

import numpy as np
import pandas as pd
from core.berg_model import BergModel
from config import MATERIAL_PARAMS

def one_factor_sensitivity(material='TiN', target_p=0.01):
    """One-factor-at-a-time sensitivity analysis."""
    base = MATERIAL_PARAMS[material]
    results = []
    
    for key in ['Y_M', 'Y_C', 'alpha_t', 'R_M', 'R_C']:
        vals = np.linspace(base[key] * 0.5, base[key] * 1.5, 10)
        for v in vals:
            params = base.copy()
            params[key] = v
            m = BergModel(material, params)
            theta = m.compute_poisoning_fraction(target_p)
            rate = m.compute_deposition_rate(theta)
            results.append({'param': key, 'value': v, 'theta': theta, 'rate': rate})
    
    return pd.DataFrame(results)

def monte_carlo_sensitivity(material='TiN', n_samples=500):
    """Monte Carlo sensitivity analysis."""
    base = MATERIAL_PARAMS[material]
    thetas, rates = [], []
    
    for _ in range(n_samples):
        params = {
            k: np.random.normal(v, v * 0.1) 
            for k, v in base.items() 
            if k in ['Y_M', 'Y_C', 'R_M', 'R_C']
        }
        m = BergModel(material, params)
        t = m.compute_poisoning_fraction(0.01)
        r = m.compute_deposition_rate(t)
        thetas.append(t)
        rates.append(r)
    
    return {
        'theta_mean': np.mean(thetas),
        'theta_std': np.std(thetas),
        'rate_mean': np.mean(rates),
        'rate_std': np.std(rates)
    }