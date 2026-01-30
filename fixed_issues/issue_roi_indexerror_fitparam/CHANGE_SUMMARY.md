# Code Change Summary

## Files Modified
- **lib9.py** (4 lines changed)
  - Line 2523: `lastpm[newpm][i][j]` → `lastpm[i][j]`
  - Line 2526: `lastpm[newpm][i][j]` → `lastpm[i][j]`
  - Line 2547: `lastpm[newpm][i][j]` → `lastpm[i][j]`
  - Line 2550: `lastpm[newpm][i][j]` → `lastpm[i][j]`

## Documentation Created
- **ISSUE_ROI_INDEXERROR_FITPARAM.md**: Detailed analysis of the bug
- **FIX_SUMMARY.md**: Summary of the fix implementation
- **verify_fix.py**: Verification script demonstrating the bug and fix

## Testing
The verification script confirms:
1. ✓ The bug scenario reproduces the exact IndexError
2. ✓ The fix resolves the IndexError
3. ✓ The logic works correctly for ROI and non-ROI scenarios
4. ✓ lib9.py compiles without syntax errors

## Impact
This fix restores the "Plot HSI from Fit Parameter" functionality when "Use ROI for parameter plot" is enabled, allowing users to visualize fit parameters on specific regions of interest.
