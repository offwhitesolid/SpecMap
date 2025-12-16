# Implementation Plan: First and Second Derivative Methods (Finite Differences)

**Document Purpose:** Step-by-step implementation guide for adding first and second derivative analysis methods to `mathlib3.py` fitkeys registry for hyperspectral contrast analysis.

**Date:** December 16, 2025  
**Target File:** `mathlib3.py`  
**Methods to Add:** `'derivative1'` (First Derivative) and `'derivative2'` (Second Derivative)

---

## 1. Understanding the fitkeys Structure

### 1.1 The 9-Element Schema

Each entry in the `fitkeys` dictionary follows this structure:

```python
'method_name': [
    window_function,      # [0] Visualization/reconstruction function
    fit_function,         # [1] Main analysis function (does the computation)
    getmax_function,      # [2] Extracts max position and intensity
    'Display Label',      # [3] Human-readable label for GUI
    param_count,          # [4] Number of output parameters (int)
    ['Param Names'],      # [5] List of parameter names (strings)
    ['Units'],            # [6] List of units for each parameter
    fwhm_function,        # [7] FWHM calculation function (or None)
    state                 # [8] Fit state: 0=not fitted, 1=fitted, 2=failed
]
```

### 1.2 Function Signatures (Standard Pattern)

From analyzing existing implementations like `'decay'`, `'moments'`, and `'derivative'` (Savitzky-Golay):

**Main Analysis Function:**
```python
def fit_function(start, end, WL, PLB, maxfev=10000, guess=None):
    """
    Perform analysis on spectrum region.
    
    Parameters:
    -----------
    start : int - Start index in wavelength array
    end : int - End index in wavelength array
    WL : array - Full wavelength/energy array
    PLB : array - Full intensity array
    maxfev : int - Max function evaluations (unused for fit-free methods)
    guess : None or array - Initial guess (unused for fit-free methods)
    
    Returns:
    --------
    param1, param2, ..., paramN, pcov
    - Returns N float parameters + pcov (usually None for fit-free)
    """
```

**Window Function:**
```python
def window_function(x, param1, param2, ..., paramN):
    """
    Reconstruct or visualize the result.
    
    Parameters:
    -----------
    x : array - Energy/wavelength array for visualization
    param1, param2, ..., paramN : float - Parameters from fit_function
    
    Returns:
    --------
    y : array - Reconstructed intensity array (same shape as x)
    """
```

**Getmax Function:**
```python
def getmax_function(xmin, xmax, param1, param2, ..., *args):
    """
    Extract peak position and intensity.
    
    Returns:
    --------
    x_max : float - Position of maximum
    y_max : float - Intensity at maximum
    """
```

**FWHM Function:**
```python
def fwhm_function(params):
    """
    Calculate FWHM from parameters.
    
    Parameters:
    -----------
    params : list/tuple - All parameters from fit_function
    
    Returns:
    --------
    fwhm : float - Full width at half maximum (or 0.0 if not applicable)
    """
```

---

## 2. Contrast Parameters for Hyperspectral Imaging

### 2.1 What Makes a Good Contrast Parameter?

In hyperspectral imaging, each pixel contains a full spectrum. When we map a contrast parameter across the image, we need quantities that:

1. **Distinguish Spectral Features:** Highlight differences between different materials/regions
2. **Are Robust to Noise:** Don't amplify measurement noise excessively
3. **Have Physical Meaning:** Can be interpreted in terms of spectral properties
4. **Show Spatial Variations:** Reveal structure that isn't visible in single-parameter maps (e.g., peak intensity alone)

### 2.2 First Derivative: Physical Meaning & Parameters

The **first derivative** $\frac{dI}{d\lambda}$ (or $\frac{dI}{dE}$ for energy units) measures the **rate of change of intensity** with wavelength/energy.

#### Physical Interpretation:
- **Zero-crossings:** Correspond to local maxima, minima, or inflection points in the spectrum
- **Magnitude:** Indicates how quickly the spectrum changes (edge sharpness)
- **Sign:** Positive = rising, negative = falling

#### Proposed Contrast Parameters for `'derivative1'`:

