"""
optimization.py - Fits Berg model parameters to experimental data.
"""

import numpy as np
from scipy.optimize import differential_evolution
from core.berg_model import BergModel
from analysis.validation import load_sproul_tin

def objective(x, material, exp):
    params = {'Y_M': x[0], 'Y_C': x[1], 'alpha_t': x[2], 'R_M': x[3], 'R_C': x[4]}
    model = BergModel(material, params)
    pred = [model.compute_deposition_rate(model.compute_poisoning_fraction(p)) for p in exp['pressure']]
    return np.mean((np.array(pred) - exp['rate'])**2)

def optimize_params(material='TiN'):
    exp = load_sproul_tin()
    bounds = [(0.5, 2.5), (0.1, 0.8), (0.5, 1.0), (50, 200), (5, 50)]
    res = differential_evolution(objective, bounds, args=(material, exp), maxiter=500)
    print(f"Optimized params: {res.x}")
    return res.x