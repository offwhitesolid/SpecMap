import os
import sys
import numpy as np
import matplotlib.pyplot as plt

# Change path three dirs up to import PMclasslib1 (testingscripts/derivativest2/ -> root)
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.append(root_dir)

try:
    import PMclasslib1
except ImportError:
    print(f"Error: Could not import PMclasslib1 from {root_dir}")
    sys.exit(1)

def load_spectrum(filepath):
    """
    Reads the spectrum file, skips metadata, and returns WL, BG, PL arrays.
    """
    wl = []
    bg = []
    pl = []
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
        
    data_start = False
    for line in lines:
        if line.strip().startswith('WL'):
            data_start = True
            continue
        
        if data_start:
            parts = line.strip().split()
            if len(parts) >= 3:
                try:
                    wl.append(float(parts[0]))
                    bg.append(float(parts[1]))
                    pl.append(float(parts[2]))
                except ValueError:
                    continue
                    
    return np.array(wl), np.array(bg), np.array(pl)

def main():
    # --- Configuration ---
    TARGET_DATASET = "HSI20240909_I03"
    TARGET_NUMBER = 2852  # Spectrum number to test
    
    # Default fallback
    DEFAULT_DATASET = "HSI20250725_HSI1"
    DEFAULT_NUMBER = 39
    # ---------------------

    def find_spectrum_file(dataset, number):
        # Look for folder named after target_dataset
        dataset_path = os.path.join(root_dir, 'testdatasets', dataset)
        if not os.path.exists(dataset_path):
            return None
        
        target_pattern = f"{number:05d}"
        
        # Search for file containing the target number
        for root, dirs, files in os.walk(dataset_path):
            for file in files:
                if target_pattern in file and file.endswith('.txt'):
                    return os.path.join(root, file)
        
        return None

    data_file = find_spectrum_file(TARGET_DATASET, TARGET_NUMBER)
    
    if data_file is None:
        print(f"Warning: Data file for {TARGET_DATASET} #{TARGET_NUMBER} not found.")
        print(f"Falling back to default: {DEFAULT_DATASET} #{DEFAULT_NUMBER}")
        data_file = find_spectrum_file(DEFAULT_DATASET, DEFAULT_NUMBER)
        
        if data_file is None:
            print(f"Error: Default data file also not found.")
            return
            
    # Extract filename without extension for folder creation
    base_filename = os.path.splitext(os.path.basename(data_file))[0]
    output_dir = os.path.join(current_dir, base_filename)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    print(f"Loading data from: {data_file}")
    wl, bg, pl = load_spectrum(data_file)
    
    # Calculate Signal = PL - BG
    signal = pl - bg
    
    # Create Spectra object
    metadata = {'source': os.path.basename(data_file)}
    spec = PMclasslib1.Spectra(signal, wl, metadata, 'HSI_Test_Spectrum')

    # Calculate derivatives
    # [first_derivative_bool, second_derivative_bool, polynomial_order, N_fitpoints]
    # Using a window of 15 points and 2nd order polynomial (same as original test)
    config = [True, True, 2, 15]
    PMclasslib1.calc_derivative(spec, config)

    # Plotting
    fig, axs = plt.subplots(3, 1, figsize=(10, 12), sharex=True)

    # Original Spectrum
    axs[0].plot(spec.WL, spec.Spec, label='Signal (PL-BG)', color='blue')
    axs[0].set_ylabel('Intensity')
    axs[0].set_title(f'Spectrum {base_filename}')
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

    plt.figtext(0.5, 0.01, explanation, ha="center", fontsize=11, 
                bbox={"facecolor":"lightyellow", "edgecolor":"black", "boxstyle":"round,pad=0.5"})

    plt.tight_layout(rect=[0, 0.15, 1, 1]) # Make room for text at bottom
    
    output_file = os.path.join(output_dir, 'derivative_test_figure_realdata.png')
    plt.savefig(output_file)
    print(f"Test complete. Figure saved to: {output_file}")

    # --- New Visualization Section: Detailed Fit Analysis ---
    print("Generating detailed fit visualization...")
    
    # Select a point for detailed visualization
    # Let's pick the max intensity point as a point of interest, or somewhere on the slope
    max_idx = np.argmax(spec.Spec)
    # Pick a point slightly to the left of the max (on the rising edge)
    target_idx = max(0, max_idx - 10)
    target_wl = spec.WL[target_idx]
    
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
    if len(wl_window) > poly_order:
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
        fig2, axs2 = plt.subplots(3, 1, figsize=(8, 12))
        
        # Plot 1: 1st Derivative Visualization
        # Shows the polynomial fit to the data and the tangent line (slope = 1st deriv)
        axs2[0].scatter(wl_window, spec_window, color='black', label='Data Points (Window)')
        axs2[0].plot(wl_dense, p_dense, 'r-', label=f'Fitted Poly P(x) (Order {poly_order})')
        axs2[0].plot(wl_dense, tangent_d1, 'b--', label=f'Tangent (Slope = 1st Deriv = {d1_eval:.2f})')
        axs2[0].plot(wl_eval, val_eval, 'bo', markersize=8, label='Evaluation Point')
        
        # Add equation text
        poly_eq = f"P(x) = {p[0]:.2e}x^2 + {p[1]:.2e}x + {p[2]:.2e}"
        axs2[0].text(0.05, 0.95, poly_eq, transform=axs2[0].transAxes, 
                     verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
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
        
        # Add equation text
        deriv_eq = f"P'(x) = {dp[0]:.2e}x + {dp[1]:.2e}"
        axs2[1].text(0.05, 0.95, deriv_eq, transform=axs2[1].transAxes, 
                     verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        axs2[1].set_title(f'2nd Derivative Visualization at {wl_eval:.1f} nm\n(Slope of Tangent to P\'(x) represents Stiffness/Curvature)')
        axs2[1].set_ylabel('Slope (Intensity/nm)')
        axs2[1].legend()
        axs2[1].grid(True, alpha=0.3)

        # Plot 3: Residuals and Quality
        # Calculate residuals
        residuals = spec_window - np.polyval(p, wl_window)
        rmse = np.sqrt(np.mean(residuals**2))
        
        axs2[2].scatter(wl_window, residuals, color='purple', label='Residuals (Data - Fit)')
        axs2[2].axhline(0, color='black', linestyle='--', alpha=0.5)
        axs2[2].set_title(f'Fit Quality (Residuals)\nRMSE = {rmse:.4f}')
        axs2[2].set_ylabel('Residuals')
        axs2[2].set_xlabel('Wavelength (nm)')
        axs2[2].legend()
        axs2[2].grid(True, alpha=0.3)
        
        output_file_2 = os.path.join(output_dir, 'derivative_fit_visualization_realdata.png')
        plt.tight_layout()
        fig2.savefig(output_file_2)
        print(f"Detailed visualization saved to: {output_file_2}")
    else:
        print("Not enough points for detailed visualization.")

    # --- New Visualization Section: Comparison of Improvements ---
    print("Generating improvement comparison...")
    
    # 1. Larger Window
    config_large_window = [True, True, 2, 45] # Increased from 15 to 45
    spec_large = PMclasslib1.Spectra(signal, wl, metadata, 'test_hsi_large')
    PMclasslib1.calc_derivative(spec_large, config_large_window)
    
    # 2. Pre-smoothing (Gaussian)
    from scipy.ndimage import gaussian_filter1d
    sigma = 2.0
    y_smooth = gaussian_filter1d(signal, sigma)
    spec_smooth = PMclasslib1.Spectra(y_smooth, wl, metadata, 'test_hsi_smooth')
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
    
    output_file_3 = os.path.join(output_dir, 'derivative_improvement_comparison_realdata.png')
    plt.tight_layout()
    fig3.savefig(output_file_3)
    print(f"Improvement comparison saved to: {output_file_3}")

if __name__ == "__main__":
    main()
