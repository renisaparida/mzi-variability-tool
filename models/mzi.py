"""
Mach-Zehnder Interferometer circuit model
"""

import numpy as np
from .waveguide import waveguide_neff, waveguide_phase, waveguide_loss
from .coupler import coupler_matrix

def simulate_mzi(width_deltas, height_delta, gap_deltas, length_delta, 
                 wavelengths, design):
    """
    Simulate MZI transfer function with process variations
    
    Args:
        width_deltas: Array of 4 width variations [arm1, arm2, coupler1, coupler2] (m)
        height_delta: Height variation (m)
        gap_deltas: Array of 2 gap variations [coupler1, coupler2] (m)
        length_delta: Arm length difference variation (m)
        wavelengths: Array of wavelengths (m)
        design: Design parameter dictionary
    
    Returns:
        wavelengths: Input wavelength array
        P_out1: Power at output port 1
        P_out2: Power at output port 2
    """
    # Extract design parameters
    w = design['waveguide_width']
    h = design['waveguide_height']
    g = design['coupler_gap']
    
    # Symmetric arm lengths
    L1 = design['arm_length_diff'] / 2
    L2 = L1 + design['arm_length_diff'] + length_delta
    
    # Storage for results
    P_out1_array = []
    P_out2_array = []
    
    # Sweep wavelength
    for lam in wavelengths:
        # === Input Coupler ===
        S_in = coupler_matrix(
            gap=g,
            width=w,
            wavelength=lam,
            gap_delta=gap_deltas[0],
            width_delta=width_deltas[2]  # Coupler 1 width
        )
        
        # === Arm 1 (Upper) ===
        neff1, alpha1 = waveguide_neff(
            width=w,
            height=h,
            wavelength=lam,
            width_delta=width_deltas[0],
            height_delta=height_delta
        )
        phi1 = waveguide_phase(L1, neff1, lam)
        T1_amplitude = np.sqrt(waveguide_loss(L1, alpha1))
        T1 = T1_amplitude * np.exp(1j * phi1)
        
        # === Arm 2 (Lower) ===
        neff2, alpha2 = waveguide_neff(
            width=w,
            height=h,
            wavelength=lam,
            width_delta=width_deltas[1],
            height_delta=height_delta
        )
        phi2 = waveguide_phase(L2, neff2, lam)
        T2_amplitude = np.sqrt(waveguide_loss(L2, alpha2))
        T2 = T2_amplitude * np.exp(1j * phi2)
        
        # === Output Coupler ===
        S_out = coupler_matrix(
            gap=g,
            width=w,
            wavelength=lam,
            gap_delta=gap_deltas[1],
            width_delta=width_deltas[3]  # Coupler 2 width
        )
        
        # === Propagate Signal ===
        # Input: port 1 excited with unit amplitude
        E_in = np.array([1.0 + 0j, 0.0 + 0j])
        
        # After input coupler
        E_after_coupler1 = S_in @ E_in
        
        # After arms (diagonal matrix)
        E_after_arms = np.array([
            E_after_coupler1[0] * T1,
            E_after_coupler1[1] * T2
        ])
        
        # After output coupler
        E_out = S_out @ E_after_arms
        
        # Calculate output powers
        P_out1 = np.abs(E_out[0]) ** 2
        P_out2 = np.abs(E_out[1]) ** 2
        
        P_out1_array.append(P_out1)
        P_out2_array.append(P_out2)
    
    return wavelengths, np.array(P_out1_array), np.array(P_out2_array)