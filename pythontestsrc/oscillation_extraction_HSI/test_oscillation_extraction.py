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
    """Generate a test signal similar to the image: background + oscillations with phase evolution"""
    # Energy range (eV)
    energy = np.linspace(1.8, 2.25, 500)
    
    # Background: polynomial trend
    background = 4000 + 2000 * energy + 5000 * energy**2
    
    # Oscillations with PHASE EVOLUTION (chirp): frequency increases with energy
    # This mimics the behavior seen in your image where oscillations get faster
    base_frequency = 25  # Initial oscillations per eV
    chirp_rate = 30  # How much frequency increases with energy (eV^-2)
    
    # Phase with quadratic term for chirp: φ(E) = 2π * (f0 * E + 0.5 * chirp * E^2)
    phase = 2 * np.pi * (base_frequency * energy + 0.5 * chirp_rate * energy**2)
    
    # Amplitude envelope: increases with energy
    amplitude_envelope = 500 + 300 * energy
    
    # Oscillations with varying frequency (chirped signal)
    oscillations = amplitude_envelope * np.sin(phase)
    
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

def test_fitoscillation(savedir=os.path.abspath((os.getcwd()))):
    """Test the fitoscillationtospec function with phase extraction"""
    print("\n" + "="*50)
    print("Testing fitoscillationtospec function with PHASE EXTRACTION...")
    print("="*50)
    
    energy, signal = generate_test_signal()
    
    # Use the fitting function
    results = fitoscillationtospec(0, len(signal), energy, signal)
    
    (background_mean, osc_amplitude, n_maxima, n_minima, 
     mean_max, mean_min, freq_est, osc_range,
     phase_chirp, initial_freq, mean_period, period_std,  # NEW phase parameters
     background, oscillations, 
     maxima_indices, minima_indices,
     maxima_wl, minima_wl,
     maxima_values, minima_values,
     instantaneous_freq, freq_centers) = results  # NEW phase arrays
    
    print(f"\nFit Results:")
    print(f"  Background mean: {background_mean:.2f} counts")
    print(f"  Oscillation amplitude (std): {osc_amplitude:.2f} counts")
    print(f"  Number of maxima: {n_maxima}")
    print(f"  Number of minima: {n_minima}")
    print(f"  Mean maxima value: {mean_max:.2f} counts")
    print(f"  Mean minima value: {mean_min:.2f} counts")
    print(f"  Oscillation frequency: {freq_est:.2f} eV^-1")
    print(f"  Oscillation range: {osc_range:.2f} counts")
    
    print(f"\n*** PHASE EVOLUTION PARAMETERS (NEW!) ***")
    print(f"  Phase chirp rate: {phase_chirp:.4f} eV^-2")
    print(f"    (How much frequency increases per eV)")
    print(f"  Initial frequency: {initial_freq:.2f} eV^-1")
    print(f"  Mean period: {mean_period:.4f} eV")
    print(f"  Period std dev: {period_std:.4f} eV")
    print(f"    (Variability indicates chirp)")
    
    print("\nAll arrays are available for further plotting:")
    print(f"  - background: shape {background.shape}")
    print(f"  - oscillations: shape {oscillations.shape}")
    print(f"  - maxima_wl: {len(maxima_wl)} points")
    print(f"  - minima_wl: {len(minima_wl)} points")
    print(f"  - instantaneous_freq: {len(instantaneous_freq)} points (NEW!)")
    print(f"  - freq_centers: {len(freq_centers)} points (NEW!)")
    
    # Create a new plot showing phase evolution
    if len(instantaneous_freq) > 0:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Plot 1: Oscillations with peak markers
        ax1.plot(energy, oscillations, 'green', label='Oscillations', linewidth=2, alpha=0.7)
        ax1.plot(maxima_wl, maxima_values, 'ro', markersize=6, label='Maxima')
        ax1.plot(minima_wl, minima_values, 'bo', markersize=6, label='Minima')
        ax1.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        ax1.set_xlabel('Energy (eV)', fontsize=12)
        ax1.set_ylabel('Oscillation Signal', fontsize=12)
        ax1.set_title('Oscillations with Varying Frequency (Chirp)', fontsize=14, fontweight='bold')
        ax1.legend(fontsize=11)
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Instantaneous frequency vs energy (PHASE EVOLUTION)
        ax2.plot(freq_centers, instantaneous_freq, 'purple', marker='o', 
                linewidth=2, markersize=5, label='Measured frequency')
        
        # Plot linear fit to show chirp trend
        if len(freq_centers) > 1:
            fit_freq = phase_chirp * freq_centers + initial_freq
            ax2.plot(freq_centers, fit_freq, 'r--', linewidth=2, 
                    label=f'Linear fit: f(E) = {phase_chirp:.3f}·E + {initial_freq:.2f}')
        
        ax2.set_xlabel('Energy (eV)', fontsize=12)
        ax2.set_ylabel('Instantaneous Frequency (eV⁻¹)', fontsize=12)
        ax2.set_title('Phase Evolution: Frequency vs Energy', fontsize=14, fontweight='bold')
        ax2.legend(fontsize=11)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{savedir}/phase_evolution_analysis.png', dpi=150)
        print(f"\nPhase evolution plot saved as '{savedir}/phase_evolution_analysis.png'")
        plt.show()

if __name__ == '__main__':
    # save the location of this file as libdir
    libdir = os.path.dirname(os.path.abspath(__file__))
    print("="*60)
    print("Oscillation Extraction Test")
    print("="*60)
    
    # Test basic oscillation extraction
    test_oscillation_extraction(savedir=libdir)
    
    # Test the fitoscillationtospec function with phase extraction
    test_fitoscillation(savedir=libdir)
    
    print("\n" + "="*60)
    print("Testing complete!")
    print("="*60)
