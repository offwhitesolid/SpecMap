# SpecMap Performance & Memory Optimization Plan

## Project Context
SpecMap is a hyperspectral imaging analysis tool handling large 3D data (x × y × λ) with datasets reaching multiple GB in RAM. Current implementation is pure Python with NumPy/SciPy, resulting in significant memory overhead and performance bottlenecks.

## Goals
1. **Reduce memory usage** by eliminating unnecessary array copies and intermediate allocations
2. **Improve runtime performance** through algorithmic improvements and vectorization
3. **Prepare for native code acceleration** by identifying and isolating hot kernels
4. **Maintain numerical correctness** - no changes to calculation results

## Optimization Strategy

### Phase 1: Memory Analysis & Reduction (HIGH PRIORITY)
**Target: Reduce memory footprint by 30-50%**

#### 1.1 Array Copy Elimination
**Files to analyze:**
- `lib9.py` - Main processing library
- `deflib1.py` - Utility functions
- `mathlib3.py` - Mathematical operations
- `PMclasslib1.py` - Data structures

**Actions:**
- [ ] Audit all `.copy()` calls and determine necessity
- [ ] Replace unnecessary copies with views/slices where safe
- [ ] Use in-place operations (`+=`, `*=`) instead of creating new arrays
- [ ] Identify and eliminate intermediate temporary arrays in chained operations

**Expected Impact:** 20-30% memory reduction

#### 1.2 Data Structure Optimization
**Files:** `lib9.py`, `PMclasslib1.py`

**Actions:**
- [ ] Review `SpectrumData` class storage patterns
- [ ] Avoid storing redundant full cubes (BG, PL, PLB, derivatives)
- [ ] Consider lazy computation for derivatives (compute on-demand vs. pre-compute all)
- [ ] Use memory-mapped arrays for very large datasets (via `numpy.memmap`)
- [ ] Profile memory usage with `memory_profiler` to identify largest consumers

**Expected Impact:** 10-20% memory reduction

### Phase 2: Performance Hotspot Analysis (HIGH PRIORITY)
**Target: Identify top 5 performance bottlenecks**

#### 2.1 Profiling
**Actions:**
- [ ] Run `cProfile` on typical workflows (load → process → fit → export)
- [ ] Use `line_profiler` on identified hot functions
- [ ] Create profiling test cases with representative data sizes
- [ ] Document baseline performance metrics

#### 2.2 Loop Optimization
**Known hotspots to investigate:**
- `PMclasslib1.py:60-108` - `calc_derivative()` - per-pixel Python loop
- `deflib1.py:67-100` - `matrix_image_correction_Matrix()` - nested Python loops
- Any per-spectrum/per-pixel iteration patterns

**Actions:**
- [ ] Identify all Python-level loops over spectra/pixels
- [ ] Vectorize where possible using NumPy broadcasting
- [ ] Batch operations across full arrays instead of element-wise

**Expected Impact:** 2-10x speedup for affected operations

### Phase 3: Algorithmic Improvements (MEDIUM PRIORITY)

#### 3.1 Derivative Calculation Optimization
**Current:** `calc_derivative()` uses sliding window with per-point polynomial fit

**Improvements:**
- [ ] Use `scipy.signal.savgol_filter()` for Savitzky-Golay derivatives (faster, vectorized)
- [ ] Pre-compute polynomial coefficients once if window/order are constant
- [ ] Apply convolution-based approach for uniform grids
- [ ] Consider using `np.gradient()` for simple finite difference

**Expected Impact:** 5-50x speedup for derivative computation

#### 3.2 Cosmic Ray Removal Vectorization
**Files:** Check cosmic removal implementations

**Actions:**
- [ ] Review current cosmic ray removal methods
- [ ] Vectorize median filtering and threshold operations
- [ ] Use `scipy.ndimage` functions instead of Python loops
- [ ] Batch process multiple spectra simultaneously

#### 3.3 Fitting Optimization
**Files:** `mathlib3.py`, fitting routines in `lib9.py`

**Actions:**
- [ ] Pre-compute parameter bounds/guesses where possible
- [ ] Use faster approximations (pseudo-Voigt already used - good)
- [ ] Batch similar fits together
- [ ] Consider parallel fitting for independent spectra

### Phase 4: Data Layout & Caching (MEDIUM PRIORITY)

