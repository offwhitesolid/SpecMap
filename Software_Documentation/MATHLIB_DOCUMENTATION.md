# Mathlib Documentation

## Overview
`mathlib3.py` is the core mathematical library for the SpecMap application. It provides a comprehensive suite of functions for analyzing hyperspectral data, ranging from standard peak fitting (Gaussian, Lorentzian, Voigt) to advanced "fit-free" analysis methods (Moments, Stiffness, Derivative).

The library is designed around a central registry called `fitkeys`, which standardizes the interface for the GUI to interact with various analysis methods.

## Core Architecture: The `fitkeys` Registry

The `fitkeys` dictionary is the heart of the library. It maps a unique string key to a list of properties that define how an analysis method behaves.

### Structure
Each entry in `fitkeys` follows this structure:

| Index | Component | Description |
| :--- | :--- | :--- |
| 0 | **Window Function** | The mathematical model used for visualization (e.g., `gaussianwind`). Returns `zeros` for fit-free methods. |
| 1 | **Fit Function** | The function that performs the analysis (e.g., `fitgaussiantospec`). Returns parameters. |
| 2 | **Max Function** | Function to calculate the peak maximum position and intensity from parameters. |
| 3 | **Label** | Human-readable name displayed in the GUI. |
| 4 | **Param Count** | Number of output parameters. |
| 5 | **Param Names** | List of strings naming each parameter. |
| 6 | **Units** | List of strings defining the unit for each parameter. |
| 7 | **FWHM Function** | Function to calculate Full Width at Half Maximum from parameters. |
| 8 | **State** | Internal state tracker (0=not fitted, 1=fitted, 2=failed). |

---

## Analysis Methods

Each analysis method in `mathlib3.py` processes the input spectral arrays `X` (Energy/Wavelength) and `Y` (Intensity) to extract specific parameters.

### 1. Standard Peak Fitting
These methods use `scipy.optimize.curve_fit` to minimize the least-squares error between the data and a model function.

#### **Gaussian Fit** (`'gaussian'`)
Models the peak as a Gaussian distribution.

$$ G(x) = A \cdot \exp\left(-\frac{(x - x_0)^2}{2w^2}\right) $$
*   **Parameters**:
    *   `Gaussian amplitude` ($A$): Peak height.
    *   `Gaussian center` ($x_0$): Peak position.
    *   `Gaussian width` ($w$): Standard deviation ($\sigma$).
*   **FWHM**: $2\sqrt{2\ln 2} \cdot w \approx 2.355 \cdot w$

#### **Lorentzian Fit** (`'lorentz'`)
Models the peak as a Lorentzian (Cauchy) distribution.

$$ L(x) = \frac{A}{1 + \left(\frac{x - x_0}{w}\right)^2} $$
*   **Parameters**:
    *   `Lorentzian amplitude` ($A$): Peak height.
    *   `Lorentzian center` ($x_0$): Peak position.
    *   `Lorentzian width` ($w$): Half-Width at Half-Maximum (HWHM).
*   **FWHM**: $2 \cdot w$

#### **Voigt Fit** (`'voigt'`)
Models the peak as a Pseudo-Voigt profile (linear combination of Gaussian and Lorentzian).

$$ V(x) = A \cdot [\eta \cdot L(x) + (1 - \eta) \cdot G(x)] $$
*   **Parameters**:
    *   `Voigt amplitude` ($A$): Peak height.
    *   `Voigt center` ($x_0$): Peak position.
    *   `Voigt width` ($w$): Full Width at Half Maximum (FWHM).
    *   `Voigt gamma` ($\eta$): Mixing parameter ($0 \le \eta \le 1$). 0 = Pure Gaussian, 1 = Pure Lorentzian.

#### **Linear Fit** (`'linear'`)
Models the background as a straight line.

$$ y = a \cdot x + b $$
*   **Parameters**:
    *   `Linear slope` ($a$): Gradient.
    *   `Linear offset` ($b$): Y-intercept.

#### **Double Variants** (`'double gaussian'`, `'double lorentz'`, `'double voigt'`)
Sum of two independent profiles.

$$ F_{double}(x) = F_1(x) + F_2(x) $$
*   **Parameters**: Concatenation of parameters for Peak 1 and Peak 2.

---

