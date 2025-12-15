# Issue Documentation: Tkinter "main thread is not in main loop" Error

**Issue Number:** (Reference issue in repository)  
**Severity:** Medium  
**Status:** Identified - Fix Proposed  
**Date:** 2025-12-15

## Summary

When loading HSI data for a second time, the application raises a `RuntimeError: main thread is not in main loop` error. This occurs during the cleanup phase of the Tkinter GUI when attempting to destroy frame widgets that are being managed from multiple contexts.

## Error Message

```
RuntimeError: main thread is not in main loop
  File "...\AppData\Local\Programs\Python\Python313\Lib\tkinter\__init__.py", line 414, in __del__
    if self._tk.getboolean(self._tk.call("info", "exists", self._name)):
```

## Steps to Reproduce

1. Launch the SpecMap application
2. Navigate to the "Load Data" tab
3. Select a folder with spectral data
4. Click "Load HSI data" button (first load - works fine)
5. Click "Load HSI data" button again (second load - error occurs)

## Root Cause Analysis

### Problem Location

The issue originates from improper frame ownership and cleanup responsibility in the `XYMap` class:

**File:** `lib9.py`  
**Method:** `XYMap.on_close()`  
**Lines:** 2181-2209

### Technical Explanation

#### Frame Ownership Architecture

The application has a clear ownership hierarchy for Tkinter frames:

```
FileProcessorApp (main9.py)
  ├─ Creates: self.cmapframe
  ├─ Creates: self.specframe
  └─ Passes to: XYMap.__init__(fnames, cmapframe, specframe, ...)
       └─ Stores: self.cmapframe = cmapframe
       └─ Stores: self.specframe = specframe
```

**Key Principle:** The component that creates a frame is responsible for destroying it.

#### Error Sequence

When data is loaded a second time, the following sequence causes the error:

1. **User Action:** Click "Load HSI data" button (second time)

2. **FileProcessorApp.spec_loadfiles() - Line 521:**
   ```python
   self.Nanomap.on_close()  # Cleanup before reload
   ```

3. **XYMap.on_close() - Lines 2184-2186:**
   ```python
   try:
       self.cmapframe.destroy()  # ❌ PROBLEM: Destroying frame it doesn't own
   except:
       pass
   ```

4. **FileProcessorApp.spec_loadfiles() - Lines 523-524:**
   ```python
   self.cmapframe.destroy()  # Attempting to destroy already-destroyed frame
   self.specframe.destroy()
   ```

5. **Tkinter Context Mismatch:**
   - Frame was destroyed from `XYMap` context (not main thread context)
   - `FileProcessorApp` tries to destroy it again from main thread
   - Tkinter detects the frame is in an invalid state
   - Raises: `RuntimeError: main thread is not in main loop`

### Why This Happens

The `XYMap.on_close()` method violates the ownership principle:
- **What it does:** Destroys `self.cmapframe` that was passed to it
- **What it should do:** Only clean up resources it creates (matplotlib, data)
- **Why it's wrong:** Frames are owned by `FileProcessorApp`, not `XYMap`

## Impact Assessment

### Affected Users
- Users who need to reload data multiple times in a single session
- Users processing multiple HSI datasets sequentially
- Automated processing scripts that call load_data repeatedly

### Severity Justification (Medium)
- **Not Critical:** First load works correctly
- **Significant Inconvenience:** Requires application restart to load new data
- **Workaround Exists:** Restart application between data loads
- **No Data Loss:** Error occurs during cleanup, not data processing

## Proposed Solution

### Fix Overview

Remove frame destruction from `XYMap.on_close()` since `XYMap` doesn't own the frames.

### Code Changes

**File:** `lib9.py`  
**Method:** `XYMap.on_close()`

**Before (lines 2181-2187):**
```python
def on_close(self):
    plt.close('all')
    # tkinter destroy
    try:
        self.cmapframe.destroy()  # ❌ Remove this - XYMap doesn't own the frame
    except:
        pass
    # explicitly clean up spectra to release file handles
    ...
```

