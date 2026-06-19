"""
latex_generator.py - Creates LaTeX tables for the manuscript.
"""

import os
import pandas as pd

class LaTeXGenerator:
    def __init__(self, df, out_dir='tables_latex'):
        self.df = df
        self.out_dir = out_dir
        os.makedirs(out_dir, exist_ok=True)

    def generate_main_table(self, material='TiN', n_sources=4):
        sub = self.df[(self.df['material'] == material) & (self.df['n_sources'] == n_sources)]
        if len(sub) == 0:
            return None
        agg = sub.groupby('scheduler')['normalized_makespan'].agg(['mean', 'std']).round(3)
        latex = agg.to_latex(caption=f"Comparison for {material} with {n_sources} sources.")
        with open(f'{self.out_dir}/table_{material}_{n_sources}.tex', 'w') as f:
            f.write(latex)
        return latex