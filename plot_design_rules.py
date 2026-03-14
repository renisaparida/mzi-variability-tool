"""
Create publication-quality design rule visualizations
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 100
plt.rcParams['font.size'] = 10

output_dir = Path("design_rules")
figures_dir = output_dir / "figures"
figures_dir.mkdir(exist_ok=True)

print("="*70)
print("PLOTTING DESIGN RULES")
print("="*70)

# ============================================================================
# PLOT 1: Yield vs. Width Variation (Key Result)
# ============================================================================

print("\n[1/4] Plotting yield vs. width variation...")

df_width = pd.read_csv(output_dir / 'yield_vs_width.csv')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Left plot: Overall yield
ax1.plot(df_width['width_sigma_nm'], df_width['yield_overall'], 
         'o-', linewidth=2.5, markersize=8, color='#2E86AB', label='Overall Yield')
ax1.axhline(90, color='green', linestyle='--', alpha=0.5, label='90% target')
ax1.axhline(70, color='orange', linestyle='--', alpha=0.5, label='70% target')
ax1.axhline(50, color='red', linestyle='--', alpha=0.5, label='50% target')

ax1.set_xlabel('Width Variation σ (nm)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Yield (%)', fontsize=12, fontweight='bold')
ax1.set_title('Process Capability Requirements', fontsize=13, fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)
ax1.set_xlim(5, 32)
ax1.set_ylim(30, 100)

# Add annotations for key points
for _, row in df_width.iterrows():
    if row['yield_overall'] >= 89 and row['yield_overall'] <= 91:
        ax1.annotate(f"{row['width_sigma_nm']:.0f}nm → {row['yield_overall']:.0f}%",
                    xy=(row['width_sigma_nm'], row['yield_overall']),
                    xytext=(row['width_sigma_nm']-3, row['yield_overall']+5),
                    fontsize=9, color='green', fontweight='bold',
                    arrowprops=dict(arrowstyle='->', color='green', lw=1.5))
        break

# Right plot: ER vs IL contribution
ax2.plot(df_width['width_sigma_nm'], df_width['yield_ER'], 
         's-', linewidth=2, markersize=7, color='#A23B72', label='ER Yield')
ax2.plot(df_width['width_sigma_nm'], df_width['yield_IL'], 
         '^-', linewidth=2, markersize=7, color='#F18F01', label='IL Yield')
ax2.plot(df_width['width_sigma_nm'], df_width['yield_overall'], 
         'o-', linewidth=2.5, markersize=8, color='#2E86AB', label='Overall')

ax2.set_xlabel('Width Variation σ (nm)', fontsize=12, fontweight='bold')
ax2.set_ylabel('Yield (%)', fontsize=12, fontweight='bold')
ax2.set_title('ER vs. IL Yield Components', fontsize=13, fontweight='bold')
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3)
ax2.set_xlim(5, 32)
ax2.set_ylim(30, 100)

plt.tight_layout()
plt.savefig(figures_dir / '1_yield_vs_width.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"  ✓ Saved {figures_dir / '1_yield_vs_width.png'}")

# ============================================================================
# PLOT 2: Tornado Diagram (Sensitivity Ranking)
# ============================================================================

print("\n[2/4] Plotting parameter sensitivity...")

df_sens = pd.read_csv(output_dir / 'parameter_sensitivity.csv')

fig, ax = plt.subplots(figsize=(10, 6))

# Calculate deltas
df_sens['delta_minus'] = df_sens['yield_at_minus_50'] - df_sens['yield_baseline']
df_sens['delta_plus'] = df_sens['yield_at_plus_50'] - df_sens['yield_baseline']

# Sort by sensitivity
df_sens = df_sens.sort_values('sensitivity', ascending=True)

y_pos = np.arange(len(df_sens))

# Plot bars
ax.barh(y_pos, df_sens['delta_plus'], left=0, height=0.8, 
        color='#C1666B', label='+50% variation', alpha=0.8)
ax.barh(y_pos, df_sens['delta_minus'], left=0, height=0.8, 
        color='#48A9A6', label='-50% variation', alpha=0.8)

ax.set_yticks(y_pos)
ax.set_yticklabels(df_sens['parameter'])
ax.set_xlabel('Yield Change (percentage points)', fontsize=12, fontweight='bold')
ax.set_title('Parameter Sensitivity Analysis (Tornado Diagram)', fontsize=13, fontweight='bold')
ax.axvline(0, color='black', linewidth=1.5)
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3, axis='x')

# Add baseline values as text
for i, row in df_sens.iterrows():
    idx = list(df_sens.index).index(i)
    ax.text(0.5, idx, f"  σ={row['baseline_value_nm']:.0f}nm", 
            va='center', fontsize=9, color='black', fontweight='bold')

plt.tight_layout()
plt.savefig(figures_dir / '2_sensitivity_tornado.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"  ✓ Saved {figures_dir / '2_sensitivity_tornado.png'}")

# ============================================================================
# PLOT 3: Design Margin Requirements
# ============================================================================

print("\n[3/4] Plotting design margin requirements...")

df_margin = pd.read_csv(output_dir / 'design_margin.csv')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Left: Nominal ER required vs. spec
ax1.plot(df_margin['ER_spec'], df_margin['nominal_ER_required'], 
         'o-', linewidth=2.5, markersize=8, color='#2E86AB')
ax1.plot([25, 35], [25, 35], '--', color='gray', alpha=0.5, label='No margin (1:1)')

ax1.set_xlabel('ER Specification (dB)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Nominal ER Required (dB)', fontsize=12, fontweight='bold')
ax1.set_title('Design Overhead Requirements', fontsize=13, fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)

# Add margin annotations
for _, row in df_margin.iterrows():
    if row['ER_spec'] in [27, 30, 32]:
        ax1.annotate(f"+{row['design_margin']:.1f}dB margin",
                    xy=(row['ER_spec'], row['nominal_ER_required']),
                    xytext=(row['ER_spec']+0.5, row['nominal_ER_required']+1),
                    fontsize=9, arrowprops=dict(arrowstyle='->', lw=1))

# Right: Margin vs. Cpk
ax2.plot(df_margin['design_margin'], df_margin['Cpk'], 
         's-', linewidth=2.5, markersize=8, color='#A23B72')
ax2.axhline(1.0, color='green', linestyle='--', alpha=0.5, label='Cpk=1.0 (capable)')
ax2.axhline(0.5, color='orange', linestyle='--', alpha=0.5, label='Cpk=0.5 (marginal)')

ax2.set_xlabel('Design Margin (dB)', fontsize=12, fontweight='bold')
ax2.set_ylabel('Process Capability (Cpk)', fontsize=12, fontweight='bold')
ax2.set_title('Margin vs. Process Capability', fontsize=13, fontweight='bold')
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(figures_dir / '3_design_margin.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"  ✓ Saved {figures_dir / '3_design_margin.png'}")

# ============================================================================
# PLOT 4: Design Space Heatmap
# ============================================================================

print("\n[4/4] Plotting design space heatmap...")

yield_matrix = np.load(output_dir / 'yield_matrix.npy')
er_specs = np.load(output_dir / 'er_specs_map.npy')
width_sigmas = np.load(output_dir / 'width_sigmas_map.npy')

fig, ax = plt.subplots(figsize=(10, 7))

im = ax.imshow(yield_matrix, cmap='RdYlGn', aspect='auto', 
               vmin=30, vmax=95, origin='lower')

# Set ticks
ax.set_xticks(range(len(width_sigmas)))
ax.set_xticklabels([f"±{int(s)}nm" for s in width_sigmas])
ax.set_yticks(range(len(er_specs)))
ax.set_yticklabels([f"{int(s)}dB" for s in er_specs])

ax.set_xlabel('Width Variation (1σ)', fontsize=12, fontweight='bold')
ax.set_ylabel('ER Specification', fontsize=12, fontweight='bold')
ax.set_title('Design Space: Achievable Yield Map', fontsize=13, fontweight='bold')

# Add text annotations
for i in range(len(er_specs)):
    for j in range(len(width_sigmas)):
        text = ax.text(j, i, f'{yield_matrix[i, j]:.0f}%',
                      ha="center", va="center", color="black", fontsize=9, fontweight='bold')

# Colorbar
cbar = plt.colorbar(im, ax=ax)
cbar.set_label('Yield (%)', fontsize=11, fontweight='bold')

# Add guidelines
ax.axhline(2.5, color='white', linestyle='--', linewidth=2, alpha=0.7)
ax.text(2.5, 2.7, 'Practical specs →', color='white', fontsize=10, 
        fontweight='bold', ha='center')

plt.tight_layout()
plt.savefig(figures_dir / '4_design_space_map.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"  ✓ Saved {figures_dir / '4_design_space_map.png'}")

print("\n" + "="*70)
print("PLOTTING COMPLETE")
print("="*70)
print(f"\nGenerated figures in '{figures_dir}/':")
print("  • 1_yield_vs_width.png")
print("  • 2_sensitivity_tornado.png")
print("  • 3_design_margin.png")
print("  • 4_design_space_map.png")