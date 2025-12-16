"""
Test script for First and Second Derivative methods (Finite Differences)
Validates the new derivative1 and derivative2 methods added to mathlib3.py

Author: Auto-generated
Date: December 16, 2025
"""

import numpy as np
import matplotlib.pyplot as plt
import mathlib3

# ============================================================================
# Test Functions
# ============================================================================

def generate_gaussian(x, amplitude, center, sigma):
    """Generate a Gaussian peak for testing."""
    return amplitude * np.exp(-(x - center)**2 / (2 * sigma**2))

def generate_lorentzian(x, amplitude, center, gamma):
    """Generate a Lorentzian peak for testing."""
    return amplitude * gamma**2 / ((x - center)**2 + gamma**2)

def add_noise(y, noise_level=0.02):
    """Add Gaussian noise to signal."""
    noise = np.random.normal(0, noise_level * np.max(y), len(y))
    return y + noise

# ============================================================================
# Test Cases
# ============================================================================

def test_derivative1_gaussian():
    """Test first derivative on Gaussian peak."""
    print("\n" + "="*70)
    print("TEST 1: First Derivative on Gaussian Peak")
    print("="*70)
    
    # Generate test data
    x = np.linspace(1.5, 2.5, 200)
    y = generate_gaussian(x, amplitude=1000, center=2.0, sigma=0.1)
    y_noisy = add_noise(y, noise_level=0.05)
    
    # Apply first derivative analysis
    params, pcov = mathlib3.fitkeys['derivative1'][1](0, len(x), x, y_noisy)
    
    print(f"\nParameters:")
    print(f"  Max Positive Derivative: {params[0]:.2f} Counts/eV")
    print(f"  Energy at Max Pos. Deriv.: {params[1]:.4f} eV")
    print(f"  Max Negative Derivative: {params[2]:.2f} Counts/eV")
    print(f"  Energy at Max Neg. Deriv.: {params[3]:.4f} eV")
    print(f"  Derivative Range: {params[4]:.2f} Counts/eV")
    print(f"  Zero-Crossing Energy: {params[5]:.4f} eV")
    
    # Validate
    expected_peak = 2.0
    error = abs(params[5] - expected_peak)
    print(f"\nValidation:")
    print(f"  Expected peak: {expected_peak:.4f} eV")
    print(f"  Detected peak: {params[5]:.4f} eV")
    print(f"  Error: {error:.4f} eV ({error/expected_peak*100:.2f}%)")
    
    if error < 0.01:
        print("  ✓ PASS: Peak position accurate")
    else:
        print("  ✗ FAIL: Peak position error too large")
    
    # Plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # Original spectrum
    ax1.plot(x, y_noisy, 'b-', label='Noisy Spectrum')
    ax1.axvline(params[5], color='r', linestyle='--', label=f'Zero-Crossing: {params[5]:.3f} eV')
    ax1.axvline(params[1], color='g', linestyle=':', label=f'Max Pos. Deriv.: {params[1]:.3f} eV')
    ax1.axvline(params[3], color='orange', linestyle=':', label=f'Max Neg. Deriv.: {params[3]:.3f} eV')
    ax1.set_xlabel('Energy (eV)')
    ax1.set_ylabel('Intensity (Counts)')
    ax1.set_title('Test 1: Gaussian Peak - Original Spectrum')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # First derivative
    dy = np.diff(y_noisy)
    dx = np.diff(x)
    deriv = dy / dx
    x_deriv = (x[:-1] + x[1:]) / 2
    
    ax2.plot(x_deriv, deriv, 'purple', label='First Derivative')
    ax2.axhline(0, color='k', linestyle='-', linewidth=0.5)
    ax2.axvline(params[5], color='r', linestyle='--', label=f'Zero-Crossing: {params[5]:.3f} eV')
    ax2.axhline(params[0], color='g', linestyle=':', label=f'Max Pos: {params[0]:.1f}')
    ax2.axhline(params[2], color='orange', linestyle=':', label=f'Max Neg: {params[2]:.1f}')
    ax2.set_xlabel('Energy (eV)')
    ax2.set_ylabel('dI/dE (Counts/eV)')
    ax2.set_title('First Derivative')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('test_derivative1_gaussian.png', dpi=150)
    print("\n  Plot saved: test_derivative1_gaussian.png")

