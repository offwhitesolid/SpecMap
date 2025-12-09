# Mathlib Documentation: The `fitkeys` Architecture

## 1. Introduction
`mathlib3.py` is the core mathematical engine of the SpecMap application. It is architected around a central registry dictionary named `fitkeys`. 

For a physicist or developer, `fitkeys` serves as the **dispatch table** that defines the contract between the application layer (GUI) and the underlying physical models. It maps a unique string identifier (the "method key") to a complete definition of the analysis protocol, encapsulating the mathematical model, the optimization algorithm, the output parameter space, and derived physical properties.

## 2. The `fitkeys` Schema
Every analysis method in the library is defined by a list of exactly 9 elements stored in `fitkeys`. Understanding this schema is essential for interpreting the analysis results.

| Index | Component | Type | Description |
| :--- | :--- | :--- | :--- |
| **0** | **Window Function** | `callable` | The theoretical model $M(x, \mathbf{p})$ used for visualization and reconstruction. <br>• For **Standard Fits**, this is the line shape function (e.g., Gaussian). <br>• For **Fit-Free Methods**, this is often a reconstruction function (e.g., split-Gaussian) or returns zeros. |
| **1** | **Fit Function** | `callable` | The core algorithm. It accepts spectral data vectors $\mathbf{X}, \mathbf{Y}$ and returns the parameter vector $\mathbf{p}$. <br>• **Optimization**: Uses `scipy.optimize.curve_fit` (Levenberg-Marquardt). <br>• **Algebraic**: Calculates metrics directly (e.g., Moments, Derivatives). |
| **2** | **Max Function** | `callable` | Calculates the peak maximum coordinates $(x_{max}, y_{max})$ from the parameter vector $\mathbf{p}$. |
| **3** | **Label** | `str` | The human-readable name of the method displayed in the GUI. |
| **4** | **Param Count** | `int` | The dimension $N$ of the parameter vector $\mathbf{p}$. |
| **5** | **Param Names** | `list[str]` | Semantic labels for each element $p_i$ in $\mathbf{p}$. |
| **6** | **Units** | `list[str]` | Physical units for each element $p_i$ (e.g., 'eV', 'Counts', 'nm'). |
| **7** | **FWHM Function** | `callable` | Calculates the Full Width at Half Maximum $\Gamma$ from the parameter vector $\mathbf{p}$. Returns 0.0 if undefined. |
| **8** | **State** | `int` | Mutable state tracker (0=Initialized, 1=Converged, 2=Failed). |

---

## 3. Catalog of Methods (The Registry)

The following sections detail the physical models and algorithms defined in `fitkeys`, grouped by their analytical approach.

### 3.1 Standard Line Shape Fits
These methods utilize non-linear least squares minimization to fit a model $M(x, \mathbf{p})$ to the data.

#### **Gaussian Fit** (`fitkeys['gaussian']`)
*   **Window Function (Index 0)**:
    $G(x) = A \cdot \exp\left(-\frac{(x - x_0)^2}{2w^2}\right)$
*   **Parameter Vector $\mathbf{p}$ (Indices 4, 5, 6)**:
    1.  `Gaussian amplitude` ($A$) [Counts]: Peak height.
    2.  `Gaussian center` ($x_0$) [nm/eV]: Peak position.
    3.  `Gaussian width` ($w$) [nm/eV]: Standard deviation $\sigma$.
*   **Derived Properties (Index 7)**:
    *   **FWHM**: $2\sqrt{2\ln 2} \cdot w \approx 2.355 \cdot w$

#### **Lorentzian Fit** (`fitkeys['lorentz']`)
*   **Window Function (Index 0)**:
    $L(x) = \frac{A}{1 + \left(\frac{x - x_0}{w}\right)^2}$
*   **Parameter Vector $\mathbf{p}$ (Indices 4, 5, 6)**:
    1.  `Lorentzian amplitude` ($A$) [Counts]
    2.  `Lorentzian center` ($x_0$) [nm/eV]
    3.  `Lorentzian width` ($w$) [nm/eV]: Half-Width at Half-Maximum (HWHM).
*   **Derived Properties (Index 7)**:
    *   **FWHM**: $2 \cdot w$

#### **Voigt Fit** (`fitkeys['voigt']`)
*   **Window Function (Index 0)**: Pseudo-Voigt profile (linear combination).
    $$ V(x) = A \cdot [\eta \cdot L(x) + (1 - \eta) \cdot G(x)] $$
