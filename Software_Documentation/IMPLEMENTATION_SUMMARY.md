# Implementation Summary: First and Second Derivative Methods

**Date:** December 16, 2025  
**Status:** ✅ COMPLETED

---

## What Was Implemented

Two new analysis methods have been added to `mathlib3.py` for hyperspectral contrast analysis:

1. **`'derivative1'`** - First Derivative (Finite Differences)
2. **`'derivative2'`** - Second Derivative (Finite Differences)

---

## Files Modified

### 1. `mathlib3.py`
**Lines Added:** ~380 lines of code

**New Functions Added:**

#### First Derivative (4 functions):
- `fitderivative1tospec(start, end, WL, PLB, maxfev, guess)` - Main analysis function
- `derivative1_window(x, *params)` - Window/visualization function
- `getmaxderivative1(xmin, xmax, *params)` - Extract max position and magnitude
- `getderivative1fwhm(params)` - FWHM calculation (returns 0.0)

#### Second Derivative (4 functions):
- `fitderivative2tospec(start, end, WL, PLB, maxfev, guess)` - Main analysis function
- `derivative2_window(x, *params)` - Window/visualization function
- `getmaxderivative2(xmin, xmax, *params)` - Extract max position and magnitude
- `getderivative2fwhm(params)` - FWHM calculation (returns inflection width)

**Dictionary Updates:**
- Added `'derivative1'` entry to `fitkeys` dictionary
- Added `'derivative2'` entry to `fitkeys` dictionary
- Added both entries to `fitunits` dictionary

---

## Output Parameters

### First Derivative (`'derivative1'`) - 6 Parameters

| # | Parameter Name | Unit | Description |
|---|----------------|------|-------------|
| 1 | Max Positive Derivative | Counts/eV | Steepest rising slope (edge sharpness) |
| 2 | Energy at Max Pos. Deriv. | eV | Position of steepest rise |
| 3 | Max Negative Derivative | Counts/eV | Steepest falling slope |
| 4 | Energy at Max Neg. Deriv. | eV | Position of steepest fall |
| 5 | Derivative Range | Counts/eV | Total derivative span (contrast measure) |
| 6 | Zero-Crossing Energy | eV | Peak position estimate |

### Second Derivative (`'derivative2'`) - 7 Parameters

| # | Parameter Name | Unit | Description |
|---|----------------|------|-------------|
| 1 | Max Negative Curvature | Counts/eV² | Peak sharpness measure |
| 2 | Energy at Max Neg. Curv. | eV | High-precision peak position |
| 3 | Max Positive Curvature | Counts/eV² | Valley/shoulder sharpness |
| 4 | Curvature Range | Counts/eV² | Total curvature span |
| 5 | Left Inflection Energy | eV | Left boundary of peak |
| 6 | Right Inflection Energy | eV | Right boundary of peak |
| 7 | Inflection Width | eV | Effective peak width |

---

## Mathematical Formulas

### First Derivative (Finite Differences)

**Discrete Derivative:**
$$
\frac{dI}{d\lambda}\bigg|_i = \frac{I_{i+1} - I_i}{\lambda_{i+1} - \lambda_i}
$$

**Derivative Range:**
$$
\Delta D = D_{\text{max}}^+ - D_{\text{min}}^-
$$

**Zero-Crossing (Peak Position):**
$$
E_0: \quad \frac{dI}{d\lambda}\bigg|_{E_0} = 0 \quad \text{(interpolated)}
$$

### Second Derivative (Finite Differences)

**Discrete Second Derivative:**
$$
\frac{d^2I}{d\lambda^2}\bigg|_i = \frac{D_{i+1} - D_i}{\lambda_{i+1} - \lambda_i}
$$
where $D_i = \frac{dI}{d\lambda}\bigg|_i$

**Inflection Width:**
$$
W_{\text{infl}} = E_{\text{infl}}^R - E_{\text{infl}}^L
$$

where inflection points are zero-crossings of the second derivative.

---

## Robustness Features

### Noise Mitigation:
1. **Percentile-Based Extrema:**
   - 95th percentile for max positive derivatives (instead of absolute max)
   - 5th percentile for max negative derivatives
   - Reduces outlier impact

2. **Edge Trimming:**
   - Ignores first and last points in derivative arrays
   - Avoids boundary artifacts

3. **Validity Filtering:**
   - Removes NaN and Inf values before analysis
   - Handles division by zero gracefully

### Edge Cases Handled:
- `len(x) < 3`: Returns zeros for first derivative
- `len(x) < 4`: Returns zeros for second derivative
- `max(y) <= 0`: Returns zeros (no signal)
- No zero-crossing found: Uses peak from `argmax(y)`
- No inflection points: Sets defaults at peak ± 10% of range

---

## Usage Example

```python
import mathlib3

# Load spectrum data
WL = [...]  # Wavelength/energy array
PLB = [...]  # Intensity array
start, end = 0, len(WL)  # Region of interest

# Apply first derivative analysis
params1, pcov1 = mathlib3.fitkeys['derivative1'][1](start, end, WL, PLB)

# Extract parameters
max_pos_deriv = params1[0]
zero_cross_energy = params1[5]
deriv_range = params1[4]

print(f"Peak position: {zero_cross_energy:.3f} eV")
print(f"Edge sharpness: {deriv_range:.2f} Counts/eV")

# Apply second derivative analysis
params2, pcov2 = mathlib3.fitkeys['derivative2'][1](start, end, WL, PLB)

# Extract parameters
peak_center = params2[1]
inflection_width = params2[6]
peak_sharpness = params2[0]

print(f"Peak center: {peak_center:.3f} eV")
print(f"Peak width: {inflection_width:.3f} eV")
print(f"Peak sharpness: {peak_sharpness:.2f} Counts/eV²")
```