def test_derivative2_gaussian():
    """Test second derivative on Gaussian peak."""
    print("\n" + "="*70)
    print("TEST 2: Second Derivative on Gaussian Peak")
    print("="*70)
    
    # Generate test data
    x = np.linspace(1.5, 2.5, 200)
    y = generate_gaussian(x, amplitude=1000, center=2.0, sigma=0.1)
    y_noisy = add_noise(y, noise_level=0.05)
    
    # Apply second derivative analysis
    params, pcov = mathlib3.fitkeys['derivative2'][1](0, len(x), x, y_noisy)
    
    print(f"\nParameters:")
    print(f"  Max Negative Curvature: {params[0]:.2f} Counts/eV²")
    print(f"  Energy at Max Neg. Curv.: {params[1]:.4f} eV")
    print(f"  Max Positive Curvature: {params[2]:.2f} Counts/eV²")
    print(f"  Curvature Range: {params[3]:.2f} Counts/eV²")
    print(f"  Left Inflection Energy: {params[4]:.4f} eV")
    print(f"  Right Inflection Energy: {params[5]:.4f} eV")
    print(f"  Inflection Width: {params[6]:.4f} eV")
    
    # Validate
    expected_peak = 2.0
    expected_infl_width = 2 * 0.1  # For Gaussian: inflection points at μ ± σ
    
    error_peak = abs(params[1] - expected_peak)
    error_width = abs(params[6] - expected_infl_width)
    
    print(f"\nValidation:")
    print(f"  Expected peak: {expected_peak:.4f} eV")
    print(f"  Detected peak: {params[1]:.4f} eV")
    print(f"  Peak error: {error_peak:.4f} eV ({error_peak/expected_peak*100:.2f}%)")
    print(f"  Expected inflection width: {expected_infl_width:.4f} eV")
    print(f"  Detected inflection width: {params[6]:.4f} eV")
    print(f"  Width error: {error_width:.4f} eV ({error_width/expected_infl_width*100:.2f}%)")
    
    if error_peak < 0.01 and error_width < 0.02:
        print("  ✓ PASS: Peak and width accurate")
    else:
        print("  ✗ FAIL: Errors too large")
    
    # Plot
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12))
    
    # Original spectrum
    ax1.plot(x, y_noisy, 'b-', label='Noisy Spectrum')
    ax1.axvline(params[1], color='r', linestyle='--', label=f'Peak (Curvature): {params[1]:.3f} eV')
    ax1.axvline(params[4], color='g', linestyle=':', label=f'Left Infl.: {params[4]:.3f} eV')
    ax1.axvline(params[5], color='orange', linestyle=':', label=f'Right Infl.: {params[5]:.3f} eV')
    ax1.set_xlabel('Energy (eV)')
    ax1.set_ylabel('Intensity (Counts)')
    ax1.set_title('Test 2: Gaussian Peak - Original Spectrum')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # First derivative
    dy = np.diff(y_noisy)
    dx = np.diff(x)
    deriv1 = dy / dx
    x_deriv1 = (x[:-1] + x[1:]) / 2
    
    ax2.plot(x_deriv1, deriv1, 'purple', label='First Derivative')
    ax2.axhline(0, color='k', linestyle='-', linewidth=0.5)
    ax2.axvline(params[4], color='g', linestyle=':', label=f'Left Infl.')
    ax2.axvline(params[5], color='orange', linestyle=':', label=f'Right Infl.')
    ax2.set_xlabel('Energy (eV)')
    ax2.set_ylabel('dI/dE (Counts/eV)')
    ax2.set_title('First Derivative')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Second derivative
    dy2 = np.diff(deriv1)
    dx2 = np.diff(x_deriv1)
    deriv2 = dy2 / dx2
    x_deriv2 = (x_deriv1[:-1] + x_deriv1[1:]) / 2
    
    ax3.plot(x_deriv2, deriv2, 'darkred', label='Second Derivative')
    ax3.axhline(0, color='k', linestyle='-', linewidth=0.5)
    ax3.axvline(params[1], color='r', linestyle='--', label=f'Peak: {params[1]:.3f} eV')
    ax3.axhline(params[0], color='b', linestyle=':', label=f'Max Neg: {params[0]:.1f}')
    ax3.set_xlabel('Energy (eV)')
    ax3.set_ylabel('d²I/dE² (Counts/eV²)')
    ax3.set_title('Second Derivative')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('test_derivative2_gaussian.png', dpi=150)
    print("\n  Plot saved: test_derivative2_gaussian.png")

