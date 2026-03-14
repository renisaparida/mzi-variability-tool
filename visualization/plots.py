"""
Plotting functions for yield analysis
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 300

def plot_nominal_response(wavelengths, P_out1, P_out2, output_dir='outputs'):
    """
    Plot nominal MZI response (no variations)
    """
    Path(output_dir).mkdir(exist_ok=True)
    
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    
    # Convert to nm and dB
    wl_nm = wavelengths * 1e9
    T1_dB = 10 * np.log10(P_out1 + 1e-12)
    T2_dB = 10 * np.log10(P_out2 + 1e-12)
    
    ax.plot(wl_nm, T1_dB, 'b-', linewidth=2, label='Output 1 (Bar)')
    ax.plot(wl_nm, T2_dB, 'r-', linewidth=2, label='Output 2 (Cross)')
    
    ax.set_xlabel('Wavelength (nm)', fontsize=12)
    ax.set_ylabel('Transmission (dB)', fontsize=12)
    ax.set_title('Nominal MZI Response (No Variations)', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/nominal_response.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_yield_analysis(df, specs, yield_stats, output_dir='outputs'):
    """
    Create comprehensive yield analysis plots
    
    Args:
        df: DataFrame with Monte Carlo results
        specs: Target specifications
        yield_stats: Dictionary with yield statistics
        output_dir: Output directory for plots
    """
    Path(output_dir).mkdir(exist_ok=True)
    
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # --- Plot 1: ER Histogram ---
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.hist(df['ER_out1'], bins=50, alpha=0.7, edgecolor='black', color='steelblue')
    ax1.axvline(specs['target_ER'], color='red', linestyle='--', linewidth=2, label=f'Spec: {specs["target_ER"]} dB')
    ax1.axvline(yield_stats['ER_mean'], color='green', linestyle='-', linewidth=2, label=f'Mean: {yield_stats["ER_mean"]:.1f} dB')
    ax1.set_xlabel('Extinction Ratio (dB)', fontsize=11)
    ax1.set_ylabel('Count', fontsize=11)
    ax1.set_title('ER Distribution', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # --- Plot 2: IL Histogram ---
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.hist(df['IL_out1'], bins=50, alpha=0.7, edgecolor='black', color='coral')
    ax2.axvline(specs['target_IL'], color='red', linestyle='--', linewidth=2, label=f'Spec: {specs["target_IL"]} dB')
    ax2.axvline(yield_stats['IL_mean'], color='green', linestyle='-', linewidth=2, label=f'Mean: {yield_stats["IL_mean"]:.2f} dB')
    ax2.set_xlabel('Insertion Loss (dB)', fontsize=11)
    ax2.set_ylabel('Count', fontsize=11)
    ax2.set_title('IL Distribution', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)
    
    # --- Plot 3: Yield Summary ---
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.axis('off')
    
    summary_text = f"""
    YIELD SUMMARY
    {'='*30}
    
    Overall Yield:  {yield_stats['yield_overall']:.1f}%
    ER Yield:       {yield_stats['yield_ER']:.1f}%
    IL Yield:       {yield_stats['yield_IL']:.1f}%
    
    ER Statistics:
      Mean: {yield_stats['ER_mean']:.2f} dB
      Std:  {yield_stats['ER_std']:.2f} dB
      Cpk:  {yield_stats['Cpk_ER']:.2f}
    
    IL Statistics:
      Mean: {yield_stats['IL_mean']:.2f} dB
      Std:  {yield_stats['IL_std']:.2f} dB
      Cpk:  {yield_stats['Cpk_IL']:.2f}
    
    Wavelength Shift:
      Mean: {yield_stats['wavelength_shift_mean_nm']:.2f} nm
      Std:  {yield_stats['wavelength_shift_std_nm']:.2f} nm
    """
    
    ax3.text(0.05, 0.95, summary_text, transform=ax3.transAxes, 
             fontsize=10, verticalalignment='top', family='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    # --- Plot 4: ER vs IL Scatter (Yield Map) ---
    ax4 = fig.add_subplot(gs[1, 0])
    
    pass_mask = df['pass_overall']
    fail_mask = ~pass_mask
    
    ax4.scatter(df.loc[pass_mask, 'ER_out1'], df.loc[pass_mask, 'IL_out1'], 
                alpha=0.6, s=20, c='green', label=f'Pass ({pass_mask.sum()})', edgecolors='none')
    ax4.scatter(df.loc[fail_mask, 'ER_out1'], df.loc[fail_mask, 'IL_out1'], 
                alpha=0.6, s=20, c='red', label=f'Fail ({fail_mask.sum()})', edgecolors='none')
    
    ax4.axvline(specs['target_ER'], color='gray', linestyle='--', linewidth=1.5, alpha=0.7)
    ax4.axhline(specs['target_IL'], color='gray', linestyle='--', linewidth=1.5, alpha=0.7)
    
    ax4.set_xlabel('Extinction Ratio (dB)', fontsize=11)
    ax4.set_ylabel('Insertion Loss (dB)', fontsize=11)
    ax4.set_title('Yield Map: ER vs IL', fontsize=12, fontweight='bold')
    ax4.legend(fontsize=9)
    ax4.grid(True, alpha=0.3)
    
    # --- Plot 5: Wavelength Shift Distribution ---
    ax5 = fig.add_subplot(gs[1, 1])
    wavelength_shift_nm = (df['lambda_peak_out1'] - 1550e-9) * 1e9
    ax5.hist(wavelength_shift_nm, bins=50, alpha=0.7, edgecolor='black', color='purple')
    ax5.axvline(0, color='red', linestyle='--', linewidth=2, label='Nominal')
    ax5.axvline(wavelength_shift_nm.mean(), color='green', linestyle='-', linewidth=2, 
                label=f'Mean: {wavelength_shift_nm.mean():.2f} nm')
    ax5.set_xlabel('Wavelength Shift (nm)', fontsize=11)
    ax5.set_ylabel('Count', fontsize=11)
    ax5.set_title('Resonance Wavelength Variation', fontsize=12, fontweight='bold')
    ax5.legend(fontsize=9)
    ax5.grid(True, alpha=0.3)
    
    # --- Plot 6: Pass/Fail Pie Chart ---
    ax6 = fig.add_subplot(gs[1, 2])
    
    sizes = [pass_mask.sum(), fail_mask.sum()]
    labels = [f'Pass\n({pass_mask.sum()} / {yield_stats["yield_overall"]:.1f}%)', 
              f'Fail\n({fail_mask.sum()} / {100-yield_stats["yield_overall"]:.1f}%)']
    colors = ['#90EE90', '#FF6B6B']
    explode = (0.05, 0)
    
    ax6.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='',
            shadow=True, startangle=90, textprops={'fontsize': 10})
    ax6.set_title('Overall Yield', fontsize=12, fontweight='bold')
    
    # --- Plot 7: Width Variation Impact on ER ---
    ax7 = fig.add_subplot(gs[2, 0])
    
    ax7.scatter(df['width_delta_arm1']*1e9, df['ER_out1'], alpha=0.5, s=10, c='blue', label='Arm 1')
    ax7.scatter(df['width_delta_arm2']*1e9, df['ER_out1'], alpha=0.5, s=10, c='red', label='Arm 2')
    ax7.axhline(specs['target_ER'], color='gray', linestyle='--', linewidth=1.5, alpha=0.7)
    ax7.set_xlabel('Width Variation (nm)', fontsize=11)
    ax7.set_ylabel('ER (dB)', fontsize=11)
    ax7.set_title('Width Variation Impact on ER', fontsize=12, fontweight='bold')
    ax7.legend(fontsize=9)
    ax7.grid(True, alpha=0.3)
    
    # --- Plot 8: Length Variation Impact on Wavelength ---
    ax8 = fig.add_subplot(gs[2, 1])
    
    ax8.scatter(df['length_delta']*1e9, wavelength_shift_nm, alpha=0.5, s=10, c='purple')
    ax8.axhline(0, color='red', linestyle='--', linewidth=1.5, alpha=0.7)
    ax8.set_xlabel('Length Variation (nm)', fontsize=11)
    ax8.set_ylabel('Wavelength Shift (nm)', fontsize=11)
    ax8.set_title('Length Variation Impact', fontsize=12, fontweight='bold')
    ax8.grid(True, alpha=0.3)
    
    # --- Plot 9: Correlation Matrix ---
    ax9 = fig.add_subplot(gs[2, 2])
    
    corr_vars = ['ER_out1', 'IL_out1', 'width_delta_arm1', 'width_delta_arm2', 
                 'height_delta', 'length_delta']
    corr_matrix = df[corr_vars].corr()
    
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                square=True, ax=ax9, cbar_kws={'shrink': 0.8})
    ax9.set_title('Parameter Correlations', fontsize=12, fontweight='bold')
    
    # Overall title
    fig.suptitle('MZI Variability-Aware Yield Analysis', fontsize=16, fontweight='bold', y=0.995)
    
    # Save
    plt.savefig(f'{output_dir}/mzi_yield_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\n✓ Plots saved to {output_dir}/mzi_yield_analysis.png")