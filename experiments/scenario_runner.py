"""
scenario_runner.py - Batch runs over multiple configurations.
"""

import pandas as pd
from tqdm import tqdm
from core.hybrid_simulator import HybridSimulator

class ScenarioRunner:
    """Batch execution of scenarios."""
    
    def __init__(self, seed=42):
        self.seed = seed
        self.results = []

    def run(self, materials=['TiN'], sources=[3, 4], schedulers=['GE'], 
            cycles=[50], repeats=3):
        """Run multiple scenarios."""
        total = len(materials) * len(sources) * len(schedulers) * len(cycles) * repeats
        
        for mat in materials:
            for n in sources:
                for sch in schedulers:
                    for c in cycles:
                        for r in range(repeats):
                            sim = HybridSimulator(
                                mat, n, sch, 
                                advanced=(sch == 'GE'), 
                                seed=self.seed + r
                            )
                            times, _ = sim.generate_cycles(c)
                            sim.run(times)
                            summary = sim.get_summary()
                            if summary:
                                summary['material'] = mat
                                summary['n_sources'] = n
                                summary['scheduler'] = sch
                                self.results.append(summary)
        
        return pd.DataFrame(self.results)