def test_comparison_lorentzian():
    """Compare first and second derivative on Lorentzian (sharper peak)."""
    print("\n" + "="*70)
    print("TEST 3: Derivative Methods on Lorentzian Peak")
    print("="*70)
    
    # Generate test data
    x = np.linspace(1.5, 2.5, 200)
    y = generate_lorentzian(x, amplitude=1000, center=2.0, gamma=0.05)
    y_noisy = add_noise(y, noise_level=0.05)
    
    # Apply both derivative methods
    params1, _ = mathlib3.fitkeys['derivative1'][1](0, len(x), x, y_noisy)
    params2, _ = mathlib3.fitkeys['derivative2'][1](0, len(x), x, y_noisy)
    
    print(f"\nFirst Derivative:")
    print(f"  Zero-Crossing Energy: {params1[5]:.4f} eV")
    print(f"  Derivative Range: {params1[4]:.2f} Counts/eV")
    
    print(f"\nSecond Derivative:")
    print(f"  Peak (Curvature): {params2[1]:.4f} eV")
    print(f"  Inflection Width: {params2[6]:.4f} eV")
    print(f"  Max Negative Curvature: {params2[0]:.2f} Counts/eV²")
    
    print(f"\nComparison:")
    print(f"  Peak position difference: {abs(params1[5] - params2[1]):.4f} eV")
    print(f"  (Should be small for consistent methods)")

def test_multi_peak():
    """Test derivative methods on multi-peak spectrum."""
    print("\n" + "="*70)
    print("TEST 4: Derivative Methods on Multi-Peak Spectrum")
    print("="*70)
    
    # Generate multi-peak data
    x = np.linspace(1.5, 2.5, 300)
    y1 = generate_gaussian(x, amplitude=800, center=1.8, sigma=0.08)
    y2 = generate_gaussian(x, amplitude=1000, center=2.1, sigma=0.10)
    y = y1 + y2
    y_noisy = add_noise(y, noise_level=0.03)
    
    # Apply both methods
    params1, _ = mathlib3.fitkeys['derivative1'][1](0, len(x), x, y_noisy)
    params2, _ = mathlib3.fitkeys['derivative2'][1](0, len(x), x, y_noisy)
    
    print(f"\nFirst Derivative:")
    print(f"  Zero-Crossing Energy: {params1[5]:.4f} eV")
    print(f"  Max Pos. Deriv. Energy: {params1[1]:.4f} eV")
    print(f"  Max Neg. Deriv. Energy: {params1[3]:.4f} eV")
    
    print(f"\nSecond Derivative:")
    print(f"  Peak (Curvature): {params2[1]:.4f} eV")
    print(f"  Left Inflection: {params2[4]:.4f} eV")
    print(f"  Right Inflection: {params2[5]:.4f} eV")
    print(f"  Inflection Width: {params2[6]:.4f} eV")
    
    print(f"\nNote: Multi-peak spectra may show combined features.")
    print(f"      For individual peak analysis, use region selection.")

# ============================================================================
# Main Test Runner
# ============================================================================

if __name__ == '__main__':
    print("="*70)
    print("DERIVATIVE METHODS TEST SUITE")
    print("Testing derivative1 and derivative2 in mathlib3.py")
    print("="*70)
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Run tests
    try:
        test_derivative1_gaussian()
        test_derivative2_gaussian()
        test_comparison_lorentzian()
        test_multi_peak()
        
        print("\n" + "="*70)
        print("ALL TESTS COMPLETED")
        print("="*70)
        print("\nPlots saved:")
        print("  - test_derivative1_gaussian.png")
        print("  - test_derivative2_gaussian.png")
        
        plt.show()
        
    except Exception as e:
        print(f"\n✗ TEST FAILED WITH ERROR: {e}")
        import traceback
        traceback.print_exc()
