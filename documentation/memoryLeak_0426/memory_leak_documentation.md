# Memory Leak Documentation — SpecMap HSI Loading with Derivatives

**Date:** 2026-04-26  
**Symptom:** Loading a hyperspectral image (HSI) dataset with all derivative options enabled causes RAM to grow to ~10 GB+, roughly **50× the expected usage**.  
**Trigger:** "Load HSI data" with checkboxes enabled for: 1st derivative, 2nd derivative, "norm counts, then derive", and "norm on I, then derive".  
**No leak observed when:** derivative checkboxes are all disabled.

---

## Summary of Findings

The memory explosion is **not a single bug** but rather the compound effect of several related design decisions in `lib9.py`, together with one critical unconditional allocation and one redundant processing path. The five root causes are described below in approximate order of impact.

---

## Root Cause 1 — Excessive Derivative Array Storage Per Pixel (PRIMARY CAUSE)

**Location:** `lib9.py` → `XYMap.calculate_derivatives()` (line ~2748), `XYMap._calculate_normalized_derivatives()` (line ~2888), `hsi_normalization.normalize_derivatives_by_signal()`.

### What happens

Every loaded `SpectrumData` pixel object starts with two signal arrays:

| Attribute | Description |
|-----------|-------------|
| `PL`      | Raw spectrometer counts, `float32[M]` |
| `PLB`     | PL minus background, `float32[M]` |

When all four derivative checkboxes are enabled, `calculate_derivatives()` adds **eight additional `float32[M]` arrays** to every pixel object:

| Attribute                | Added by                                | Condition                        |
|--------------------------|-----------------------------------------|----------------------------------|
| `Specdiff1`              | `calculate_derivatives` main loop       | calc_d1=True                     |
| `Specdiff2`              | `calculate_derivatives` main loop       | calc_d2=True                     |
| `Specdiff1_norm`         | `normalize_derivatives_by_signal`       | **UNCONDITIONAL** (see Cause 2)  |
| `Specdiff2_norm`         | `normalize_derivatives_by_signal`       | **UNCONDITIONAL** (see Cause 2)  |
| `Specdiff1_norm_counts`  | `_calculate_normalized_derivatives`     | calc_norm_and_derive=True        |
| `Specdiff2_norm_counts`  | `_calculate_normalized_derivatives`     | calc_norm_and_derive=True        |
| `Specdiff1_norm_intensity` | `_calculate_normalized_derivatives`   | calc_norm_on_intensity=True      |
| `Specdiff2_norm_intensity` | `_calculate_normalized_derivatives`   | calc_norm_on_intensity=True      |

**Memory multiplier:**  
Each spectrum of `M` wavelength points now holds `10 × M × 4 bytes` instead of `2 × M × 4 bytes` → **5× base memory** from stored data alone, not counting transient allocations during the calculation.

### Fix suggestion

- Store only the derivative variants the user actually requests; skip the others entirely.
- Use lazy computation: calculate a derivative only when a pixel or HSI map is plotted for that data type, rather than pre-computing and storing all variants up front.
- If all variants must be pre-computed, delete the arrays that are intermediate (e.g., `Specdiff1`/`Specdiff2` could be derived on-the-fly from the stored polynomial coefficients, or replaced in-place).
- Use `float16` instead of `float32` for derivative arrays when precision allows (halves their footprint).

---

## Root Cause 2 — `normalize_derivatives_by_signal` Called Unconditionally

**Location:** `lib9.py`, `calculate_derivatives()`, line ~2860:

```python
hsi_normalization.normalize_derivatives_by_signal(self.SpecDataMatrix, signal_key='PLB')
```

### What happens

This call is **not guarded by any user checkbox**. It runs every time derivatives are calculated, regardless of whether the "Normalize HSI" option is enabled. It adds `Specdiff1_norm` and `Specdiff2_norm` to every pixel in `SpecDataMatrix` — even when the user has not requested normalized derivatives.

This means two `float32[M]` arrays per pixel are allocated unconditionally when either derivative is enabled, contributing to the memory growth even in "basic derivative" mode.

### Fix suggestion

Wrap the call inside the existing `calc_d1`/`calc_d2` guard and add an explicit check for whether the normalized display type is needed:

```python
if (calc_d1 or calc_d2) and <user_requested_norm_derivatives>:
    hsi_normalization.normalize_derivatives_by_signal(self.SpecDataMatrix, signal_key='PLB')
```

---

## Root Cause 3 — `_calculate_normalized_derivatives` Processes Both `self.specs` AND `self.SpecDataMatrix`

