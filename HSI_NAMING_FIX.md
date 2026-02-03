# HSI Naming Bug Fix - Implementation Summary

## Problem Description

The HSI (Hyperspectral Image) naming system in SpecMap had a critical bug where HSI names could duplicate under certain conditions:

1. **After deletion**: When HSIs were deleted, the naming algorithm tried to find gaps in the numbering sequence and reuse them, potentially causing duplicates.
2. **On loading**: When loading HSIs from files, the code used `len(PMdict)` which could conflict with existing names.
3. **ROI-based HSIs**: These combined parent HSI names with ROI names, which could also duplicate.

## Root Cause Analysis

The original implementation in `writetopixmatrix()` (lines 2798-2816) used a gap-filling algorithm:

```python
pmi = 0
for i in range(len(list(self.PMdict.keys()))+1):
    newpmname = '{}{}'.format('HSI', i)
    if newpmname in list(self.PMdict.keys()):
        pmi += 1
    else:
        newpmname = '{}{}'.format('HSI', pmi)
        break
```

This approach had several issues:
- After deleting HSI1, it would try to reuse 'HSI1' for a new HSI
- The logic was complex and error-prone
- No persistence across save/load cycles

## Solution

Implemented a **monotonically increasing global counter** that ensures unique HSI names:

### Key Changes

1. **Added persistent counter** (`_hsi_counter`) to XYMap class initialization (line 262):
```python
self._hsi_counter = 0  # Global counter for unique HSI naming
```

2. **Updated `writetopixmatrix()`** (lines 2799-2809) to use the counter:
```python
if name == None or name not in self.PMdict.keys():
    # Use monotonically increasing counter for unique HSI names
    newpmname = f'HSI{self._hsi_counter}'
    self._hsi_counter += 1
else: 
    newpmname = name
```

3. **Updated `loadHSI()`** (lines 847-859) to use the counter:
```python
hsiname = f'HSI{self._hsi_counter}'
self._hsi_counter += 1
```

4. **Updated `multiroitopixmatrix()`** (lines 2712-2720) to use the counter:
```python
# Use counter to ensure unique name
newroiname = f"HSI{self._hsi_counter}"
self._hsi_counter += 1
```

5. **Updated initial HSI creation** in `load_data()` (lines 2591-2598):
```python
initial_hsi_name = f'HSI{self._hsi_counter}'
self._hsi_counter += 1
```

6. **Updated `save_state()`** (line 3183) to persist the counter:
```python
'_hsi_counter': self._hsi_counter if hasattr(self, '_hsi_counter') else 0,
```

7. **Updated `load_state()`** (lines 3307-3335) to restore and validate the counter:
```python
# Restore HSI counter and ensure it's higher than any existing HSI numbers
self._hsi_counter = state.get('_hsi_counter', 0)

# Ensure counter is higher than any existing HSI numbers to prevent duplicates
max_hsi_num = -1
for hsi_name in self.PMdict.keys():
    if hsi_name.startswith('HSI'):
        try:
            num = int(hsi_name[3:])  # Extract number after 'HSI'
            max_hsi_num = max(max_hsi_num, num)
        except ValueError:
            pass

# Set counter to be one more than the highest existing number
if max_hsi_num >= self._hsi_counter:
    self._hsi_counter = max_hsi_num + 1
```

## Benefits

1. **Guaranteed uniqueness**: HSI names never duplicate, even after deletions
2. **Simple logic**: Counter just increments, no complex gap-filling
3. **Persistent**: Counter survives save/load cycles
4. **Backward compatible**: Validates and updates counter when loading old saves
5. **Scalable**: Integer counter can handle millions of HSIs (way more than any user would create)

## Testing

Created comprehensive test suite (`testingscripts/test_hsi_naming.py`) with 6 tests:

1. ✅ Counter initialization
2. ✅ Counter increments correctly
3. ✅ Names not reused after deletion
4. ✅ Counter preserved across save/load
5. ✅ Counter correctly updated for high-numbered HSIs
6. ✅ Complex scenario with deletions and multiple creations

All tests pass successfully.

## Files Modified

- `lib9.py`: Main implementation
- `testingscripts/test_hsi_naming.py`: New test file

## Minimal Changes

The implementation follows the principle of minimal changes:
- Only 5 functions modified
- Counter added as a single line in `__init__`
- Simple counter increment logic replaces complex gap-filling
- No changes to HSI class structure or API
- Backward compatible with existing saved states
