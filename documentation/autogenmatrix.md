# autogenmatrix — How Spectra Are Placed Into SpecDataMatrix

## Overview

`autogenmatrix` (in `lib9.py`) converts a flat list of `SpectrumData` objects (`self.specs`) into a 2-D grid called `self.SpecDataMatrix`.  
Each spectrum carries a physical `x-position` and `y-position` in its `data` dictionary.  
The method works out which row and column each spectrum belongs to and stores it at `self.SpecDataMatrix[row][col]` — **row = Y-index, column = X-index**.

---

## Step-by-Step Data Flow

### 1. Collect unique physical coordinates

```
for every spectrum i in self.specs:
    add i.data['x-position'] to self.mxcoords   (if not already present)
    add i.data['y-position'] to self.mycoords   (if not already present)

self.mxcoords = sorted(self.mxcoords)   # ascending
self.mycoords = sorted(self.mycoords)   # ascending
```

After this step `self.mxcoords` and `self.mycoords` are the **sorted lists of unique physical positions** found in the loaded files.

---

### 2. Build the grid axes — `genmatgrid(xar, yar)`

`genmatgrid` constructs the regular-grid axes `self.PixAxX` and `self.PixAxY` and initialises the empty `SpecDataMatrix`.

#### Determining the grid step size

```
dxa = consecutive differences of self.mxcoords
dya = consecutive differences of self.mycoords

if all differences are equal:
    self.gdx = dxa[0]          # perfectly regular grid
else:
    self.gdx = most_frequent(dxa)   # irregular — fall back to majority step

(same logic for gdy)

self.gdx = round(self.gdx, 10)     # guard against floating-point noise
self.gdy = round(self.gdy, 10)
```

#### Building the axis arrays

```
self.PixAxX = [round(i*gdx + x_min, 10)  for i in range(N_x)]
self.PixAxY = [round(i*gdy + y_min, 10)  for i in range(N_y)]

where N_x = int((x_max - x_min + gdx) / gdx)
      N_y = int((y_max - y_min + gdy) / gdy)
```

These are **evenly-spaced grids** that span from the minimum to the maximum observed coordinate.

#### Initialising the empty matrix

```
self.SpecDataMatrix = [[np.nan] * N_x  for _ in range(N_y)]
```

Every cell starts as `np.nan` (no spectrum assigned).

---

### 3. Populate the matrix — `SpecdataintoMatrix()`

For every spectrum `i` in `self.specs`:

```
x = i.data['x-position']
y = i.data['y-position']

xind = argmin(|self.PixAxX - x|)   # index in X-axis  (column)
yind = argmin(|self.PixAxY - y|)   # index in Y-axis  (row)

self.SpecDataMatrix[yind][xind] = i
```

The mapping from physical coordinates to matrix indices is done by `deflib.closest_indices`, which performs a **nearest-neighbour lookup** on both axes independently.

#### Index convention

| Matrix index | Axis array   | Physical direction |
|---|---|---|
| `[0]` (outer / row) | `self.PixAxY` | Y (vertical) |
| `[1]` (inner / column) | `self.PixAxX` | X (horizontal) |

So to retrieve the spectrum at physical position `(px, py)`:

```python
xind, yind = deflib.closest_indices(self.PixAxX, self.PixAxY, px, py)
spec = self.SpecDataMatrix[yind][xind]
```

---

## Possible Bugs That Place Spectra in the Wrong Position

### Bug 1 — Floating-point coordinate mismatch

**Scenario:** Two spectra share a physical coordinate in principle (e.g., both at `x = 10.0`) but their stored values differ by floating-point noise (e.g., `10.0` vs `10.000000001`).

**Effect:**
- `autogenmatrix` treats them as two distinct X positions.
- The grid is over-populated with extra columns that are nearly identical in physical space.
- One spectrum ends up in a column that is shifted by one index relative to where it should be.

**Root location:** `for i in self.specs: if i.data['x-position'] not in self.mxcoords` — this comparison is an exact equality check.

---

### Bug 2 — Irregular step sizes and the `most_frequent` heuristic

**Scenario:** The scan has a non-uniform step size (e.g., most steps are 1 µm but one gap is 2 µm due to a missed measurement).

