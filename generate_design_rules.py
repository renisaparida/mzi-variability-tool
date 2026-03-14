"""
Generate design rules by sweeping process variations
"""

import numpy as np
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns

from config import DESIGN, SPECS, CORRELATION_MATRIX, MONTE_CARLO
from simulation import run_monte_carlo
from analysis import analyze_yield

print("="*70)
print("GENERATING DESIGN RULES FOR MZI SWITCHES")
print("="*70)

# Create output directory
output_dir = Path("design_rules")
output_dir.mkdir(exist_ok=True)

# ============================================================================
# EXPERIMENT 1: Yield vs. Width Variation (Main Driver)
# ============================================================================

print("\n[1/4] Analyzing yield vs. width variation...")

width_sigmas = [8e-9, 10e-9, 12e-9, 15e-9, 18e-9, 20e-9, 22e-9, 25e-9, 30e-9]
results_width = []

# Fixed other variations at baseline
VARIATIONS_BASE = {
    'height_sigma': 12e-9,
    'gap_sigma': 6e-9,
    'length_sigma': 60e-9,
    'correlation_length': 100e-6,
}

for width_sigma in tqdm(width_sigmas, desc="Width sweep"):
    variations = VARIATIONS_BASE.copy()
    variations['width_sigma'] = width_sigma
    
    # Run Monte Carlo (use 2000 samples for speed, still accurate)
    metrics = run_monte_carlo(
        design=DESIGN,
        variations=variations,
        correlation_matrix=CORRELATION_MATRIX,
        specs=SPECS,
        n_samples=2000,
        random_seed=MONTE_CARLO['random_seed'],
        verbose=False
    )
    
    df, stats = analyze_yield(metrics, SPECS, verbose=False)
    
    results_width.append({
        'width_sigma_nm': width_sigma * 1e9,
        'yield_overall': stats['yield_overall'],
        'yield_ER': stats['yield_ER'],
        'yield_IL': stats['yield_IL'],
        'ER_mean': stats['ER_mean'],
        'ER_std': stats['ER_std'],
        'IL_mean': stats['IL_mean'],
        'IL_std': stats['IL_std'],
        'Cpk_ER': stats['Cpk_ER'],
        'Cpk_IL': stats['Cpk_IL'],
    })

df_width = pd.DataFrame(results_width)
df_width.to_csv(output_dir / 'yield_vs_width.csv', index=False)
print(f"  ✓ Saved to {output_dir / 'yield_vs_width.csv'}")

# ============================================================================
# EXPERIMENT 2: Individual Parameter Sensitivity (Tornado Diagram)
# ============================================================================

print("\n[2/4] Analyzing individual parameter sensitivity...")

# Baseline variations
VARIATIONS_NOMINAL = {
    'width_sigma': 18e-9,
    'height_sigma': 12e-9,
    'gap_sigma': 6e-9,
    'length_sigma': 60e-9,
    'correlation_length': 100e-6,
}

# Test each parameter at ±50% from nominal
sensitivity_results = []

# Baseline
metrics_base = run_monte_carlo(
    design=DESIGN,
    variations=VARIATIONS_NOMINAL,
    correlation_matrix=CORRELATION_MATRIX,
    specs=SPECS,
    n_samples=2000,
    random_seed=MONTE_CARLO['random_seed'],
    verbose=False
)
df_base, stats_base = analyze_yield(metrics_base, SPECS, verbose=False)
baseline_yield = stats_base['yield_overall']

print(f"  Baseline yield: {baseline_yield:.2f}%")

# Test each parameter
parameters = ['width_sigma', 'height_sigma', 'gap_sigma', 'length_sigma']
param_labels = ['Width σ', 'Height σ', 'Gap σ', 'Length σ']

for param, label in zip(parameters, param_labels):
    # -50% case
    vars_low = VARIATIONS_NOMINAL.copy()
    vars_low[param] = VARIATIONS_NOMINAL[param] * 0.5
    
    metrics_low = run_monte_carlo(
        design=DESIGN,
        variations=vars_low,
        correlation_matrix=CORRELATION_MATRIX,
        specs=SPECS,
        n_samples=2000,
        random_seed=MONTE_CARLO['random_seed'],
        verbose=False
    )
    df_low, stats_low = analyze_yield(metrics_low, SPECS, verbose=False)
    
    # +50% case
    vars_high = VARIATIONS_NOMINAL.copy()
    vars_high[param] = VARIATIONS_NOMINAL[param] * 1.5
    
    metrics_high = run_monte_carlo(
        design=DESIGN,
        variations=vars_high,
        correlation_matrix=CORRELATION_MATRIX,
        specs=SPECS,
        n_samples=2000,
        random_seed=MONTE_CARLO['random_seed'],
        verbose=False
    )
    df_high, stats_high = analyze_yield(metrics_high, SPECS, verbose=False)
    
    delta_low = stats_low['yield_overall'] - baseline_yield
    delta_high = stats_high['yield_overall'] - baseline_yield
    sensitivity = max(abs(delta_low), abs(delta_high))
    
    sensitivity_results.append({
        'parameter': label,
        'baseline_value_nm': VARIATIONS_NOMINAL[param] * 1e9,
        'yield_at_minus_50': stats_low['yield_overall'],
        'yield_baseline': baseline_yield,
        'yield_at_plus_50': stats_high['yield_overall'],
        'sensitivity': sensitivity,
    })
    
    print(f"  {label:12s}: -50%→{stats_low['yield_overall']:5.1f}%, "
          f"baseline→{baseline_yield:5.1f}%, +50%→{stats_high['yield_overall']:5.1f}% "
          f"(sensitivity: {sensitivity:.1f}%)")

