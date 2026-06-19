"""
run_full_pipeline.py - Executes the entire workflow.
"""

import os
import pandas as pd
from experiments.scenario_runner import ScenarioRunner
from output.final_plots import FinalFigureGenerator
from analysis.validation import validate_model
from submission.compliance_checker import check_structure

def main():
    print("\n" + "="*60)
    print("Running Full Pipeline for Reactive Sputtering Framework")
    print("="*60 + "\n")
    
    os.makedirs('output', exist_ok=True)
    os.makedirs('figures', exist_ok=True)
    
    # 1. Validate model
    print("Step 1: Validating Berg model...")
    validate_model('TiN')
    
    # 2. Run scenarios
    print("\nStep 2: Running simulation scenarios...")
    runner = ScenarioRunner(seed=42)
    df = runner.run(
        materials=['TiN', 'TiO2', 'Al2O3'],
        sources=[3, 4, 6],
        schedulers=['GE', 'Cyclic', 'JSQ-CF'],
        cycles=[50],
        repeats=3
    )
    
    if len(df) > 0:
        df.to_csv('output/simulation_results.csv', index=False)
        print(f"  Saved {len(df)} simulation results to output/simulation_results.csv")
    
    # 3. Generate figures
    print("\nStep 3: Generating figures...")
    fig_gen = FinalFigureGenerator(df if len(df) > 0 else pd.DataFrame())
    fig_gen.generate_all()
    
    # 4. Check compliance
    print("\nStep 4: Checking compliance...")
    check_structure()
    
    print("\n" + "="*60)
    print("Pipeline completed successfully!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()