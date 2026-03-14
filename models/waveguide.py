"""
Waveguide compact model with variability
"""

import numpy as np

def waveguide_neff(width, height, wavelength, width_delta=0, height_delta=0):
    """
    Calculate effective index and loss for strip waveguide
    """
    w = width + width_delta
    h = height + height_delta
    lam = wavelength
    
    n_base = 2.45
    dn_dw = 0.38 * (w / 500e-9 - 1.0)
    dn_dh = 0.18 * (h / 220e-9 - 1.0)
    dn_dlam = -1.55 * (lam / 1550e-9 - 1.0)
    
    n_eff = n_base + dn_dw + dn_dh + dn_dlam
    
    alpha_base = 2.5
    alpha_roughness = 8.0 * abs(width_delta / 15e-9)
    alpha_mode_mismatch = 2.0 * abs(height_delta / 10e-9)
    
    alpha = alpha_base + alpha_roughness + alpha_mode_mismatch
    
    return n_eff, alpha


def waveguide_phase(length, neff, wavelength):
    """
    Calculate phase accumulation
    """
    return 2 * np.pi * neff * length / wavelength


def waveguide_loss(length, alpha_db_cm):
    """
    Calculate transmission (power)
    """
    length_cm = length * 100
    loss_db = alpha_db_cm * length_cm
    transmission = 10 ** (-loss_db / 10)
    return transmission