| Parameter | Symbol | Description | Physical Meaning | Hyperspectral Use Case |
|-----------|--------|-------------|------------------|------------------------|
| **Max Positive Derivative** | $\frac{dI}{d\lambda}\bigg\|_{\text{max}}^{+}$ | Steepest rising slope | Edge sharpness (blue shift) | Maps sharp absorption edges, emission onset |
| **Max Negative Derivative** | $\frac{dI}{d\lambda}\bigg\|_{\text{min}}^{-}$ | Steepest falling slope | Edge sharpness (red shift) | Maps emission cutoffs, band edges |
| **Energy at Max Positive Derivative** | $E^+$ | Position of steepest rise | Blue-side edge position | Tracks edge shifts across sample |
| **Energy at Max Negative Derivative** | $E^-$ | Position of steepest fall | Red-side edge position | Tracks edge shifts across sample |
| **Derivative Range** | $\Delta D = D_{\text{max}} - D_{\text{min}}$ | Total derivative span | Overall spectral contrast | Distinguishes sharp vs. broad features |
| **Zero-Crossing Energy** | $E_0$ | Where $\frac{dI}{d\lambda} = 0$ | Peak/valley position | Alternative peak position estimate |

**Recommended 6 Parameters:**
1. **Max Positive Derivative** (Counts/eV)
2. **Energy at Max Positive Derivative** (eV)
3. **Max Negative Derivative** (Counts/eV)
4. **Energy at Max Negative Derivative** (eV)
5. **Derivative Range** (Counts/eV)
6. **Zero-Crossing Energy** (eV) - position of peak

### 2.3 Second Derivative: Physical Meaning & Parameters

The **second derivative** $\frac{d^2I}{d\lambda^2}$ measures the **curvature** of the spectrum (how the slope changes).

#### Physical Interpretation:
- **Negative values:** Convex regions (peaks, shoulders)
- **Positive values:** Concave regions (valleys, dips)
- **Zero-crossings:** Inflection points (where curvature changes sign)
- **Magnitude:** Sharpness of peaks/valleys

#### Proposed Contrast Parameters for `'derivative2'`:

| Parameter | Symbol | Description | Physical Meaning | Hyperspectral Use Case |
|-----------|--------|-------------|------------------|------------------------|
| **Max Negative Curvature** | $\frac{d^2I}{d\lambda^2}\bigg\|_{\text{min}}^{-}$ | Sharpest peak curvature | Peak sharpness | Maps sharp vs. broad peaks |
| **Energy at Max Negative Curvature** | $E_{\text{curv}}^-$ | Position of peak center | High-precision peak position | Sub-pixel peak localization |
| **Max Positive Curvature** | $\frac{d^2I}{d\lambda^2}\bigg\|_{\text{max}}^{+}$ | Sharpest valley curvature | Dip/shoulder sharpness | Identifies shoulders, dips |
| **Curvature Range** | $\Delta C = C_{\text{max}} - C_{\text{min}}$ | Total curvature span | Feature complexity | Distinguishes multi-peak structures |
| **Left Inflection Energy** | $E_{\text{infl}}^L$ | Blue-side inflection point | Peak boundary (left) | Maps peak width asymmetry |
| **Right Inflection Energy** | $E_{\text{infl}}^R$ | Red-side inflection point | Peak boundary (right) | Maps peak width asymmetry |
| **Inflection Width** | $W_{\text{infl}} = E_{\text{infl}}^R - E_{\text{infl}}^L$ | Distance between inflections | Effective peak width | Alternative to FWHM |

**Recommended 7 Parameters:**
1. **Max Negative Curvature** (Counts/eV²)
2. **Energy at Max Negative Curvature** (eV)
3. **Max Positive Curvature** (Counts/eV²)
4. **Curvature Range** (Counts/eV²)
5. **Left Inflection Energy** (eV)
6. **Right Inflection Energy** (eV)
7. **Inflection Width** (eV)

### 2.4 Why These Parameters Are Optimal for Hyperspectral Imaging

#### Complementarity:
- **Peak intensity** (from existing methods) → total signal strength
- **Peak position** (from fits) → spectral shift
- **First derivative** → edge sharpness, transition rates
- **Second derivative** → peak sharpness, fine structure

#### Noise Robustness:
- Finite differences are noisier than Savitzky-Golay filters, but:
  - Using percentiles (5th/95th) instead of absolute min/max reduces outlier sensitivity
  - Derivative range is robust because it's a difference of robust estimates
  - Inflection points from zero-crossings are naturally smoothed by the second derivative

#### Physical Interpretability:
- Derivatives are standard in spectroscopy (e.g., derivative spectroscopy for resolving overlapping bands)
- Curvature relates to Lorentzian/Gaussian line shapes (second derivative at peak is proportional to $-A/\sigma^2$)

---

## 3. Step-by-Step Implementation Plan

### Step 1: Implement First Derivative Analysis Functions

#### 3.1.1 Create `fitderivative1tospec()`

