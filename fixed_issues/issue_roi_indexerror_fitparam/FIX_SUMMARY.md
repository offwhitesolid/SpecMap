# Fix Summary: IndexError in plotHSIfromfitparam

## Problem
IndexError when using "Plot HSI from Fit Parameter" with "Use ROI for parameter plot" checkbox enabled (and also when not using ROI in certain edge cases).

## Root Cause
The `plotHSIfromfitparam()` method in `lib9.py` incorrectly used `newpm` (a string variable containing the name of a newly created HSI) as an array index instead of using integer indices `i` and `j` directly.

### Incorrect Code Pattern
```python
lastpm[newpm][i][j] = np.nan  # BUG: newpm is a string like "HSI0"
```

### Why This Was Wrong
- `newpm` is returned from `writetopixmatrix()` and contains a **string** (e.g., "HSI0", "HSI1")
- `lastpm` is a **numpy array** that requires integer indices
- Attempting to index a numpy array with a string raises: `IndexError: only integers, slices (:), ... are valid indices`

## Fix Implementation

### Changes Made
Modified four lines in `lib9.py` in the `plotHSIfromfitparam()` method to use correct integer indexing:

1. **Line 2523** (in `if useroi:` block, when `dataokay == False`):
   ```python
   # BEFORE:
   lastpm[newpm][i][j] = np.nan
   
   # AFTER:
   lastpm[i][j] = np.nan
   ```

2. **Line 2526** (in `if useroi:` block, when pixel is outside ROI or not SpectrumData):
   ```python
   # BEFORE:
   lastpm[newpm][i][j] = np.nan
   
   # AFTER:
   lastpm[i][j] = np.nan
   ```

3. **Line 2547** (in `else:` block when ROI not used, when `dataokay == False`):
   ```python
   # BEFORE:
   lastpm[newpm][i][j] = np.nan
   
   # AFTER:
   lastpm[i][j] = np.nan
   ```

4. **Line 2550** (in `else:` block when ROI not used, when pixel is not SpectrumData):
   ```python
   # BEFORE:
   lastpm[newpm][i][j] = np.nan
   
   # AFTER:
   lastpm[i][j] = np.nan
   ```

### Why This Fix Works
- `lastpm` is a reference to the existing numpy array (`self.PMdict[self.hsiselect.get()].PixMatrix`)
- Modifying `lastpm[i][j]` directly updates the values in the working array
- Later, this modified array is used to update the pixel matrix with normalized values
- The `newpm` variable correctly identifies the dictionary key for the new HSI entry but should **not** be used as an array index

## Verification Strategy
1. Test "Plot HSI from Fit Parameter" with ROI enabled
2. Test with ROI disabled
3. Test with various edge cases (invalid pixels, missing data)
4. Verify that NaN values are correctly assigned to pixels outside ROI or with invalid data
5. Verify that the HSI plot displays correctly

## Files Modified
- `lib9.py`: Fixed four incorrect array indexing statements in `plotHSIfromfitparam()` method

## Impact
- Users can now successfully use "Plot HSI from Fit Parameter" with ROI enabled
- Edge cases with invalid pixel data are handled correctly without crashes
- Core workflow for visualizing fit parameters on regions of interest is restored