**Location:** `lib9.py`, `_calculate_normalized_derivatives()`, lines ~2907 and ~2974.

### What happens

The function contains **two separate iteration loops**:

1. **Loop over `self.specs`** (lines ~2907–2971)
2. **Loop over `self.SpecDataMatrix`** (lines ~2974–3038)

After `autogenmatrix()` runs, `self.specs` is cleared (`self.specs = []`), so the first loop does nothing at this point. However:

- The design assumes `self.specs` is already empty — which is a fragile assumption. If `_calculate_normalized_derivatives` were called before `autogenmatrix` (or during a future refactoring that changes the order), both loops would process **the same SpectrumData objects twice**, because `SpecdataintoMatrix` stores *references* (not copies) of `self.specs` elements into `SpecDataMatrix`.
- Even today, the redundant first loop is dead code that obscures the data flow and makes future bugs more likely.
- Inside the second loop, for every pixel a `plb_normalized = plb / max_counts` or `plb.copy()` temporary array (size `M`) is created. While Python releases this each iteration, with large datasets (N × M large) this adds peak-memory pressure during the loop.

### Fix suggestion

- Remove the `self.specs` loop from `_calculate_normalized_derivatives` entirely — `SpecDataMatrix` is the single source of truth after `autogenmatrix`.
- Create `plb_normalized` views (using numpy slicing or `np.divide` with `out=` parameter) rather than full copies where possible.
- Add a clear comment or assertion that the function must only be called after `self.specs` has been transferred to `SpecDataMatrix`.

---

## Root Cause 4 — Manual Sliding Window Loop Instead of Optimized `savgol_filter`

**Location:** `lib9.py`, `calculate_derivatives()`, lines ~2830–2856; also `_calculate_normalized_derivatives`, lines ~2945–2970.

### What happens

The `calculate_derivatives` method uses a **manual per-point polynomial fitting loop**:

```python
for i in range(half_window, n_points - half_window):
    wl_window = wl[start_idx:end_idx]
    plb_window = plb[start_idx:end_idx]
    p = np.polyfit(wl_window - wl_center, plb_window, poly_order)
    dp = np.polyder(p)
    spec.Specdiff1[i] = np.polyval(dp, 0.0)
    ddp = np.polyder(np.polyder(p))
    spec.Specdiff2[i] = np.polyval(ddp, 0.0)
```

For each of the `M` wavelength points per pixel, this creates:
- 1 temporary array `wl_window - wl_center` (size `N_fitpoints`)
- 1 polynomial coefficient array `p` (size `poly_order+1`)
- 1–2 derivative coefficient arrays `dp`, `ddp`

For a dataset with `N` pixels and `M = 1000` wavelength points, this means on the order of `4 × N × M` temporary small numpy array allocations during the derivative calculation phase. Python's garbage collector processes these eventually, but the **peak memory during the loop** can be significantly higher than the post-loop steady state.

**Critically:** an already-implemented optimized alternative exists in `PMclasslib1.py`:

```python
def calc_derivative(spec_obj, derivative_polynomarray):
    ...
    spec_obj.Spec_d1 = savgol_filter(spec_obj.Spec, window_size, poly_order, deriv=1, delta=delta)
    spec_obj.Spec_d2 = savgol_filter(spec_obj.Spec, window_size, poly_order, deriv=2, delta=delta)
```

`scipy.signal.savgol_filter` is fully vectorized and allocates only 1–2 output arrays per call rather than `M` intermediate arrays. This is used in `averageHSItoSpecData` (line ~1158) but **not** in `calculate_derivatives` for the full SpecDataMatrix.

### Fix suggestion

Replace the manual sliding window loops in both `calculate_derivatives` and `_calculate_normalized_derivatives` with calls to `PMlib.calc_derivative` (or directly with `savgol_filter`). This reduces peak memory pressure during the calculation by orders of magnitude and also gives a 10–50× speedup.

---

## Root Cause 5 — Unbounded `PMdict` Accumulation

**Location:** `lib9.py`, `writetopixmatrix()` (line ~3176), called from `buildandPlotIntCmap` (line ~1676), `buildandPlotSpecCmap` (line ~1696), `plotHSIfromfitparam` (line ~3200).

### What happens

Every time the user clicks "Plot Colormap" or similar buttons, `writetopixmatrix` creates a **new `PMclass` entry** in `self.PMdict` with a unique incrementing name (`HSI0`, `HSI1`, `HSI2`, …). The old entries are never removed automatically. Each entry holds a 2D `float64` numpy matrix of shape `(rows, cols)`.

