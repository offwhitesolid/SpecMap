# Optimization of Derivative Calculation Parameters for Hyperspectral Imaging Analysis

## 1. Introduction
Derivative spectroscopy is a powerful technique used to enhance spectral resolution and resolve overlapping peaks in hyperspectral imaging (HSI) data. However, the differentiation process inherently amplifies high-frequency noise. To mitigate this, a smoothing step is required. This study aims to optimize the parameters of a sliding window polynomial fitting algorithm (Savitzky-Golay filter) to achieve an optimal balance between **noise reduction** and **signal fidelity**.

## 2. Methodology

### 2.1 Algorithm Description
The derivative calculation is performed using a local polynomial regression method. For each spectral point $x_i$ with intensity $y_i$, a polynomial $P(x)$ of order $k$ is fitted to a window of $N$ adjacent points centered at $x_i$.

$$ P(x) = \sum_{j=0}^{k} c_j x^j $$

The derivatives at the center point $x_i$ are then computed analytically from the coefficients of the fitted polynomial:
- **1st Derivative**: $P'(x_i)$
- **2nd Derivative**: $P''(x_i)$

This approach combines smoothing and differentiation in a single step, avoiding the noise amplification associated with finite difference methods.

### 2.2 Parameter Space
The critical parameter governing the filter's performance is the **Window Size ($N$)**.
- **Small $N$**: Preserves subtle spectral features but provides minimal noise suppression.
- **Large $N$**: Offers strong noise suppression but risks signal distortion (peak broadening and amplitude attenuation).

In this study, we perform a parameter scan over $N$ ranging from **5 to 59 points**, while keeping the polynomial order fixed at **$k=2$**.

## 3. Quantitative Evaluation Metrics

To objectively assess the quality of the derivatives, three complementary metrics are calculated for each window size:

### 3.1 Fit Fidelity: Root Mean Square Error (RMSE)
The RMSE quantifies the deviation of the fitted polynomial from the raw spectral data. It serves as a measure of "goodness of fit".

$$ RMSE = \sqrt{\frac{1}{M} \sum_{i=1}^{M} (y_{raw, i} - y_{fit, i})^2} $$

*   **Interpretation**: A lower RMSE indicates a fit that closely follows the raw data. However, an extremely low RMSE may indicate overfitting (tracking noise), while a high RMSE indicates underfitting (oversmoothing).

### 3.2 Derivative Roughness (Noise Quantification)
Roughness measures the high-frequency noise remaining in the derivative signal. It is calculated as the standard deviation of the finite difference of the derivative spectrum.

$$ R_{deriv} = \sigma( \Delta y'_{deriv} ) = \sqrt{\frac{1}{M-1} \sum_{i=1}^{M-1} ((y'_{i+1} - y'_i) - \mu_{\Delta})^2} $$

*   **Interpretation**: Lower roughness corresponds to a smoother derivative profile. A rapid decrease in roughness with increasing $N$ indicates effective noise suppression.

### 3.3 Signal Preservation (Max Amplitude)
Smoothing filters inevitably attenuate the amplitude of spectral peaks. We monitor the maximum absolute amplitude of the derivative as a proxy for signal preservation.

$$ A_{max} = \max(|y'_{deriv}|) $$

*   **Interpretation**: A significant drop in $A_{max}$ indicates over-smoothing and loss of spectral information. The optimal window size should maximize smoothness while maintaining $A_{max}$ relatively stable.

## 4. Visualization and Output

The analysis script (`test_derivative_window_scan.py`) generates a comprehensive set of visualizations stored in a directory named after the source spectrum (e.g., `HSI20250725_HSI1_00040/`).

### 4.1 Metric Scan (`scan_metrics.png`)
A 3x2 grid visualizing the evolution of the metrics:
- **Top Row**: Fit RMSE vs. Window Size.
- **Middle Row**: Roughness of 1st and 2nd derivatives.
- **Bottom Row**: Maximum Amplitude of 1st and 2nd derivatives.

### 4.2 Waterfall Plots (`scan_derivative_d1/d2_comparison.png`)
To visualize the morphological changes in the derivative signals, waterfall plots are generated. These plots stack the derivative spectra for selected window sizes ($N \in \{2, 5, 10, 15, 20, 25, 30, 35\}$) vertically, allowing for a direct comparison of noise levels and peak shapes.

### 4.3 Individual Profiles (`d1_individual/`, `d2_individual/`)
Individual plots for each selected window size are saved to facilitate detailed inspection of specific parameter sets.

## 5. Conclusion and Recommendation
(This section is to be completed based on the specific dataset analysis)
*   **Noise Regime**: For high-noise data, a window size of $N > 25$ is typically recommended.
*   **Feature Regime**: For spectra with narrow features, $N < 15$ is preferred to avoid peak broadening.
*   **General Recommendation**: A window size of **$N \approx 15-25$** often provides a robust compromise for typical HSI data.
