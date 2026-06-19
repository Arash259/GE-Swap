"""
hybrid_simulator.py - Orchestrates scheduling and physics.
"""

import numpy as np
import pandas as pd
import os
from core.berg_model import BergModel
from core.scheduler import create_scheduler
from core.advanced_scheduler import AdvancedSchedulerInterface

class HybridSimulator:
    """
    Hybrid simulator coupling scheduling algorithms with the Berg physics model.
    """
    
    def __init__(self, material='TiN', n_sources=4, scheduler='GE', 
                 advanced=False, seed=42):
        self.material = material
        self.n = n_sources
        self.seed = seed
        self.advanced = advanced
        
        np.random.seed(seed)
        
        # Create physics models for each source
        self.models = [BergModel(material) for _ in range(n_sources)]
        
        # Create scheduler
        if advanced and scheduler == 'GE':
            self.sched = AdvancedSchedulerInterface(n_sources)
            self.sched.set_physical_model(self.models[0])
        else:
            self.sched = create_scheduler(scheduler, n_sources)
        
        self.results = None
        self.summary = None

    def generate_cycles(self, n_cycles, t_range=(10, 120), 
                        p_base=0.01, p_noise=0.002):
        """Generate random cycle data."""
        times = np.random.uniform(t_range[0], t_range[1], n_cycles)
        pressures = np.clip(p_base + np.random.normal(0, p_noise, n_cycles), 
                           0.001, 0.05)
        return times, pressures

    def run(self, cycle_times, pressures=None, n_sub=50):
        """Run complete simulation."""
        if pressures is None:
            pressures = [0.01] * len(cycle_times)
        
        data = {
            'cycle': [], 'duration': [], 'source': [],
            'theta': [], 'rate': [], 'load': [], 'time': []
        }
        
        total_t = 0.0
        
        for i, (dur, p) in enumerate(zip(cycle_times, pressures)):
            # Assign cycle using scheduler
            if self.advanced:
                remaining = cycle_times[i+1:i+1+self.sched.scheduler.lookahead]
                src = self.sched.scheduler.assign_cycle(dur, remaining)
            else:
                src = self.sched.assign_cycle(dur)
            
            # Run physics cycle on selected source
            model = self.models[src]
            res = model.run_sputtering_cycle(p, dur, n_sub)
            
            # Store results
            data['cycle'].append(i)
            data['duration'].append(dur)
            data['source'].append(src)
            data['theta'].append(res['theta_avg'])
            data['rate'].append(res['rate_avg'])
            
            if self.advanced:
                data['load'].append(self.sched.scheduler.sources[src].load)
            else:
                data['load'].append(self.sched.loads[src])
            
            data['time'].append(total_t + dur)
            total_t += dur
        
        self.results = pd.DataFrame(data)
        self._compute_summary()
        return self.results

    def _compute_summary(self):
        """Compute key metrics from simulation results."""
        if self.results is None:
            return
        
        df = self.results
        
        if self.advanced:
            loads = [s.load for s in self.sched.scheduler.sources]
        else:
            loads = self.sched.loads
        
        self.makespan = max(loads)
        self.avg_load = np.mean(loads)
        self.nm = self.makespan / self.avg_load if self.avg_load > 0 else 1.0
        self.avg_theta = df['theta'].mean()
        self.avg_rate = df['rate'].mean()
        self.roughness = 1.2 + 2.8 * self.nm
        
        self.summary = {
            'material': self.material,
            'scheduler': 'GE+Swap' if self.advanced else getattr(self.sched, 'name', 'Unknown'),
            'n_sources': self.n,
            'n_cycles': len(df),
            'makespan': self.makespan,
            'avg_load': self.avg_load,
            'normalized_makespan': self.nm,
            'avg_theta': self.avg_theta,
            'avg_rate': self.avg_rate,
            'roughness': self.roughness
        }
        return self.summary

    def get_results(self):
        return self.results

    def get_summary(self):
        return self.summary