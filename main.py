"""
Main execution script for MZI Variability Analysis Tool

This tool performs:
1. Nominal design simulation
2. Monte Carlo analysis with process variations
3. Yield calculation and statistical analysis
4. Design optimization for maximum yield
5. Comprehensive visualization

Author: [Your Name]
Date: 2026
"""

import numpy as np
import pandas as pd
from pathlib import Path
import time

# Import configuration
from config import DESIGN, SPECS, VARIATIONS, CORRELATION_MATRIX, MONTE_CARLO, OPTIMIZATION, OUTPUT

# Import modules
from models import simulate_mzi
from simulation import run_monte_carlo, extract_metrics
from analysis import analyze_yield, optimize_design
from visualization import plot_yield_analysis, plot_nominal_response

def main():
    """
    Main execution function
    """
    print("\n" + "="*70)
    print(" "*15 + "MZI VARIABILITY-AWARE DESIGN TOOL")
    print("="*70)
    print("\nObjective: Predict and optimize yield for Mach-Zehnder Interferometer")
    print("          optical switches under process variations")
    print("\n" + "="*70)
    
    # Create output directory
    output_dir = OUTPUT['output_dir']
    Path(output_dir).mkdir(exist_ok=True)
    
    # ========================================================================
    # STEP 1: Simulate Nominal Design
    # ========================================================================
    print("\n[STEP 1/5] Simulating nominal design...")
    start_time = time.time()
    
    wavelengths = np.linspace(
        DESIGN['wavelength_range'][0],
        DESIGN['wavelength_range'][1],
        DESIGN['wavelength_points']
    )
    
    # Nominal simulation (no variations)
    lam_nom, P_out1_nom, P_out2_nom = simulate_mzi(
        width_deltas=[0, 0, 0, 0],
        height_delta=0,
        gap_deltas=[0, 0],
        length_delta=0,
        wavelengths=wavelengths,
        design=DESIGN
    )
    
    metrics_nom = extract_metrics(wavelengths, P_out1_nom, P_out2_nom)
    
    print(f"  Nominal ER:  {metrics_nom['ER_out1']:.2f} dB")
    print(f"  Nominal IL:  {metrics_nom['IL_out1']:.2f} dB")
    print(f"  Peak λ:      {metrics_nom['lambda_peak_out1']*1e9:.2f} nm")
    print(f"  Completed in {time.time() - start_time:.2f}s")
    
    # Plot nominal response
    plot_nominal_response(wavelengths, P_out1_nom, P_out2_nom, output_dir)
    print(f"  ✓ Nominal response plot saved")
    
    # ========================================================================
    # STEP 2: Run Monte Carlo Simulation
    # ========================================================================
    print(f"\n[STEP 2/5] Running Monte Carlo simulation ({MONTE_CARLO['n_samples']} samples)...")
    start_time = time.time()
    
    all_metrics = run_monte_carlo(
        design=DESIGN,
        variations=VARIATIONS,
        correlation_matrix=CORRELATION_MATRIX,
        specs=SPECS,
        n_samples=MONTE_CARLO['n_samples'],
        random_seed=MONTE_CARLO['random_seed'],
        verbose=True
    )
    
    print(f"  Completed in {time.time() - start_time:.2f}s")
    
    # ========================================================================
    # STEP 3: Analyze Yield
    # ========================================================================
    print(f"\n[STEP 3/5] Analyzing yield...")
    start_time = time.time()
    
    df, yield_stats = analyze_yield(
        all_metrics=all_metrics,
        specs=SPECS,
        verbose=True
    )
    
    # Save results to CSV
    if OUTPUT['save_csv']:
        csv_path = f"{output_dir}/results.csv"
        df.to_csv(csv_path, index=False)
        print(f"  ✓ Results saved to {csv_path}")
    
    print(f"  Completed in {time.time() - start_time:.2f}s")
    
    # ========================================================================
    # STEP 4: Generate Visualizations
    # ========================================================================
    print(f"\n[STEP 4/5] Generating visualizations...")
    start_time = time.time()
    
    plot_yield_analysis(
        df=df,
        specs=SPECS,
        yield_stats=yield_stats,
        output_dir=output_dir
    )
    
    print(f"  Completed in {time.time() - start_time:.2f}s")
    
   # ========================================================================
    # STEP 5: Optimize Design
    # ========================================================================
    '''print(f"\n[STEP 5/5] Optimizing design for maximum yield...")
    start_time = time.time()
    
    optimization_result = optimize_design(
        design=DESIGN,
        variations=VARIATIONS,
        correlation_matrix=CORRELATION_MATRIX,
        specs=SPECS,
        width_bounds=OPTIMIZATION['width_offset_bounds'],
        length_bounds=OPTIMIZATION['length_offset_bounds'],
        maxiter=OPTIMIZATION['maxiter'],
        popsize=OPTIMIZATION['popsize'],
        n_eval_samples=OPTIMIZATION['quick_eval_samples'],
        random_seed=MONTE_CARLO['random_seed'],
        verbose=True
    )
    
    print(f"  Completed in {time.time() - start_time:.2f}s")'''
    
    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    print("\n" + "="*70)
    print(" "*25 + "FINAL SUMMARY")
    print("="*70)
    
    print(f"\nNominal Design:")
    print(f"  ER: {metrics_nom['ER_out1']:.2f} dB")
    print(f"  IL: {metrics_nom['IL_out1']:.2f} dB")
    
    print(f"\nProcess Variations Applied:")
    print(f"  Width:  ±{VARIATIONS['width_sigma']*1e9:.1f} nm (1σ)")
    print(f"  Height: ±{VARIATIONS['height_sigma']*1e9:.1f} nm (1σ)")
    print(f"  Gap:    ±{VARIATIONS['gap_sigma']*1e9:.1f} nm (1σ)")
    print(f"  Length: ±{VARIATIONS['length_sigma']*1e9:.1f} nm (1σ)")
    
    print(f"\nYield (Current Design):")
    print(f"  Overall: {yield_stats['yield_overall']:.2f}%")
    print(f"  ER>20dB: {yield_stats['yield_ER']:.2f}%")
    print(f"  IL<1dB:  {yield_stats['yield_IL']:.2f}%")
    
    '''print(f"\nOptimized Design:")
    print(f"  Width offset:  {optimization_result['optimal_width_offset_nm']:+.2f} nm")
    print(f"  Length offset: {optimization_result['optimal_length_offset_nm']:+.2f} nm")
    print(f"  Predicted yield: {optimization_result['optimal_yield']:.2f}%")
    print(f"  Improvement: {optimization_result['optimal_yield'] - yield_stats['yield_overall']:+.2f}%")'''
    
    print(f"\nOutputs:")
    print(f"  Plots: {output_dir}/mzi_yield_analysis.png")
    print(f"  Plots: {output_dir}/nominal_response.png")
    if OUTPUT['save_csv']:
        print(f"  Data:  {output_dir}/results.csv")
    
    # Save text report
    report_path = f"{output_dir}/report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("MZI VARIABILITY ANALYSIS REPORT\n")
        f.write("="*70 + "\n\n")
        f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("NOMINAL DESIGN\n")
        f.write("-"*70 + "\n")
        f.write(f"Waveguide width:  {DESIGN['waveguide_width']*1e9:.1f} nm\n")
        f.write(f"Waveguide height: {DESIGN['waveguide_height']*1e9:.1f} nm\n")
        f.write(f"Coupler gap:      {DESIGN['coupler_gap']*1e9:.1f} nm\n")
        f.write(f"Arm length diff:  {DESIGN['arm_length_diff']*1e6:.1f} μm\n")
        f.write(f"ER (nominal):     {metrics_nom['ER_out1']:.2f} dB\n")
        f.write(f"IL (nominal):     {metrics_nom['IL_out1']:.2f} dB\n\n")
        
        f.write("PROCESS VARIATIONS\n")
        f.write("-"*70 + "\n")
        f.write(f"Width variation:  ±{VARIATIONS['width_sigma']*1e9:.1f} nm (1σ)\n")
        f.write(f"Height variation: ±{VARIATIONS['height_sigma']*1e9:.1f} nm (1σ)\n")
        f.write(f"Gap variation:    ±{VARIATIONS['gap_sigma']*1e9:.1f} nm (1σ)\n")
        f.write(f"Length variation: ±{VARIATIONS['length_sigma']*1e9:.1f} nm (1σ)\n\n")
        
        f.write("YIELD RESULTS\n")
        f.write("-"*70 + "\n")
        f.write(f"Monte Carlo samples: {MONTE_CARLO['n_samples']}\n")
        f.write(f"Overall yield:       {yield_stats['yield_overall']:.2f}%\n")
        f.write(f"ER yield:            {yield_stats['yield_ER']:.2f}%\n")
        f.write(f"IL yield:            {yield_stats['yield_IL']:.2f}%\n")
        f.write(f"ER Cpk:              {yield_stats['Cpk_ER']:.2f}\n")
        f.write(f"IL Cpk:              {yield_stats['Cpk_IL']:.2f}\n\n")
        
        '''f.write("OPTIMIZED DESIGN\n")
        f.write("-"*70 + "\n")
        f.write(f"Width offset:    {optimization_result['optimal_width_offset_nm']:+.2f} nm\n")
        f.write(f"Length offset:   {optimization_result['optimal_length_offset_nm']:+.2f} nm\n")
        f.write(f"Predicted yield: {optimization_result['optimal_yield']:.2f}%\n")
        f.write(f"Improvement:     {optimization_result['optimal_yield'] - yield_stats['yield_overall']:+.2f}%\n")'''
    
    print(f"  Report: {report_path}")
    
    print("\n" + "="*70)
    print(" "*20 + "✓ ANALYSIS COMPLETE")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()