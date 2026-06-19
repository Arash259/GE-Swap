"""
compliance_checker.py - Checks if the project meets journal guidelines.
"""

import os

def check_structure():
    """Check if all required files exist."""
    required = [
        'core/berg_model.py',
        'core/scheduler.py',
        'core/advanced_scheduler.py',
        'core/hybrid_simulator.py',
        'analysis/validation.py',
        'config.py'
    ]
    
    missing = [r for r in required if not os.path.exists(r)]
    
    if missing:
        print(f"❌ Missing required files: {missing}")
        return False
    else:
        print("✅ All required files are present.")
        return True