By contrast, `self.disspecs` (the averaged spectrum cache) has an explicit 50-entry limit enforced by `_enforce_disspecs_memory_limit`. No such limit exists for `PMdict`.

With repeated user interaction (re-plotting after adjusting parameters), `PMdict` can accumulate dozens of pixel matrices, each occupying `rows × cols × 8 bytes`. For a 200×200 map, each is 320 KB, and 100 entries = 32 MB — not 50× by itself, but it compounds with the derivative arrays above.

Additionally, `buildandPlotIntCmap` and `buildandPlotSpecCmap` call `copy.deepcopy(self.PMdict[...].PixMatrix)` before passing to `writetopixmatrix`, meaning the matrix exists in memory twice transiently during each plot operation.

### Fix suggestion

- Implement a `_enforce_pmdict_memory_limit()` analogous to `_enforce_disspecs_memory_limit()`, removing the oldest entries when `PMdict` exceeds a configurable maximum (e.g., 10 entries).
- Replace `copy.deepcopy(...)` with `np.array(...)` (which copies only the ndarray data, not any Python wrapper overhead) as already done in `multiroitopixmatrix` (line ~3069).

---

## Memory Interaction: How the Causes Combine to 50×

With all derivative checkboxes enabled on a large dataset:

| Data stored per pixel | Without derivatives | With all derivatives |
|-----------------------|--------------------|-----------------------|
| `PL`                  | 1 array            | 1 array               |
| `PLB`                 | 1 array            | 1 array               |
| `Specdiff1`           | —                  | +1 array              |
| `Specdiff2`           | —                  | +1 array              |
| `Specdiff1_norm`      | —                  | +1 array (unconditional) |
| `Specdiff2_norm`      | —                  | +1 array (unconditional) |
| `Specdiff1_norm_counts` | —                | +1 array              |
| `Specdiff2_norm_counts` | —                | +1 array              |
| `Specdiff1_norm_intensity` | —             | +1 array              |
| `Specdiff2_norm_intensity` | —             | +1 array              |
| **Total arrays**      | **2**              | **10**                |

Persistent RAM: **5× base** from stored arrays alone.  
Peak RAM during calculation: further elevated by:
- `M` temporary arrays per pixel per wavelength point in the manual polynomial loop (Cause 4)
- `plb_normalized` copy per pixel in `_calculate_normalized_derivatives` (Cause 3)
- Parallel file loading (all `N` raw file `lines` lists alive simultaneously during `parallel_load_spectra`)
- Transient `deepcopy` of the full pixel matrix in each plot operation (Cause 5)

The combination of a **5× steady-state overhead** with **peak transients** during a multi-pass derivative calculation over the full dataset can plausibly push total RAM 10–50× above the raw data size, especially for large maps.

---

## Recommended Fix Priority

| Priority | Cause | Expected impact |
|----------|-------|----------------|
| 1 (highest) | Replace manual sliding window with `savgol_filter` (Cause 4) | Eliminates peak-memory spike; 10–50× computation speedup |
| 2 | Guard `normalize_derivatives_by_signal` call (Cause 2) | Removes 2 unconditional arrays per pixel |
| 3 | Lazy / on-demand derivative computation (Cause 1) | Reduces steady-state RAM by up to 4× |
| 4 | Remove redundant `self.specs` loop in `_calculate_normalized_derivatives` (Cause 3) | Prevents future double-processing bugs |
| 5 | Add `PMdict` size limit (Cause 5) | Prevents interactive memory growth over session |

---

## References

- `lib9.py` — `XYMap.calculate_derivatives` (~line 2748)
- `lib9.py` — `XYMap._calculate_normalized_derivatives` (~line 2888)
- `lib9.py` — `XYMap.autogenmatrix` (~line 2660, especially `self.specs = []` at ~2740)
- `lib9.py` — `XYMap.buildandPlotIntCmap` (~line 1676)
- `lib9.py` — `XYMap.buildandPlotSpecCmap` (~line 1696)
- `lib9.py` — `XYMap.writetopixmatrix` (~line 3176)
- `lib9.py` — `XYMap._enforce_disspecs_memory_limit` (~line 1083)
- `PMclasslib1.py` — `calc_derivative` (optimized savgol_filter implementation)
- `hsi_normalization.py` — `normalize_derivatives_by_signal` (~line 14)
- `documentation/memoryLeak_0426/finde_memory_leak.txt` — original problem description