#### 4.1 Memory Layout Optimization
**Actions:**
- [ ] Ensure hyperspectral cubes are C-contiguous for cache efficiency
- [ ] Verify axis ordering for optimal access patterns
- [ ] Consider array transposition if access pattern favors different layout
- [ ] Use `np.ascontiguousarray()` before intensive operations

#### 4.2 Intermediate Result Caching
**Actions:**
- [ ] Identify repeatedly computed values
- [ ] Add caching/memoization for expensive pure functions
- [ ] Avoid recomputing background corrections
- [ ] Store computed derivatives if accessed multiple times

### Phase 5: Native Code Preparation (LOW PRIORITY - Future)

#### 5.1 Kernel Identification
**Candidates for C/Cython/C++ implementation:**
- [ ] Derivative calculation kernel
- [ ] Cosmic ray removal kernel
- [ ] Inner loop of fitting routines
- [ ] Background subtraction operations

**Actions:**
- [ ] Document input/output interfaces for each kernel
- [ ] Create reference implementations with unit tests
- [ ] Measure pure-Python baseline performance
- [ ] Estimate expected speedup from native implementation

#### 5.2 C/C++ Extension Framework
**Setup when needed:**
- [ ] Create `setup.py` for building extensions
- [ ] Set up CMake build system (as mentioned in requirements)
- [ ] Implement one proof-of-concept extension (e.g., derivative kernel)
- [ ] Benchmark native vs Python performance
- [ ] Create SIMD-optimized versions (AVX2/AVX-512) if beneficial

**Tools to use:**
- NumPy C API for direct array access
- Cython for easier Python/C integration
- OpenMP for multi-threading if needed

### Phase 6: Testing & Validation (CONTINUOUS)

#### 6.1 Correctness Testing
**Actions:**
- [ ] Create reference outputs with current implementation
- [ ] Validate all optimizations produce identical results (within numerical tolerance)
- [ ] Add regression tests for optimized functions
- [ ] Test with various data sizes and edge cases

#### 6.2 Performance Benchmarking
**Actions:**
- [ ] Create standardized benchmark suite
- [ ] Measure before/after for each optimization
- [ ] Track memory usage vs runtime tradeoffs
- [ ] Document performance improvements

## Implementation Priority

### Immediate Actions (Week 1)
1. Set up profiling infrastructure
2. Audit `.copy()` calls in main libraries
3. Profile typical workflow to identify hotspots
4. Implement low-hanging fruit (unnecessary copies, obvious vectorization)

### Short Term (Week 2-3)
1. Optimize derivative calculation (Savitzky-Golay or vectorized approach)
2. Vectorize cosmic ray removal
3. Reduce intermediate array allocations
4. Implement memory-efficient data structure patterns

### Medium Term (Week 4-6)
1. Optimize fitting routines
2. Implement caching for expensive operations
3. Improve data layout and memory access patterns
4. Consider lazy computation for derivatives

### Long Term (Month 2+)
1. Implement proof-of-concept C/C++ extension
2. Create SIMD-optimized kernels if warranted
3. Multi-threading for embarrassingly parallel operations
4. Advanced memory management (memory pools, custom allocators)

## Success Metrics

### Memory
- **Target:** 30-50% reduction in peak memory usage
- **Measure:** Track RSS/heap size with `memory_profiler`
- **Test cases:** Load 1GB, 5GB, 10GB datasets

### Performance
- **Target:** 2-10x overall speedup for typical workflows
- **Specific targets:**
  - Derivative calculation: 10-50x speedup
  - Cosmic removal: 3-5x speedup
  - Fitting: 2-3x speedup
- **Measure:** `cProfile` timing before/after

### Code Quality
- All optimizations pass existing tests
- New unit tests for optimized functions
- Code remains readable and maintainable
- No loss of numerical accuracy

## Notes & Constraints

- **Python API remains unchanged** - optimizations are internal only
- **NumPy/SciPy remain primary dependencies** - avoid adding heavy dependencies
- **Gradual, incremental changes** - validate each step before proceeding
- **Measure, don't guess** - always profile before optimizing
- **Safety first** - don't sacrifice correctness for speed

## Current Status
- [x] Initial plan created
- [ ] Profiling infrastructure set up
- [ ] Baseline measurements taken
- [ ] Phase 1 started
- [ ] Phase 2 started
- [ ] Phase 3 started
- [ ] Phase 4 started
- [ ] Phase 5 started
- [ ] Phase 6 framework in place

---
**Last Updated:** 2026-01-29
**Author:** Optimization Initiative
**Version:** 1.0
