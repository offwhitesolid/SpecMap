# Test Plan: Fix for Repeated Data Loading Issue

**Issue:** Tkinter "main thread is not in main loop" error on repeated data loading  
**Fix:** Remove frame destruction from `XYMap.on_close()` method  
**Date:** 2025-12-15

## Overview

This test plan verifies that the fix for the repeated data loading issue works correctly and doesn't introduce regressions.

## Pre-requisites

### Environment Setup
- Python 3.13 or compatible
- All dependencies installed from `requirements.txt`
- Display/GUI environment available (not headless)
- Test data: At least 2 different HSI datasets available

### Test Data Requirements
- **Dataset A:** Small HSI dataset (e.g., 5x5 grid) for quick loading
- **Dataset B:** Different small HSI dataset for testing reload with different data
- **Dataset C (optional):** Larger dataset for stress testing

## Test Execution

### Critical Tests (Must Pass)

#### Test 1: Basic Repeated Data Loading
**Objective:** Verify that loading data twice in a row works without errors

**Steps:**
1. Launch the application: `python main9.py`
2. Navigate to "Load Data" tab
3. Select Dataset A folder
4. Enter filename pattern (e.g., "spec")
5. Click "Load HSI data" button
6. Wait for data to load completely
7. **Without closing the application**, click "Load HSI data" button again
8. Wait for reload to complete

**Expected Results:**
-  First load completes successfully
-  Second load completes successfully
-  NO "RuntimeError: main thread is not in main loop" error
-  NO error dialog appears
-  GUI remains responsive
-  New data is displayed in Hyperspectra tab

**Failure Indicators:**
-  Error message in console
-  Application crash
-  Frozen GUI
-  Error dialog appears

---

#### Test 2: Load Different Datasets Sequentially
**Objective:** Verify loading different datasets works correctly

**Steps:**
1. Launch application
2. Load Dataset A
3. Verify data loaded correctly in Hyperspectra tab
4. Switch back to "Load Data" tab
5. Select Dataset B folder (different data)
6. Click "Load HSI data" button
7. Verify new data loaded

**Expected Results:**
-  Both datasets load successfully
-  Old data is replaced by new data
-  No memory leaks or hung frames
-  GUI updates correctly
-  No errors in console

---

#### Test 3: Rapid Repeated Loading (Stress Test)
**Objective:** Test stability with rapid repeated loads

