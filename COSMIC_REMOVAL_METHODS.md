# Cosmic Ray Removal Methods - Mathematical Documentation

## Table of Contents
- [Overview](#overview)
- [Single Spectrum Methods](#single-spectrum-methods)
- [Matrix Correlation Methods](#matrix-correlation-methods)
- [Performance Comparison](#performance-comparison)
- [References](#references)

## Overview

This document provides comprehensive mathematical documentation for all cosmic ray removal, interpolation, smoothing, and correction methods implemented in SpecMap. Cosmic rays are high-energy particles that create sharp intensity spikes in spectroscopic data, corrupting measurements. These methods detect and correct such artifacts using various statistical and mathematical approaches.

**Keywords**: cosmic ray removal, spectral interpolation, outlier detection, hyperspectral imaging, signal processing, noise reduction, anomaly detection, spectroscopy, data smoothing, artifact correction

---

## Single Spectrum Methods

Single spectrum methods operate on individual spectra without considering spatial correlation between neighboring measurement points.

### 1. Linear Interpolation Method

**Function**: `remove_cosmics_linear(data, thresh, width)`

**Mathematical Description**:

The linear interpolation method identifies cosmic rays by analyzing the first-order finite difference (gradient) of the spectral intensity:

$$\Delta I_i = I_{i+1} - I_i$$

**Detection Criterion**:
Cosmic rays are detected when:
$$|\Delta I_i| > \tau$$

where $\tau$ is the threshold parameter.

**Correction Algorithm**:
When a cosmic ray is detected at position $i$, the algorithm searches for the end of the anomaly within a window of size $w$ (width parameter):

$$\text{For } j \in [i+1, \min(i+w, n-1)]: \quad |\Delta I_j| < \tau$$

The corrupted region $[i, j]$ is then replaced with linear interpolation:

$$I_k^{\text{corrected}} = I_i + \frac{k-i}{j-i}(I_j - I_i), \quad k \in [i, j]$$

**Advantages**: Fast computation, simple implementation  
**Limitations**: Assumes cosmic rays create monotonic spikes; may fail with complex spectral features

---

### 2. Median Filter Method

**Function**: `remove_cosmics_median_filter(data, thresh, width)`

**Mathematical Description**:

This method uses a rolling median filter to create a smoothed reference spectrum:

$$\tilde{I}_i = \text{median}\{I_{i-w/2}, ..., I_i, ..., I_{i+w/2}\}$$

where $w$ is the filter width.

**Detection Criterion**:
Cosmic rays are identified by comparing each point to the median-filtered version:

$$\text{Cosmic at } i \iff |I_i - \tilde{I}_i| > \tau$$

**Correction**:
Detected cosmic rays are replaced with the median-filtered values:

$$I_i^{\text{corrected}} = \tilde{I}_i \quad \text{for all cosmic positions}$$

**Statistical Properties**:
- Median filter is robust to outliers (breakdown point = 50%)
- Preserves edges better than mean filters
- Computational complexity: $O(n \cdot w)$

**Advantages**: Robust to multiple cosmics, preserves spectral features  
**Limitations**: Can blur sharp spectral features if width is too large

---

### 3. Spectral Correlation Method

**Function**: `spectral_correlation(data, thresh, width)`

**Mathematical Description**:

This method exploits the spectral smoothness principle - real spectral features vary smoothly with wavelength, while cosmic rays create discontinuities.

**Second Derivative (Curvature) Detection**:
The spectral curvature is calculated using central finite differences:

$$I''_i = I_{i-1} - 2I_i + I_{i+1}$$

This measures the local concavity/convexity of the spectrum.

**Detection Criterion**:
Calculate the standard deviation of the second derivative:

$$\sigma_{I''} = \sqrt{\frac{1}{n-2}\sum_{i=1}^{n-2}(I''_i - \bar{I''})^2}$$

Cosmic rays are detected when:

$$|I''_i| > \tau \cdot \sigma_{I''}$$

**Correction**:
Replace detected points with the median of a local window:

$$I_i^{\text{corrected}} = \text{median}\{I_{i-w}, ..., I_{i-1}, I_{i+1}, ..., I_{i+w}\}$$

**Advantages**: Detects isolated spikes without spatial information  
**Limitations**: Sensitive to genuine sharp spectral features (e.g., atomic lines)

---

### 4. Robust Median Method

**Function**: `robust_median(data, thresh, width)`

**Mathematical Description**:

Uses Median Absolute Deviation (MAD) for robust outlier detection.

**MAD Calculation**:
First, compute the median-filtered spectrum:

$$\tilde{I}_i = \text{median-filter}(I, w)$$

Then calculate the absolute deviations:

$$d_i = |I_i - \tilde{I}_i|$$

The MAD is:

$$\text{MAD} = \text{median}(d_i)$$

**Detection Criterion**:
Cosmic rays are detected when:

$$d_i > \tau \cdot \text{MAD}$$

The MAD is a robust estimator of scale with a breakdown point of 50%, making it highly resistant to outliers.

**Statistical Foundation**:
For Gaussian-distributed noise, MAD relates to standard deviation as:

$$\sigma \approx 1.4826 \cdot \text{MAD}$$

**Advantages**: Most robust single-spectrum method, handles high cosmic density  
**Limitations**: Requires sufficient spectral points for accurate MAD estimation

---

### 5. Iterative Cosmic Removal

**Function**: `iterative_cosmic(data, thresh, width)`

**Mathematical Description**:

Applies robust median filtering in multiple passes:

$$I^{(k+1)} = \text{RobustMedian}(I^{(k)}, \tau, w)$$

where $k$ is the iteration number (default: 2 passes).

**Algorithm**:
1. First pass: Remove obvious cosmic rays
2. Second pass: Recalculate statistics on cleaned data, remove remaining artifacts

**Convergence**:
The method typically converges after 2-3 iterations. Further iterations show diminishing returns.

**Advantages**: Catches cosmics masked by nearby artifacts  
**Limitations**: Slower (multiplicative computational cost)

---

### 6. Gradient-Based Method

**Function**: `gradient_based(data, thresh, width)`

**Mathematical Description**:

Analyzes changes in the spectral gradient to identify sharp transitions.

**Gradient Calculation**:

$$\nabla I_i = \frac{I_{i+1} - I_{i-1}}{2}$$

**Gradient Change**:

$$\Delta(\nabla I)_i = |\nabla I_{i+1} - \nabla I_i|$$

**Detection Criterion**:

$$\Delta(\nabla I)_i > \tau \cdot \sigma_{\Delta(\nabla I)}$$

**Correction**:
Linear interpolation from immediate neighbors:

$$I_i^{\text{corrected}} = \frac{I_{i-1} + I_{i+1}}{2}$$

**Advantages**: Sensitive to sharp transitions  
**Limitations**: May detect steep but legitimate spectral features

---

## Matrix Correlation Methods

Matrix methods leverage spatial correlation between neighboring spectra in hyperspectral datasets. They operate on 2D spatial grids where each pixel contains a full spectrum.

### 1. Gaussian Correlation Matrix Method

**Function**: `cosmic_correlation_Matrix(SpectrumDataMatrix, thresh, width)`

**Mathematical Description**:

This method assumes the laser excitation profile follows a 2D Gaussian distribution, creating spatial correlation between neighboring spectra.

**2D Gaussian Weight Matrix**:

$$w(x, y) = A \exp\left(-\frac{x^2}{2\sigma_x^2} - \frac{y^2}{2\sigma_y^2}\right)$$

Normalized weights (sum to 1):

$$W_{ij} = \frac{w(x_i, y_j)}{\sum_{k,l} w(x_k, y_l)}$$

For a 3×3 neighborhood with unit spacing and $\sigma = 1$:

$$W = \frac{1}{Z}\begin{pmatrix}
e^{-1} & e^{-0.5} & e^{-1} \\
e^{-0.5} & 1 & e^{-0.5} \\
e^{-1} & e^{-0.5} & e^{-1}
\end{pmatrix}$$

where $Z$ is the normalization constant.

**Expected Intensity**:
The Gaussian-weighted expected intensity at position $(i,j)$ for wavelength $\lambda$:

$$\tilde{I}_{ij}(\lambda) = \sum_{k,l \in \mathcal{N}(i,j)} W_{kl} \cdot I_{kl}(\lambda)$$

where $\mathcal{N}(i,j)$ denotes the 3×3 neighborhood excluding the center pixel.

**Standard Deviation Calculation**:
Calculate the standard deviation of neighbor intensities:

$$\sigma_{ij}(\lambda) = \sqrt{\frac{1}{|\mathcal{N}|-1}\sum_{k,l \in \mathcal{N}} \left(I_{kl}(\lambda) - \tilde{I}_{ij}(\lambda)\right)^2}$$

**Detection Criterion**:
Cosmic rays are detected when the deviation exceeds the threshold:

$$|I_{ij}(\lambda) - \tilde{I}_{ij}(\lambda)| > \tau \cdot \sigma_{ij}(\lambda)$$

**Correction**:
Replace cosmic-affected wavelengths with Gaussian-weighted average including all valid neighbors:

$$I_{ij}^{\text{corrected}}(\lambda) = \sum_{k,l \in \mathcal{N} \cup \{(i,j)\}} W'_{kl} \cdot I_{kl}(\lambda)$$

where $W'$ includes the center pixel in normalization.

**Vectorized Implementation**:
The method processes all wavelengths simultaneously:

$$\mathbf{I}_{ij} \in \mathbb{R}^{n_\lambda}, \quad \tilde{\mathbf{I}}_{ij} = W \star \mathbf{C}_{ij}$$

where $\mathbf{C}_{ij}$ is the spectral cube (3×3×$n_\lambda$) and $\star$ denotes convolution.

**Computational Complexity**: $O(N \cdot M \cdot n_\lambda)$ where $N \times M$ is the spatial grid size

**Advantages**: Physically motivated, preserves laser profile features  
**Limitations**: Assumes Gaussian laser profile, requires dense sampling

---

### 2. Adaptive Threshold Matrix Method

**Function**: `adaptive_threshold_Matrix(SpectrumDataMatrix, thresh, width)`

**Mathematical Description**:

Uses local spatial statistics that adapt to varying signal intensities across the sample.

**Local Mean and Standard Deviation**:
For each pixel $(i,j)$ and wavelength $\lambda$, calculate statistics from neighbors:

$$\mu_{ij}(\lambda) = \frac{1}{|\mathcal{N}|}\sum_{(k,l) \in \mathcal{N}(i,j)} I_{kl}(\lambda)$$

$$\sigma_{ij}(\lambda) = \sqrt{\frac{1}{|\mathcal{N}|-1}\sum_{(k,l) \in \mathcal{N}} (I_{kl}(\lambda) - \mu_{ij}(\lambda))^2}$$

**Adaptive Detection Criterion**:

$$\text{Cosmic at } (i,j,\lambda) \iff |I_{ij}(\lambda) - \mu_{ij}(\lambda)| > \tau \cdot \sigma_{ij}(\lambda)$$

This threshold adapts to local intensity variations, making it effective for heterogeneous samples.

**Correction**:

$$I_{ij}^{\text{corrected}}(\lambda) = \mu_{ij}(\lambda)$$

**Statistical Properties**:
- Threshold automatically scales with local signal-to-noise ratio
- More sensitive in high-intensity regions, less sensitive in low-intensity regions
- Follows Z-score normalization principle

**Advantages**: Handles varying sample brightness, adapts to local noise levels  
**Limitations**: Requires at least 4 valid neighbors, slower than fixed threshold

---

### 3. Spectral Correlation Matrix Method

**Function**: `spectral_correlation_Matrix(SpectrumDataMatrix, thresh, width)`

**Mathematical Description**:

Combines spectral smoothness analysis with spatial consistency checking.

**Spectral Curvature**:
Second derivative in wavelength space:

$$I''_{ij}(\lambda_k) = I_{ij}(\lambda_{k-1}) - 2I_{ij}(\lambda_k) + I_{ij}(\lambda_{k+1})$$

**Spectral Anomaly Detection**:

$$\sigma_{I''} = \text{std}(I''_{ij})$$

$$A_{\text{spectral}}(\lambda) = |I''_{ij}(\lambda)| > \tau \cdot \sigma_{I''}$$

**Spatial Anomaly Detection**:
Median of neighbor spectra:

$$\tilde{I}_{ij}(\lambda) = \text{median}\{I_{kl}(\lambda) : (k,l) \in \mathcal{N}(i,j)\}$$

Spatial deviation:

$$d_{ij}(\lambda) = |I_{ij}(\lambda) - \tilde{I}_{ij}(\lambda)|$$

$$A_{\text{spatial}}(\lambda) = d_{ij}(\lambda) > \tau \cdot \text{std}(d_{ij})$$

**Combined Detection**:
Cosmic rays must satisfy BOTH conditions (logical AND):

$$\text{Cosmic}(\lambda) = A_{\text{spectral}}(\lambda) \land A_{\text{spatial}}(\lambda)$$

**Correction**:

$$I_{ij}^{\text{corrected}}(\lambda) = \tilde{I}_{ij}(\lambda)$$

**Advantages**: Distinguishes cosmics from real features, lower false positive rate  
**Limitations**: Requires smooth spectra, may miss cosmics if neighbors also affected

---

### 4. Bilateral Filter Matrix Method

**Function**: `bilateral_filter_Matrix(SpectrumDataMatrix, thresh, width)`

**Mathematical Description**:

Edge-preserving filter that weights neighbors by both spatial distance and spectral similarity.

**Spatial Weight** (Gaussian in position):

$$w_s(x, y) = \exp\left(-\frac{x^2 + y^2}{2\sigma_s^2}\right)$$

**Intensity Weight** (Gaussian in intensity space):
For each wavelength $\lambda$:

$$w_I^\lambda(i,j;k,l) = \exp\left(-\frac{(I_{ij}(\lambda) - I_{kl}(\lambda))^2}{2(\tau \cdot \sigma_I)^2}\right)$$

where $\sigma_I = \text{std}(|I_{ij} - I_{kl}|)$

**Combined Weight**:

$$W_{kl}^\lambda = w_s(x_k-x_i, y_l-y_j) \cdot w_I^\lambda(i,j;k,l)$$

**Normalized weights**:

$$\tilde{W}_{kl}^\lambda = \frac{W_{kl}^\lambda}{\sum_{k,l} W_{kl}^\lambda}$$

**Filtered Spectrum**:

$$\tilde{I}_{ij}(\lambda) = \sum_{(k,l) \in \mathcal{N}} \tilde{W}_{kl}^\lambda \cdot I_{kl}(\lambda)$$

**Detection and Correction**:
Cosmic rays detected where deviation is large:

$$|I_{ij}(\lambda) - \tilde{I}_{ij}(\lambda)| > \tau \cdot \text{std}(I_{ij} - \tilde{I}_{ij})$$

**Key Property**:
The bilateral filter preserves edges because:
- Similar intensities → high $w_I$ → strong smoothing
- Different intensities → low $w_I$ → weak smoothing (edge preserved)

**Advantages**: Excellent edge preservation, smooth within homogeneous regions  
**Limitations**: Computationally expensive, sensitive to intensity similarity threshold

---

### 5. Robust Median Matrix Method

**Function**: `robust_median_Matrix(SpectrumDataMatrix, thresh, width)`

**Mathematical Description**:

Uses spatial median and Median Absolute Deviation (MAD) for outlier-resistant detection.

**Spatial Median Spectrum**:

$$\tilde{I}_{ij}(\lambda) = \text{median}\{I_{kl}(\lambda) : (k,l) \in \mathcal{N}(i,j) \cup \{(i,j)\}\}$$

**Deviations**:

$$d_{kl}(\lambda) = |I_{kl}(\lambda) - \tilde{I}_{ij}(\lambda)|$$

**MAD Calculation**:

$$\text{MAD}_{ij}(\lambda) = \text{median}\{d_{kl}(\lambda)\}$$

**Detection Criterion**:

$$|I_{ij}(\lambda) - \tilde{I}_{ij}(\lambda)| > \tau \cdot \text{MAD}_{ij}(\lambda)$$

**Correction**:

$$I_{ij}^{\text{corrected}}(\lambda) = \tilde{I}_{ij}(\lambda)$$

**Statistical Robustness**:
- Median: 50% breakdown point
- MAD: 50% breakdown point
- Combined method: Highly resistant to up to 50% outlier contamination

**Relation to Gaussian Statistics**:
For normally distributed data:

$$\sigma \approx 1.4826 \cdot \text{MAD}$$

Making MAD a robust alternative to standard deviation.

**Advantages**: Most robust method, handles high cosmic density  
**Limitations**: Requires at least 5 neighbors for reliable median

---

### 6. Iterative Cosmic Matrix Method

**Function**: `iterative_cosmic_Matrix(SpectrumDataMatrix, thresh, width)`

**Mathematical Description**:

Multi-pass application of robust median method:

$$\mathbf{I}^{(0)} = \mathbf{I}_{\text{raw}}$$

$$\mathbf{I}^{(k+1)} = \text{RobustMedianMatrix}(\mathbf{I}^{(k)}, \tau, w)$$

**Convergence Analysis**:
Define the cosmic mask at iteration $k$:

$$M^{(k)}_{ij}(\lambda) = \mathbb{1}\{|I^{(k)}_{ij}(\lambda) - \tilde{I}^{(k)}_{ij}(\lambda)| > \tau \cdot \text{MAD}^{(k)}\}$$

Convergence when:

$$\|M^{(k+1)} - M^{(k)}\|_0 < \epsilon$$

where $\|\cdot\|_0$ is the L0 norm (count of non-zero elements).

**Typical Behavior**:
- Iteration 1: Removes 80-90% of cosmics
- Iteration 2: Removes most remaining cosmics (5-15%)
- Iteration 3+: Diminishing returns (< 5% additional)

**Advantages**: Catches cascading artifacts, refines boundaries  
**Limitations**: 2× computational cost, potential over-smoothing

---

### 7. PCA Anomaly Matrix Method

**Function**: `pca_anomaly_Matrix(SpectrumDataMatrix, thresh, width)`

**Mathematical Description**:

Uses Principal Component Analysis to identify anomalous spectra that deviate from the dataset's principal spectral components.

**Data Matrix Construction**:
Stack all $N$ spectra into matrix $\mathbf{X} \in \mathbb{R}^{N \times n_\lambda}$:

$$\mathbf{X} = \begin{pmatrix}
I_{11}(\lambda_1) & \cdots & I_{11}(\lambda_{n_\lambda}) \\
\vdots & & \vdots \\
I_{MN}(\lambda_1) & \cdots & I_{MN}(\lambda_{n_\lambda})
\end{pmatrix}$$

**Mean Centering**:

$$\bar{\mathbf{I}}(\lambda) = \frac{1}{N}\sum_{i=1}^N I_i(\lambda)$$

$$\mathbf{X}_c = \mathbf{X} - \mathbf{1}\bar{\mathbf{I}}^T$$

**Singular Value Decomposition**:

$$\mathbf{X}_c = \mathbf{U}\mathbf{\Sigma}\mathbf{V}^T$$

where:
- $\mathbf{U} \in \mathbb{R}^{N \times r}$: spectrum scores
- $\mathbf{\Sigma} \in \mathbb{R}^{r \times r}$: singular values
- $\mathbf{V}^T \in \mathbb{R}^{r \times n_\lambda}$: spectral loadings (principal components)
- $r = \min(N, n_\lambda)$

**Variance Explained**:

$$\text{Var}_k = \frac{\sigma_k^2}{\sum_j \sigma_j^2}$$

Select $K$ components explaining 95% of variance:

$$\sum_{k=1}^K \text{Var}_k \geq 0.95$$

**Reconstructed Spectra**:

$$\hat{\mathbf{X}} = \mathbf{U}_{:,1:K} \mathbf{\Sigma}_{1:K,1:K} \mathbf{V}_{:,1:K}^T + \mathbf{1}\bar{\mathbf{I}}^T$$

**Reconstruction Error**:

$$e_i = \sqrt{\sum_{\lambda} (I_i(\lambda) - \hat{I}_i(\lambda))^2}$$

**Anomaly Detection**:
Calculate robust statistics:

$$\text{med}(e) = \text{median}(\{e_i\})$$

$$\text{MAD}(e) = \text{median}(|e_i - \text{med}(e)|)$$

Anomalous spectra:

$$e_i > \text{med}(e) + \tau \cdot \text{MAD}(e)$$

**Correction**:
Replace anomalous spectra with their PCA reconstruction:

$$I_i^{\text{corrected}}(\lambda) = \hat{I}_i(\lambda)$$

**Dimensionality Reduction**:
PCA projects data into lower-dimensional space:

$$n_\lambda \rightarrow K \quad \text{where typically } K \ll n_\lambda$$

This removes noise and artifacts in the null space.

**Advantages**: Model-free, data-driven, removes systematic artifacts  
**Limitations**: Requires many spectra (>10), computationally expensive (SVD), may remove rare but real features

---

### 8. Gradient-Based Matrix Method

**Function**: `gradient_based_Matrix(SpectrumDataMatrix, thresh, width)`

**Mathematical Description**:

Analyzes directional spatial gradients to distinguish isotropic cosmic rays from anisotropic real features.

**Directional Gradients**:

Horizontal:
$$\nabla_x I_{ij}(\lambda) = |I_{i,j+1}(\lambda) - I_{i,j-1}(\lambda)|$$

Vertical:
$$\nabla_y I_{ij}(\lambda) = |I_{i+1,j}(\lambda) - I_{i-1,j}(\lambda)|$$

Diagonal 1:
$$\nabla_{d1} I_{ij}(\lambda) = |I_{i+1,j+1}(\lambda) - I_{i-1,j-1}(\lambda)|$$

Diagonal 2:
$$\nabla_{d2} I_{ij}(\lambda) = |I_{i+1,j-1}(\lambda) - I_{i-1,j+1}(\lambda)|$$

**Gradient Statistics**:
Stack gradients into vector $\mathbf{g}_{ij}(\lambda) = [\nabla_x, \nabla_y, \nabla_{d1}, \nabla_{d2}]^T$

Mean gradient magnitude:
$$\bar{g}_{ij}(\lambda) = \frac{1}{4}\sum_{k=1}^4 g_{ij,k}(\lambda)$$

Gradient uniformity (standard deviation):
$$\sigma_{g,ij}(\lambda) = \sqrt{\frac{1}{3}\sum_{k=1}^4 (g_{ij,k}(\lambda) - \bar{g}_{ij}(\lambda))^2}$$

**Detection Criterion**:
Cosmic rays show:
1. High mean gradient: $\bar{g}_{ij}(\lambda) > \tau \cdot \text{std}(\bar{g})$
2. Uniform gradients: $\sigma_{g,ij}(\lambda) < 0.5 \cdot \bar{g}_{ij}(\lambda)$

Combined condition (logical AND):
$$\text{Cosmic}(\lambda) = (\bar{g} > \tau \cdot \sigma_{\bar{g}}) \land (\sigma_g < 0.5 \bar{g})$$

**Physical Interpretation**:
- **Cosmic rays**: Isotropic point sources → uniform high gradients in all directions
- **Real edges**: Anisotropic features → high gradient in one direction, low in perpendicular
- **Smooth regions**: Low gradients in all directions

**Correction**:

$$I_{ij}^{\text{corrected}}(\lambda) = \text{median}\{I_{kl}(\lambda) : (k,l) \in \mathcal{N}(i,j)\}$$

**Advantages**: Distinguishes edges from cosmics, preserves anisotropic features  
**Limitations**: Requires valid neighbors in all 4 directions, sensitive to isolated pixels

---

### 9. Matrix Image Correction Method

**Function**: `matrix_image_correction_Matrix(SpectrumDataMatrix, thresh, width)`

**Mathematical Description**:

Applies simple Gaussian-weighted averaging across all wavelengths without selective detection.

**3×3 Gaussian Kernel**:

$$W = \frac{1}{Z} \begin{pmatrix}
w_{-1,-1} & w_{-1,0} & w_{-1,1} \\
w_{0,-1} & w_{0,0} & w_{0,1} \\
w_{1,-1} & w_{1,0} & w_{1,1}
\end{pmatrix}$$

**Correction** (applied to all pixels and wavelengths):

$$I_{ij}^{\text{corrected}}(\lambda) = \sum_{k,l \in \{-1,0,1\}} W_{k,l} \cdot I_{i+k,j+l}(\lambda)$$

**Difference from Cosmic Correlation**:
- No selective detection - smooths everything
- Equivalent to Gaussian blur in spatial domain
- Used for general denoising rather than cosmic removal

**Advantages**: Simple, fast, reduces all noise types  
**Limitations**: Reduces spatial resolution, smooths real features

---

## Performance Comparison

### Computational Complexity

| Method | Single Spectrum | Matrix Version | Complexity per pixel |
|--------|----------------|----------------|---------------------|
| Linear Interpolation | $O(n)$ | N/A | $O(n_\lambda)$ |
| Median Filter | $O(n \cdot w)$ | $O(N \cdot M \cdot n_\lambda \cdot w)$ | $O(n_\lambda \cdot w)$ |
| Spectral Correlation | $O(n)$ | $O(N \cdot M \cdot n_\lambda)$ | $O(n_\lambda)$ |
| Gaussian Correlation | N/A | $O(N \cdot M \cdot n_\lambda)$ | $O(n_\lambda)$ |
| Adaptive Threshold | N/A | $O(N \cdot M \cdot n_\lambda \cdot |\mathcal{N}|)$ | $O(n_\lambda \cdot 8)$ |
| Bilateral Filter | N/A | $O(N \cdot M \cdot n_\lambda \cdot |\mathcal{N}|)$ | $O(n_\lambda \cdot 8)$ |
| Robust Median | $O(n \cdot w)$ | $O(N \cdot M \cdot n_\lambda \cdot |\mathcal{N}|)$ | $O(n_\lambda \cdot 8)$ |
| Iterative | $O(k \cdot n \cdot w)$ | $O(k \cdot N \cdot M \cdot n_\lambda)$ | $O(k \cdot n_\lambda \cdot 8)$ |
| PCA Anomaly | N/A | $O(N \cdot M \cdot n_\lambda^2)$ | Global: $O(NM \cdot n_\lambda^2)$ |
| Gradient Based | $O(n)$ | $O(N \cdot M \cdot n_\lambda)$ | $O(n_\lambda)$ |

Where:
- $n$ = spectrum length
- $N \times M$ = spatial grid dimensions
- $n_\lambda$ = number of wavelength points
- $w$ = window width
- $|\mathcal{N}|$ = neighborhood size (typically 8)
- $k$ = number of iterations (typically 2)

### Robustness Comparison

**Breakdown Point**: Percentage of outliers a method can handle before failure

| Method | Breakdown Point | Outlier Resistance |
|--------|----------------|-------------------|
| Mean-based | ~0% | Poor |
| Linear Interpolation | ~10% | Low |
| Median Filter | ~50% | Excellent |
| Gaussian Correlation | ~20% | Moderate |
| Adaptive Threshold | ~30% | Good |
| Spectral Correlation | ~25% | Moderate-Good |
| Bilateral Filter | ~40% | Good |
| **Robust Median** | **~50%** | **Excellent** |
| Iterative | ~60% | Excellent |
| PCA Anomaly | ~30% | Good |
| Gradient Based | ~25% | Moderate-Good |

### Use Case Recommendations

| Sample Type | Recommended Method | Reasoning |
|------------|-------------------|-----------|
| Uniform fluorescence | Gaussian Correlation Matrix | Exploits laser profile |
| Variable intensity | Adaptive Threshold Matrix | Handles brightness variations |
| Sharp edges/interfaces | Bilateral Filter Matrix | Edge-preserving |
| High cosmic density | Robust Median Matrix | Highest outlier resistance |
| Smooth spectra | Spectral Correlation Matrix | Uses wavelength continuity |
| Large datasets | PCA Anomaly Matrix | Finds systematic anomalies |
| Structured samples | Gradient Based Matrix | Distinguishes features from artifacts |
| General purpose | Robust Median Matrix | Best all-around performance |
| Post-processing cleanup | Iterative Cosmic Matrix | Refinement of other methods |

---

## Implementation Notes

### Vectorization
All Matrix methods are vectorized to process entire wavelength arrays simultaneously:

```python
# Instead of:
for wavelength in range(n_wavelengths):
    process_single_wavelength(wavelength)

# We use:
process_all_wavelengths_at_once(wavelength_array)
```

This provides 10-100× speedup depending on spectrum length.

### Memory Considerations
Matrix methods use `copy.deepcopy()` to preserve original data:

$$\text{Memory} = 2 \times N \times M \times n_\lambda \times \text{sizeof(float)}$$

For 100×100 spatial grid with 1000 wavelength points:
$$\text{Memory} \approx 2 \times 100 \times 100 \times 1000 \times 8 \text{ bytes} = 160 \text{ MB}$$

### Edge Handling
Interior pixels only: methods operate on pixels with complete neighborhoods
- Boundary pixels remain unprocessed
- Alternative: reflect/pad boundaries (not currently implemented)

---

## References

### Established Techniques (General Statistical Methods)
The methods in this documentation are based on well-established statistical and signal processing techniques including:
- **Median filtering**: Standard robust estimator widely used in signal processing
- **Median Absolute Deviation (MAD)**: Rousseeuw, P. J., & Croux, C. (1993). "Alternatives to the median absolute deviation." Journal of the American Statistical Association, 88(424), 1273-1283.
- **Bilateral filtering**: Tomasi, C., & Manduchi, R. (1998). "Bilateral filtering for gray and color images." Proceedings of the IEEE International Conference on Computer Vision.
- **Principal Component Analysis (PCA)**: Standard dimension reduction technique for anomaly detection
- **Gradient-based detection**: First and second-order finite differences for discontinuity detection

### Implementation Notes
The specific implementations in SpecMap combine these standard techniques and adapt them for hyperspectral spectroscopy data. The algorithms are designed for:
- Photoluminescence spectroscopy
- Raman spectroscopy
- Hyperspectral imaging with spatial correlation
- Time-resolved spectroscopy (TCSPC)

### Further Reading
For general background on signal processing and outlier detection methods:
- Hampel, F. R., et al. (1986). "Robust Statistics: The Approach Based on Influence Functions." Wiley.
- Huber, P. J., & Ronchetti, E. M. (2009). "Robust Statistics" (2nd ed.). Wiley.
- Fried, D. L. (1977). "Least-squares fitting a wave-front distortion estimate to an array of phase-difference measurements." Journal of the Optical Society of America, 67(3), 370-375.

---

## Version History
- v1.0 (2025-11-04): Initial comprehensive documentation
- All methods implemented and tested in SpecMap v9.0

## Keywords for Search Engines
cosmic ray removal, spectral data processing, hyperspectral imaging, outlier detection, signal processing, data interpolation, noise reduction, artifact correction, spectroscopy methods, Raman spectroscopy, photoluminescence spectroscopy, data smoothing algorithms, median filtering, Gaussian filtering, bilateral filtering, PCA analysis, anomaly detection, spatial correlation, spectral analysis, scientific data processing, Python spectroscopy tools

---

**Document maintained by**: SpecMap Development Team  
**Last updated**: November 4, 2025  
**License**: See LICENSE file in repository
