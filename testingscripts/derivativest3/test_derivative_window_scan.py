import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# Change path three dirs up to import PMclasslib1
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

def calculate_fit_rmse(wl, y, window_size, poly_order):
    """
    Calculates the RMSE of the polynomial fit at the center point across the spectrum.
    This replicates the sliding window logic to evaluate fit quality.
    """
    n_points = len(wl)
    half_window = window_size // 2
    residuals = []
    
    for i in range(n_points):
        start_idx = max(0, i - half_window)
        end_idx = min(n_points, i + half_window + 1)
        
        if end_idx - start_idx <= poly_order:
            continue
            
        x_window = wl[start_idx:end_idx]
        y_window = y[start_idx:end_idx]
        
        try:
            p = np.polyfit(x_window, y_window, poly_order)
            val_fit = np.polyval(p, wl[i])
            residuals.append(y[i] - val_fit)
        except np.linalg.LinAlgError:
            pass
            
    if not residuals:
        return 0.0
        
    return np.sqrt(np.mean(np.array(residuals)**2))

def main():
    # --- Configuration ---
    TARGET_DATASET = "HSI20240909_I03"
    TARGET_NUMBER = 2852  # Spectrum number to test
    
    # Default fallback
    DEFAULT_DATASET = "HSI20250725_HSI1"
    DEFAULT_NUMBER = 39
    
    # Scan Parameters
    # We want to visualize specific windows
    example_windows = [2, 5, 10, 15, 20, 25, 30, 35]
    
    # Create a comprehensive list of windows to scan
    # Base scan: 5 to 59, step 2
    base_scan = list(range(5, 60, 2))
    # Combine with examples and sort unique
    WINDOW_SIZES = sorted(list(set(base_scan + example_windows)))
    
    POLY_ORDER = 2
    # ---------------------

    # 1. Load Data
    data_file = find_spectrum_file(TARGET_DATASET, TARGET_NUMBER)
    
    if data_file is None:
        print(f"Warning: Data file for {TARGET_DATASET} #{TARGET_NUMBER} not found.")
        data_file = find_spectrum_file(DEFAULT_DATASET, DEFAULT_NUMBER)
        if data_file is None:
            print("Error: Could not find target or default data file.")
            return

    # Setup Output Directory
    base_filename = os.path.splitext(os.path.basename(data_file))[0]
    output_dir = os.path.join(current_dir, base_filename)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    print(f"Loading data from: {data_file}")
    wl, bg, pl = load_spectrum(data_file)
    signal = pl - bg
    
    # 2. Perform Scan
    results = {
        'window_size': [],
        'rmse': [],
        'd1_roughness': [],
        'd1_max_amp': [],
        'd2_roughness': [],
        'd2_max_amp': []
    }
    
    print(f"Starting scan over window sizes: {list(WINDOW_SIZES)}")
    
    # Store some representative spectra for plotting later
    # example_windows is already defined above
    example_spectra = {}

    for w in WINDOW_SIZES:
        print(f"Processing window size: {w}", end='\r')
        
        # Create fresh spectra object
        metadata = {'source': os.path.basename(data_file)}
        spec = PMclasslib1.Spectra(signal, wl, metadata, 'Scan_Test')
        
        # Calculate Derivatives
        config = [True, True, POLY_ORDER, w]
        PMclasslib1.calc_derivative(spec, config)
        
        # Calculate Metrics
        # A. Fit RMSE (Expensive, so maybe skip if too slow, but fine for one spectrum)
        rmse = calculate_fit_rmse(wl, signal, w, POLY_ORDER)
        
        # B. Roughness (Standard deviation of the difference)
        d1_roughness = np.std(np.diff(spec.Spec_d1))
        d2_roughness = np.std(np.diff(spec.Spec_d2))
        
        # C. Max Amplitude (To check for signal loss/oversmoothing)
        d1_max_amp = np.max(np.abs(spec.Spec_d1))
        d2_max_amp = np.max(np.abs(spec.Spec_d2))
        
        results['window_size'].append(w)
        results['rmse'].append(rmse)
        results['d1_roughness'].append(d1_roughness)
        results['d1_max_amp'].append(d1_max_amp)
        results['d2_roughness'].append(d2_roughness)
        results['d2_max_amp'].append(d2_max_amp)
        
        if w in example_windows:
            example_spectra[w] = spec

    print("\nScan complete.")
    
    # 3. Visualization
    
    # Figure 1: Metrics Scan
    fig1, axs1 = plt.subplots(3, 2, figsize=(14, 12), sharex=True)
    
    # Row 1: Fit RMSE (Spanning both columns if possible, or just left)
    # Let's put RMSE on top left, and maybe something else top right or leave empty
    axs1[0, 0].plot(results['window_size'], results['rmse'], 'b-o')
    axs1[0, 0].set_ylabel('Fit RMSE (Counts)')
    axs1[0, 0].set_title('Fit Quality vs Window Size')
    axs1[0, 0].grid(True)
    
    axs1[0, 1].axis('off') # Hide top right
    
    # Row 2: Roughness
    axs1[1, 0].plot(results['window_size'], results['d1_roughness'], 'r-o')
    axs1[1, 0].set_ylabel('D1 Roughness')
    axs1[1, 0].set_title('1st Derivative Roughness')
    axs1[1, 0].grid(True)
    
    axs1[1, 1].plot(results['window_size'], results['d2_roughness'], 'r-o')
    axs1[1, 1].set_ylabel('D2 Roughness')
    axs1[1, 1].set_title('2nd Derivative Roughness')
    axs1[1, 1].grid(True)
    
    # Row 3: Amplitude
    axs1[2, 0].plot(results['window_size'], results['d1_max_amp'], 'g-o')
    axs1[2, 0].set_ylabel('Max D1 Amplitude')
    axs1[2, 0].set_xlabel('Window Size (Points)')
    axs1[2, 0].set_title('1st Derivative Signal Preservation')
    axs1[2, 0].grid(True)
    
    axs1[2, 1].plot(results['window_size'], results['d2_max_amp'], 'g-o')
    axs1[2, 1].set_ylabel('Max D2 Amplitude')
    axs1[2, 1].set_xlabel('Window Size (Points)')
    axs1[2, 1].set_title('2nd Derivative Signal Preservation')
    axs1[2, 1].grid(True)
    
    plt.tight_layout()
    fig1.savefig(os.path.join(output_dir, 'scan_metrics.png'))
    
    # Figure 2 & 3: Visual Comparison of Derivatives (Waterfall Plot)
    for deriv_type in ['d1', 'd2']:
        # Create subfolder for individual plots
        indiv_dir = os.path.join(output_dir, f'{deriv_type}_individual')
        if not os.path.exists(indiv_dir):
            os.makedirs(indiv_dir)
            
        fig, ax = plt.subplots(figsize=(12, 10))
        
        colors = plt.cm.viridis(np.linspace(0, 1, len(example_windows)))
        
        # Determine offset for waterfall
        max_vals = []
        min_vals = []
        for w in example_windows:
            if w in example_spectra:
                data = example_spectra[w].Spec_d1 if deriv_type == 'd1' else example_spectra[w].Spec_d2
                max_vals.append(np.max(data))
                min_vals.append(np.min(data))
                
        if max_vals:
            global_max = max(max_vals)
            global_min = min(min_vals)
            range_val = global_max - global_min
            offset_step = range_val * 0.8 
        else:
            offset_step = 1.0

        for i, w in enumerate(example_windows):
            if w in example_spectra:
                s = example_spectra[w]
                data = s.Spec_d1 if deriv_type == 'd1' else s.Spec_d2
                
                # Waterfall Plot
                offset = i * offset_step
                ax.plot(s.WL, data + offset, label=f'Window {w}', color=colors[i], alpha=0.9, linewidth=1.5)
                ax.axhline(offset, color=colors[i], linestyle=':', alpha=0.3)
                ax.text(s.WL[0], offset, f"W={w}", color=colors[i], fontweight='bold', va='bottom')
                
                # Save Individual Plot
                fig_ind, ax_ind = plt.subplots(figsize=(10, 6))
                ax_ind.plot(s.WL, data, color=colors[i])
                label = "1st Derivative" if deriv_type == 'd1' else "2nd Derivative"
                ax_ind.set_title(f'{label} - Window Size {w}')
                ax_ind.set_xlabel('Wavelength (nm)')
                ax_ind.set_ylabel(label)
                ax_ind.grid(True, alpha=0.3)
                fig_ind.savefig(os.path.join(indiv_dir, f'window_{w:03d}.png'))
                plt.close(fig_ind)
                
        ax.set_xlabel('Wavelength (nm)')
        label = "1st Derivative" if deriv_type == 'd1' else "2nd Derivative"
        ax.set_ylabel(f'{label} (Waterfall Offset)')
        ax.set_title(f'{label} Waterfall Plot (Poly Order {POLY_ORDER})')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        
        # Ensure y-ticks are visible
        ax.yaxis.set_tick_params(labelleft=True)
        
        plt.tight_layout()
        fig.savefig(os.path.join(output_dir, f'scan_derivative_{deriv_type}_comparison.png'))
        plt.close(fig)
    
    print(f"Results saved to {output_dir}")

if __name__ == "__main__":
    main()
