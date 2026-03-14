"""
Design optimization for maximum yield
"""

import numpy as np
from scipy.optimize import differential_evolution
from models import simulate_mzi
from simulation.metrics import extract_metrics
from utils import generate_correlated_samples

def optimize_design(design, variations, correlation_matrix, specs, 
                    width_bounds, length_bounds, maxiter=20, popsize=10, 
                    n_eval_samples=100, random_seed=42, verbose=True):
    """
    Optimize MZI design for maximum yield
    """
    
    lam_min, lam_max = design['wavelength_range']
    wavelengths = np.linspace(lam_min, lam_max, 50)
    
    # Store best result for debugging
    best_yield = 0
    best_params = None
    eval_count = [0]
    
    def objective_function(params):
        """
        Objective: Maximize yield (minimize negative yield)
        
        Args:
            params: [width_offset, length_offset]
        
        Returns:
            -yield: Negative yield percentage (for minimization)
        """
        width_offset, length_offset = params
        eval_count[0] += 1
        
        # CRITICAL: Use fixed seed for each evaluation for reproducibility
        # Add eval_count to seed so each evaluation explores different samples
        eval_seed = random_seed + eval_count[0]
        np.random.seed(eval_seed)
        
        # Generate correlated width variations with this specific seed
        width_variations = generate_correlated_samples(
            n_samples=n_eval_samples,
            correlation_matrix=correlation_matrix,
            sigma=variations['width_sigma'],
            random_state=eval_seed
        )
        
        passes = 0
        
        for i in range(n_eval_samples):
            # CRITICAL: Apply design offsets CORRECTLY
            # The offset shifts the NOMINAL design, not the variations
            # So we create a modified design dictionary
            modified_design = design.copy()
            modified_design['waveguide_width'] = design['waveguide_width'] + width_offset
            modified_design['arm_length_diff'] = design['arm_length_diff'] + length_offset
            
            # Sample variations (these are deltas from nominal)
            width_deltas = width_variations[i]  # Already variations, don't add offset here
            height_delta = np.random.normal(0, variations['height_sigma'])
            gap_deltas = np.random.normal(0, variations['gap_sigma'], size=2)
            length_delta = np.random.normal(0, variations['length_sigma'])
            
            # Simulate with MODIFIED design + variations
            lam, P_out1, P_out2 = simulate_mzi(
                width_deltas=width_deltas,
                height_delta=height_delta,
                gap_deltas=gap_deltas,
                length_delta=length_delta,
                wavelengths=wavelengths,
                design=modified_design  # Use modified design
            )
            
            # Extract metrics
            metrics = extract_metrics(wavelengths, P_out1, P_out2)
            
            # Check if passes specs (use the SAME specs as Monte Carlo)
            if metrics['ER_out1'] > specs['target_ER'] and metrics['IL_out1'] < specs['target_IL']:
                passes += 1
        
        yield_pct = 100 * passes / n_eval_samples
        
        # Track best
        nonlocal best_yield, best_params
        if yield_pct > best_yield:
            best_yield = yield_pct
            best_params = params.copy()
            if verbose and eval_count[0] % 10 == 0:
                print(f"  Eval {eval_count[0]}: width={params[0]*1e9:+.2f}nm, "
                      f"length={params[1]*1e9:+.2f}nm → yield={yield_pct:.1f}%")
        
        # Return negative (we're minimizing)
        return -yield_pct
    
    if verbose:
        print("\n" + "="*60)
        print("DESIGN OPTIMIZATION")
        print("="*60)
        print(f"Optimization parameters:")
        print(f"  Width offset bounds:  {width_bounds[0]*1e9:.1f} to {width_bounds[1]*1e9:.1f} nm")
        print(f"  Length offset bounds: {length_bounds[0]*1e9:.1f} to {length_bounds[1]*1e9:.1f} nm")
        print(f"  Max iterations:       {maxiter}")
        print(f"  Population size:      {popsize}")
        print(f"  Samples per eval:     {n_eval_samples}")
        print(f"  Target specs:         ER>{specs['target_ER']}dB, IL<{specs['target_IL']}dB")
        print("\nRunning optimization...\n")
    
    # Run differential evolution
    result = differential_evolution(
        objective_function,
        bounds=[width_bounds, length_bounds],
        maxiter=maxiter,
        popsize=popsize,
        seed=random_seed,
        disp=False,
        polish=True,
        workers=1,  # Single-threaded for reproducibility
        updating='deferred'
    )
    
    optimal_width_offset = result.x[0]
    optimal_length_offset = result.x[1]
    optimal_yield = -result.fun  # Convert back to positive
    
    optimization_result = {
        'optimal_width_offset_nm': optimal_width_offset * 1e9,
        'optimal_length_offset_nm': optimal_length_offset * 1e9,
        'optimal_yield': optimal_yield,
        'width_offset_m': optimal_width_offset,
        'length_offset_m': optimal_length_offset,
    }
    
    if verbose:
        print("\n" + "="*60)
        print("OPTIMIZATION RESULTS")
        print("="*60)
        print(f"\nOptimal Design Offsets:")
        print(f"  Width offset:  {optimal_width_offset*1e9:+7.2f} nm")
        print(f"  Length offset: {optimal_length_offset*1e9:+7.2f} nm")
        print(f"\nPredicted Yield: {optimal_yield:.2f}%")
        print(f"Best seen during optimization: {best_yield:.2f}%")
        print("="*60 + "\n")
    
    return optimization_result