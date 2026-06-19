"""
graphical_abstract.py - Creates a visual summary of the framework.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

def create_graphical_abstract(out_dir='figures'):
    fig, ax = plt.subplots(figsize=(12, 3))
    ax.axis('off')
    # Input
    ax.add_patch(patches.FancyBboxPatch((0.1, 0.5), 1.5, 1.5, boxstyle="round", facecolor='#D3D3D3'))
    ax.text(0.85, 1.25, 'Deposition\nCycles', ha='center', va='center')
    ax.annotate('', xy=(2.2, 1.25), xytext=(1.6, 1.25), arrowprops=dict(arrowstyle='->'))
    # Scheduler
    ax.add_patch(patches.FancyBboxPatch((2.3, 0.5), 1.8, 1.5, boxstyle="round", facecolor='#4CAF50'))
    ax.text(3.2, 1.25, 'GE+Swap\nAlgorithm', ha='center', va='center', color='white')
    ax.annotate('', xy=(4.6, 1.25), xytext=(4.1, 1.25), arrowprops=dict(arrowstyle='->'))
    # Physics
    ax.add_patch(patches.FancyBboxPatch((4.7, 0.5), 2.0, 1.5, boxstyle="round", facecolor='#2196F3'))
    ax.text(5.7, 1.25, 'Berg Physics\nModel', ha='center', va='center', color='white')
    ax.annotate('', xy=(7.2, 1.25), xytext=(6.7, 1.25), arrowprops=dict(arrowstyle='->'))
    # Output
    ax.add_patch(patches.FancyBboxPatch((7.3, 0.5), 2.0, 1.5, boxstyle="round", facecolor='#FF9800'))
    ax.text(8.3, 1.25, 'Lower Makespan\nSmoother Films', ha='center', va='center')
    plt.tight_layout()
    os.makedirs(out_dir, exist_ok=True)
    plt.savefig(f'{out_dir}/graphical_abstract.png', dpi=300)
    plt.close()