*   **Parameter Vector $\mathbf{p}$ (Indices 4, 5, 6)**:
    1.  `Voigt amplitude` ($A$) [Counts]
    2.  `Voigt center` ($x_0$) [nm/eV]
    3.  `Voigt width` ($w$) [nm/eV]: FWHM.
    4.  `Voigt gamma` ($\eta$) [nm/eV]: Mixing parameter ($0 \le \eta \le 1$).
*   **Derived Properties (Index 7)**:
    *   **FWHM**: Returns parameter $w$ directly.

#### **Linear Fit** (`fitkeys['linear']`)
*   **Window Function (Index 0)**:
    $$ y = a \cdot x + b $$
*   **Parameter Vector $\mathbf{p}$ (Indices 4, 5, 6)**:
    1.  `Linear slope` ($a$) [nm/Counts]
    2.  `Linear offset` ($b$) [Counts]

#### **Double Variants** (`'double gaussian'`, `'double lorentz'`, `'double voigt'`)
*   **Window Function (Index 0)**: Superposition of two independent profiles.
    $$ F_{double}(x) = F_1(x) + F_2(x) $$
*   **Parameter Vector $\mathbf{p}$**: Concatenation of parameters for Peak 1 and Peak 2.

---

### 3.2 Fit-Free Analysis
These methods do not optimize a model function. Instead, the **Fit Function (Index 1)** performs direct algebraic transformations on the data vectors $\mathbf{X}, \mathbf{Y}$ to populate the parameter vector $\mathbf{p}$.

#### **Stiffness Analysis** (`fitkeys['stiffness']`)
Analyzes peak shape via flank slopes and top curvature.
*   **Algorithm (Index 1)**:
    1.  **Slopes**: Linear regression on left/right flanks (baseline to 50% max).
    2.  **Curvature**: Quadratic fit to top 10% of peak.
*   **Parameter Vector $\mathbf{p}$ (Indices 4, 5, 6)**:
    1.  `Peak Energy` ($E_{max}$) [eV]
    2.  `Peak Intensity` ($I_{max}$) [Counts]
    3.  `Left Stiffness` ($a_L$) [Counts/eV]: Slope of rising flank.
    4.  `Right Stiffness` ($a_R$) [Counts/eV]: Slope of falling flank.
    5.  `Asymmetry` ($S_{asym}$): $\frac{|a_R| - a_L}{|a_R| + a_L}$
    6.  `Curvature` ($c_2$) [Counts/eV²]: 2nd derivative proxy.
*   **Window Function (Index 0)**: Reconstructs a split-Gaussian using widths estimated from the slopes $a_L, a_R$.

#### **Derivative Analysis** (`fitkeys['derivative']`)
Uses Savitzky-Golay filtering to analyze derivatives.
*   **Algorithm (Index 1)**:
    1.  Computes $1^{st}$ ($d1$) and $2^{nd}$ ($d2$) derivatives.
    2.  Finds extrema in $d1$ (max rise/fall slopes).
*   **Parameter Vector $\mathbf{p}$ (Indices 4, 5, 6)**:
    1.  `Peak Energy` [eV]
    2.  `Peak Intensity` [Counts]
    3.  `Max Rise Slope` [Counts/eV]: $\max(d1)$
    4.  `Max Fall Slope` [Counts/eV]: $\min(d1)$
    5.  `Peak Curvature` [Counts/eV²]: $d2$ at peak.
    6.  `Slope Asymmetry`: $\frac{|Slope_{fall}| - Slope_{rise}}{|Slope_{fall}| + Slope_{rise}}$
    7.  `Inflection Width` [eV]: Distance between max rise and max fall.
    8.  `Inflection Asymmetry`: Asymmetry of inflection point positions.
*   **Window Function (Index 0)**: Reconstructs a split-Gaussian based on inflection width and asymmetry.

#### **Moment Analysis** (`fitkeys['moments']`)
Treats the spectrum as a probability distribution $P(x)$.
*   **Algorithm (Index 1)**: Calculates statistical moments.
*   **Parameter Vector $\mathbf{p}$ (Indices 4, 5, 6)**:
    1.  `Center of Mass` ($\mu$) [eV]: $\sum x_i P_i$
    2.  `Total Intensity` [Counts]: $\sum I_i$
    3.  `Sigma (Variance)` ($\sigma$) [eV]: $\sqrt{\sum (x_i - \mu)^2 P_i}$
    4.  `Skewness` ($\gamma$): $3^{rd}$ standardized moment.
    5.  `Quantile Width (16-84%)` ($W_{68}$) [eV]: Width containing 68% of intensity.
    6.  `Quantile Asymmetry`: Asymmetry of the 16-50-84% quantiles.
