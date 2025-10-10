# Oscillation Extraction Documentation

## Overview

The `isolate_oscillation` function and related utilities in `mathlib3.py` provide powerful tools for extracting oscillatory signals from data that contains both a slowly-varying background and faster oscillations.

## Key Functions

### 1. `isolate_oscillation(signal, wl, window_length=51, polyorder=3, prominence=None, distance=5)`

**Purpose**: Separates a signal into its background component and oscillatory component, then finds maxima and minima.

**Parameters**:
- `signal`: Array of signal values (e.g., DR Signal in counts)
- `wl`: Array of wavelength/energy values corresponding to the signal
- `window_length`: Length of the smoothing filter window (default: 51, must be odd)
- `polyorder`: Order of polynomial for smoothing (default: 3)
- `prominence`: Required prominence of peaks (default: auto-calculated as 10% of oscillation range)
- `distance`: Minimum distance between peaks in data points (default: 5)

**Returns** (8 arrays):
1. `background`: Smoothed background signal
2. `oscillations`: Isolated oscillations (signal - background)
3. `maxima_indices`: Indices of maxima in the oscillations
4. `minima_indices`: Indices of minima in the oscillations
5. `maxima_wl`: Wavelength/energy values at maxima
6. `minima_wl`: Wavelength/energy values at minima
7. `maxima_values`: Oscillation signal values at maxima
8. `minima_values`: Oscillation signal values at minima

**Example Usage**:
```python
import numpy as np
from mathlib3 import isolate_oscillation

# Your data
energy = np.array([...])  # Energy in eV
signal = np.array([...])  # DR signal in counts

# Extract oscillations
(background, oscillations, 
 maxima_indices, minima_indices,
 maxima_wl, minima_wl,
 maxima_values, minima_values) = isolate_oscillation(signal, energy)

# Now you can plot:
import matplotlib.pyplot as plt

# Plot 1: Original signal with extracted components
plt.figure(figsize=(12, 5))
plt.plot(energy, signal, 'orange', label='DR Signal', linewidth=2)
plt.plot(energy, background, 'black', label='Background (Smoothed)', linewidth=2)
plt.plot(energy, oscillations + np.mean(signal), 'green', label='Oscillations', linewidth=1.5)
plt.plot(maxima_wl, oscillations[maxima_indices] + np.mean(signal), 'rx', markersize=8, label='Peaks')
plt.xlabel('Energy (eV)')
plt.ylabel('DR Signal (counts)')
plt.legend()
plt.show()

# Plot 2: Isolated oscillations with maxima and minima
plt.figure(figsize=(12, 5))
plt.plot(energy, oscillations, 'green', label='Oscillations', linewidth=2)
plt.plot(maxima_wl, maxima_values, 'ro', markersize=8, label='Maxima')
plt.plot(minima_wl, minima_values, 'bo', markersize=8, label='Minima')
plt.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
plt.xlabel('Energy (eV)')
plt.ylabel('Signal')
plt.legend()
plt.show()
```

### 2. `fitoscillationtospec(start, end, WL, PLB, maxfev=10000, guess=None)`

**Purpose**: Wrapper function that fits into the `fitkeys` framework used by the rest of the spectrum analysis code.

**Parameters**:
- `start`: Start index of the spectrum region
- `end`: End index of the spectrum region
- `WL`: Wavelength/energy array
- `PLB`: Signal intensity array
- `maxfev`: Not used, kept for compatibility
- `guess`: Optional dict with keys: 'window_length', 'polyorder', 'prominence', 'distance'

**Returns** (16 values):
- First 8 are scalar summary statistics:
  1. `background_mean`: Mean of the background signal
  2. `osc_amplitude`: Standard deviation of oscillations
  3. `n_maxima`: Number of maxima found
  4. `n_minima`: Number of minima found
  5. `mean_max`: Mean value of maxima
  6. `mean_min`: Mean value of minima
  7. `freq_est`: Estimated oscillation frequency (peaks per eV)
  8. `osc_range`: Range of oscillation values (max - min)
  
