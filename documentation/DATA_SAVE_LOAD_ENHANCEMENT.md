# Data Save/Load Enhancement Documentation

## Section 1: Overview

### Purpose
This document describes the enhanced save/load system in SpecMap that now includes:
- **ROI (Region of Interest) mask persistence** - ROI masks are automatically saved and restored
- **Averaged spectra storage** - All averaged spectra are saved with the dataset
- **Multiple spectral data types** - Support for PL-BG and derivative spectra (1st/2nd derivatives, normalized)
- **Enhanced export capabilities** - Export HSI data with associated spectra

### What Data is Now Saved

When you save a SpecMap dataset using `save_state()`, the following data is preserved in the pickle file:

1. **Core spectral data**
   - Individual spectrum objects (`specs`)
   - 2D spectrum data matrix (`SpecDataMatrix`)
   - Wavelength axis (`WL`, `WL_eV`)
   - Background data (`BG`)

2. **HSI images**
   - All hyperspectral images (`PMdict`)
   - Fit results and parameters
   - Image metadata

3. **ROI masks** ✨ NEW
   - All defined ROI masks with their names
   - Mask dimensions validated on load

4. **Averaged spectra** ✨ NEW
   - All averaged spectra (`disspecs`)
   - Multiple data types (PL-BG, derivatives, normalized derivatives)
   - Metadata for each averaged spectrum

5. **Processing parameters**
   - Wavelength range, thresholds, grid parameters
   - Configuration settings

### Benefits

- **Workflow continuity**: Your ROI definitions and averaged spectra are preserved between sessions
- **Data integrity**: ROI dimensions are validated against HSI data on load
- **Comprehensive analysis**: All spectral data types (including derivatives) can be generated and saved
- **Efficient export**: Export all analysis results in one operation

---

## Section 2: ROI Mask Saving

### How ROI Masks are Saved

ROI masks are automatically saved when you use the `save_state()` method. The system:

1. Collects all ROI masks from `roihandler.roilist`
2. Stores them as numpy arrays in the pickle file
3. Logs the number and names of saved ROI masks

### Data Structure of `roilist`

The `roilist` is a dictionary where:
- **Keys**: ROI names (strings) defined by the user
- **Values**: 2D numpy arrays representing the mask
  - Shape matches the HSI image dimensions
  - Values are typically floats (1.0 for included pixels, NaN for excluded pixels)

Example structure:
```python
roilist = {
    'ROI_1': np.array([[1.0, 1.0, np.nan],
                       [1.0, 1.0, np.nan],
                       [np.nan, np.nan, np.nan]]),
    'ROI_bright': np.array([[np.nan, 1.0, 1.0],
                            [np.nan, 1.0, 1.0],
                            [np.nan, np.nan, np.nan]])
}
```

### Validation on Load

When loading a saved state, the system:

1. Restores all ROI masks from the pickle file
2. **Validates dimensions** - checks that each ROI mask matches the HSI image dimensions
3. **Logs validation results**:
   - ✓ Success message for matching dimensions
   - ⚠ Warning for mismatched dimensions

Example output:
```
Successfully loaded XYMap state from: my_dataset.pkl
  - Loaded 50 spectra
  - Loaded 3 HSI images
  - Loaded 2 ROI masks
    ROI names: ['ROI_1', 'ROI_bright']
  ✓ ROI 'ROI_1' dimensions validated: (10, 10)
  ✓ ROI 'ROI_bright' dimensions validated: (10, 10)
```

### Accessing ROI Masks After Loading

After loading a dataset, you can access ROI masks programmatically:

```python
# Access all ROI masks
roi_masks = xymap_instance.roihandler.roilist

# Get a specific ROI by name
roi_1_mask = xymap_instance.roihandler.roilist['ROI_1']

# List all ROI names
roi_names = list(xymap_instance.roihandler.roilist.keys())

# Check if a specific ROI exists
if 'ROI_1' in xymap_instance.roihandler.roilist:
    print("ROI_1 is available")
```

---

## Section 3: Spectra Averaging and Export

### Available Spectral Data Types

SpecMap now supports averaging and saving multiple types of spectral data:

