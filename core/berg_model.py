"""
berg_model.py - Berg model for reactive sputtering hysteresis and dynamics.
Based on Berg et al. (1987) and Berg & Nyberg (2005).
"""

import numpy as np
from config import get_material_params

class BergModel:
    def __init__(self, material='TiN', params=None):
        self.params = get_material_params(material) if params is None else params
        self.Y_M = self.params['Y_M']
        self.Y_C = self.params['Y_C']
        self.alpha_t = self.params['alpha_t']
        self.R_M = self.params['R_M']
        self.R_C = self.params['R_C']
        self.e = self.params['e']
        self.J = self.params['J']
        self.M_g = self.params['M_g']
        self.k_B = self.params['k_B']
        self.T = self.params['T']
        
        self.ion_flux = self.J / self.e
        self.theta = 0.0
        self.time = 0.0
        self.deposition_rate = self.R_M
        self.k1 = 0.05
        self.k2 = 0.02

    def compute_flux(self, pressure):
        """Compute reactive gas flux."""
        return pressure / np.sqrt(2 * np.pi * self.k_B * self.T * self.M_g)

    def compute_poisoning_fraction(self, pressure):
        """Compute steady-state poisoning fraction."""
        F = self.compute_flux(pressure)
        num = 2 * self.alpha_t * F
        den = self.ion_flux * self.Y_C + 2 * self.alpha_t * F
        return num / den if den > 0 else 1.0

    def compute_deposition_rate(self, theta=None):
        """Compute effective deposition rate."""
        if theta is None:
            theta = self.theta
        return self.alpha_t * (1 - theta) * self.R_M + self.alpha_t * theta * self.R_C

    def update_poisoning_dynamics(self, pressure, dt):
        """Update poisoning dynamics using Euler method."""
        F = self.compute_flux(pressure)
        Phi = F / (F + self.ion_flux * self.Y_C / (2 * self.alpha_t) + 1e-10)
        dtheta = self.k1 * Phi * (1 - self.theta) - self.k2 * self.theta
        self.theta += dtheta * dt
        self.theta = np.clip(self.theta, 0.0, 1.0)
        self.deposition_rate = self.compute_deposition_rate()
        self.time += dt
        return self.theta

    def run_sputtering_cycle(self, pressure, duration, n_substeps=50):
        """Run a complete sputtering cycle."""
        duration_sec = duration * 60.0
        dt = duration_sec / n_substeps
        theta_hist, rate_hist = [], []
        for _ in range(n_substeps):
            self.update_poisoning_dynamics(pressure, dt)
            theta_hist.append(self.theta)
            rate_hist.append(self.deposition_rate)
        return {
            'theta_avg': np.mean(theta_hist),
            'rate_avg': np.mean(rate_hist),
            'thickness': np.mean(rate_hist) * duration,
            'theta_final': theta_hist[-1]
        }

    def compute_hysteresis_curve(self, pressure_range, n_points=100):
        """Compute hysteresis curve (forward and backward paths)."""
        pressures = np.linspace(pressure_range[0], pressure_range[1], n_points)
        self.theta = 0.0
        forward = []
        for p in pressures:
            for _ in range(50):
                self.update_poisoning_dynamics(p, 0.1)
            forward.append(self.theta)
        
        self.theta = 1.0
        backward = []
        for p in reversed(pressures):
            for _ in range(50):
                self.update_poisoning_dynamics(p, 0.1)
            backward.append(self.theta)
        return {'pressures': pressures, 'theta_forward': forward, 'theta_backward': list(reversed(backward))}

    def reset(self):
        """Reset model to initial state."""
        self.theta = 0.0
        self.time = 0.0
        self.deposition_rate = self.R_M