"""
Monte Carlo simulation engine
"""

import numpy as np
from tqdm import tqdm
from models import simulate_mzi
from .metrics import extract_metrics
from utils import generate_correlated_samples

def run_monte_carlo(design, variations, correlation_matrix, specs, n_samples=1000, 
                    random_seed=42, verbose=True):
    """
    Run Monte Carlo simulation for MZI with process variations
    """
    np.random.seed(random_seed)
    
    lam_min, lam_max = design['wavelength_range']
    wavelengths = np.linspace(lam_min, lam_max, design['wavelength_points'])
    
    width_variations = generate_correlated_samples(
        n_samples=n_samples,
        correlation_matrix=correlation_matrix,
        sigma=variations['width_sigma'],
        random_state=random_seed
    )
    
    all_metrics = []
    
    iterator = tqdm(range(n_samples), desc="Monte Carlo") if verbose else range(n_samples)
    
    for i in iterator:
        width_deltas = width_variations[i]
        height_delta = np.random.normal(0, variations['height_sigma'])
        gap_deltas = np.random.normal(0, variations['gap_sigma'], size=2)
        length_delta = np.random.normal(0, variations['length_sigma'])
        
        lam, P_out1, P_out2 = simulate_mzi(
            width_deltas=width_deltas,
            height_delta=height_delta,
            gap_deltas=gap_deltas,
            length_delta=length_delta,
            wavelengths=wavelengths,
            design=design
        )
        
        metrics = extract_metrics(wavelengths, P_out1, P_out2)
        
        metrics['sample_id'] = i
        metrics['width_delta_arm1'] = width_deltas[0]
        metrics['width_delta_arm2'] = width_deltas[1]
        metrics['width_delta_coupler1'] = width_deltas[2]
        metrics['width_delta_coupler2'] = width_deltas[3]
        metrics['height_delta'] = height_delta
        metrics['gap_delta_1'] = gap_deltas[0]
        metrics['gap_delta_2'] = gap_deltas[1]
        metrics['length_delta'] = length_delta
        
        metrics['pass_ER'] = metrics['ER_out1'] > specs['target_ER']
        metrics['pass_IL'] = metrics['IL_out1'] < specs['target_IL']
        metrics['pass_overall'] = metrics['pass_ER'] and metrics['pass_IL']
        
        all_metrics.append(metrics)
    
    return all_metrics