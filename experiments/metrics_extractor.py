"""
metrics_extractor.py - Extracts final numbers for the paper.
"""

import numpy as np
from analysis.statistics import compute_ci

class MetricsExtractor:
    def __init__(self, df):
        self.df = df

    def get_best_performance(self, material='TiN', n_sources=4):
        sub = self.df[(self.df['material'] == material) & (self.df['n_sources'] == n_sources)]
        ge = sub[sub['scheduler'] == 'GE']['normalized_makespan']
        cyclic = sub[sub['scheduler'] == 'Cyclic']['normalized_makespan']
        impr = (cyclic.mean() - ge.mean()) / cyclic.mean() * 100 if cyclic.mean() > 0 else 0
        return {'GE_mean': ge.mean(), 'Cyclic_mean': cyclic.mean(), 'Improvement_%': impr}