"""
main.py - Single-run entry point for the simulator.
"""

import argparse
import os
import numpy as np
from core.hybrid_simulator import HybridSimulator

def main():
    parser = argparse.ArgumentParser(description='Reactive Sputtering Simulator')
    parser.add_argument('--material', default='TiN', choices=['TiN', 'TiO2', 'Al2O3'])
    parser.add_argument('--n_sources', type=int, default=4)
    parser.add_argument('--n_cycles', type=int, default=50)
    parser.add_argument('--scheduler', default='GE', choices=['GE', 'Cyclic', 'JSQ-CF'])
    parser.add_argument('--advanced', action='store_true', help='Use GE+Swap')
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()

    os.makedirs('output', exist_ok=True)
    
    sim = HybridSimulator(
        args.material, args.n_sources, args.scheduler,
        advanced=args.advanced, seed=args.seed
    )
    
    times, pressures = sim.generate_cycles(args.n_cycles)
    results = sim.run(times, pressures)
    summary = sim.get_summary()
    
    print(f"\n{'='*50}")
    print(f"Material: {args.material}")
    print(f"Scheduler: {summary['scheduler'] if summary else args.scheduler}")
    print(f"Makespan: {sim.makespan:.2f}")
    print(f"Normalized Makespan: {sim.nm:.3f}")
    print(f"Predicted Roughness: {sim.roughness:.2f} nm")
    print(f"{'='*50}\n")
    
    results.to_csv('output/simulation_results.csv', index=False)
    print("Results saved to output/simulation_results.csv")

if __name__ == "__main__":
    main()