---

## Hyperspectral Imaging Applications

When applied pixel-by-pixel across hyperspectral images, these methods provide:

### First Derivative Maps:
- **Max Positive Derivative:** Highlights sharp blue-side edges (absorption onset)
- **Max Negative Derivative:** Highlights sharp red-side edges (emission cutoff)
- **Derivative Range:** Overall spectral contrast (distinguishes sharp vs. broad features)
- **Zero-Crossing Map:** Alternative peak position (less sensitive to peak asymmetry)

### Second Derivative Maps:
- **Max Negative Curvature:** Peak sharpness (narrow peaks bright, broad peaks dark)
- **Energy at Max Curvature:** High-precision peak position map
- **Inflection Width:** Effective peak width (alternative to FWHM)
- **Curvature Range:** Spectral complexity (multi-peak structures)

---

## Comparison with Existing Methods

| Method | Peak Position | Edge Sharpness | Peak Width | Noise Robustness |
|--------|--------------|----------------|------------|------------------|
| **Gaussian Fit** | ✓✓✓ | ✗ | ✓✓✓ (FWHM) | ✓✓ |
| **Derivative (SG)** | ✓✓ | ✓✓ | ✓✓ (Infl. Width) | ✓✓✓ |
| **derivative1 (FD)** | ✓✓ | ✓✓✓ | ✗ | ✓ |
| **derivative2 (FD)** | ✓✓✓ | ✓ | ✓✓ (Infl. Width) | ✓ |
| **Moments** | ✓✓ (COM) | ✗ | ✓✓ (Quantile) | ✓✓✓ |

**Key:**
- ✓✓✓ = Excellent
- ✓✓ = Good
- ✓ = Fair
- ✗ = Not provided

**Notes:**
- Finite differences (FD) are faster but noisier than Savitzky-Golay (SG)
- Second derivative provides best peak localization (sub-pixel accuracy)
- First derivative provides best edge detection

---

## Testing

A test script has been created: `test_derivative_methods.py`

**Test Cases:**
1. Gaussian peak (validates peak position and derivatives)
2. Second derivative on Gaussian (validates inflection width)
3. Lorentzian peak (sharper features)
4. Multi-peak spectrum (complex structure)

**To run tests:**
```bash
python test_derivative_methods.py
```

**Expected Output:**
- Console printout with parameter values and validation
- Two PNG plots: `test_derivative1_gaussian.png` and `test_derivative2_gaussian.png`

---

## Documentation Files

Three documentation files have been created/updated:

1. **`DERIVATIVE_METHODS_IMPLEMENTATION.md`** (NEW)
   - Complete implementation plan
   - Step-by-step guide
   - Mathematical formulas
   - Contrast parameter discussion
   - ~600 lines of detailed documentation

2. **`IMPLEMENTATION_SUMMARY.md`** (THIS FILE)
   - Quick reference
   - Usage examples
   - Parameter tables

3. **`MATHLIB_DOCUMENTATION.md`** (TO BE UPDATED)
   - Should add sections 3.2.7 and 3.2.8 for new methods
   - Include mathematical formulas and use cases

---

## Integration with GUI (`main9.py`)

The new methods are automatically available in the GUI:
- Appear in fit method dropdown menus
- Generate parameter maps when applied to hyperspectral data
- Export parameters to CSV with proper units

**No modifications to `main9.py` are required** - the methods are automatically discovered via the `fitkeys` registry.

---

## Next Steps (Optional Enhancements)

1. **Add to MATHLIB_DOCUMENTATION.md:**
   - Create sections 3.2.7 (First Derivative FD) and 3.2.8 (Second Derivative FD)
   - Include mathematical formulas from implementation plan
   - Add comparison with Savitzky-Golay derivative method

2. **Smoothing Options:**
   - Could add optional Gaussian smoothing before derivative calculation
   - Would improve noise robustness at cost of edge resolution

3. **Adaptive Window:**
   - Could implement adaptive edge trimming based on derivative variance
   - Would improve robustness on short spectra

4. **Visualization Enhancement:**
   - Could implement actual window functions (instead of returning zeros)
   - Would show tangent lines at derivative extrema

---

## Verification Checklist

- ✅ Functions implemented with proper signatures
- ✅ Added to `fitkeys` dictionary with correct 9-element structure
- ✅ Added to `fitunits` dictionary
- ✅ Error handling for edge cases
- ✅ Robustness features (percentiles, trimming, validity checks)
- ✅ Documentation created (implementation plan)
- ✅ Test script created
- ✅ No syntax errors in `mathlib3.py`
- ✅ Parameter counts match function returns
- ✅ Units specified correctly
- ✅ Mathematical formulas documented

---

## Contact & Support

For questions or issues with these methods:
1. Refer to `DERIVATIVE_METHODS_IMPLEMENTATION.md` for detailed explanations
2. Run `test_derivative_methods.py` to validate installation
3. Check `MATHLIB_DOCUMENTATION.md` for usage in context

---

**Implementation Complete! ✅**

The first and second derivative methods are now fully integrated into the mathlib3 analysis framework and ready for use in hyperspectral imaging applications.
