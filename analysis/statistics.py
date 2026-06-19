"""
statistics.py - Statistical tests and confidence intervals.
"""

import numpy as np
from scipy import stats

def compute_ci(data, conf=0.95):
    n = len(data)
    mean = np.mean(data)
    se = np.std(data, ddof=1) / np.sqrt(n)
    t = stats.t.ppf((1 + conf) / 2, n - 1)
    return (mean - t * se, mean + t * se)

def t_test_compare(group1, group2):
    return stats.ttest_ind(group1, group2, equal_var=False)

def pearson_corr(x, y):
    return stats.pearsonr(x, y)