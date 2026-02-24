# FastestUp – Lightweight HSI Creator

A minimal, standalone **tkinter** GUI for generating a **Hyperspectral Image (HSI)**
from raw spectrometer data files as quickly as possible.

---

## Overview

`FastestUp` is an intentionally lightweight alternative to the full **SpecMap**
pipeline (`main9.py` / `lib9.py`).  It focuses **only** on:

| Feature | Included |
|---------|----------|
| Load spectra from folder | ✅ |
| Background (BG) subtraction | ✅ |
| Linear BG averaging | ✅ |
| Cosmic-ray removal | ✅ |
| Wavelength-range integration (HSI) | ✅ |
| Display HSI via matplotlib | ✅ |
| Save image via matplotlib toolbar | ✅ |
| Derivative calculation | ❌ intentionally omitted |
| Spectrum averaging / export | ❌ intentionally omitted |
| Pickle save / load of HSI objects | ❌ intentionally omitted |
| ROI selection / fitting | ❌ intentionally omitted |

---

## Location

```
SpecMap/
└── standalone/
    └── fastestup/
        ├── fastestup.py   ← the GUI application
        └── README.md      ← this file
```

---

## Requirements

FastestUp relies on the same dependencies as the main SpecMap project:

| Package | Purpose |
|---------|---------|
| `tkinter` | GUI (bundled with Python ≥ 3.8) |
| `numpy` | Numerical operations |
| `matplotlib` | HSI display and toolbar save |
| `scipy` | Cosmic-ray removal filters (optional) |

`deflib1.py` (from the SpecMap root) is imported automatically when the script
is run; it provides the cosmic-removal functions.  If it cannot be found,
FastestUp falls back to a built-in linear-interpolation implementation.

---

## How to run

```bash
# from the SpecMap root directory
python standalone/fastestup/fastestup.py

# or from the fastestup folder itself
cd standalone/fastestup
python fastestup.py
```

---

## GUI Layout

```
┌──────────────────────────────────────────────────────────────────────────┐
│  Data Input                                                               │
│  Data Folder  [ /path/to/data ]                          [ Browse … ]    │
│  Filename pattern  [ spectrum ]                                           │
│  File extension    [ .txt ]                                               │
├─────────────────────────────┬────────────────────────────────────────────┤
│  Background Correction      │  Cosmic Ray Removal                        │
│  ☑ Linear Background        │  ☑ Remove Cosmic Rays                      │
│    (average BG)             │  Method  [ Linear + Neighbor (Combined) ▼] │
│                             │  Threshold  [ 100 ]                        │
│                             │  Width      [ 10  ]                        │
├─────────────────────────────┴────────────────────────────────────────────┤
│  Wavelength Range & Display                                               │
│  Start wavelength (nm)  [ 500 ]   End wavelength (nm)  [ 700 ]           │
│  Count threshold        [ 0   ]   Colormap  [ hot ▼ ]                    │
├──────────────────────────────────────────────────────────────────────────┤
│  [ Create HSI ]  [ Clear Plot ]                                           │
├──────────────────────────────────────────────────────────────────────────┤
│  HSI Preview  (matplotlib canvas – use the toolbar to save)              │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │                  [ HSI image rendered here ]                      │    │
│  └──────────────────────────────────────────────────────────────────┘    │
│  Status: HSI created: 20×20 pixels | 500.0–700.0 nm | use toolbar …      │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Parameters

### Data Input

| Field | Description | Default |
|-------|-------------|---------|
| **Data Folder** | Directory (and sub-directories) that will be searched for spectrum files. | *(empty)* |
| **Filename pattern** | Sub-string that every matching filename must contain. | `spectrum` |
| **File extension** | File extension of the spectrum files. | `.txt` |

### Background Correction

| Option | Description | Default |
|--------|-------------|---------|
| **Linear Background** | When checked, the BG column read from the first file is **averaged** to a single constant value before subtraction.  This removes pixel-to-pixel variation in the detector dark current and results in a uniform background level across the whole map. | ✅ |

### Cosmic Ray Removal

| Option | Description | Default |
|--------|-------------|---------|
| **Remove Cosmic Rays** | Enable/disable cosmic-ray removal. | ✅ |
| **Method** | Algorithm used for removal (see table below). | `Linear + Neighbor (Combined)` |
| **Threshold** | Minimum spike height (in counts) to be considered a cosmic. | `100` |
| **Width** | Pixel window width used by the removal algorithm. | `10` |

#### Available methods

| Method | Description |
|--------|-------------|
| **Linear + Neighbor (Combined)** *(recommended)* | Two-stage removal: (1) linear interpolation across gradient-detected spikes; (2) nearest-neighbour median averaging for residual outliers. |
| **Linear Interpolation** | Single-pass gradient-based linear interpolation. |
| **Nearest Neighbor average** | Replaces outliers with the median of their local neighbourhood. |

### Wavelength Range & Display

| Field | Description | Default |
|-------|-------------|---------|
| **Start wavelength (nm)** | Lower bound of the integration window. | `500` |
| **End wavelength (nm)** | Upper bound of the integration window. | `700` |
| **Count threshold** | Pixels whose integrated intensity falls below this value are shown as NaN (transparent/white in most colormaps). Set to `0` to display all pixels. | `0` |
| **Colormap** | matplotlib colormap applied to the HSI. | `hot` |

---

## Processing pipeline

1. **File discovery** – walk the selected folder recursively and collect all
   files whose name contains the *filename pattern* and ends with the
   *file extension*.

2. **WL / BG axis** – read the shared wavelength (WL) axis and background (BG)
   spectrum from the first valid file.  If *Linear Background* is enabled,
   the BG values are replaced by their mean before any subtraction.

3. **Per-pixel processing** – for each spectrum file:
   - read PL (raw signal) column
   - compute `PLB = PL − BG`
   - if cosmic removal is enabled, apply the chosen algorithm to `PLB`
   - sum `PLB` over the wavelength integration window → single intensity value

4. **Pixel matrix** – x/y stage positions are read from the file headers;
   the intensity values are arranged into a 2-D array (rows = Y, columns = X).

5. **Display** – the pixel matrix is shown in the embedded matplotlib canvas.
   Use the **matplotlib toolbar** (floppy-disk icon) to save the image to disk
   in any format supported by matplotlib (PNG, PDF, SVG, …).

---

## Saving the HSI image

FastestUp does **not** implement a custom save dialog.  To save:

1. Generate the HSI with the **Create HSI** button.
2. Click the **floppy-disk (save)** icon in the matplotlib toolbar below the
   plot.
3. Choose the desired file format and destination in the system dialog.

---

## Relationship to the full SpecMap GUI

FastestUp is a read-only, display-only subset of the main `main9.py` /
`lib9.py` pipeline:

```
main9.py / lib9.py                FastestUp
──────────────────────────────    ─────────────────────────────
load_data() → loadfiles()    →    _read_wl_bg() + _read_spectrum()
deflib.cosmicfuncts[...]     →    same (via sys.path import)
XYMap.getPLpixelIntervalMaxIndex  →    np.sum(PLB[aq_start:aq_end])
plotPixelMatrix()            →    ax.imshow(pixel_matrix)
```

Because derivatives, ROI masks, fitting, and pickle I/O are omitted, the
memory footprint and processing time are significantly reduced.
