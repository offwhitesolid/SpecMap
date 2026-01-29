# SpecMap Optimization Plan

This document outlines the plan to reduce runtime and memory usage for the SpecMap project, focusing on large hyperspectral datasets.

## Goals
- Reduce memory footprint (avoid full copies, use efficient dtypes).
- Speed up numeric kernels (derivatives, fitting, background subtraction).
- Eliminate Python loops over pixels and spectral points.

## Current Bottlenecks Identified
1.  **Derivative Calculation (`PMclasslib1.py`)**:
    -   Currently iterates over every wavelength point `for i in range(n_points):` and calls `np.polyfit`.
    -   This is extremely slow ($O(N)$ with high constant factor per spectrum).
    -   **Solution**: Replace with `scipy.signal.savgol_filter` which implements sliding window polynomial smoothing/derivatives using convolution (vectorized C code).

2.  **Memory Usage**:
    -   Need to verify `PixMatrix` is stored as a contiguous numpy array, not a list of lists.
    -   Need to check if `float64` is used where `float32` would suffice (halves memory).

3.  **Fitting (`mathlib3.py`)**:
    -   `curve_fit` overhead per pixel can be high.
    -   **Solution**: Use `numba` to JIT compile the fit functions (`voigtwind`, etc.) to speed up the inner loop of the optimizer.

## Optimization Tasks

### Phase 1: Immediate Algorithmic Improvements (High Impact)

- [ ] **Optimize Derivatives**: Rewrite `calc_derivative` in `PMclasslib1.py` to use `scipy.signal.savgol_filter`.
    -   *Expected Impact*: 100x-1000x speedup for derivative calculation.
- [ ] **Data Type Check**: Ensure loaded data in `PixMatrix` converts to `np.float32`.
    -   *Expected Impact*: 50% memory reduction.

### Phase 2: Vectorization and Memory Management

- [ ] **Analyze Global Loops**: Identify where `calc_derivative` or fitting is called in `main9.py` or other controllers. Ensure it operates on the full 3D array or large chunks, not pixel-by-pixel if possible.
- [ ] **In-place Operations**: Identify where `self.Spec_d1` etc. are allocated. If `PixMatrix` is 3D, store derivatives as 3D arrays rather than attaching to `Spectra` objects (which implies object overhead per pixel?).
    -   *Note*: If `PMclass` holds a list of `Spectra` objects, that is a huge memory overhead. It should hold one 3D array `(x, y, lambda)`.

### Phase 3: Native Kernels & JIT

- [ ] **JIT Compilation**: Apply `@numba.jit` to math functions in `mathlib3.py` (Voigt, Gaussian, etc.).
- [ ] **Custom Kernels**: If `savgol_filter` is not flexible enough (e.g. variable width), write a Cython or Numba kernel.

## Execution Log

### Step 1 (Current)
-   Created this plan.
-   Action: Analyze `PMclass` structure to see if it holds `Spectra` objects or a raw array.
-   Action: Implement `savgol_filter` in `calc_derivative`.

