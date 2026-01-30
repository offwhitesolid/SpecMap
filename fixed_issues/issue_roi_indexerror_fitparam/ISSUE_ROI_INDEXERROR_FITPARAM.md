# Issue: IndexError in plotHSIfromfitparam when "Use ROI for parameter plot" is enabled

## Problem Description
When the user clicks the "Plot HSI from Fit Parameter" button with the "Use ROI for parameter plot" checkbox enabled, the application crashes with an IndexError:

```
IndexError: only integers, slices (`:`), ellipsis (`...`), numpy.newaxis (`None`) and integer or boolean arrays are valid indices
```

The error occurs in `lib9.py` at line 2526:
```python
lastpm[newpm][i][j] = np.nan
```

## Error Trace
```
File "c:\Users\volib\Desktop\Evaluation\code\SpecMap\SpecMap1\lib9.py", line 1178, in <lambda>
    b5 = tk.Button(fitframe, text="Plot HSI from Fit Parameter", command= lambda: self.plotHSIfromfitparam())
                                                                                  ~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "c:\Users\volib\Desktop\Evaluation\code\SpecMap\SpecMap1\lib9.py", line 2526, in plotHSIfromfitparam
    lastpm[newpm][i][j] = np.nan
    ~~~~~~^^^^^^^
IndexError: only integers, slices (`:`), ellipsis (`...`), numpy.newaxis (`None`) and integer or boolean arrays are valid indices
```

## Root Cause Analysis

### Code Structure
The `plotHSIfromfitparam()` method in `lib9.py` performs the following steps:

1. **Line 2487**: Gets the existing HSI pixel matrix:
   ```python
   lastpm = self.PMdict[self.hsiselect.get()].PixMatrix
   ```

2. **Line 2488**: Creates a new HSI by writing to a pixel matrix and returns the **name** of the new HSI:
   ```python
   newpm = self.writetopixmatrix(lastpm, None)
   ```
   
   Note: `writetopixmatrix()` returns a **string** (the name of the newly created HSI, e.g., "HSI0", "HSI1", etc.)

3. **Lines 2503-2526**: Loops through the spectrum data matrix to populate fit parameter values:
   - When ROI is enabled (`if useroi:`), the code attempts to set values using `lastpm[i][j]` for valid pixels
   - However, in the `else` branches (lines 2523, 2526), it incorrectly uses `lastpm[newpm][i][j]`

### The Bug
The critical bug is in lines 2523, 2526, 2547, and 2550 where the code attempts to use `newpm` (a **string**) as an index:

```python
lastpm[newpm][i][j] = np.nan  # BUG: newpm is a string, not an integer!
```

This attempts to index a numpy array with a string, which causes the IndexError. The correct code should be:

```python
lastpm[i][j] = np.nan  # CORRECT: Use integer indices directly
```

### Why This Happens Only with ROI Enabled
When ROI is enabled, the error occurs in the exception handlers and edge cases within the `if useroi:` block (lines 2523 and 2526). When ROI is disabled, the same bug exists in the `else:` block (lines 2547 and 2550), so this bug affects both code paths.

## Location of Bugs
The bug appears in **four locations** in the `plotHSIfromfitparam()` method in `lib9.py`:

1. **Line 2523**: Inside `if useroi:` block, when `dataokay == False`
   ```python
   else:
       lastpm[newpm][i][j] = np.nan  # BUG
   ```

2. **Line 2526**: Inside `if useroi:` block, when ROI mask is NaN or pixel is not SpectrumData
   ```python
   else:
       lastpm[newpm][i][j] = np.nan  # BUG
   ```

3. **Line 2547**: Inside `else:` block (when ROI not used), when `dataokay == False`
   ```python
   else:
       lastpm[newpm][i][j] = np.nan  # BUG
   ```

4. **Line 2550**: Inside `else:` block (when ROI not used), when pixel is not SpectrumData
   ```python
   else:
       lastpm[newpm][i][j] = np.nan  # BUG
   ```

## Expected Behavior
The code should directly assign NaN values to the `lastpm` matrix using integer indices `[i][j]`, since:
- `lastpm` is a reference to a numpy array (the PixMatrix)
- `i` and `j` are integer loop counters
- `newpm` is a string identifier for the newly created HSI dictionary entry

The assignment should modify the original `lastpm` array in-place before it's later updated in the pixel matrix dictionary.

## Impact
- Users cannot use the "Plot HSI from Fit Parameter" feature with ROI enabled
- The feature also fails without ROI when encountering pixels with invalid data
- This breaks a core workflow for visualizing fit parameters on specific regions of interest