**After:**
```python
def on_close(self):
    plt.close('all')
    # Note: Frame destruction is handled by FileProcessorApp, the frame owner
    # XYMap only cleans up resources it creates
    
    # explicitly clean up spectra to release file handles
    if hasattr(self, 'specs'):
        ...
```

### Justification

1. **Ownership Principle:** Only destroy what you create
   - `FileProcessorApp` creates frames → `FileProcessorApp` destroys frames
   - `XYMap` creates data/matplotlib → `XYMap` destroys data/matplotlib

2. **Thread Safety:** Frame destruction must happen in the creating thread context
   - `FileProcessorApp.spec_loadfiles()` runs in main thread
   - Frame destruction must stay in `FileProcessorApp.spec_loadfiles()`

3. **Separation of Concerns:**
   - `XYMap.on_close()` handles: matplotlib cleanup, data array cleanup, file handle release
   - `FileProcessorApp.spec_loadfiles()` handles: frame destruction, object deletion

## Validation Plan

### Test Cases

1. **Primary Test: Repeated Data Loading**
   - Load HSI data from folder A
   - Verify successful load and display
   - Load HSI data from folder B
   - Verify no error, successful reload
   - Repeat 5 times
   - **Expected:** No "main thread is not in main loop" error

2. **Frame Cleanup Test**
   - Load HSI data
   - Verify GUI elements appear correctly
   - Load new data
   - Verify old GUI elements destroyed, new ones created
   - Check for memory leaks with repeated loads
   - **Expected:** No zombie frames, clean memory usage

3. **Multiple HSI Processing Test**
   - Enable "Process Multiple HSIs" option
   - Select directory with 10+ HSI folders
   - Start processing
   - **Expected:** Process all folders without errors

4. **Application Exit Test**
   - Load HSI data
   - Close application
   - **Expected:** Clean exit, no error dialogs, no hung processes

### Regression Testing

Ensure existing functionality still works:
- [ ] Initial data load works
- [ ] Single data load with visualization
- [ ] Save/Load HSI state
- [ ] ROI selection and processing
- [ ] Clara image loading
- [ ] Newton spectrum loading
- [ ] TCSPC data loading
- [ ] Application close button

## References

### Related Code Sections

1. **FileProcessorApp.spec_loadfiles()** (`main9.py:501-584`)
   - Handles frame creation/destruction
   - Calls `XYMap.on_close()` for cleanup
   - Creates new `XYMap` instance

2. **XYMap.on_close()** (`lib9.py:2181-2209`)
   - Should clean up: matplotlib, data arrays, file handles
   - Should NOT clean up: frames, GUI widgets created by caller

3. **FileProcessorApp.init_spec_loadfiles()** (`main9.py:460-498`)
   - Handles multiple HSI processing loop
   - Calls `on_close()` before each load

### Related Documentation

- **GUI_HIERARCHY_AND_LIFECYCLE.md** - Section on "Cleanup & Closing Flow"
- **PROGRAM_STRUCTURE.md** - Section on "FileProcessorApp workflow"

## Implementation Checklist

- [x] Analyze root cause
- [ ] Implement fix in `lib9.py`
- [ ] Test repeated data loading
- [ ] Test multiple HSI processing
- [ ] Test application exit
- [ ] Run regression tests
- [ ] Update documentation if needed
- [ ] Create pull request

## Notes

### User Comment Reference

From issue comments:
> "issue fix: on_close event of XYMap class is called before load_data, to destroy XYMaps TK root instance. It looks like this fixed the issue"

This comment correctly identifies that `on_close()` is called before `load_data()`, which is the right sequence. However, the issue is that `on_close()` itself tries to destroy the frame, which it shouldn't do. The fix is to remove frame destruction from `on_close()` entirely.

### Design Pattern: Dependency Injection

This issue highlights the importance of following proper dependency injection patterns:
- When a component receives a resource via constructor (frame passed to XYMap)
- That component should NOT manage the lifecycle of that resource
- The component that creates the resource manages its lifecycle
- This prevents ownership conflicts and context mismatches

---

**Document Version:** 1.0  
**Last Updated:** 2025-12-15  
**Author:** Copilot Analysis