df_sensitivity = pd.DataFrame(sensitivity_results)
df_sensitivity = df_sensitivity.sort_values('sensitivity', ascending=False)
df_sensitivity.to_csv(output_dir / 'parameter_sensitivity.csv', index=False)
print(f"  ✓ Saved to {output_dir / 'parameter_sensitivity.csv'}")

# ============================================================================
# EXPERIMENT 3: Design Margin Requirements
# ============================================================================

print("\n[3/4] Analyzing design margin requirements...")

# Test different ER specs to find required nominal ER
er_specs = [25, 27, 28, 29, 30, 32, 35]
margin_results = []

for er_spec in tqdm(er_specs, desc="ER spec sweep"):
    specs_test = SPECS.copy()
    specs_test['target_ER'] = er_spec
    
    metrics = run_monte_carlo(
        design=DESIGN,
        variations=VARIATIONS_NOMINAL,
        correlation_matrix=CORRELATION_MATRIX,
        specs=specs_test,
        n_samples=2000,
        random_seed=MONTE_CARLO['random_seed'],
        verbose=False
    )
    
    df_test, stats_test = analyze_yield(metrics, specs_test, verbose=False)
    
    nominal_ER = stats_test['ER_mean']
    margin = nominal_ER - er_spec
    
    margin_results.append({
        'ER_spec': er_spec,
        'nominal_ER_required': nominal_ER,
        'design_margin': margin,
        'yield_70pct': stats_test['yield_overall'] if stats_test['yield_overall'] > 60 else np.nan,
        'Cpk': stats_test['Cpk_ER'],
    })

df_margin = pd.DataFrame(margin_results)
df_margin.to_csv(output_dir / 'design_margin.csv', index=False)
print(f"  ✓ Saved to {output_dir / 'design_margin.csv'}")

# ============================================================================
# EXPERIMENT 4: Design Space Map (ER spec vs Width sigma)
# ============================================================================

print("\n[4/4] Generating design space map...")

er_specs_map = [25, 27, 30, 32, 35]
width_sigmas_map = [10e-9, 12e-9, 15e-9, 18e-9, 22e-9]

yield_matrix = np.zeros((len(er_specs_map), len(width_sigmas_map)))

for i, er_spec in enumerate(tqdm(er_specs_map, desc="Design space")):
    for j, width_sigma in enumerate(width_sigmas_map):
        specs_test = SPECS.copy()
        specs_test['target_ER'] = er_spec
        
        vars_test = VARIATIONS_NOMINAL.copy()
        vars_test['width_sigma'] = width_sigma
        
        metrics = run_monte_carlo(
            design=DESIGN,
            variations=vars_test,
            correlation_matrix=CORRELATION_MATRIX,
            specs=specs_test,
            n_samples=1000,  # Fewer samples for speed
            random_seed=MONTE_CARLO['random_seed'],
            verbose=False
        )
        
        df_test, stats_test = analyze_yield(metrics, specs_test, verbose=False)
        yield_matrix[i, j] = stats_test['yield_overall']

# Save matrix
np.save(output_dir / 'yield_matrix.npy', yield_matrix)
np.save(output_dir / 'er_specs_map.npy', np.array(er_specs_map))
np.save(output_dir / 'width_sigmas_map.npy', np.array(width_sigmas_map) * 1e9)

print(f"  ✓ Saved to {output_dir / 'yield_matrix.npy'}")

print("\n" + "="*70)
print("DATA GENERATION COMPLETE")
print("="*70)
print(f"\nGenerated files in '{output_dir}/':")
print("  • yield_vs_width.csv")
print("  • parameter_sensitivity.csv")
print("  • design_margin.csv")
print("  • yield_matrix.npy")
print("\nNext: Run 'plot_design_rules.py' to visualize")