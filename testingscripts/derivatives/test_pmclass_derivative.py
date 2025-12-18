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
        f"Sliding Window Polynomial Fit \n"
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

    # --- New Visualization Section: Detailed Fit Analysis ---
    print("Generating detailed fit visualization...")
    
    # Select a point for detailed visualization (e.g., on the slope of the first peak)
    # Peak 1 is at 500nm. Slope is steepest around sigma away.
    target_wl = 490
    idx = np.argmin(np.abs(spec.WL - target_wl))
    
    # Get window parameters
    poly_order = config[2]
    N_fitpoints = config[3]
    half_window = N_fitpoints // 2
    
    # Extract window
    start_idx = max(0, idx - half_window)
    end_idx = min(len(spec.WL), idx + half_window + 1)
    
    wl_window = spec.WL[start_idx:end_idx]
    spec_window = spec.Spec[start_idx:end_idx]
    
    # Re-perform fit for visualization (replicating logic in calc_derivative)
    p = np.polyfit(wl_window, spec_window, poly_order)
    dp = np.polyder(p)      # First derivative polynomial
    ddp = np.polyder(dp)    # Second derivative polynomial
    
    # Evaluation point
    wl_eval = spec.WL[idx]
    val_eval = np.polyval(p, wl_eval)
    d1_eval = np.polyval(dp, wl_eval)
    d2_eval = np.polyval(ddp, wl_eval)
    
    # Create dense arrays for plotting smooth curves
    wl_dense = np.linspace(wl_window[0], wl_window[-1], 100)
    p_dense = np.polyval(p, wl_dense)
    dp_dense = np.polyval(dp, wl_dense)
    
    # Tangent for 1st derivative (Tangent to P(x))
    # y = y0 + m*(x-x0)
    tangent_d1 = val_eval + d1_eval * (wl_dense - wl_eval)
    
    # Tangent for 2nd derivative (Tangent to P'(x))
    # y = y0' + m'*(x-x0)
    # The slope of P'(x) is P''(x), which is the 2nd derivative
    tangent_d2 = np.polyval(dp, wl_eval) + d2_eval * (wl_dense - wl_eval)
    
    # Create new figure for detailed visualization
    fig2, axs2 = plt.subplots(2, 1, figsize=(8, 10))
    
    # Plot 1: 1st Derivative Visualization
    # Shows the polynomial fit to the data and the tangent line (slope = 1st deriv)
    axs2[0].scatter(wl_window, spec_window, color='black', label='Data Points (Window)')
    axs2[0].plot(wl_dense, p_dense, 'r-', label=f'Fitted Poly P(x) (Order {poly_order})')
    axs2[0].plot(wl_dense, tangent_d1, 'b--', label=f'Tangent (Slope = 1st Deriv = {d1_eval:.2f})')
    axs2[0].plot(wl_eval, val_eval, 'bo', markersize=8, label='Evaluation Point')
    axs2[0].set_title(f'1st Derivative Visualization at {wl_eval:.1f} nm\n(Slope of Tangent to P(x))')
    axs2[0].set_ylabel('Intensity')
    axs2[0].legend()
    axs2[0].grid(True, alpha=0.3)
    
    # Plot 2: 2nd Derivative Visualization
    # Shows the derivative of the polynomial P'(x) and its tangent (slope = 2nd deriv)
    # We also plot finite difference slopes of the raw data for context
    fd_slopes = np.diff(spec_window) / np.diff(wl_window)
    wl_fd = (wl_window[:-1] + wl_window[1:]) / 2
    
    axs2[1].scatter(wl_fd, fd_slopes, color='gray', alpha=0.5, label='Finite Diff Slopes (Raw Data)')
    axs2[1].plot(wl_dense, dp_dense, 'g-', label=f'Derivative Poly P\'(x)')
    axs2[1].plot(wl_dense, tangent_d2, 'm--', label=f'Tangent to P\'(x) (Slope = 2nd Deriv = {d2_eval:.2f})')
    axs2[1].plot(wl_eval, np.polyval(dp, wl_eval), 'mo', markersize=8, label='Evaluation Point')
    axs2[1].set_title(f'2nd Derivative Visualization at {wl_eval:.1f} nm\n(Slope of Tangent to P\'(x) represents Stiffness/Curvature)')
    axs2[1].set_ylabel('Slope (Intensity/nm)')
    axs2[1].set_xlabel('Wavelength (nm)')
    axs2[1].legend()
    axs2[1].grid(True, alpha=0.3)
    
    output_file_2 = os.path.join(current_dir, 'derivative_fit_visualization.png')
    plt.tight_layout()
    fig2.savefig(output_file_2)
    print(f"Detailed visualization saved to: {output_file_2}")

    # --- New Visualization Section: Comparison of Improvements ---
    print("Generating improvement comparison...")
    
    # 1. Larger Window
    config_large_window = [True, True, 2, 45] # Increased from 15 to 45
    spec_large = PMclasslib1.Spectra(y_noise, x, metadata, 'test_hsi_large')
    PMclasslib1.calc_derivative(spec_large, config_large_window)
    
    # 2. Pre-smoothing (Gaussian)
    from scipy.ndimage import gaussian_filter1d
    sigma = 2.0
    y_smooth = gaussian_filter1d(y_noise, sigma)
    spec_smooth = PMclasslib1.Spectra(y_smooth, x, metadata, 'test_hsi_smooth')
    # Use original window size on smoothed data
    PMclasslib1.calc_derivative(spec_smooth, config) 
    
    fig3, axs3 = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
    
    # Plot 1: Original 2nd Derivative (Noisy)
    axs3[0].plot(spec.WL, spec.Spec_d2, color='green', alpha=0.7)
    axs3[0].set_title(f'Original 2nd Derivative (Window={config[3]}, No Pre-smoothing)')
    axs3[0].set_ylabel('2nd Deriv')
    axs3[0].grid(True, alpha=0.3)
    
    # Plot 2: Larger Window
    axs3[1].plot(spec_large.WL, spec_large.Spec_d2, color='purple', alpha=0.7)
    axs3[1].set_title(f'Improvement 1: Larger Window (Window={config_large_window[3]})')
    axs3[1].set_ylabel('2nd Deriv')
    axs3[1].grid(True, alpha=0.3)
    
    # Plot 3: Pre-smoothing
    axs3[2].plot(spec_smooth.WL, spec_smooth.Spec_d2, color='teal', alpha=0.7)
    axs3[2].set_title(f'Improvement 2: Pre-smoothing (Gaussian sigma={sigma}) + Window={config[3]}')
    axs3[2].set_ylabel('2nd Deriv')
    axs3[2].set_xlabel('Wavelength (nm)')
    axs3[2].grid(True, alpha=0.3)
    
    output_file_3 = os.path.join(current_dir, 'derivative_improvement_comparison.png')
    plt.tight_layout()
    fig3.savefig(output_file_3)
    print(f"Improvement comparison saved to: {output_file_3}")

if __name__ == "__main__":
    main()
