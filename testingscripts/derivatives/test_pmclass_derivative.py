import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import wofz

# Change path two dirs up to import PMclasslib1
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.append(root_dir)

try:
    import PMclasslib1
except ImportError:
    print(f"Error: Could not import PMclasslib1 from {root_dir}")
    sys.exit(1)

def voigt(x, amp, pos, fwhm_g, fwhm_l):
    """
    Voigt profile.
    x: x-axis
    amp: Amplitude
    pos: Center position
    fwhm_g: Gaussian FWHM
    fwhm_l: Lorentzian FWHM
    """
    sigma = fwhm_g / (2 * np.sqrt(2 * np.log(2)))
    gamma = fwhm_l / 2
    z = ((x - pos) + 1j * gamma) / (sigma * np.sqrt(2))
    v = np.real(wofz(z))
    return amp * v / np.max(v)

def main():
    # Generate test spectrum
    x = np.linspace(400, 800, 1000)
    # Double Voigt peak
    y = voigt(x, 100, 500, 10, 10) + voigt(x, 50, 600, 20, 20)
    
    # Add some noise to demonstrate smoothing effect of polynomial fit
    np.random.seed(42)
    y_noise = y + np.random.normal(0, 0.5, len(x))

    # Create Spectra object
    # Note: PMclasslib1.Spectra takes (yax, xax, metadata, parenthsiname)
    metadata = {'test': 'data'}
    spec = PMclasslib1.Spectra(y_noise, x, metadata, 'test_hsi')

    # Calculate derivatives
    # [first_derivative_bool, second_derivative_bool, polynomial_order, N_fitpoints]
    # Using a window of 15 points and 2nd order polynomial
    config = [True, True, 2, 15]
    PMclasslib1.calc_derivative(spec, config)
    #spec.calc_derivative(config)

    # Plotting
    fig, axs = plt.subplots(3, 1, figsize=(10, 12), sharex=True)

    # Original Spectrum
    axs[0].plot(spec.WL, spec.Spec, label='Noisy Data', color='gray', alpha=0.5)
    axs[0].plot(spec.WL, y, label='True Signal', color='blue', linestyle='--')
    axs[0].set_ylabel('Intensity')
    axs[0].set_title('Original Spectrum (Double Voigt)')
    axs[0].legend()
    axs[0].grid(True, alpha=0.3)

    # First Derivative
    axs[1].plot(spec.WL, spec.Spec_d1, color='orange')
    axs[1].set_ylabel('1st Derivative')
    axs[1].set_title('First Derivative')
    axs[1].grid(True, alpha=0.3)

    # Second Derivative
    axs[2].plot(spec.WL, spec.Spec_d2, color='green')
    axs[2].set_ylabel('2nd Derivative')
    axs[2].set_xlabel('Wavelength (nm)')
    axs[2].set_title('Second Derivative')
    axs[2].grid(True, alpha=0.3)

    # Explanation text
    explanation = (
        f"Derivative Calculation Method:\n"
        f"Sliding Window Polynomial Fit (Savitzky-Golay style)\n"
        f"Polynomial Order: {config[2]}\n"
        f"Window Size: {config[3]} points\n\n"
        f"For each point in the spectrum, a polynomial is fitted to the local window of data points.\n"
        f"The analytical derivative of this fitted polynomial is then evaluated at the center point.\n"
        f"This method provides smoothing and derivative calculation in one step."
    )

    plt.figtext(0.5, 0.02, explanation, ha="center", fontsize=11, 
                bbox={"facecolor":"lightyellow", "edgecolor":"black", "boxstyle":"round,pad=0.5"})

    plt.tight_layout(rect=[0, 0.1, 1, 1]) # Make room for text at bottom
    
    output_file = os.path.join(current_dir, 'derivative_test_figure.png')
    plt.savefig(output_file)
    print(f"Test complete. Figure saved to: {output_file}")

if __name__ == "__main__":
    main()
