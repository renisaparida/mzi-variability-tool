"""
Publication-quality sensitivity analysis plots
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyArrowPatch
from pathlib import Path

# ── style ────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family': 'Arial',
    'font.size': 11,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'grid.alpha': 0.25,
    'grid.linestyle': '--',
    'figure.dpi': 150,
})

BLUE   = '#1F4E79'
LBLUE  = '#2E86AB'
RED    = '#C73E1D'
ORANGE = '#F18F01'
GREEN  = '#2D6A4F'
GRAY   = '#888888'

# ── load data ────────────────────────────────────────────────────────────────
df_sens   = pd.read_csv('design_rules/parameter_sensitivity.csv')
df_width  = pd.read_csv('design_rules/yield_vs_width.csv')
df_margin = pd.read_csv('design_rules/design_margin.csv')

df_sens = df_sens.sort_values('sensitivity', ascending=True).reset_index(drop=True)

out = Path('outputs')
out.mkdir(exist_ok=True)

# ════════════════════════════════════════════════════════════════════════════
# FIGURE 1 — 2x2 overview panel
# ════════════════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(14, 10))
gs  = gridspec.GridSpec(2, 2, hspace=0.42, wspace=0.38)

# ── A: Tornado diagram ───────────────────────────────────────────────────────
ax1 = fig.add_subplot(gs[0, 0])

params  = df_sens['parameter'].tolist()
d_minus = (df_sens['yield_at_minus_50'] - df_sens['yield_baseline']).tolist()
d_plus  = (df_sens['yield_at_plus_50']  - df_sens['yield_baseline']).tolist()
y_pos   = np.arange(len(params))

ax1.barh(y_pos, d_plus,  height=0.55, color=RED,   alpha=0.85, label='+50% variation')
ax1.barh(y_pos, d_minus, height=0.55, color=LBLUE, alpha=0.85, label='-50% variation')
ax1.axvline(0, color='black', linewidth=1.2)
ax1.set_yticks(y_pos)
ax1.set_yticklabels(params, fontsize=11)
ax1.set_xlabel('Yield Change (percentage points)', fontsize=11)
ax1.set_title('(a) Parameter Sensitivity — Tornado', fontsize=12, fontweight='bold', pad=10)
ax1.legend(fontsize=9, loc='lower right')

# annotate sensitivity values
for i, (dm, dp) in enumerate(zip(d_minus, d_plus)):
    val = max(abs(dm), abs(dp))
    ax1.text(max(dp, 0) + 0.3, i, f'{val:.1f}pp', va='center', fontsize=9, color=GRAY)

# ── B: Yield vs width sigma ──────────────────────────────────────────────────
ax2 = fig.add_subplot(gs[0, 1])

w   = df_width['width_sigma_nm']
y   = df_width['yield_overall']
yer = df_width['yield_ER']
yil = df_width['yield_IL']

ax2.plot(w, y,   'o-', color=BLUE,   lw=2.5, ms=7, label='Overall yield',  zorder=4)
ax2.plot(w, yer, 's--',color=RED,    lw=1.8, ms=6, label='ER yield only',  zorder=3, alpha=0.8)
ax2.plot(w, yil, '^--',color=ORANGE, lw=1.8, ms=6, label='IL yield only',  zorder=3, alpha=0.8)

ax2.axhline(90, color=GREEN,  ls=':', lw=1.5, alpha=0.7, label='90% target')
ax2.axhline(70, color=ORANGE, ls=':', lw=1.5, alpha=0.7, label='70% target')

# shade the "good" region
ax2.fill_between(w, 90, 100, alpha=0.06, color=GREEN)
ax2.fill_between(w, 70, 90,  alpha=0.06, color=ORANGE)
ax2.fill_between(w, 0,  70,  alpha=0.06, color=RED)

# annotate current design point
cur_w, cur_y = 12, df_width.loc[df_width['width_sigma_nm']==12.0, 'yield_overall'].values[0]
ax2.annotate(f'This work\n({cur_w}nm, {cur_y:.0f}%)',
             xy=(cur_w, cur_y), xytext=(cur_w+4, cur_y-8),
             fontsize=9, color=BLUE, fontweight='bold',
             arrowprops=dict(arrowstyle='->', color=BLUE, lw=1.2))

ax2.set_xlabel('Width Variation σ (nm)', fontsize=11)
ax2.set_ylabel('Yield (%)', fontsize=11)
ax2.set_title('(b) Yield vs. Process Capability', fontsize=12, fontweight='bold', pad=10)
ax2.legend(fontsize=9, loc='upper right')
ax2.set_ylim(35, 102)
ax2.set_xlim(6, 32)

# ── C: Cpk vs width sigma ────────────────────────────────────────────────────
ax3 = fig.add_subplot(gs[1, 0])

ax3.plot(w, df_width['Cpk_ER'], 'o-', color=RED,   lw=2.2, ms=7, label='Cpk (ER)')
ax3.plot(w, df_width['Cpk_IL'], 's-', color=LBLUE, lw=2.2, ms=7, label='Cpk (IL)')

ax3.axhline(1.0, color=GREEN,  ls='--', lw=1.5, label='Cpk=1.0 (capable)')
ax3.axhline(0.5, color=ORANGE, ls='--', lw=1.5, label='Cpk=0.5 (marginal)')

ax3.fill_between(w, 1.0, ax3.get_ylim()[1] if ax3.get_ylim()[1]>1 else 1.5,
                 alpha=0.06, color=GREEN)
ax3.fill_between(w, 0.5, 1.0, alpha=0.06, color=ORANGE)
ax3.fill_between(w, 0,   0.5, alpha=0.06, color=RED)

ax3.set_xlabel('Width Variation σ (nm)', fontsize=11)
ax3.set_ylabel('Process Capability Index (Cpk)', fontsize=11)
ax3.set_title('(c) Process Capability vs. Width Variation', fontsize=12, fontweight='bold', pad=10)
ax3.legend(fontsize=9)
ax3.set_xlim(6, 32)
ax3.set_ylim(-0.05, 0.85)

# ── D: Design margin ─────────────────────────────────────────────────────────
ax4 = fig.add_subplot(gs[1, 1])

specs   = df_margin['ER_spec']
margins = df_margin['design_margin']
cpks    = df_margin['Cpk']

color_bars = [GREEN if m >= 6 else ORANGE if m >= 4 else RED for m in margins]
bars = ax4.bar(specs, margins, color=color_bars, alpha=0.8, width=1.2, edgecolor='white', lw=1)

ax4.axhline(6, color=GREEN,  ls='--', lw=1.5, label='6 dB margin (70% yield)')
ax4.axhline(8, color=LBLUE,  ls='--', lw=1.5, label='8 dB margin (85% yield)')

# add Cpk labels on bars
for spec, margin, cpk in zip(specs, margins, cpks):
    ax4.text(spec, margin + 0.15, f'Cpk={cpk:.2f}', ha='center', fontsize=8.5, color='#333333')

ax4.set_xlabel('ER Specification (dB)', fontsize=11)
ax4.set_ylabel('Required Design Margin (dB)', fontsize=11)
ax4.set_title('(d) Design Margin Requirements', fontsize=12, fontweight='bold', pad=10)
ax4.legend(fontsize=9)

fig.suptitle('MZI Yield Sensitivity Analysis\nSilicon Photonics — 220nm SOI, Monte Carlo N=2000',
             fontsize=13, fontweight='bold', y=1.01)

plt.savefig(out / 'sensitivity_analysis.png', dpi=300, bbox_inches='tight')
plt.close()
print("Saved: sensitivity_analysis.png")

# ════════════════════════════════════════════════════════════════════════════
# FIGURE 2 — standalone tornado (clean, for presentations)
# ════════════════════════════════════════════════════════════════════════════
fig2, ax = plt.subplots(figsize=(9, 4.5))

bar_h = 0.45
ax.barh(y_pos, d_plus,  height=bar_h, color=RED,   alpha=0.88, label='+50% variation (worse process)')
ax.barh(y_pos, d_minus, height=bar_h, color=LBLUE, alpha=0.88, label='-50% variation (better process)')
ax.axvline(0, color='black', linewidth=1.5)

ax.set_yticks(y_pos)
ax.set_yticklabels(params, fontsize=12)
ax.set_xlabel('Change in Yield (percentage points)', fontsize=12)
ax.set_title('Parameter Sensitivity — Tornado Diagram\n(Each parameter varied ±50% from nominal while others held fixed)',
             fontsize=12, fontweight='bold')
ax.legend(fontsize=10)

# add impact labels
for i, (dm, dp, sens) in enumerate(zip(d_minus, d_plus, df_sens['sensitivity'])):
    x = max(abs(dm), abs(dp))
    side = dp if abs(dp) > abs(dm) else dm
    offset = 0.4 if side > 0 else -0.4
    ha = 'left' if side > 0 else 'right'
    label = 'CRITICAL' if sens > 15 else 'Important' if sens > 5 else 'Low'
    color = RED if sens > 15 else ORANGE if sens > 5 else GRAY
    ax.text(side + offset, i, f'{sens:.1f}pp  [{label}]',
            va='center', ha=ha, fontsize=10, color=color, fontweight='bold')

ax.set_xlim(-25, 25)
plt.tight_layout()
plt.savefig(out / 'tornado_diagram.png', dpi=300, bbox_inches='tight')
plt.close()
print("Saved: tornado_diagram.png")

# ════════════════════════════════════════════════════════════════════════════
# FIGURE 3 — yield vs width with process node annotations
# ════════════════════════════════════════════════════════════════════════════
fig3, ax = plt.subplots(figsize=(10, 6))

ax.plot(w, y, 'o-', color=BLUE, lw=2.8, ms=9, zorder=5, label='Monte Carlo prediction')

# shade regions
ax.fill_between(w, 85, 100, alpha=0.08, color=GREEN,  label='High yield region (>85%)')
ax.fill_between(w, 70, 85,  alpha=0.08, color=ORANGE, label='Moderate yield (70-85%)')
ax.fill_between(w, 0,  70,  alpha=0.08, color=RED,    label='Low yield (<70%)')

ax.axhline(90, color=GREEN,  ls=':', lw=1.8, alpha=0.8)
ax.axhline(70, color=ORANGE, ls=':', lw=1.8, alpha=0.8)

# process node annotations
process_nodes = [
    (4.8,  96, '193nm DUV\n(Xing 2020)\nσ≈4.8nm',  LBLUE),
    (5.0,  92, '193nm DUV\n(Bogaerts 2022)\nσ≈5nm',   GREEN),
    (10.0, 76, '248nm DUV\n(Lu 2017)\nσ≈10nm',       ORANGE),
    (12.0, cur_y, f'This work\nσ=12nm',               BLUE),
]

for x_node, y_node, label, col in process_nodes:
    ax.scatter([x_node], [y_node], s=120, color=col, zorder=6, edgecolors='white', lw=1.5)
    ax.annotate(label, xy=(x_node, y_node),
                xytext=(x_node + 1.5, y_node - 6),
                fontsize=8.5, color=col, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=col, lw=1.0))

ax.set_xlabel('Waveguide Width Variation σ (nm)', fontsize=13)
ax.set_ylabel('Predicted Manufacturing Yield (%)', fontsize=13)
ax.set_title('Manufacturing Yield vs. Process Capability\nAnnotated with Published Fab Process Nodes',
             fontsize=13, fontweight='bold')
ax.legend(fontsize=10, loc='upper right')
ax.set_xlim(4, 32)
ax.set_ylim(35, 102)
ax.tick_params(labelsize=11)

plt.tight_layout()
plt.savefig(out / 'yield_vs_process_annotated.png', dpi=300, bbox_inches='tight')
plt.close()
print("Saved: yield_vs_process_annotated.png")

print("\nAll 3 figures saved to outputs/")