1. **Spectrum (PL-BG)** - `PLB`
   - Background-corrected photoluminescence data
   - Raw spectral intensity after background subtraction

2. **First derivative** - `Specdiff1`
   - First derivative of the spectrum: d(PLB)/dλ
   - Highlights spectral features and transitions
   - Calculated using Savitzky-Golay filter

3. **Second derivative** - `Specdiff2`
   - Second derivative of the spectrum: d²(PLB)/dλ²
   - Enhances fine spectral features
   - Useful for identifying overlapping peaks

4. **First derivative (normalized)** - `Specdiff1_norm`
   - First derivative normalized by signal intensity
   - Removes intensity variations, focuses on spectral shape

5. **Second derivative (normalized)** - `Specdiff2_norm`
   - Second derivative normalized by signal intensity
   - Enhanced feature detection independent of intensity

### Using the "Average HSI to Spectrum" Function

#### Single Data Type Averaging (Original Method)

1. Select the HSI image from the dropdown
2. Select the desired data type from "Select Data Set" dropdown
3. Click **"average hsi to spectrum"** button
4. The averaged spectrum is added to the spectral data list

#### Multiple Data Type Averaging (New Method)

Use the new **"Export All Averaged Spectra"** button to:
1. Generate averaged spectra for ALL data types simultaneously
2. Automatically calculate derivatives if needed
3. Save all averaged spectra to the dataset
4. Export to a CSV file in one operation

**Programmatic usage:**
```python
# Generate all spectral data types at once
generated_spectra = xymap_instance.averageHSItoSpecDataMultiple()

# Or specify specific types
data_types = ['PLB', 'Specdiff1', 'Specdiff2']
generated_spectra = xymap_instance.averageHSItoSpecDataMultiple(data_types)
```

### Averaged Spectrum Naming Convention

Averaged spectra are automatically named using the format:
```
{HSI_name}_{data_type}_avg
```

Examples:
- `HSI0_PLB_avg` - Averaged PL-BG spectrum from HSI0
- `HSI0_Specdiff1_avg` - Averaged first derivative from HSI0
- `HSI1_Specdiff2_norm_avg` - Averaged normalized second derivative from HSI1

### File Format and Structure of Exported Spectra

#### Export All Averaged Spectra Format

When using **"Export All Averaged Spectra"**, the CSV file contains:

**Header section:**
```
# All averaged spectra from HSI: HSI0
# Wavelength range: 400.0 - 800.0 nm
# Generated: 5 spectral data types
#
```

**Data columns:**
```
Wavelength (nm),Spectrum (PL-BG),first derivative,second derivative,first derivative (normalized),second derivative (normalized)
400.0,1234.5,12.3,-0.5,0.01,-0.0001
401.0,1245.6,13.1,-0.6,0.011,-0.00012
...
```

#### Export HSI with Spectra Format

Using `exportHSIWithSpectra()` creates two files:

1. **`{basename}_matrix.csv`** - HSI pixel matrix data
2. **`{basename}_avg_spectra.csv`** - All associated averaged spectra

---

## Section 4: Usage Examples

### Example 1: Creating and Saving ROI Masks

```python
# Step 1: Load your data
xymap = XYMap(fnames=['data1.txt', 'data2.txt', ...])

# Step 2: Create ROI masks using the GUI
#    - Click "ROI Editing last Selection"
#    - Draw your region of interest
#    - Save with a descriptive name (e.g., "bright_region")

# Step 3: Create additional ROIs as needed
#    - Repeat the ROI creation process
#    - Each ROI is added to roihandler.roilist

# Step 4: Save the complete dataset
xymap.save_state('my_analysis.pkl')
```

Expected output:
```
Successfully saved XYMap state to: my_analysis.pkl
  - Saved 50 spectra
  - Saved 3 HSI images
  - Saved 2 ROI masks
    ROI names: ['bright_region', 'edge_region']
  - Saved 0 averaged spectra
```

### Example 2: Loading Dataset and Verifying ROIs

```python
# Load the saved dataset
xymap = XYMap([])  # Initialize without files
xymap.load_state('my_analysis.pkl')
```