**Effect:**
- `genmatgrid` picks `gdx = most_frequent_step = 1 µm`.
- The axis `self.PixAxX` is built with 1 µm steps, but the large gap creates a hole in the middle of the axis.
- Any spectrum that physically lived at 2 µm past a previous point is now `closest_indices`-mapped to the wrong column — the column at 1 µm past, not 2 µm past.
- In an extreme case two spectra map to the same column; one is silently discarded with a console message ("Point neglected…") and no exception is raised.

**Root location:** `genmatgrid` → `deflib.most_freq_element(dxa)`; and subsequently the axis reconstruction loop that assumes uniform spacing.

---

### Bug 3 — Axis reconstruction accumulates rounding errors

**Scenario:** `gdx` is an irrational or repeating decimal (e.g., `0.333…`).

**Effect:**
- The axis is built as `[i * gdx + x_min for i in range(N)]`, so each point inherits a different accumulated rounding error from `i * gdx`.
- A spectrum stored at the exact physical value `x_min + 2*gdx` may be mapped by `closest_indices` to the neighbouring column because the axis value at that index has drifted.

**Root location:** `genmatgrid` axis construction loop; mitigated but not fully solved by the `round(..., 10)` calls.

---

### Bug 4 — Grid size under-count due to integer truncation

**Scenario:** `(x_max - x_min + gdx) / gdx` yields something like `4.9999999…` due to floating-point arithmetic.

**Effect:**
- `int(...)` truncates to `4` instead of `5`, so the rightmost column is never created.
- The spectrum that belongs there cannot be placed in the matrix.
- `closest_indices` will map it to the last existing column, colliding with the spectrum that legitimately lives there.

**Root location:** `genmatgrid` range calculation: `int((self.matend[0]-self.matstart[0]+self.gdx)/self.gdx)`.

---

### Bug 5 — Collision on the same grid cell (silent discard)

**Scenario:** Two spectra have coordinates that both round to the same `(xind, yind)`.  
This can happen because of Bug 1, Bug 2, or genuinely overlapping scan positions.

**Effect:**
- `SpecdataintoMatrix` checks whether the cell already contains a `SpectrumData` object.
- If it does and `overwrite=False` (the default), the second spectrum is **silently ignored** with a print message.
- No exception is raised; the programme continues, and the discarded spectrum is never stored anywhere.

**Root location:** `SpecdataintoMatrix` — the `if type(...) == SpectrumData` branch with the `else: pass` (no-overwrite) path.

---

### Bug 6 — `self.specs` is cleared before secondary calls to `SpecdataintoMatrix`

**Scenario:** At the end of `autogenmatrix`, `self.specs = []` is executed as a memory optimisation.  
If any downstream code (e.g., loading additional spectra without a full reinitialisation) calls `SpecdataintoMatrix()` a second time, `self.specs` is empty and nothing is written.

**Effect:** A silent no-op that leaves the matrix unchanged, potentially causing confusion when the user expects newly added spectra to appear.

**Root location:** End of `autogenmatrix` — `self.specs = []` after `gc.collect()`.

---

### Bug 7 — Single-spectrum edge case bypasses `genmatgrid`

**Scenario:** Exactly one spectrum is loaded.

**Effect:**
- `autogenmatrix` takes the `elif len(self.specs) == 1` branch and hardcodes  
  `self.PixAxX = [0]`, `self.PixAxY = [0]`.
- The axes no longer contain the actual physical coordinates; they contain `[0]`.
- Any code that later looks up a spectrum by physical coordinate via `closest_indices` will behave incorrectly because the axis no longer encodes real positions.

**Root location:** `autogenmatrix` `elif len(self.specs) == 1` branch.

---

## Quick Reference: Index Convention

```
self.SpecDataMatrix  shape: [N_y][N_x]

self.SpecDataMatrix[j][i]
                    │   └── column = X-index (self.PixAxX[i])
                    └────── row    = Y-index (self.PixAxY[j])

Physical → Matrix:
    i = argmin(|self.PixAxX - x_physical|)
    j = argmin(|self.PixAxY - y_physical|)
```
