import numpy as np
import matplotlib.pyplot as plt
import time
from scipy.signal import savgol_filter

def generate_spectral_data(n_points):
    """Generate synthetic spectral data with noise."""
    x = np.linspace(400, 2500, n_points)
    # Multiple Gaussian peaks
    y = (1000 * np.exp(-(x - 650)**2 / (2 * 30**2)) +
         800 * np.exp(-(x - 1100)**2 / (2 * 50**2)) +
         600 * np.exp(-(x - 1600)**2 / (2 * 40**2)))
    # Add noise
    y += np.random.normal(0, 20, size=len(x))
    return x, y

def polyfit_derivative(x, y, window_size=11, poly_order=3):
    """
    Polyfit approach: Fit polynomial at each point iteratively.
    """
    half_window = window_size // 2
    deriv = np.zeros_like(y)
    
    for i in range(half_window, len(y) - half_window):
        x_window = x[i - half_window : i + half_window + 1]
        y_window = y[i - half_window : i + half_window + 1]
        
        # Fit polynomial
        p = np.polyfit(x_window, y_window, poly_order)
        # Get derivative coefficients
        dp = np.polyder(p)
        # Evaluate at center point
        deriv[i] = np.polyval(dp, x[i])
    
    return deriv

def savgol_derivative(y, window_size=11, poly_order=3):
    """
    Savitzky-Goyal approach: Vectorized filter.
    """
    return savgol_filter(y, window_length=window_size, polyorder=poly_order, deriv=1)

def main():
    # Configuration
    array_sizes = [500, 1000, 2000, 5000, 10000, 20000]
    window_size = 11
    poly_order = 3
    runs_per_size = 5

    # Benchmark
    polyfit_times = []
    savgol_times = []
    polyfit_times_std = []
    savgol_times_std = []
    speedup_factors = []

    print("Running benchmarks...")
    print("-" * 60)

    for size in array_sizes:
        polyfit_times_list = []
        savgol_times_list = []
        
        for _ in range(runs_per_size):
            x, y = generate_spectral_data(size)
            
            # Polyfit timing
            start = time.perf_counter()
            polyfit_derivative(x, y, window_size, poly_order)
            polyfit_times_list.append(time.perf_counter() - start)
            
            # Savgol timing
            start = time.perf_counter()
            savgol_derivative(y, window_size, poly_order)
            savgol_times_list.append(time.perf_counter() - start)
        
        # Average times and std deviations
        polyfit_avg = np.mean(polyfit_times_list)
        polyfit_std = np.std(polyfit_times_list)
        savgol_avg = np.mean(savgol_times_list)
        savgol_std = np.std(savgol_times_list)
        
        polyfit_times.append(polyfit_avg)
        polyfit_times_std.append(polyfit_std)
        savgol_times.append(savgol_avg)
        savgol_times_std.append(savgol_std)
        
        speedup = polyfit_avg / savgol_avg if savgol_avg > 0 else 0
        speedup_factors.append(speedup)
        
        print(f"Size: {size:6d} | Polyfit: {polyfit_avg*1000:8.3f}ms | "
              f"Savgol: {savgol_avg*1000:7.3f}ms | Speedup: {speedup:6.1f}x")

    print("-" * 60)

    # Use a scientific matplotlib style
    plt.rcParams.update({
        'font.family': 'serif',
        'font.size': 12,
        'axes.labelsize': 13,
        'axes.titlesize': 14,
        'legend.fontsize': 11,
        'xtick.direction': 'in',
        'ytick.direction': 'in',
        'xtick.top': True,
        'ytick.right': True,
        'lines.linewidth': 2
    })

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.subplots_adjust(wspace=0.3)

    # Convert to arrays and scale to milliseconds
    polyfit_ms = np.array(polyfit_times) * 1000
    polyfit_std_ms = np.array(polyfit_times_std) * 1000
    savgol_ms = np.array(savgol_times) * 1000
    savgol_std_ms = np.array(savgol_times_std) * 1000

    # Left subplot: Timing comparison (Log-Log scale)
    ax1.errorbar(array_sizes, polyfit_ms, yerr=polyfit_std_ms, fmt='-o', color='firebrick', 
                 capsize=4, label='Iterative Polyfit')
    ax1.errorbar(array_sizes, savgol_ms, yerr=savgol_std_ms, fmt='-s', color='navy', 
                 capsize=4, label='Savitzky-Golay Filter')

    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.set_xlabel(r'Array Size (points)')
    ax1.set_ylabel(r'Execution Time (ms)')
    ax1.set_title('(a) Computational Complexity')
    ax1.legend(loc='upper left', frameon=False)
    ax1.grid(True, which='major', color='gray', linestyle='-', alpha=0.3)
    ax1.grid(True, which='minor', color='gray', linestyle=':', alpha=0.2)

    # Right subplot: Speedup factor (Semi-Log X scale)
    ax2.plot(array_sizes, speedup_factors, '-d', color='black', markerfacecolor='white', markeredgewidth=1.5)
    
    # Add textual annotations for points
    for size, speedup in zip(array_sizes, speedup_factors):
        ax2.annotate(f"{speedup:.1f}$\\times$", 
                     (size, speedup),
                     textcoords="offset points", 
                     xytext=(0, 10), 
                     ha='center',
                     fontsize=10)

    ax2.set_xscale('log')
    ax2.set_xlabel(r'Array Size (points)')
    ax2.set_ylabel(r'Speedup Factor ($t_{polyfit} / t_{savgol}$)')
    ax2.set_title('(b) Relative Performance Gain')
    ax2.grid(True, color='gray', linestyle='-', alpha=0.3)
    
    # Set ylim to ensure text annotations fit
    ax2.set_ylim(0, max(speedup_factors) * 1.15)

    plt.savefig('savgol_speed_advantage.png', dpi=300, bbox_inches='tight')
    print("\n✓ Scientific plot saved to 'savgol_speed_advantage.png'")
    # plt.show()

if __name__ == "__main__":
    main()
