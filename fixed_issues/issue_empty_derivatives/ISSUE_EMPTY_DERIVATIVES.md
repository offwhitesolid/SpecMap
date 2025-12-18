# Issue: Empty Derivatives

## Problem Description
The user reports that the first and second derivatives (`Specdiff1` and `Specdiff2`) are "completely empty" in the application, even when the calculation is requested.

## Investigation
1.  **Initialization**: `SpectrumData` initializes `Specdiff1` and `Specdiff2` as empty lists `[]`.
2.  **Calculation**: `XYMap.calculate_derivatives` is supposed to populate these with `numpy` arrays if the corresponding flags in `derivative_polynomarray` are set.
3.  **Potential Causes**:
    *   `derivative_polynomarray` flags are evaluating to `False` (0).
    *   The `calculate_derivatives` method returns early.
    *   The loop inside `calculate_derivatives` fails silently due to the `try...except` block.
    *   `derivative_polynomarray` elements (Tkinter variables) are not accessible or empty.

## Plan
1.  Verify `main9.py` initialization of `derivative_polynomarray`.
2.  Verify `defaults.txt` values.
3.  Create a reproduction script to test `calculate_derivatives` with mocked Tkinter variables.
4.  Remove the silent `try...except` block in `lib9.py` to expose errors.
5.  Ensure `Specdiff1` and `Specdiff2` are initialized to `None` or `NaN` arrays instead of `[]` to distinguish between "not calculated" and "empty".

## Fix
(To be documented after implementation)
