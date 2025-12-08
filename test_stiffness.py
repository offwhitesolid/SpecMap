"""
Test script for stiffness analysis functions in mathlib3.py
"""

import numpy as np
import matplotlib.pyplot as plt
from mathlib3 import fitstiffnesstospec, calculate_flank_slopes, calculate_peak_curvature, calculate_asymmetry

# Create synthetic test spectra
def create_symmetric_peak(energy_range, center=2.0, width=0.2, amplitude=1000):
    """Create a symmetric Gaussian peak"""
    energy = np.linspace(energy_range[0], energy_range[1], 200)
    intensity = amplitude * np.exp(-(energy - center)**2 / (2 * width**2))
    # Add small baseline
    intensity += 50
    return energy, intensity

def create_asymmetric_peak(energy_range, center=2.0, left_width=0.15, right_width=0.3, amplitude=1000):
    """Create an asymmetric peak (steeper left side)"""
    energy = np.linspace(energy_range[0], energy_range[1], 200)
    intensity = np.zeros_like(energy)
    
    # Left side (steeper)
    left_mask = energy < center
    intensity[left_mask] = amplitude * np.exp(-(energy[left_mask] - center)**2 / (2 * left_width**2))
    
    # Right side (broader)
    right_mask = energy >= center
    intensity[right_mask] = amplitude * np.exp(-(energy[right_mask] - center)**2 / (2 * right_width**2))
    
    # Add small baseline
    intensity += 50
    return energy, intensity

# Test 1: Symmetric peak
print("=" * 60)
print("Test 1: Symmetric Gaussian Peak")
print("=" * 60)
energy1, intensity1 = create_symmetric_peak([1.0, 3.0], center=2.0, width=0.2, amplitude=1000)

# Run stiffness analysis
E_max, I_max, a_L, a_R, S_asym, curvature, _ = fitstiffnesstospec(0, len(energy1), energy1, intensity1)

print(f"Peak Energy (E_max): {E_max:.4f} eV")
print(f"Peak Intensity (I_max): {I_max:.2f} counts")
print(f"Left Stiffness (a_L): {a_L:.2f} counts/eV")
print(f"Right Stiffness (a_R): {a_R:.2f} counts/eV")
print(f"Asymmetry (S_asym): {S_asym:.4f}")
print(f"Curvature: {curvature:.2f} counts/eV²")
print(f"\nExpected: S_asym ≈ 0 (symmetric peak)")
print(f"Expected: |a_L| ≈ |a_R| (similar slopes)")

# Test 2: Asymmetric peak
print("\n" + "=" * 60)
print("Test 2: Asymmetric Peak (Steeper Left Side)")
print("=" * 60)
energy2, intensity2 = create_asymmetric_peak([1.0, 3.0], center=2.0, left_width=0.15, right_width=0.3, amplitude=1000)

# Run stiffness analysis
E_max2, I_max2, a_L2, a_R2, S_asym2, curvature2, _ = fitstiffnesstospec(0, len(energy2), energy2, intensity2)

print(f"Peak Energy (E_max): {E_max2:.4f} eV")
print(f"Peak Intensity (I_max): {I_max2:.2f} counts")
print(f"Left Stiffness (a_L): {a_L2:.2f} counts/eV")
print(f"Right Stiffness (a_R): {a_R2:.2f} counts/eV")
print(f"Asymmetry (S_asym): {S_asym2:.4f}")
print(f"Curvature: {curvature2:.2f} counts/eV²")
print(f"\nExpected: S_asym < 0 (steeper left side means larger a_L)")
print(f"Expected: |a_L| > |a_R| (steeper left flank)")

# Test 3: Direct component testing
print("\n" + "=" * 60)
print("Test 3: Component Function Testing")
print("=" * 60)

# Test flank slope calculation
a_L_test, a_R_test, E_left, E_right = calculate_flank_slopes(energy1, intensity1, peak_fraction=0.5)
print(f"Flank slopes (symmetric): a_L={a_L_test:.2f}, a_R={a_R_test:.2f}")
print(f"Baseline points: E_left={E_left:.4f}, E_right={E_right:.4f}")