Expected output:
```
Successfully loaded XYMap state from: my_analysis.pkl
  - Loaded 50 spectra
  - Loaded 3 HSI images
  - Loaded 2 ROI masks
    ROI names: ['bright_region', 'edge_region']
  ✓ ROI 'bright_region' dimensions validated: (10, 10)
  ✓ ROI 'edge_region' dimensions validated: (10, 10)
  - Loaded 0 averaged spectra
  - WL axis: 800 points from 400.00 to 800.00 nm
```

### Example 3: Averaging Spectra with Different Data Types

```python
# After loading data with an HSI image

# Method 1: Single data type (using GUI)
# Select "first derivative" from dropdown, click "average hsi to spectrum"

# Method 2: All data types at once (programmatic)
xymap.averageHSItoSpecDataMultiple()
```

Expected output:
```
Checking if derivatives are calculated for individual spectra...
Derivatives not found in SpecDataMatrix. Calculating derivatives...
Calculating derivatives: d1=True, d2=True, order=3, window=11
Averaging Spectrum (PL-BG)...
  Created averaged spectrum: HSI0_PLB_avg
Averaging first derivative...
  Created averaged spectrum: HSI0_Specdiff1_avg
Averaging second derivative...
  Created averaged spectrum: HSI0_Specdiff2_avg
Averaging first derivative (normalized)...
  Created averaged spectrum: HSI0_Specdiff1_norm_avg
Averaging second derivative (normalized)...
  Created averaged spectrum: HSI0_Specdiff2_norm_avg
Generated 5 averaged spectra
```

### Example 4: Saving Dataset with Averaged Spectra

```python
# After generating averaged spectra
xymap.save_state('my_analysis_with_spectra.pkl')
```

Expected output:
```
Successfully saved XYMap state to: my_analysis_with_spectra.pkl
  - Saved 50 spectra
  - Saved 3 HSI images
  - Saved 2 ROI masks
    ROI names: ['bright_region', 'edge_region']
  - Saved 5 averaged spectra
    Averaged spectra names: ['HSI0_PLB_avg', 'HSI0_Specdiff1_avg', 'HSI0_Specdiff2_avg', 'HSI0_Specdiff1_norm_avg', 'HSI0_Specdiff2_norm_avg']
```

### Example 5: Exporting All Analysis Results

```python
# Export everything - HSI matrix and all averaged spectra
xymap.exportHSIWithSpectra()
# This will prompt for a filename and create two files:
#   - selected_name_matrix.csv
#   - selected_name_avg_spectra.csv

# Or export just the averaged spectra with all data types
xymap.exportAllAveragedSpectra()
# This generates all spectral data types and exports to one CSV
```

---

## Section 5: API Reference

### `save_state(filename)`

Save the complete XYMap state to a pickle file.

**Parameters:**
- `filename` (str): Path to the output pickle file

**Saves:**
- Core spectral data (specs, SpecDataMatrix, WL, WL_eV, BG)
- HSI images with fit results (PMdict)
- ROI masks (roilist) ✨ NEW
- Averaged spectra (disspecs) ✨ NEW
- Processing parameters and configuration

**Returns:**
- `True` if successful, `False` otherwise

**Example:**
```python
success = xymap.save_state('/path/to/dataset.pkl')
```

### `load_state(filename)`

Load a previously saved XYMap state from a pickle file.

**Parameters:**
- `filename` (str): Path to the input pickle file

**Restores:**
- All saved data (see `save_state`)
- Validates ROI dimensions ✨ NEW
- Updates GUI elements

**Returns:**
- `True` if successful, `False` otherwise

**Example:**
```python
success = xymap.load_state('/path/to/dataset.pkl')
```

### `averageHSItoSpecData()`

Average the selected HSI to a single spectrum using the currently selected data type.

**Parameters:** None (uses GUI selections)

**Behavior:**
- Gets data type from `selectspecbox` dropdown
- Averages over all valid pixels in the selected HSI
- Calculates derivatives if configured
- Adds result to `disspecs` with auto-generated name

**Returns:** None

**Example:**
```python
# Set the desired data type in GUI, then:
xymap.averageHSItoSpecData()
```

