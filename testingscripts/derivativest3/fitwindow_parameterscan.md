# Fit Window Parameter Scan for Derivative Calculation

## Objective
To determine the optimal window size (number of fit points) for the sliding window polynomial derivative calculation. The goal is to balance **noise reduction** (smoothing) with **signal fidelity** (preserving peak shapes and positions).

## Methodology
We will perform a parameter scan over the `window_size` parameter (N_fitpoints) while keeping the polynomial order constant (typically 2nd order).

### Parameters
- **Polynomial Order**: 2 (Fixed)
- **Window Size Range**: 5 to 101 (Odd numbers only)
- **Dataset**: Single representative spectrum (e.g., `HSI20250725_HSI1_00040` or similar).

## Evaluation Criteria

### 1. Fit Quality (RMSE)
- **Metric**: Root Mean Square Error (RMSE) of the polynomial fit residuals.
- **Calculation**: For each window, calculate the difference between the actual data points and the fitted polynomial value at the center point.
- **Interpretation**: 
    - Very low RMSE suggests the fit is tracking the data very closely, potentially including noise (overfitting).
    - High RMSE suggests the fit is deviating significantly from the data (underfitting/oversmoothing).

### 2. Derivative Smoothness (Roughness)
- **Metric**: Standard deviation of the difference of the derivative (2nd difference of the signal).
- **Calculation**: `std(diff(derivative))`
- **Interpretation**: 
    - High roughness indicates a noisy derivative.
    - Low roughness indicates a smooth derivative.

### 3. Peak Preservation (Signal Fidelity)
- **Metric**: Maximum amplitude of the 2nd derivative (for peak detection).
- **Interpretation**: 
    - As window size increases, peaks tend to broaden and their derivative amplitude decreases.
    - We want to maximize smoothing without significantly reducing the peak signal.

## Visualizations
The script `test_derivative_window_scan.py` generates the following outputs in a folder named after the spectrum (e.g., `HSI20250725_HSI1_00040`):

1.  **Metric Scan** (`scan_metrics.png`): 
    - A 3x2 grid of plots showing Fit RMSE, Roughness (1st & 2nd Deriv), and Max Amplitude (1st & 2nd Deriv) vs. Window Size.
    
2.  **Derivative Waterfall Plots**:
    - `scan_derivative_d1_comparison.png`: Waterfall plot of the 1st derivative for selected window sizes.
    - `scan_derivative_d2_comparison.png`: Waterfall plot of the 2nd derivative for selected window sizes.
    
3.  **Individual Derivative Plots**:
    - `d1_individual/`: Folder containing individual plots of the 1st derivative for each selected window size.
    - `d2_individual/`: Folder containing individual plots of the 2nd derivative for each selected window size.

## Conclusion
(To be filled after running the scan)
- Optimal range appears to be between X and Y points.