*   **Window Function (Index 0)**: Reconstructs a Gaussian using $\mu$ and $\sigma$.

#### **Center of Mass** (`fitkeys['com']`)
*   **Algorithm (Index 1)**: Weighted average position.
*   **Parameter Vector $\mathbf{p}$**:
    1.  `Center of Mass` [eV]
    2.  `Integrated Intensity` [Counts]
*   **Window Function (Index 0)**: Returns zeros (no shape reconstruction).

#### **Decay/Rise Slope** (`fitkeys['decay']`)
*   **Algorithm (Index 1)**: Discrete derivatives on flanks. Uses percentiles (5th/95th) for robustness.
*   **Parameter Vector $\mathbf{p}$**:
    1.  `Peak Energy` [eV]
    2.  `Peak Intensity` [Counts]
    3.  `Max Decay Slope` [Counts/eV]: Steepest descent on right flank.
    4.  `Decay Slope Energy` [eV]: Position of max decay.
    5.  `Max Rise Slope` [Counts/eV]: Steepest ascent on left flank.
    6.  `Rise Slope Energy` [eV]: Position of max rise.
*   **Window Function (Index 0)**: Returns zeros.

#### **Binning Decay** (`fitkeys['binning']`)
*   **Algorithm (Index 1)**: Resamples spectrum to 11 equidistant points and calculates differences.
*   **Parameter Vector $\mathbf{p}$**:
    1.  `Start Intensity` [Counts]
    2.  `Bin Diff 1`...`Bin Diff 10` [Counts]: Change in intensity between bins.
*   **Window Function (Index 0)**: Reconstructs the piecewise linear binned spectrum.

---

### 3.3 Signal Processing

#### **Oscillation Analysis** (`fitkeys['oscillations']`)
Extracts periodic signals overlaying a broad background.
*   **Algorithm (Index 1)**:
    1.  Background estimation via Savitzky-Golay.
    2.  Subtraction to isolate oscillations.
    3.  Peak finding to determine phase evolution.
*   **Parameter Vector $\mathbf{p}$ (Indices 4, 5, 6)**:
    *   12 parameters including:
        *   `Oscillation frequency estimate` [eV⁻¹]
        *   `Phase chirp rate` [eV⁻²]
        *   `Oscillation amplitude` [Counts]
*   **Window Function (Index 0)**: `None` (Visualization handled by specialized routines).

## 2D Fitting Functions
`mathlib3.py` also includes functions for fitting 2D Gaussian profiles to image data (PixelMatrix).

*   **`fitgaussian2dtomatrix`**: Fits an axis-aligned 2D Gaussian.
*   **`fitgaussiand2dtomatrixrot`**: Fits a rotated 2D Gaussian.
*   **Outputs**: Beam Waist (X/Y), FWHM (X/Y), Rotation Angle.

## Helper Functions
*   **`estimate_..._params`**: Heuristics for guessing initial fit parameters (essential for convergence).
*   **`get...fwhm`**: Standardized calculation of FWHM for different profile types.
*   **`Newtonmax` / `Maxbyinsert`**: Numerical methods for finding the precise maximum of a fitted function.

## Usage Example
To access a specific analysis method programmatically:

```python
import mathlib3 as lib

# Get the fit function for Gaussian
method_key = 'gaussian'
fit_func = lib.fitkeys[method_key][1]

# Perform the fit
# params = fit_func(start_index, end_index, wavelength_array, intensity_array)
```

## References
    A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of Data by
    Simplified Least Squares Procedures. Analytical Chemistry, 1964, 36 (8),
    pp 1627-1639, DOI: [10.1021/ac60214a047](https://doi.org/10.1021/ac60214a047).

    Jianwen Luo, Kui Ying, and Jing Bai. 2005. Savitzky-Golay smoothing and
    differentiation filter for even number data. Signal Process.
    85, 7 (July 2005), 1429-1434. DOI: [j.sigpro.2005.02.002](https://doi.org/10.1016/j.sigpro.2005.02.002).
