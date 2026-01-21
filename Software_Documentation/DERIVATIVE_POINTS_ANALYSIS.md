# Derivative Points Analysis Function

A new contrast method for Hyperspectral Imaging (HSI) has been added to the suite of analysis tools. This method extracts characteristic points from the first and second derivatives of the spectrum.

## Function Name
`fitderivativepoints`

## Description

The `fitderivativepoints` function uses **pre-calculated** derivatives to find:
1.  **First Derivative Zero Points (up to 5)**: These correspond to local maxima and minima (peaks and valleys) in the original spectrum where the slope is zero.
2.  **Second Derivative Maxima (up to 10)**: These correspond to points of maximum curvature in the spectrum.

For each found point, two values are stored:
*   **Wavelength (or Energy)**: The x-position of the feature.
*   **Intensity**: The intensity of the original spectrum at that position.

**Important**: This function does **not** calculate derivatives itself to ensure consistency with the displayed derivative plots and to avoid redundant calculations. It expects the derivatives (`Specdiff1`/`Specdiff2` or `Spec_d1`/`Spec_d2`) to be available in the spectrum object.

## Parameters Output

The function returns a fixed set of 30 parameters (plus covariance, which is unused). Indices 0-9 correspond to First Derivative features, and 10-29 correspond to Second Derivative features. Unused slots are filled with zeros.

| Parameter Index | Description | Unit |
| :--- | :--- | :--- |
| **First Derivative Zero Crossings (Peaks/Valleys)** | | |
| 0 | WL of Zero Point 1 | nm / eV |
| 1 | Intensity at Zero Point 1 | Counts |
| 2 | WL of Zero Point 2 | nm / eV |
| 3 | Intensity at Zero Point 2 | Counts |
| ... | ... | ... |
| 8 | WL of Zero Point 5 | nm / eV |
| 9 | Intensity at Zero Point 5 | Counts |
| **Second Derivative Maxima (Curvature Peaks)** | | |
| 10 | WL of D2 Max 1 | nm / eV |
| 11 | Intensity at D2 Max 1 | Counts |
| 12 | WL of D2 Max 2 | nm / eV |
| 13 | Intensity at D2 Max 2 | Counts |
| ... | ... | ... |
| 28 | WL of D2 Max 10 | nm / eV |
| 29 | Intensity at D2 Max 10 | Counts |

## Usage

This method is available in the **Fit Function** selection menu as "Derivative Points". 

## Integration

- **mathlib3.py**: Contains the `fitderivativepoints` logic.
- **lib9.py**: Updated to pass `Specdiff1` / `Specdiff2` (HSI) or `Spec_d1` / `Spec_d2` (Newton) to the analysis function.