**Steps:**
1. Launch application
2. Load Dataset A
3. Immediately click "Load HSI data" again (don't wait for full load)
4. Repeat step 3 five more times (total 6 loads)
5. Let final load complete

**Expected Results:**
-  Application handles rapid clicks gracefully
-  Final load completes successfully
-  No crash or freeze
-  No error accumulation

**Note:** Application may queue loads or ignore duplicate clicks - both are acceptable behaviors

---

#### Test 4: Multiple HSI Processing
**Objective:** Verify batch processing of multiple HSI folders works

**Steps:**
1. Launch application
2. Go to "Load Data" tab
3. Check "Process Multiple HSIs" checkbox
4. Set "File Main Directory" to folder containing 3+ subfolders with HSI data
5. Set "Save Directory" to valid output folder
6. Click "Load HSI data" button
7. Wait for all folders to process

**Expected Results:**
-  All folders process without errors
-  No "main thread is not in main loop" error
-  HSI images saved to output directory
-  Console shows progress for each folder
-  Application remains responsive after completion

---

### Regression Tests (Should Not Break)

#### Test 5: Application Close After Loading
**Objective:** Verify clean application exit

**Steps:**
1. Launch application
2. Load Dataset A
3. Click window close button [X]

**Expected Results:**
-  Application closes cleanly
-  No error dialog on close
-  No hung processes
-  No matplotlib windows left open

---

#### Test 6: Save and Load HSI State
**Objective:** Verify pickle save/load still works

**Steps:**
1. Launch application
2. Load Dataset A
3. Go to "Load Data" tab
4. Enter save path in "Save the current Data object" section
5. Click "Save" button
6. Close application
7. Launch application again
8. Go to "Load Data" tab
9. Enter same save path in "Load a saved Data object" section
10. Click "Load" button

**Expected Results:**
-  Save completes without errors
-  Load restores data correctly
-  Hyperspectra tab shows loaded data
-  All HSI images restored

---

#### Test 7: GUI Element Creation
**Objective:** Verify GUI elements are created correctly

**Steps:**
1. Launch application
2. Load Dataset A
3. Go to "Hyperspectra" tab
4. Verify all GUI elements visible:
   - Wavelength min/max entries
   - "Create intensity colormap" button
   - "Create spectral maximum colormap" button
   - Colormap selection dropdown
   - Font size entry
5. Load Dataset B
6. Verify same GUI elements still present and functional

**Expected Results:**
-  All GUI elements present after first load
-  All GUI elements present after second load
-  Elements are interactive (not greyed out)
-  No duplicate widgets

---

#### Test 8: Frame Lifecycle
**Objective:** Verify frames are properly destroyed and recreated

**Steps:**
1. Launch application with console visible
2. Enable Python garbage collection debugging (optional):
   ```python
   # Add to top of main9.py for this test:
   import gc
   gc.set_debug(gc.DEBUG_STATS | gc.DEBUG_LEAK)
   ```
3. Load Dataset A
4. Note memory usage (Task Manager/Activity Monitor)
5. Load Dataset B
6. Note memory usage again
7. Repeat loads 5 more times
8. Check final memory usage

**Expected Results:**
-  Memory usage increases on first load
-  Memory usage stays relatively stable on subsequent loads
-  No continuously growing memory (no major leaks)
-  Garbage collection runs successfully

---

### Edge Case Tests (Optional but Recommended)

#### Test 9: Load With Empty Folder
**Objective:** Test error handling with no valid files

**Steps:**
1. Launch application
2. Select folder with no matching spec files
3. Click "Load HSI data"

**Expected Results:**
-  Error message: "No files found with the specified name."
-  Application remains stable
-  Can load valid data afterwards

---

#### Test 10: Load Then Clara/Newton
**Objective:** Verify other loaders work after HSI load

**Steps:**
1. Launch application
2. Load HSI dataset
3. Go to "Load Data" tab
4. Load Clara image
5. Verify Clara image displays
6. Load HSI dataset again
7. Load Newton spectrum
8. Verify Newton spectrum displays

**Expected Results:**
-  All loaders work independently
-  No interference between different data types
-  No errors when switching between loaders

---

## Test Results Template

Copy this template for each test run:

```markdown
### Test Run: [Date/Time]
**Tester:** [Your Name]
**Environment:** [OS, Python Version]
**Branch:** copilot/fix-repeated-data-loading

| Test ID | Test Name | Status | Notes |
|---------|-----------|--------|-------|
| Test 1  | Basic Repeated Loading | ⬜ Pass / ⬜ Fail | |
| Test 2  | Different Datasets | ⬜ Pass / ⬜ Fail | |
| Test 3  | Rapid Loading | ⬜ Pass / ⬜ Fail | |
| Test 4  | Multiple HSI | ⬜ Pass / ⬜ Fail | |
| Test 5  | Clean Close | ⬜ Pass / ⬜ Fail | |
| Test 6  | Save/Load State | ⬜ Pass / ⬜ Fail | |
| Test 7  | GUI Elements | ⬜ Pass / ⬜ Fail | |
| Test 8  | Frame Lifecycle | ⬜ Pass / ⬜ Fail | |
| Test 9  | Empty Folder | ⬜ Pass / ⬜ Fail | |
| Test 10 | Other Loaders | ⬜ Pass / ⬜ Fail | |

**Overall Result:** ⬜ All Pass / ⬜ Some Failures

**Issues Found:**
- [List any issues discovered]

**Performance Notes:**
- [Memory usage observations]
- [Load time observations]
- [GUI responsiveness notes]
```

## Success Criteria

The fix is considered successful if:
-  **Test 1-4** (Critical Tests) all pass
-  **Test 5-8** (Regression Tests) all pass
-  No new errors introduced
-  No performance degradation observed

## Debugging Tips

If tests fail:

1. **Check Console Output:**
   - Look for stack traces
   - Note error messages
   - Check for warnings

2. **Enable Debug Logging:**
   ```python
   # Add to main9.py for debugging:
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

3. **Check Frame References:**
   ```python
   # Add to XYMap.on_close() to verify:
   print(f"Frames exist: cmap={hasattr(self, 'cmapframe')}, spec={hasattr(self, 'specframe')}")
   ```

4. **Monitor Thread State:**
   ```python
   # Add to spec_loadfiles():
   import threading as thr
   print(f"Active threads: {len(thr.enumerate())}")
   for t in thr.enumerate():
       print(f"  - {t.name}: {'alive' if t.is_alive() else 'dead'}")
   ```

5. **Check Tkinter Widget States:**
   ```python
   # Add after frame operations:
   try:
       print(f"cmapframe exists: {self.cmapframe.winfo_exists()}")
   except:
       print("cmapframe destroyed or invalid")
   ```

## Known Limitations

- GUI testing requires manual execution (no automated GUI tests in CI)
- Memory leak detection is approximate (use profiling tools for precise measurement)
- Threading issues may be intermittent (run tests multiple times)

## References

- **Issue Documentation:** `ISSUE_TKINTER_ROOT_CLEANUP.md`
- **Architecture Documentation:** `Software_Documentation/GUI_HIERARCHY_AND_LIFECYCLE.md`
- **Code Changes:** `lib9.py` line 2181-2187

---

**Version:** 1.0  
**Last Updated:** 2025-12-15  
**Status:** Ready for Execution