# Test curvature calculation
curv_test, E_max_test, I_max_test = calculate_peak_curvature(energy1, intensity1, window_fraction=0.1)
print(f"Peak curvature: {curv_test:.2f} counts/eV²")
print(f"Peak position: E_max={E_max_test:.4f}, I_max={I_max_test:.2f}")

# Test asymmetry calculation
S_asym_test = calculate_asymmetry(a_L_test, a_R_test)
print(f"Asymmetry metric: {S_asym_test:.4f}")

# Visualization
print("\n" + "=" * 60)
print("Creating visualization plots...")
print("=" * 60)

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Plot 1: Symmetric peak
ax1 = axes[0, 0]
ax1.plot(energy1, intensity1, 'b-', linewidth=2, label='Symmetric Peak')
ax1.axvline(E_max, color='r', linestyle='--', label=f'E_max = {E_max:.3f} eV')
ax1.axhline(I_max, color='g', linestyle='--', alpha=0.5, label=f'I_max = {I_max:.0f}')
ax1.set_xlabel('Energy (eV)')
ax1.set_ylabel('Intensity (counts)')
ax1.set_title(f'Symmetric Peak\nS_asym = {S_asym:.4f}')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: Asymmetric peak
ax2 = axes[0, 1]
ax2.plot(energy2, intensity2, 'r-', linewidth=2, label='Asymmetric Peak')
ax2.axvline(E_max2, color='r', linestyle='--', label=f'E_max = {E_max2:.3f} eV')
ax2.axhline(I_max2, color='g', linestyle='--', alpha=0.5, label=f'I_max = {I_max2:.0f}')
ax2.set_xlabel('Energy (eV)')
ax2.set_ylabel('Intensity (counts)')
ax2.set_title(f'Asymmetric Peak (Steeper Left)\nS_asym = {S_asym2:.4f}')
ax2.legend()
ax2.grid(True, alpha=0.3)

# Plot 3: Stiffness comparison
ax3 = axes[1, 0]
x_labels = ['Test 1\n(Symmetric)', 'Test 2\n(Asymmetric)']
a_L_values = [np.abs(a_L), np.abs(a_L2)]
a_R_values = [np.abs(a_R), np.abs(a_R2)]
x_pos = np.arange(len(x_labels))
width = 0.35

ax3.bar(x_pos - width/2, a_L_values, width, label='Left Stiffness |a_L|', color='blue', alpha=0.7)
ax3.bar(x_pos + width/2, a_R_values, width, label='Right Stiffness |a_R|', color='red', alpha=0.7)
ax3.set_ylabel('Stiffness (counts/eV)')
ax3.set_title('Flank Stiffness Comparison')
ax3.set_xticks(x_pos)
ax3.set_xticklabels(x_labels)
ax3.legend()
ax3.grid(True, alpha=0.3, axis='y')

# Plot 4: Asymmetry metrics
ax4 = axes[1, 1]
S_asym_values = [S_asym, S_asym2]
colors = ['green' if abs(s) < 0.1 else 'orange' for s in S_asym_values]
ax4.bar(x_pos, S_asym_values, color=colors, alpha=0.7)
ax4.axhline(0, color='black', linestyle='-', linewidth=0.8)
ax4.set_ylabel('Asymmetry S_asym')
ax4.set_title('Peak Asymmetry\n(0 = symmetric, <0 = steeper left, >0 = steeper right)')
ax4.set_xticks(x_pos)
ax4.set_xticklabels(x_labels)
ax4.set_ylim([-1.1, 1.1])
ax4.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('stiffness_analysis_test.png', dpi=150, bbox_inches='tight')
print("Plot saved as 'stiffness_analysis_test.png'")
plt.show()

print("\n" + "=" * 60)
print("Test completed successfully!")
print("=" * 60)