### 2. Fit-Free Analysis
These methods calculate metrics directly from the data arrays `X` and `Y` without optimizing a model function.

#### **Stiffness Analysis** (`'stiffness'`)
Analyzes the steepness of the peak flanks.
1.  **Flank Slopes**: Performs linear regression on the left ($a_L$) and right ($a_R$) flanks (between baseline and 50% peak height).
2.  **Asymmetry**:

    $$ S_{asym} = \frac{|a_R| - a_L}{|a_R| + a_L} $$
3.  **Curvature**: Fits a quadratic $I(E) = c_0 + c_1(E-E_{max}) + c_2(E-E_{max})^2$ to the peak top (top 10%).
    *   `Curvature` = $c_2$ (Second derivative proxy).

#### **Derivative Analysis** (`'derivative'`)
Uses a Savitzky-Golay filter to compute smooth derivatives.
1.  **Smoothing**: Computes $1^{st}$ ($d1$) and $2^{nd}$ ($d2$) derivatives.
2.  **Max Rise Slope**: $\max(d1)$ on the left flank (steepest ascent).
3.  **Max Fall Slope**: $\min(d1)$ on the right flank (steepest descent).
4.  **Inflection Width**: Distance between the energy positions of Max Rise and Max Fall slopes.
5.  **Slope Asymmetry**:

    $$ A_{slope} = \frac{|Slope_{fall}| - Slope_{rise}}{|Slope_{fall}| + Slope_{rise}} $$

#### **Moment Analysis** (`'moments'`)
Treats the normalized spectrum $P(x) = \frac{I(x)}{\sum I(x)}$ as a probability distribution.
1.  **Center of Mass** ($\mu$): First Moment.

    $$ \mu = \sum x_i \cdot P(x_i) $$
2.  **Sigma** ($\sigma$): Square root of Second Moment (Variance).

    $$ \sigma = \sqrt{\sum (x_i - \mu)^2 \cdot P(x_i)} $$
3.  **Skewness** ($\gamma$): Third Standardized Moment.

    $$ \gamma = \frac{\sum (x_i - \mu)^3 \cdot P(x_i)}{\sigma^3} $$
4.  **Quantile Width**: Width containing 68% of total intensity.

    $$ W_{68} = x_{84\%} - x_{16\%} $$
    Where $x_{p\%}$ is the energy where the cumulative sum reaches $p\%$.

#### **Center of Mass** (`'com'`)
Calculates the intensity-weighted average position.

$$ \lambda_{COM} = \frac{\sum \lambda_i \cdot I_i}{\sum I_i} $$
*   **Parameters**: `Center of Mass`, `Integrated Intensity` ($\sum I_i$).

#### **Decay/Rise Slope** (`'decay'`)
Calculates the steepest slopes using discrete derivatives $s_i = \frac{I_{i+1} - I_i}{x_{i+1} - x_i}$.
1.  **Max Decay Slope**: The 5th percentile of slopes on the right flank (robust minimum).
2.  **Max Rise Slope**: The 95th percentile of slopes on the left flank (robust maximum).
*   **Parameters**: Slope values and their corresponding energy positions.

#### **Binning Decay** (`'binning'`)
Resamples the spectrum to reduce dimensionality.
1.  **Resampling**: Interpolates the spectrum onto 11 equidistant points across the range.
2.  **Differencing**: Calculates the intensity change between consecutive bins.

    $$ \Delta I_j = I_{bin, j+1} - I_{bin, j} $$
*   **Parameters**: `Start Intensity` ($I_{bin, 0}$) and 10 `Bin Diff` values.

---

### 3. Oscillation Analysis (`'oscillations'`)
Extracts periodic signals overlaying a broad background.
1.  **Background Removal**: $B(x)$ is estimated using a Savitzky-Golay filter (window=51, order=3).
2.  **Isolation**: $O(x) = Y(x) - B(x)$.
3.  **Peak Finding**: Identifies local maxima and minima in $O(x)$.
4.  **Phase Evolution**: Calculates instantaneous frequency $f(E)$ from peak spacing.

    $$ f(E) \approx \frac{1}{\Delta E_{peaks}} $$
    Fits a linear trend $f(E) = m \cdot E + c$ to quantify "chirp".
*   **Parameters**: Amplitude, Frequency Estimate, Phase Chirp Rate, etc.

---

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
