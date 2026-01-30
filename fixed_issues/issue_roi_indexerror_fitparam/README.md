# Issue: IndexError in plotHSIfromfitparam with ROI

## Quick Summary
Fixed an IndexError that occurred when clicking "Plot HSI from Fit Parameter" with the "Use ROI for parameter plot" checkbox enabled.

## The Bug
The error occurred because the code attempted to index a numpy array with a string variable instead of integer indices:
```python
lastpm[newpm][i][j] = np.nan  # WRONG: newpm is a string like "HSI0"
```

## The Fix
Changed to use proper integer indexing:
```python
lastpm[i][j] = np.nan  # CORRECT: i and j are integers
```

## Files in This Folder
- **README.md** (this file): Quick overview
- **ISSUE_ROI_INDEXERROR_FITPARAM.md**: Detailed analysis of the bug
- **FIX_SUMMARY.md**: Implementation details and rationale
- **CHANGE_SUMMARY.md**: Summary of code changes
- **verify_fix.py**: Verification script that demonstrates the bug and validates the fix

## Running the Verification
```bash
cd fixed_issues/issue_roi_indexerror_fitparam
python verify_fix.py
```

The script will demonstrate:
1. ✓ The bug scenario (produces the exact IndexError)
2. ✓ The fix (resolves the IndexError)
3. ✓ The complete logic (works correctly)

## Impact
Users can now successfully use "Plot HSI from Fit Parameter" with ROI enabled, restoring the ability to visualize fit parameters on specific regions of interest.