- Next 8 are arrays (for plotting):
  9. `background`: Full background array
  10. `oscillations`: Full oscillations array
  11. `maxima_indices`: Indices of maxima
  12. `minima_indices`: Indices of minima
  13. `maxima_wl`: Wavelength/energy at maxima
  14. `minima_wl`: Wavelength/energy at minima
  15. `maxima_values`: Oscillation values at maxima
  16. `minima_values`: Oscillation values at minima

**Example Usage**:
```python
from mathlib3 import fitoscillationtospec

# Analyze a spectrum region
energy = np.array([...])
signal = np.array([...])

# Custom parameters
params = {
    'window_length': 61,  # Smoother background
    'polyorder': 3,
    'prominence': 100,    # Only find peaks > 100 counts
    'distance': 10        # Peaks must be at least 10 points apart
}

results = fitoscillationtospec(0, len(signal), energy, signal, guess=params)

# Unpack results
(background_mean, osc_amplitude, n_maxima, n_minima, 
 mean_max, mean_min, freq_est, osc_range,
 background, oscillations, 
 maxima_indices, minima_indices,
 maxima_wl, minima_wl,
 maxima_values, minima_values) = results

print(f"Found {n_maxima} maxima with mean value {mean_max:.2f}")
print(f"Oscillation frequency: {freq_est:.2f} eV^-1")
```

## Integration with fitkeys

The oscillation extraction is now integrated into the `fitkeys` dictionary:

```python
from mathlib3 import fitkeys

# Access oscillation fitting function
osc_fit_func = fitkeys['oscillations'][1]  # fitoscillationtospec
osc_description = fitkeys['oscillations'][3]  # 'Oscillation Extraction'
osc_param_names = fitkeys['oscillations'][5]  # Parameter names
osc_param_units = fitkeys['oscillations'][6]  # Parameter units

# The 8 scalar parameters stored:
# ['Background mean', 'Oscillation amplitude', 'Number of maxima', 'Number of minima', 
#  'Mean maxima value', 'Mean minima value', 'Oscillation frequency estimate', 'Oscillation range']

# With units:
# ['Counts', 'Counts', '', '', 'Counts', 'Counts', 'eV^-1', 'Counts']
```

## Parameter Tuning Guide

### `window_length`
- **Small values (11-31)**: Tight fit to signal, may capture some oscillations as "background"
- **Medium values (31-71)**: Good general-purpose smoothing
- **Large values (71-151)**: Very smooth background, better for high-frequency oscillations
- **Must be odd** and larger than `polyorder + 1`

### `polyorder`
- **Low values (2-3)**: Simpler polynomial fit, faster computation
- **High values (4-5)**: Better fit to complex background shapes
- **Must be less than `window_length`**

### `prominence`
- **None (default)**: Auto-calculates as 10% of oscillation range
- **Small values**: Find more peaks, including small ones
- **Large values**: Only find prominent peaks
- **Units**: Same as signal (e.g., counts)

### `distance`
- **Small values (3-5)**: Can find closely-spaced peaks
- **Large values (10-20)**: Ensures peaks are well-separated
- **Units**: Data points (not wavelength/energy units)

## Tips for Best Results

1. **Visualize first**: Plot your signal to understand the oscillation frequency
2. **Adjust window_length**: Make it ~2-3 times the oscillation period in data points
3. **Check background**: If oscillations appear in the background, increase `window_length`
4. **Verify peaks**: If too many/few peaks, adjust `prominence` and `distance`
5. **Noisy data**: Use larger `window_length` and higher `prominence`

## Common Use Cases

### Case 1: Extract oscillations for analysis
```python
(background, oscillations, *_) = isolate_oscillation(signal, energy)
# Analyze oscillation properties
period = estimate_period(oscillations)
```

### Case 2: Store fit results in database
```python
results = fitoscillationtospec(0, len(signal), energy, signal)
scalar_params = results[:8]  # First 8 are summary statistics
# Store scalar_params in your database/file
```

### Case 3: Recreate plots for publication
```python
results = fitoscillationtospec(0, len(signal), energy, signal)
background = results[8]
oscillations = results[9]
maxima_wl = results[12]
maxima_values = results[14]
# Create publication-quality plots
```

## Testing

Run the test script to verify installation:
```bash
python test_oscillation_extraction.py
```

This will generate synthetic data, extract oscillations, and create plots similar to the reference images in the references_images folder