### `averageHSItoSpecDataMultiple(data_types=None)` ✨ NEW

Generate multiple averaged spectra simultaneously for different data types.

**Parameters:**
- `data_types` (list, optional): List of data type keys to average
  - Default: `['PLB', 'Specdiff1', 'Specdiff2', 'Specdiff1_norm', 'Specdiff2_norm']`
  - Valid keys: `'PLB'`, `'Specdiff1'`, `'Specdiff2'`, `'Specdiff1_norm'`, `'Specdiff2_norm'`

**Behavior:**
- Ensures derivatives are calculated for SpecDataMatrix
- Averages each specified data type
- Names results as `{HSI}_{type}_avg`
- Updates GUI combobox

**Returns:**
- `dict`: Dictionary of generated spectra `{name: Spectra_object}`

**Example:**
```python
# Generate all data types
all_spectra = xymap.averageHSItoSpecDataMultiple()

# Generate specific types
selected_spectra = xymap.averageHSItoSpecDataMultiple(['PLB', 'Specdiff1'])
```

### `exportHSI()`

Export the selected HSI to a CSV file.

**Parameters:** None (uses GUI selection)

**Behavior:**
- Opens file dialog for filename
- Exports HSI metadata and pixel matrix
- Handles NaN values properly

**Returns:** None

### `exportHSIWithSpectra()` ✨ NEW

Export HSI along with associated averaged spectra to separate CSV files.

**Parameters:** None (uses GUI selection)

**Creates:**
- `{basename}_matrix.csv` - HSI pixel matrix with metadata
- `{basename}_avg_spectra.csv` - All averaged spectra from this HSI

**Returns:** None

**Example:**
```python
# Prompts for filename, creates two files
xymap.exportHSIWithSpectra()
```

### `exportAllAveragedSpectra()` ✨ NEW

Generate and export all averaged spectra types in one operation.

**Parameters:** None (uses GUI selection)

**Behavior:**
1. Calls `averageHSItoSpecDataMultiple()` to generate all types
2. Opens file dialog for CSV filename
3. Exports all spectra to single CSV file with:
   - Metadata header
   - Column for each data type
   - Wavelength as first column

**Returns:** None

**Example:**
```python
# Generates all types and exports to CSV
xymap.exportAllAveragedSpectra()
```

---

## Backward Compatibility

The enhanced save/load system maintains full backward compatibility:

- **Old pickle files** without `disspecs` can still be loaded
  - `disspecs` defaults to empty dictionary `{}`
- **Old pickle files** without enhanced ROI validation still load correctly
- **No migration** required for existing datasets

---

## Best Practices

1. **Save frequently** during analysis to preserve ROI definitions and averaged spectra
2. **Use descriptive ROI names** for easier identification later
3. **Generate all spectral types** before saving for comprehensive analysis
4. **Validate ROI dimensions** by checking console output after loading
5. **Export results** in addition to saving pickle files for long-term storage

---

## Troubleshooting

### ROI Dimension Mismatch Warning

**Issue:** `⚠ Warning: ROI 'name' dimensions (10, 10) don't match HSI dimensions (12, 12)`

**Cause:** ROI was created on a different HSI image or data was modified

**Solution:** 
- Recreate the ROI on the current HSI image
- Or discard the incompatible ROI

### Derivatives Not Available

**Issue:** Normalized derivatives show as empty or missing

**Cause:** Derivatives haven't been calculated yet

**Solution:**
```python
# Ensure derivatives are calculated
xymap.calculate_derivatives()

# Then average
xymap.averageHSItoSpecDataMultiple()
```

### No Averaged Spectra After Loading

**Issue:** Loaded dataset shows 0 averaged spectra

**Cause:** Dataset was saved before this enhancement or no averaging was performed

**Solution:** Generate averaged spectra after loading:
```python
xymap.averageHSItoSpecDataMultiple()
xymap.save_state('dataset_updated.pkl')  # Save with spectra
```

---

## Version History

- **v1.0** (2026-02-02): Initial enhanced save/load implementation
  - ROI mask persistence with validation
  - Averaged spectra (disspecs) save/load
  - Multiple spectral data type averaging
  - Enhanced export capabilities
