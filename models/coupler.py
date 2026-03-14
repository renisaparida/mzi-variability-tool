"""
Directional coupler compact model
"""

import numpy as np

def coupler_matrix(gap, width, wavelength, gap_delta=0, width_delta=0, 
                   coupling_length=10e-6):
    """
    Calculate 2x2 directional coupler S-parameters
    
    Args:
        gap: Nominal coupler gap (m)
        width: Waveguide width (m)
        wavelength: Wavelength (m)
        gap_delta: Gap variation (m)
        width_delta: Width variation (m)
        coupling_length: Coupler interaction length (m)
    
    Returns:
        S: 2x2 S-parameter matrix (complex)
           S[0,0] = through port (input 1 -> output 1)
           S[0,1] = cross port (input 2 -> output 1)
           S[1,0] = cross port (input 1 -> output 2)
           S[1,1] = through port (input 2 -> output 2)
    
    Note:
        This is a simplified model. Production version should use
        CMT (Coupled Mode Theory) or FDTD-fitted coupling coefficients.
    """
    g = gap + gap_delta
    w = width + width_delta
    
    # Nominal coupling coefficient for 3dB coupler
    # kappa = 0.480 means 48% power couples to cross port
    kappa_nominal = 0.480
    
    # Gap dependence: coupling decreases with larger gap
    # Rule of thumb: 10nm gap increase -> 5% coupling decrease
    kappa_gap = kappa_nominal * (1 - 0.5 * (g / 200e-9 - 1.0))
    
    # Width dependence: wider waveguides -> tighter mode confinement -> less coupling
    kappa_width = kappa_gap * (1 - 0.2 * (w / 500e-9 - 1.0))
    
    # Wavelength dependence
    kappa_wavelength = kappa_width * (1 + 0.1 * (wavelength / 1550e-9 - 1.0))
    
    # Clip to physical bounds
    kappa = np.clip(kappa_wavelength, 0.05, 0.95)
    
    # Excess loss (increases with fabrication errors)
    # More realistic coupler loss model
    excess_loss_db = 0.06 + 0.15 * abs(gap_delta / 5e-9) + 0.10 * abs(width_delta / 15e-9)
    transmission_factor = 10 ** (-excess_loss_db / 10)
    
    # S-matrix for ideal lossless coupler
    # Based on coupled mode theory
    t = np.sqrt(1 - kappa)  # Through coefficient
    k = np.sqrt(kappa)       # Coupling coefficient
    
    # Phase factors (90° phase shift in through port is typical)
    S_ideal = np.array([
        [1j * t,  k     ],
        [k,       1j * t]
    ])
    
    # Apply excess loss
    S = np.sqrt(transmission_factor) * S_ideal
    
    return S