**Location:** After `fitbinningtospec()`, before `fitkeys` definition (around line 1900)

**Function Logic:**
1. Extract spectrum region `x = WL[start:end]`, `y = PLB[start:end]`
2. Calculate first derivative using finite differences:
   $$\frac{dI}{d\lambda}\bigg|_i = \frac{I_{i+1} - I_i}{\lambda_{i+1} - \lambda_i}$$
3. Find max positive derivative and its energy position
4. Find max negative derivative (min value) and its energy position
5. Calculate derivative range: $\Delta D = D_{\text{max}} - D_{\text{min}}$
6. Find zero-crossing closest to peak (interpolate between sign changes)
7. Return 6 parameters + `None` (for pcov)

**Edge Cases:**
- If `len(x) < 3`: return zeros
- If `max(y) <= 0`: return zeros
- Use `np.errstate(divide='ignore', invalid='ignore')` to handle division by zero
- Filter out NaN/Inf values with `np.isfinite()`

#### 3.1.2 Create `derivative1_window()`

**Visualization Strategy:**
- Option 1: Return zeros (no reconstruction)
- Option 2: Show tangent lines at max positive and max negative derivative positions
- **Recommended:** Return zeros (simpler, fit-free methods don't need window functions)

#### 3.1.3 Create `getmaxderivative1()`

**Return:** `(zero_crossing_energy, max_positive_derivative)`  
Rationale: Zero-crossing is the best peak position estimate from first derivative

#### 3.1.4 Create `getderivative1fwhm()`

**Return:** `0.0` (no FWHM estimate from first derivative alone)

---

### Step 2: Implement Second Derivative Analysis Functions

#### 3.2.1 Create `fitderivative2tospec()`

**Function Logic:**
1. Extract spectrum region
2. Calculate first derivative (as in Step 1)
3. Calculate second derivative from first derivative:
   $$\frac{d^2I}{d\lambda^2}\bigg|_i = \frac{D_{i+1} - D_i}{\lambda_{i+1} - \lambda_i}$$
   where $D_i$ is the first derivative at point $i$
4. Find max negative curvature (min value of second derivative) → peak sharpness
5. Find energy at max negative curvature → peak center
6. Find max positive curvature → valley sharpness
7. Calculate curvature range
8. Find zero-crossings of second derivative (inflection points)
   - Interpolate to find exact positions
   - Identify left and right inflections relative to peak
9. Calculate inflection width
10. Return 7 parameters + `None`

**Edge Cases:**
- If `len(x) < 4`: return zeros (need at least 4 points for second derivative)
- Handle division by zero in both derivative calculations
- If no zero-crossings found: set inflection energies to peak position ± some default

#### 3.2.2 Create `derivative2_window()`

**Return:** Zeros (fit-free method, no reconstruction needed)

#### 3.2.3 Create `getmaxderivative2()`

**Return:** `(energy_at_max_negative_curvature, intensity_at_peak)`  
Note: Need to interpolate or lookup intensity at the curvature maximum position

#### 3.2.4 Create `getderivative2fwhm()`

**Return:** Inflection width (parameter 7)  
Rationale: Inflection width is a measure of peak width comparable to FWHM

---

### Step 3: Add Entries to fitkeys Dictionary

#### 3.3.1 First Derivative Entry

```python
'derivative1': [
    derivative1_window,          # [0] Window function
    fitderivative1tospec,        # [1] Analysis function
    getmaxderivative1,           # [2] Get max function
    'First Derivative (FD)',     # [3] Label
    6,                           # [4] Parameter count
    [                            # [5] Parameter names
        'Max Positive Derivative',
        'Energy at Max Pos. Deriv.',
        'Max Negative Derivative',
        'Energy at Max Neg. Deriv.',
        'Derivative Range',
        'Zero-Crossing Energy'
    ],
    [                            # [6] Units
        'Counts/eV',
        'eV',
        'Counts/eV',
        'eV',
        'Counts/eV',
        'eV'
    ],
    getderivative1fwhm,          # [7] FWHM function
    0                            # [8] State
]
```

#### 3.3.2 Second Derivative Entry

```python
'derivative2': [
    derivative2_window,              # [0] Window function
    fitderivative2tospec,            # [1] Analysis function
    getmaxderivative2,               # [2] Get max function
    'Second Derivative (FD)',        # [3] Label
    7,                               # [4] Parameter count
    [                                # [5] Parameter names
        'Max Negative Curvature',
        'Energy at Max Neg. Curv.',
        'Max Positive Curvature',
        'Curvature Range',
        'Left Inflection Energy',
        'Right Inflection Energy',
        'Inflection Width'
    ],
    [                                # [6] Units
        'Counts/eV²',
        'eV',
        'Counts/eV²',
        'Counts/eV²',
        'eV',
        'eV',
        'eV'
    ],
    getderivative2fwhm,              # [7] FWHM function
    0                                # [8] State
]
```

---

### Step 4: Update fitunits Dictionary

After the `fitkeys` definition, add entries to `fitunits`:

```python
fitunits = {
    # ... existing entries ...
    'derivative1': fitkeys['derivative1'][6][:] + unitstoaddfit,
    'derivative2': fitkeys['derivative2'][6][:] + unitstoaddfit
}
```

---

## 4. Mathematical Formulas (for Documentation)

### 4.1 First Derivative (Finite Differences)

**Discrete Derivative:**

$$
\frac{dI}{d\lambda}\bigg|_i = \frac{I_{i+1} - I_i}{\lambda_{i+1} - \lambda_i}
$$

**Parameters:**

1. **Max Positive Derivative:**
   $$
   D_{\text{max}}^+ = \max_i \left( \frac{dI}{d\lambda}\bigg|_i \right) \quad \text{where} \quad \frac{dI}{d\lambda}\bigg|_i > 0
   $$

2. **Max Negative Derivative:**
   $$
   D_{\text{min}}^- = \min_i \left( \frac{dI}{d\lambda}\bigg|_i \right) \quad \text{where} \quad \frac{dI}{d\lambda}\bigg|_i < 0
   $$

3. **Derivative Range:**
   $$
   \Delta D = D_{\text{max}}^+ - D_{\text{min}}^-
   $$

4. **Zero-Crossing (Peak Position):**
   $$
   E_0: \quad \frac{dI}{d\lambda}\bigg|_{E_0} = 0 \quad \text{(interpolated between sign changes)}
   $$

### 4.2 Second Derivative (Finite Differences)

**Discrete Second Derivative:**

$$
\frac{d^2I}{d\lambda^2}\bigg|_i = \frac{D_{i+1} - D_i}{\lambda_{i+1} - \lambda_i}
$$

where $D_i = \frac{dI}{d\lambda}\bigg|_i$ is the first derivative.

**Parameters:**

1. **Max Negative Curvature (Peak Sharpness):**
   $$
   C_{\text{min}}^- = \min_i \left( \frac{d^2I}{d\lambda^2}\bigg|_i \right)
   $$

2. **Curvature Range:**
   $$
   \Delta C = \max_i \left( \frac{d^2I}{d\lambda^2}\bigg|_i \right) - \min_i \left( \frac{d^2I}{d\lambda^2}\bigg|_i \right)
   $$

3. **Inflection Points (Zero-Crossings of Second Derivative):**
   $$
   E_{\text{infl}}^{L,R}: \quad \frac{d^2I}{d\lambda^2}\bigg|_{E_{\text{infl}}} = 0
   $$

4. **Inflection Width:**
   $$
   W_{\text{infl}} = E_{\text{infl}}^R - E_{\text{infl}}^L
   $$

---

## 5. Robustness Considerations

### 5.1 Noise Sensitivity

Derivatives amplify noise. Mitigation strategies:

1. **Percentile-Based Extrema:**
   - Use 95th percentile for max positive derivative (instead of absolute max)
   - Use 5th percentile for max negative derivative
   - Reduces impact of outliers

2. **Edge Trimming:**
   - Ignore first and last 2 points when finding extrema
   - Boundary effects in finite differences are unreliable

3. **Validity Filtering:**
   - Remove NaN and Inf values before finding extrema
   - Check for division by zero in non-uniform grids

### 5.2 Edge Cases

| Condition | Handling |
|-----------|----------|
| `len(x) < 3` | Return all zeros (insufficient data for derivative) |
| `len(x) < 4` | Return zeros for second derivative |
| `max(y) <= 0` | Return zeros (no signal) |
| No zero-crossing found | Return peak position from `argmax(y)` |
| No inflection points | Set inflections to peak ± 10% of range |

---

## 6. Testing Strategy

### 6.1 Test Cases

1. **Gaussian Peak:**
   - First derivative: Should have clear positive/negative flanks, zero at peak
   - Second derivative: Negative at peak, zero-crossings at $\mu \pm \sigma$

2. **Lorentzian Peak:**
   - Similar to Gaussian but sharper
   - Inflection width should be narrower than Gaussian with same FWHM

3. **Noisy Data:**
   - Use percentile-based extrema to show robustness
   - Compare to Savitzky-Golay derivative method

4. **Multi-Peak Spectrum:**
   - First derivative should show multiple zero-crossings
   - Second derivative should show multiple negative regions

### 6.2 Validation

Compare with existing `'derivative'` method (Savitzky-Golay):
- Finite differences should be noisier but faster
- Inflection width from second derivative should correlate with SG inflection width
- Zero-crossing energy should match peak energy from other methods

---

## 7. Usage Example (Pseudocode)

```python
# In main9.py or analysis script:

# Load hyperspectral data
WL, PLB = load_spectrum(...)  # Wavelength, Intensity arrays

# Apply first derivative analysis to region
start, end = 100, 200  # Region of interest
params1, pcov1 = mathlib3.fitkeys['derivative1'][1](start, end, WL, PLB)

# Extract parameters
max_pos_deriv = params1[0]
energy_max_pos = params1[1]
max_neg_deriv = params1[2]
energy_max_neg = params1[3]
deriv_range = params1[4]
zero_cross_energy = params1[5]

print(f"Peak position (zero-crossing): {zero_cross_energy:.3f} eV")
print(f"Edge sharpness (derivative range): {deriv_range:.3f} Counts/eV")

# Apply second derivative analysis
params2, pcov2 = mathlib3.fitkeys['derivative2'][1](start, end, WL, PLB)

# Extract curvature parameters
max_neg_curv = params2[0]
peak_center = params2[1]
inflection_width = params2[6]

print(f"Peak sharpness (curvature): {max_neg_curv:.3f} Counts/eV²")
print(f"Peak width (inflection): {inflection_width:.3f} eV")
```

---

## 8. Summary of Changes to mathlib3.py

### Functions to Add (12 total):

**First Derivative (4 functions):**
1. `fitderivative1tospec(start, end, WL, PLB, maxfev, guess)` → 6 params + pcov
2. `derivative1_window(x, *params)` → zeros array
3. `getmaxderivative1(xmin, xmax, *params)` → (x_max, y_max)
4. `getderivative1fwhm(params)` → 0.0

**Second Derivative (4 functions):**
1. `fitderivative2tospec(start, end, WL, PLB, maxfev, guess)` → 7 params + pcov
2. `derivative2_window(x, *params)` → zeros array
3. `getmaxderivative2(xmin, xmax, *params)` → (x_max, y_max)
4. `getderivative2fwhm(params)` → inflection_width

### Modifications:
- Add `'derivative1'` entry to `fitkeys` dictionary
- Add `'derivative2'` entry to `fitkeys` dictionary
- Add both entries to `fitunits` dictionary

---

## 9. Expected Output for Hyperspectral Imaging

When these methods are applied pixel-by-pixel across a hyperspectral image:

### First Derivative Maps:
- **Max Positive Derivative Map:** Shows regions with sharp blue-side edges (e.g., absorption onset)
- **Max Negative Derivative Map:** Shows regions with sharp red-side edges (e.g., emission cutoff)
- **Derivative Range Map:** Overall spectral contrast (sharp vs. broad features)
- **Zero-Crossing Map:** Alternative peak position map (less sensitive to peak shape than center-of-mass)

### Second Derivative Maps:
- **Max Negative Curvature Map:** Peak sharpness (narrow peaks appear bright)
- **Energy at Max Curvature Map:** High-precision peak position
- **Inflection Width Map:** Effective peak width (alternative to FWHM)
- **Curvature Range Map:** Spectral complexity (multi-peak vs. single-peak)

These maps provide complementary information to existing intensity-based and fit-based contrast mechanisms, enabling more sophisticated material identification and spatial analysis.

---

## 10. Next Steps for Implementation

1. **Implement First Derivative Functions** (Section 3.1)
2. **Test First Derivative on Sample Spectra** (Gaussian, Lorentzian, noisy data)
3. **Implement Second Derivative Functions** (Section 3.2)
4. **Test Second Derivative on Sample Spectra**
5. **Add Both Entries to fitkeys** (Section 3.3)
6. **Update fitunits Dictionary** (Section 4)
7. **Create Test Script** (`test_derivative_methods.py`)
8. **Validate Against Existing Methods** (Compare to Savitzky-Golay derivative)
9. **Document in MATHLIB_DOCUMENTATION.md** (Add sections 3.2.X for new methods)
10. **Test in Hyperspectral Imaging Context** (Apply to real HSI data in `main9.py`)

---

**End of Implementation Plan**
