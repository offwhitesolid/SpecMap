"""
Test script for oscillation extraction functionality in mathlib3.py

This script demonstrates how to use the isolate_oscillation function
to extract oscillations from a signal with an underlying trend.
"""

import numpy as np
import matplotlib.pyplot as plt
import os, sys

# since this test dir is ../.. below the library needed, the workingdir must be added to path to import mathlib3 for the testing
os.sys.path.append(os.path.abspath(os.getcwd()))

from mathlib3 import isolate_oscillation, fitoscillationtospec

def generate_test_signal():
    """Generate a test signal similar to the image: background + oscillations"""
    # Energy range (eV)
    energy = np.linspace(1.8, 2.25, 500)
    
    # Background: polynomial trend
    background = 4000 + 2000 * energy + 5000 * energy**2
    
    # Oscillations: sinusoidal with varying amplitude
    frequency = 30  # oscillations per eV
    amplitude_envelope = 500 + 300 * energy  # Increasing amplitude
    oscillations = amplitude_envelope * np.sin(2 * np.pi * frequency * energy)
    
    # Combined signal
    signal = background + oscillations
    
    # Add some noise
    noise = np.random.normal(0, 50, len(signal))
    signal += noise
    
    return energy, signal

def test_oscillation_extraction(savedir=os.path.abspath((os.getcwd()))):
    """Test the oscillation extraction with synthetic data"""
    print("Generating test signal...")
    energy, signal = generate_test_signal()
    
    print("Extracting oscillations...")
    # Call isolate_oscillation
    (background, oscillations, 
     maxima_indices, minima_indices,
     maxima_wl, minima_wl,
     maxima_values, minima_values) = isolate_oscillation(
        signal, energy, window_length=51, polyorder=3
    )
    
    print(f"Found {len(maxima_indices)} maxima and {len(minima_indices)} minima")
    print(f"Oscillation range: {np.max(oscillations) - np.min(oscillations):.2f} counts")
    print(f"Background mean: {np.mean(background):.2f} counts")
    
    # Create plots similar to the reference images
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Plot 1: Original signal with background and oscillations
    ax1.plot(energy, signal, 'orange', label='DR Signal', linewidth=2)
    ax1.plot(energy, background, 'black', label='Background (Smoothed)', linewidth=2)
    ax1.plot(energy, oscillations + np.mean(signal), 'green', 
             label='Oscillations', linewidth=1.5, alpha=0.7)
    
    # Mark peaks on the oscillations
    if len(maxima_indices) > 0:
        ax1.plot(maxima_wl, oscillations[maxima_indices] + np.mean(signal), 
                'rx', markersize=8, label='Peaks')
    
    ax1.set_xlabel('Energy (eV)', fontsize=12)
    ax1.set_ylabel('DR Signal (counts)', fontsize=12)
    ax1.set_title('Oscillation Extraction', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Isolated oscillations with maxima and minima
    ax2.plot(energy, oscillations, 'green', label='Oscillations', linewidth=2)
    
    if len(maxima_indices) > 0:
        ax2.plot(maxima_wl, maxima_values, 'ro', markersize=8, label='Maxima')
    if len(minima_indices) > 0:
        ax2.plot(minima_wl, minima_values, 'bo', markersize=8, label='Minima')
    
    ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax2.set_xlabel('Energy (eV)', fontsize=12)
    ax2.set_ylabel('Signal', fontsize=12)
    ax2.set_title('Maxima and Minima in Oscillatory Signal', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{savedir}/oscillation_extraction_test.png', dpi=150)
    print(f"\nPlot saved as '{savedir}/oscillation_extraction_test.png'")
    plt.show()

def test_fitoscillation():
    """Test the fitoscillationtospec function"""
    print("\n" + "="*50)
    print("Testing fitoscillationtospec function...")
    print("="*50)
    
    energy, signal = generate_test_signal()
    
    # Use the fitting function
    results = fitoscillationtospec(0, len(signal), energy, signal)
    
    (background_mean, osc_amplitude, n_maxima, n_minima, 
     mean_max, mean_min, freq_est, osc_range,
     background, oscillations, 
     maxima_indices, minima_indices,
     maxima_wl, minima_wl,
     maxima_values, minima_values) = results
    
    print(f"\nFit Results:")
    print(f"  Background mean: {background_mean:.2f} counts")
    print(f"  Oscillation amplitude (std): {osc_amplitude:.2f} counts")
    print(f"  Number of maxima: {n_maxima}")
    print(f"  Number of minima: {n_minima}")
    print(f"  Mean maxima value: {mean_max:.2f} counts")
    print(f"  Mean minima value: {mean_min:.2f} counts")
    print(f"  Oscillation frequency: {freq_est:.2f} eV^-1")
    print(f"  Oscillation range: {osc_range:.2f} counts")
    
    print("\nAll arrays are available for further plotting:")
    print(f"  - background: shape {background.shape}")
    print(f"  - oscillations: shape {oscillations.shape}")
    print(f"  - maxima_wl: {len(maxima_wl)} points")
    print(f"  - minima_wl: {len(minima_wl)} points")

if __name__ == '__main__':
    # save the location of this file as libdir
    libdir = os.path.dirname(os.path.abspath(__file__))
    print("="*60)
    print("Oscillation Extraction Test")
    print("="*60)
    
    # Test basic oscillation extraction
    test_oscillation_extraction(savedir=libdir)
    
    # Test the fitoscillationtospec function
    test_fitoscillation()
    
    print("\n" + "="*60)
    print("Testing complete!")
    print("="*60)
