# Save/Load Fit Results and ROI Documentation

## Problem Statement

The current `save_state()` and `load_state()` functions in `lib9.py` do not properly save and restore:
1. **Fit results** stored in individual `SpectrumData` objects
2. **ROI (Region of Interest)** masks (though the structure exists, it needs verification)

## Current State Analysis

### What IS Currently Saved

The `save_state()` function (lines 2644-2728 in lib9.py) saves:
- `specs` - List of spectrum objects
- `SpecDataMatrix` - 2D matrix of SpectrumData objects
- `PMdict` - Dictionary of HSI images (PixMatrix/PMclass objects)
- `roilist` - ROI masks from roihandler
- Processing parameters (wlstart, wlend, aqpixstart, aqpixend, etc.)
- Grid parameters (mxcoords, mycoords, PixAxX, PixAxY, gdx, gdy)
- Configuration settings (colormap, linearbg, removecosmics, etc.)

### What IS MISSING

When `SpecDataMatrix` and `specs` are pickled, the **fit results stored within each SpectrumData object** are preserved in the pickle. However, there's a potential issue with **numpy nan values** taking excessive space.

The fit results in each `SpectrumData` object include:
- `fitdata` - Raw fit parameters array
- `fitparams` - Structured fit parameters dictionary
- `fitmaxX` - Peak X coordinate
- `fitmaxY` - Peak Y coordinate
- `fwhm` - Full width at half maximum

**Key Finding**: Since `SpecDataMatrix` is a 2D list of `SpectrumData` objects, pickle DOES save all nested attributes including fit results. However, the issue is with **np.nan values consuming excessive space and time** during pickling.

## Required Changes

### 1. Optimize np.nan Handling in PixMatrix Data

**Problem**: Pickling np.nan values is inefficient - they take excessive space and time.

**Solution**: Implement a nan-to-number swap before pickling:

1. **Before saving**:
   - For each PixMatrix in PMdict, scan for np.nan values
   - Find a unique number not present in the data (e.g., use min(data) - 1 or max(data) + 1)
   - Replace all np.nan with this unique number
   - Store metadata: `'_nan_replacement': unique_number`

2. **After loading**:
   - Check for `_nan_replacement` in metadata
   - If present, replace all instances of that number back to np.nan

### 2. Verify ROI Save/Load

The ROI functionality appears to be correctly implemented:
- Saved at line 2668: `'roilist': self.roihandler.roilist`
- Loaded at line 2773: `self.roihandler.roilist = state.get('roilist', {})`

However, need to verify that roihandler is properly initialized before loading.

### 3. Add Metadata for Fit Results (Optional Enhancement)

While fit results ARE pickled with SpecDataMatrix, we could add summary metadata:
- Number of fitted spectra
- Fit function used
- Fit quality statistics

## Implementation Plan

### Phase 1: np.nan Optimization

Add helper functions to lib9.py:

```python
def _prepare_pmdict_for_pickle(pmdict):
    """
    Replace np.nan values in PMdict PixMatrix data with unique numbers.
    Returns modified pmdict and mapping of replacements.
    """
    nan_replacements = {}
    
    for hsi_name, pm_obj in pmdict.items():
        if hasattr(pm_obj, 'PixMatrix'):
            matrix = pm_obj.PixMatrix
            
            # Check if matrix contains np.nan
            if np.any(np.isnan(matrix)):
                # Find a unique number not in the data
                valid_data = matrix[~np.isnan(matrix)]
                if len(valid_data) > 0:
                    unique_num = np.min(valid_data) - 1
                else:
                    unique_num = -999999.0  # fallback for all-nan matrices
                
                # Replace nan with unique number
                matrix_copy = np.copy(matrix)
                matrix_copy[np.isnan(matrix_copy)] = unique_num
                pm_obj.PixMatrix = matrix_copy
                
                # Store replacement info
                nan_replacements[hsi_name] = unique_num
    
    return pmdict, nan_replacements

def _restore_nan_in_pmdict(pmdict, nan_replacements):
    """
    Restore np.nan values in PMdict PixMatrix data from unique numbers.
    """
    for hsi_name, unique_num in nan_replacements.items():
        if hsi_name in pmdict:
            pm_obj = pmdict[hsi_name]
            if hasattr(pm_obj, 'PixMatrix'):
                matrix = pm_obj.PixMatrix
                pm_obj.PixMatrix = np.where(matrix == unique_num, np.nan, matrix)
    
    return pmdict
```

### Phase 2: Update save_state()

Modify the `save_state()` function:

```python
def save_state(self, filename):
    # Prepare PMdict by replacing nan values
    pmdict_prepared, nan_replacements = _prepare_pmdict_for_pickle(self.PMdict)
    
    state = {
        # ... existing fields ...
        'PMdict': pmdict_prepared,
        '_nan_replacements': nan_replacements,  # Store replacement info
        # ... rest of fields ...
    }
    
    # Pickle to file
    with open(filename, 'wb') as f:
        pickle.dump(state, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    # Restore nan values in self.PMdict (don't leave it modified)
    self.PMdict = _restore_nan_in_pmdict(pmdict_prepared, nan_replacements)
```

### Phase 3: Update load_state()

Modify the `load_state()` function:

```python
def load_state(self, filename):
    with open(filename, 'rb') as f:
        state = pickle.load(f)
    
    # ... restore other fields ...
    
    # Restore PMdict with nan values
    pmdict_loaded = state['PMdict']
    nan_replacements = state.get('_nan_replacements', {})
    self.PMdict = _restore_nan_in_pmdict(pmdict_loaded, nan_replacements)
    
    # ... rest of restoration ...
```

## Testing Plan

1. **Create test data** with fit results:
   - Load HSI data
   - Perform fits on spectra
   - Create ROI masks
   - Save state

2. **Verify save**:
   - Check file size (should be smaller with nan optimization)
   - Verify pickle file can be opened

3. **Verify load**:
   - Load saved state
   - Verify fit results are present (check fitdata, fitparams)
   - Verify ROI masks are restored
   - Verify nan values are correctly restored

4. **Compare before/after**:
   - Save without optimization, note file size and time
   - Save with optimization, compare improvements

## Benefits

1. **Reduced file size**: np.nan objects are replaced with simple numbers
2. **Faster save/load**: Numeric data pickles faster than np.nan objects
3. **Data integrity**: All fit results and ROIs are preserved
4. **Backward compatibility**: Add version checks to handle old save files

## Risks and Mitigations

**Risk**: Chosen replacement number might conflict with actual data
**Mitigation**: Use min(data) - 1 or max(data) + 1 to ensure uniqueness

**Risk**: Old save files won't have _nan_replacements
**Mitigation**: Use `state.get('_nan_replacements', {})` with empty dict default

**Risk**: Modifying PMdict during save might have side effects
**Mitigation**: Restore original nan values immediately after pickling
