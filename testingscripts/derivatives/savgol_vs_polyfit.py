import numpy as np
import matplotlib.pyplot as plt
import time
from scipy.signal import savgol_filter

def generate_dummy_data(n_points=1000):
    """Generate a dummy spectrum with a Gaussian peak and some noise."""
    x = np.linspace(400, 800, n_points)
    # Gaussian centered at 600nm, width 20nm
    y = 1000 * np.exp(-(x - 600)**2 / (2 * 20**2)) 
    # Add random noise
    y += np.random.normal(0, 15, size=len(x))
    return x, y

def original_polyfit_derivative(x, y, window_size, poly_order):
    """
    Original approach: Iterating through the spectrum point-by-point.
    At each point, it slices a window of data, fits a polynomial using np.polyfit,
    calculates the analytical derivative of that polynomial, and evaluates it.
    """
    half_window = window_size // 2
    deriv1 = np.zeros_like(y)
    
    # We skip the edges here for simplicity, similar to typical sliding windows
    for i in range(half_window, len(y) - half_window):
        x_window = x[i - half_window : i + half_window + 1]
        y_window = y[i - half_window : i + half_window + 1]
        
        # 1. Fit polynomial to the window
        p = np.polyfit(x_window, y_window, poly_order)
        # 2. Get the derivative of the polynomial
        dp = np.polyder(p)
        # 3. Evaluate the derivative at the center point
        deriv1[i] = np.polyval(dp, x[i])
        
    return deriv1

def optimized_savgol_derivative(x, y, window_size, poly_order):
    """
    Optimized approach: Using scipy.signal.savgol_filter.
    
    Why it's faster:
    Savitzky-Golay also fits a polynomial of `poly_order` to `window_size` points. 
    However, because the window size and polynomial degree are constant across the 
    entire signal, the least-squares equations have a constant analytical solution!
    This means the polynomial fitting operation simplifies down to a single 
    Linear Convolution operation with pre-calculated coefficient weights. 
    There is no need to run iterative matrix inversions/solvers at every point.
    """
    delta = np.mean(np.diff(x))
    return savgol_filter(y, window_size, poly_order, deriv=1, delta=delta)

def main():
    print("=" * 60)
    print("  EXPLANATION: SAVITZKY-GOLAY VS ITERATIVE POLYFIT  ")
    print("=" * 60)
    print("Conceptually, both methods do the SAME thing:")
    print("  1. Take a sliding window of N points around a center pixel.")
    print("  2. Fit a polynomial of degree P to those N points.")
    print("  3. Calculate the derivative of that polynomial at the center pixel.\n")
    
    print("Why Savitzky-Golay is orders of magnitude faster:")
    print("  - 'np.polyfit' solves a matrix equation from scratch for EVERY single point.")
    print("  - Savitzky-Golay recognizes that if the grid spacing, window size, and")
    print("    polynomial order are constant, the matrix math always yields the same")
    print("    linear combinations. It pre-computes these 'convolution coefficients'")
    print("    and applies them using an extremely fast C-based convolution function.\n")
    
    # Parameters
    N_POINTS = 2000
    WINDOW_SIZE = 21   # Must be odd for savgol filter
    POLY_ORDER = 3
    
    # Run test
    print(f"Generating synthetic spectrum with {N_POINTS} points...")
    x, y = generate_dummy_data(N_POINTS)
    
    print(f"\nRunning benchmark (Window Size={WINDOW_SIZE}, Poly Order={POLY_ORDER})...")
    
    # Time original polyfit method
    t0 = time.time()
    deriv_poly = original_polyfit_derivative(x, y, WINDOW_SIZE, POLY_ORDER)
    t1 = time.time()
    time_poly = t1 - t0
    
    # Time optimized Savitzky-Golay method
    t0 = time.time()
    deriv_savgol = optimized_savgol_derivative(x, y, WINDOW_SIZE, POLY_ORDER)
    t1 = time.time()
    time_savgol = t1 - t0
    
    print("-" * 40)
    print(f"Iterative Polyfit Time : {time_poly:.5f} seconds")
    print(f"Savitzky-Golay Time    : {time_savgol:.5f} seconds")
    
    speedup = time_poly / time_savgol if time_savgol > 0 else float('inf')
    print(f"Speedup Factor         : {speedup:.1f}x FASTER")
    print("-" * 40)
    
    # Visual Comparison
    print("\nGenerating comparison plot (compare_derivatives.png)...")
    plt.figure(figsize=(10, 8))
    
    # Plot original spectrum
    plt.subplot(2, 1, 1)
    plt.title("Original Synthetic Spectrum (Gaussian + Noise)")
    plt.plot(x, y, color='black', alpha=0.6, label='Spectrum')
    plt.ylabel('Intensity')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot derivatives
    plt.subplot(2, 1, 2)
    plt.title("Calculated First Derivatives")
    
    # Note: we omit the edges in plotting because the iterative polyfit 
    # doesn't calculate them, resulting in 0s. 
    trim = WINDOW_SIZE // 2
    plt.plot(x[trim:-trim], deriv_poly[trim:-trim], 
             label='Iterative Polyfit', linewidth=3, alpha=0.5, color='blue')
    plt.plot(x[trim:-trim], deriv_savgol[trim:-trim], 
             label='Savitzky-Golay (savgol_filter)', linewidth=1.5, color='red', linestyle='--')
             
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('First Derivative')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('compare_derivatives.png', dpi=150)
    print("Plot saved to 'compare_derivatives.png'")
    # uncomment below to show interactively
    # plt.show()

if __name__ == "__main__":
    main()