# Data Types Documentation

This document explains the various data types available in the "Select Data Set" dropdown menu in the SpecMap software. These datasets determine what information is plotted, analyzed, or exported.

## Basic Spectral Data

### Counts (PL)
*   **Description:** The raw Photoluminescence (PL) intensity as recorded by the spectrometer.
*   **Math:** $I_{raw}(\lambda)$
*   **Use Case:** Inspection of raw data levels, saturation checks, and absolute intensity measurements including background.

### Spectrum (PL-BG)
*   **Description:** The background-corrected spectrum. The background spectrum (dark current/noise) is subtracted from the raw counts.
*   **Math:** $S(\lambda) = I_{raw}(\lambda) - I_{background}(\lambda)$
*   **Use Case:** Standard spectral analysis. This is the primary dataset used for most standard PL characterization.

## Standard Derivatives

Derivatives are calculated using a sliding window polynomial fit (Savitzky-Golay method) to smooth noise while calculating the slope.

### first derivative
*   **Description:** The rate of change of the spectrum with respect to wavelength.
*   **Math:** $\frac{dS}{d\lambda}$
*   **Use Case:** Finding inflection points and accurate peak positions (where $1^{st}$ derivative is 0).

### second derivative
*   **Description:** The rate of change of the slope (curvature) of the spectrum.
*   **Math:** $\frac{d^2S}{d\lambda^2}$
*   **Use Case:** Identifying hidden peaks (shoulders) and resolving overlapping peaks. Negative minima in the 2nd derivative correspond to peak centers.

## Point-wise Normalized Derivatives

These methods normalize the derivative value *at each specific point* by the signal intensity at that same point.

### first derivative (normalized)
*   **Description:** The first derivative divided by the signal intensity. This effectively calculates the logarithmic derivative.
*   **Math:** $\frac{1}{S(\lambda)} \frac{dS}{d\lambda} = \frac{d(\ln S)}{d\lambda}$
*   **Use Case:** Enhancing features in low-intensity regions of the spectrum (tails) that would otherwise be invisible in a standard derivative plot.

### second derivative (normalized)
*   **Description:** The second derivative divided by the signal intensity.
*   **Math:** $\frac{1}{S(\lambda)} \frac{d^2S}{d\lambda^2}$
*   **Use Case:** Similar to the normalized first derivative, useful for identifying curvature changes in weak signal regions.

## Pre-Normalized Derivatives (Global Normalization)

These methods normalize the *entire spectrum first* (globally), and then calculate the derivative of that normalized shape.

### first/second derivative (norm on intensity, then derive)
*   **Description:** The spectrum is first normalized by its **total integrated area** (sum of all counts), then the derivative is calculated.
*   **Math:** 
    1. $S_{norm} = \frac{S}{\sum S}$
    2. Calculate deriv of $S_{norm}$
*   **Use Case:** Comparing spectral **shape changes** independent of total brightness. Effectively treats the spectrum as a Probability Distribution Function (PDF). Useful for comparing samples where absolute brightness varies significantly due to experimental factors (e.g. thickness, focus) but the relative spectral distribution is of interest.

### first/second derivative (norm on counts, then derive)
*   **Description:** The spectrum is first normalized by its **maximum peak value**, then the derivative is calculated.
*   **Math:** 
    1. $S_{norm} = \frac{S}{\max(S)}$
    2. Calculate deriv of $S_{norm}$
*   **Use Case:** Analyzing peak shape relative to peak height. This scales every spectrum's main peak to 1.0, allowing distinct comparison of peak width and shoulder features relative to the main peak, regardless of the signal strength.
