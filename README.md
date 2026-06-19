# Ge+Swap: Hybrid Computational Framework for Reactive Sputtering

## Overview
This repository contains the complete Python implementation of the hybrid computational framework coupling scheduling algorithms with the Berg physics model for reactive sputtering, as described in the manuscript:

**"Physics-Aware Scheduling for Reactive Sputtering: A Hybrid Computational Framework with (2n−1)/(n−1)-Approximation Guarantee"**

## Features
- Berg Physics Model for reactive sputtering
- Greedy-Eligible (GE) algorithm with provable (2n−1)/(n−1)-approximation guarantee
- Advanced GE+Swap with physics-aware cost function, lookahead, and block-swap optimization
- Hybrid simulation coupling scheduling with physics
- Validation against experimental data for TiN, TiO₂, and Al₂O₃
- Sensitivity analysis, ablation study, and statistical analysis
- Publication-quality figures and LaTeX tables

## Installation
```bash
git clone https://github.com/Arash259/Ge+Swap.git
cd Ge+Swap
pip install -r requirements.txt