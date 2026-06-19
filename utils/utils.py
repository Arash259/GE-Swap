"""
utils.py - General helper functions.
"""

import os
import numpy as np

def ensure_dir(path):
    """Create directory if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path)

def normalize_array(arr):
    """Normalize array to [0, 1] range."""
    if np.max(arr) - np.min(arr) < 1e-10:
        return np.zeros_like(arr)
    return (arr - np.min(arr)) / (np.max(arr) - np.min(arr) + 1e-9)

def compute_ci(data, confidence=0.95):
    """Compute confidence interval."""
    from scipy import stats
    n = len(data)
    mean = np.mean(data)
    se = np.std(data, ddof=1) / np.sqrt(n)
    t_val = stats.t.ppf((1 + confidence) / 2, n - 1)
    return (mean - t_val * se, mean + t_val * se)