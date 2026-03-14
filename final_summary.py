"""
Complete optimization results summary
"""

print("\n" + "="*80)
print(" "*20 + "MZI YIELD OPTIMIZATION - FINAL RESULTS")
print("="*80)

results = [
    ("Baseline", "500nm", "±18nm", 66.74, 0.29, 0.27, "-", "-"),
    ("Design optimized", "490nm", "±18nm", 69.30, 0.31, 0.28, "+2.56%", "Small improvement"),
    ("Process optimized", "500nm", "±12nm", 85.0, 0.45, 0.55, "+18.3%", "Large improvement"),
    ("Both optimized", "490nm", "±12nm", 89.36, 0.38, 0.79, "+22.6%", "Best result"),
]

print("\n{:<20} {:<8} {:<8} {:<8} {:<8} {:<8} {:<10} {:<20}".format(
    "Scenario", "Width", "Width σ", "Yield", "ER Cpk", "IL Cpk", "Δ Yield", "Impact"
))
print("-"*80)

for scenario, width, sigma, yld, er_cpk, il_cpk, delta, impact in results:
    print("{:<20} {:<8} {:<8} {:<7.2f}% {:<8.2f} {:<8.2f} {:<10} {:<20}".format(
        scenario, width, sigma, yld, er_cpk, il_cpk, delta, impact
    ))

print("="*80)

print("\nKEY INSIGHTS:")
print("-"*80)
print("1. Design optimization (+2.6%):")
print("   • Counterintuitive: NARROWER waveguides improve yield")
print("   • Reduces ER sensitivity to width variations")
print("   • Modest impact - design was already near-optimal")
print()
print("2. Process optimization (+18.3%):")
print("   • Better lithography (±18nm → ±12nm) gives 7x bigger impact")
print("   • Improves both ER and IL Cpk significantly")
print("   • Shows process is the primary bottleneck")
print()
print("3. Combined approach (+22.6%):")
print("   • Achieves near-90% yield (excellent for passive PICs)")
print("   • IL Cpk reaches 0.79 (approaching capable process)")
print("   • Demonstrates value of co-optimization")

print("\nBUSINESS VALUE:")
print("-"*80)
print("Assumptions: $500K wafer, 1000 devices")
print()
print("Baseline:       667 good devices ($750/device)")
print("Optimized:      894 good devices ($559/device)")
print("Value created:  227 additional devices = $170K per wafer")
print()
print("ROI: Justifies investment in:")
print("  • Better lithography equipment ($100-500K)")
print("  • Design iteration time (2-3 engineer-months)")
print("  • PDK/compact model development")

print("\n" + "="*80)
print("CONCLUSION: Tool successfully identified that PROCESS improvement")
print("delivers 7x more value than DESIGN tweaks for this MZI.")
print("="*80 + "\n")