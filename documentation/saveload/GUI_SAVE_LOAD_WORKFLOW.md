# SpecMap GUI Workflow: Saving and Loading HSI Data with ROIs and Averaged Spectra

## Document Overview

This document provides a comprehensive guide to using the SpecMap GUI for saving and loading hyperspectral imaging (HSI) data, including ROI (Region of Interest) masks and averaged spectra. It covers the complete workflow from loading raw data to saving analysis results.

**Target Audience:** SpecMap users who want to:
- Preserve their analysis work across sessions
- Save and restore ROI definitions
- Maintain averaged spectral data
- Export results for publication or further analysis

---

## Table of Contents

1. [Quick Start Guide](#quick-start-guide)
2. [The Load Data Tab](#the-load-data-tab)
3. [Saving Your Work](#saving-your-work)
4. [Loading Saved Data](#loading-saved-data)
5. [Working with ROIs](#working-with-rois)
6. [Working with Averaged Spectra](#working-with-averaged-spectra)
7. [Complete Workflow Examples](#complete-workflow-examples)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start Guide

### Saving HSI Data with ROIs and Averaged Spectra

1. **Load your raw spectral data** via the Load Data tab
2. **Create and process HSI images** in the Hyperspectra tab
3. **Define ROI masks** using the ROI editing tools
4. **Generate averaged spectra** using the averaging functions
5. **Save everything** using the Save HSI State button
6. **Verify** the console shows ROIs and spectra were saved

### Loading Previously Saved Data

1. **Navigate to the Load Data tab**
2. **Click "Load HSI State"** button
3. **Select your .pkl file**
4. **Wait for loading to complete**
5. **Verify** ROIs and averaged spectra appear in the console log
6. **Switch to Hyperspectra tab** to continue analysis

---

## The Load Data Tab

### Purpose

The **Load Data** tab is the starting point for all SpecMap workflows. It provides two main functions:

1. **Loading raw spectral files** - Import new measurement data
2. **Loading saved HSI states** - Restore previous analysis sessions

### Tab Layout

The Load Data tab contains several sections:

#### 1. File Loading Section
- **Filename pattern entry**: Specify file naming pattern
- **File extension selector**: Choose file type (.txt, .csv, etc.)
- **Directory browser**: Navigate to data location
- **File list**: Preview files to be loaded

#### 2. Preprocessing Options
- **Background correction**: Select correction method
  - None
  - Single background file
  - Linear background correction
  - Each file has background
- **Cosmic ray removal**: Enable/disable and select algorithm
- **Power correction**: Apply if needed
- **Count threshold**: Set minimum signal level

#### 3. Save/Load State Section
Located at the bottom of the Load Data tab:

**Save HSI State:**
- Input field for save filename
- "Save HSI State" button
- Saves complete analysis including:
  - All loaded spectra
  - HSI images and fit results
  - ROI masks (with names)
  - Averaged spectra (all types)
  - Processing parameters
  - GUI settings

**Load HSI State:**
- Input field for load filename
- "Load HSI State" button or file browser
- Restores everything from saved .pkl file

### Using the Load Data Tab

#### Loading Raw Data (First Time)

1. **Set filename pattern**
   ```
   Example: HSI20240903_I01_*.txt
   ```

2. **Configure preprocessing**
   - Select background correction method
   - Enable cosmic ray removal if needed
   - Set appropriate threshold values

3. **Click "Load Files"**
   - Files are loaded and preprocessed
   - Progress shown in console
   - Switch to Hyperspectra tab to continue

#### Loading Saved State (Continuing Previous Work)

1. **Click "Browse" next to Load HSI State**
   - Or type the filename directly
   
2. **Select your .pkl file**
   ```
   Example: my_analysis_2024-02-02.pkl
   ```

3. **Click "Load HSI State"**
   - Complete state is restored
   - Console shows what was loaded:
     ```
     Successfully loaded XYMap state from: my_analysis.pkl
       - Loaded 50 spectra
       - Loaded 3 HSI images
       - Restored nan values in 3 HSI images
       - Loaded 2 ROI masks
         ROI names: ['bright_region', 'edge_region']
       - Restored nan values in 2 ROI masks
       ROI 'bright_region' dimensions validated: (10, 10)
       ROI 'edge_region' dimensions validated: (10, 10)
       - Loaded 3 averaged spectra
         Averaged spectra names: ['HSI0_PLB_avg', 'HSI0_Specdiff1_avg', 'HSI0_Specdiff2_avg']
       - WL axis: 800 points from 400.00 to 800.00 nm
     ```

4. **Switch to Hyperspectra tab**
   - All HSI images are available
   - ROI masks are ready to use
   - Averaged spectra appear in dropdown

---

## Saving Your Work

### When to Save

Save your work:
- **After defining ROIs** - Preserve your region definitions
- **After generating averaged spectra** - Keep analysis results
- **After fitting HSI data** - Save fit parameters and results
- **Periodically during long analysis sessions** - Prevent data loss
- **Before closing the application** - Save final results

### How to Save

#### Method 1: Using the GUI (Load Data Tab)

1. **Navigate to Load Data tab**

2. **Enter save filename**
   ```
   Example: HSI_analysis_2024-02-02.pkl
   ```
   - File extension .pkl is automatically added if not present
   - Use descriptive names for easy identification

3. **Click "Save HSI State"**

4. **Verify success**
   - Success dialog appears
   - Console shows save details:
     ```
     Successfully saved XYMap state to: HSI_analysis_2024-02-02.pkl
       - Saved 50 spectra
       - Saved 3 HSI images
       - Replaced nan values in 3 HSI images for optimization
       - Saved 2 ROI masks
         ROI names: ['bright_region', 'edge_region']
       - Replaced nan values in 2 ROI masks for optimization
       - Saved 3 averaged spectra
         Averaged spectra names: ['HSI0_PLB_avg', 'HSI0_Specdiff1_avg', 'HSI0_Specdiff2_avg']
     ```

5. **Note file location**
   - By default, files are saved in the working directory
   - Use full paths for specific locations

#### Method 2: Programmatic Save

```python
# Access the XYMap instance
nanomap = app.Nanomap

# Save state
success = nanomap.save_state('/path/to/save_file.pkl')

if success:
    print("Data saved successfully!")
```

### What Gets Saved

When you save HSI state, **everything** is preserved:

**Core Data**
- Individual spectrum objects
- 2D spectrum data matrix
- Wavelength axis (nm and eV)
- Background data

**HSI Images**
- All hyperspectral images (PMdict)
- Fit results and parameters
- Image metadata
- Pixel matrices with NaN optimization

**ROI Masks** 
- All defined ROI masks
- ROI names
- Mask arrays (with NaN compression)
- Dimensions validated on load

**Averaged Spectra** 
- All averaged spectra (disspecs)
- Multiple data types:
  - PL-BG (background-corrected)
  - First derivative
  - Second derivative
  - Normalized derivatives
- Spectrum metadata

**Processing Parameters**
- Wavelength range settings
- Count thresholds
- Grid parameters
- Cosmic ray removal settings
- Background correction settings

**GUI Settings**
- Colormap selection
- Font size
- Selected wavelength
- ROI usage flags

### File Size Optimization

SpecMap automatically optimizes save files:

- **NaN compression**: Replaces NaN values with unique numbers
- **Typical reduction**: 10x smaller file size
- **Faster save/load**: Improved performance
- **Automatic**: No user action required

**Example:**
```
Without optimization: 500 MB
With optimization:     50 MB
```

---

## Loading Saved Data

### Step-by-Step Guide

1. **Start SpecMap application**

2. **Navigate to Load Data tab**

3. **Locate your saved file**
   - Use the file browser button next to "Load HSI State"
   - Or type the full path directly

4. **Click "Load HSI State"**

5. **Monitor console output**
   ```
   Loading XYMap state from: my_analysis.pkl
   Successfully loaded XYMap state from: my_analysis.pkl
     - Loaded 50 spectra
     - Loaded 3 HSI images
     - Restored nan values in 3 HSI images
     - Loaded 2 ROI masks
       ROI names: ['bright_region', 'edge_region']
     - Restored nan values in 2 ROI masks
     ROI 'bright_region' dimensions validated: (10, 10)
     ROI 'edge_region' dimensions validated: (10, 10)
     - Loaded 3 averaged spectra
       Averaged spectra names: ['HSI0_PLB_avg', 'HSI0_Specdiff1_avg', 'HSI0_Specdiff2_avg']
     - WL axis: 800 points from 400.00 to 800.00 nm
   ```

6. **Success dialog appears**
   - Confirms successful load
   - Shows filename

7. **Switch to Hyperspectra tab**
   - GUI is rebuilt with loaded data
   - All functionality is restored

### What Happens During Load

The system automatically:

1. **Loads pickled data** from file
2. **Decompresses NaN values** in HSI images
3. **Decompresses NaN values** in ROI masks
4. **Validates ROI dimensions** against HSI data
5. **Restores averaged spectra** to dropdown menus
6. **Rebuilds GUI elements** with loaded data
7. **Updates all dropdowns** and selectors
8. **Logs validation results** to console

### Validation Checks

During loading, the system validates:

**File integrity**
- Pickle file can be opened
- Data structure is valid

**ROI dimensions**
- Each ROI mask matches HSI dimensions
- Warnings for mismatches:
  ```
  Warning: ROI 'old_roi' dimensions (8, 8) don't match HSI dimensions (10, 10)
  ```

**Data consistency**
- Wavelength arrays are consistent
- Spectral data is complete
- Metadata is preserved

### After Loading

Once loaded, you can immediately:

- **View HSI images** - Select from HSI dropdown
- **Use ROI masks** - Enable "Use ROI" checkboxes
- **Access averaged spectra** - Select from spectra dropdown
- **Continue analysis** - Fit data, create new ROIs, etc.
- **Export results** - CSV, images, etc.

---

## Working with ROIs

### Creating ROI Masks

1. **Navigate to Hyperspectra tab**

2. **Load or create an HSI image**

3. **Click "ROI Editing last Selection"**

4. **Draw your region**
   - Click to define vertices
   - Close the polygon to complete
   - Pixels inside = included in ROI
   - Pixels outside = excluded (NaN)

5. **Name your ROI**
   - Dialog prompts for name
   - Use descriptive names:
     ```
     Good: bright_region, edge_defect, sample_A
     Bad: roi1, test, x
     ```

6. **Save the complete state**
   - ROI masks are only preserved when you save
   - Click "Save HSI State" in Load Data tab

### Using ROI Masks

**For HSI Fitting:**
1. Check "Use ROI for fitting"
2. Select ROI from dropdown
3. Only pixels in ROI are fitted

**For HSI Creation:**
1. Check "Use ROI from fit param"
2. HSI uses only ROI pixels
3. Other pixels are NaN

**For Averaging:**
- Averaged spectra can use ROI-masked HSI
- Create HSI from fit param with ROI
- Then average that HSI

### ROI Persistence

**Saved automatically** with save_state()
**Loaded automatically** with load_state()
**Validated on load** - dimensions checked
**NaN compressed** - optimized file size
**Names preserved** - same ROI names after load

### ROI Best Practices

1. **Use descriptive names**
   - Include sample ID, region type, date
   - Example: `Sample_A_bright_spot_2024-02-02`

2. **Create ROIs before averaging**
   - Define regions first
   - Then create HSI from fit param with ROI
   - Then average to get ROI-specific spectra

3. **Save frequently**
   - ROIs are lost if you close without saving
   - Save after creating each important ROI

4. **Document ROI purpose**
   - Keep notes on what each ROI represents
   - Use consistent naming conventions

---

## Working with Averaged Spectra

### What Are Averaged Spectra?

Averaged spectra are single spectra created by averaging over all pixels in an HSI image. They reduce noise and reveal overall spectral characteristics.

### Available Data Types

1. **Spectrum (PL-BG)** - `PLB`
   - Raw intensity after background correction
   - Use for: Overall signal level, peak positions

2. **First derivative** - `Specdiff1`
   - Rate of change: d(PLB)/dλ
   - Use for: Transition identification, peak location

3. **Second derivative** - `Specdiff2`
   - Curvature: d²(PLB)/dλ²
   - Use for: Fine features, overlapping peaks

4. **Normalized first derivative** - `Specdiff1_norm`
   - Intensity-independent shape
   - Use for: Comparing spectral shapes

5. **Normalized second derivative** - `Specdiff2_norm`
   - Enhanced feature detection
   - Use for: Subtle feature identification

### Creating Averaged Spectra

#### Method 1: Single Data Type (GUI)

1. **Select HSI** from dropdown
2. **Select data type** from "Select Data Set" dropdown
3. **Click "average hsi to spectrum"**
4. **Result**:
   - New spectrum added to spectra list
   - Named: `{HSI_name}_{datatype}_avg`
   - Example: `HSI0_PLB_avg`

#### Method 2: All Data Types at Once

1. **Select HSI** from dropdown
2. **Click "Export All Averaged Spectra"**
3. **Choose save location**
4. **Result**:
   - All 5 data types generated
   - All added to spectra list
   - Exported to CSV file
   - Names: `HSI0_PLB_avg`, `HSI0_Specdiff1_avg`, etc.

### Viewing Averaged Spectra

After creating averaged spectra:

1. **Select from dropdown**
   - Spectra dropdown shows all averaged spectra
   - Format: `{HSI}_{type}_avg`

2. **Plot appears**
   - Wavelength vs. intensity
   - Interactive matplotlib plot
   - Can zoom, pan, save image

3. **Access data**
   - Right-click for options
   - Export individual spectrum
   - Delete if not needed

### Averaged Spectra Persistence

**Saved automatically** with save_state()
**Loaded automatically** with load_state()
**Names preserved** - same names after load
**Metadata preserved** - parent HSI, data type
**Derivatives preserved** - d1, d2 arrays saved

When you load a saved state:
```
- Loaded 3 averaged spectra
  Averaged spectra names: ['HSI0_PLB_avg', 'HSI0_Specdiff1_avg', 'HSI0_Specdiff2_avg']
```

All averaged spectra are immediately available in the dropdown.

### Exporting Averaged Spectra

**Individual spectrum:**
1. Select spectrum from dropdown
2. Right-click → Save
3. Saves as tab-delimited text file

**All averaged spectra:**
1. Click "Export All Averaged Spectra"
2. Choose filename
3. Creates CSV with all data types in columns:
   ```
   Wavelength (nm),Spectrum (PL-BG),first derivative,second derivative,...
   400.0,1234.5,12.3,-0.5,...
   401.0,1245.6,13.1,-0.6,...
   ```

**HSI with spectra:**
1. Select HSI
2. Click "Export HSI with Spectra"
3. Creates two files:
   - `{name}_matrix.csv` - HSI pixel data
   - `{name}_avg_spectra.csv` - Associated averaged spectra

---

## Complete Workflow Examples

### Example 1: First-Time Analysis with ROIs

**Scenario:** You have new HSI measurement data and want to analyze specific regions.

**Steps:**

1. **Load Data tab → Load raw files**
   ```
   - Set filename pattern: HSI20240903_I01_*.txt
   - Configure preprocessing
   - Click "Load Files"
   ```

2. **Hyperspectra tab → Create HSI**
   ```
   - Select wavelength
   - Click "Create HSI image"
   - Image appears
   ```

3. **Hyperspectra tab → Define ROI**
   ```
   - Click "ROI Editing last Selection"
   - Draw bright region
   - Name it "bright_spot"
   - Draw another ROI
   - Name it "edge_region"
   ```

4. **Hyperspectra tab → Generate averaged spectra**
   ```
   - Select HSI from dropdown
   - Click "Export All Averaged Spectra"
   - Choose save location: "HSI0_all_spectra.csv"
   - 5 spectra types generated
   ```

5. **Load Data tab → Save everything**
   ```
   - Enter filename: "HSI0_analysis_2024-02-02.pkl"
   - Click "Save HSI State"
   - Verify console shows:
     * Saved 2 ROI masks
     * Saved 5 averaged spectra
   ```

6. **Done!**
   - All work preserved
   - Can close SpecMap
   - Resume later by loading the .pkl file

### Example 2: Continuing Previous Analysis

**Scenario:** You saved your work yesterday and want to continue today.

**Steps:**

1. **Start SpecMap**

2. **Load Data tab → Load saved state**
   ```
   - Click "Browse" next to "Load HSI State"
   - Navigate to: "HSI0_analysis_2024-02-02.pkl"
   - Click "Load HSI State"
   - Wait for loading...
   ```

3. **Verify in console**
   ```
   Successfully loaded XYMap state from: HSI0_analysis_2024-02-02.pkl
     - Loaded 50 spectra
     - Loaded 3 HSI images
     - Loaded 2 ROI masks
       ROI names: ['bright_spot', 'edge_region']
     - Loaded 5 averaged spectra
   ```

4. **Switch to Hyperspectra tab**
   ```
   - All HSI images available in dropdown
   - ROI masks ready to use
   - Averaged spectra in spectra dropdown
   ```

5. **Continue analysis**
   ```
   - Create new ROIs
   - Fit more HSI images
   - Generate more averaged spectra
   - Export results
   ```

6. **Save when done**
   ```
   - Load Data tab → "Save HSI State"
   - Use same filename or new one
   - Everything updated
   ```

### Example 3: ROI-Specific Averaged Spectra

**Scenario:** You want averaged spectra for only a specific region.

**Steps:**

1. **Load or create your data**

2. **Fit HSI image**
   ```
   - Select wavelength range
   - Configure fitting parameters
   - Click "Fit all spectra"
   ```

3. **Create ROI**
   ```
   - Draw ROI on HSI plot
   - Name it "region_of_interest"
   ```

4. **Create ROI-masked HSI**
   ```
   - Check "Use ROI from fit param"
   - Select "region_of_interest" from ROI dropdown
   - Click "Create HSI from fit param"
   - New HSI created with only ROI pixels
   ```

5. **Average ROI-masked HSI**
   ```
   - Select the new ROI-masked HSI
   - Click "Export All Averaged Spectra"
   - Result: averaged spectra from ROI only
   ```

6. **Save**
   ```
   - Load Data tab → "Save HSI State"
   - ROI and ROI-specific spectra saved
   ```

---

## Troubleshooting

### Issue: ROIs Not Appearing After Load

**Symptoms:**
- Load completes successfully
- Console shows ROIs were loaded
- But can't see ROIs in dropdown

**Solutions:**
1. Switch to Hyperspectra tab - GUI might need refresh
2. Check console for dimension warnings
3. Verify you're looking in correct HSI
4. Try rebuilding GUI: restart and reload

### Issue: Averaged Spectra Missing After Load

**Symptoms:**
- Load completes
- Console shows "Loaded 0 averaged spectra"
- Spectra dropdown is empty

**Causes:**
- Spectra were never generated before saving
- Old save file without disspecs support

**Solutions:**
1. Generate spectra again using "Export All Averaged Spectra"
2. Re-save the state
3. If using old file, it's expected - just regenerate

### Issue: ROI Dimension Mismatch Warning

**Symptoms:**
```
Warning: ROI 'old_roi' dimensions (8, 8) don't match HSI dimensions (10, 10)
```

**Causes:**
- ROI created with different HSI size
- HSI was recreated with different dimensions
- Data from different measurement

**Solutions:**
1. ROI can still load but might not work correctly
2. Recreate ROI for current HSI dimensions
3. Or use the original HSI it was created with

### Issue: Large Save File Size

**Symptoms:**
- .pkl file is hundreds of MB
- Save takes a long time
- Load is slow

**Causes:**
- Many HSI images with lots of data
- Very large pixel matrices

**Solutions:**
1. **Normal** - optimization already applied
2. File size reflects amount of data
3. NaN compression already reducing by ~10x
4. Consider:
   - Saving only essential HSI images
   - Deleting intermediate results before saving
   - Using external compression (zip, gzip)

### Issue: Cannot Load Old Save Files

**Symptoms:**
- Error when loading .pkl file
- Exception in console
- Load fails

**Causes:**
- Incompatible Python version
- Corrupted file
- Very old SpecMap version

**Solutions:**
1. Try loading in same Python version that saved
2. Check file isn't corrupted (size, modified date)
3. Contact support with error message
4. Re-analyze from raw data if necessary

### Issue: Spectra Dropdown Not Updating

**Symptoms:**
- Generate averaged spectra
- Console shows "Created averaged spectrum"
- But dropdown doesn't show new spectrum

**Causes:**
- GUI not refreshed
- Focus on wrong element

**Solutions:**
1. Click on dropdown to refresh
2. Switch tabs and back
3. Check console - verify spectra was actually created
4. Restart if persistent

---

## Summary

### Key Takeaways

**Load Data tab** is your starting point for both new data and saved states

**Save frequently** to preserve ROIs and averaged spectra

**ROI masks are automatically saved** with save_state()

**Averaged spectra are automatically saved** with save_state()

**Loading is automatic** - just load the .pkl file and continue working

**File size is optimized** - NaN compression applied automatically

**Everything is preserved** - data, ROIs, spectra, settings, parameters

### Recommended Workflow

1. **Session Start**
   - Load Data tab
   - Either load raw files OR load saved state

2. **Analysis**
   - Hyperspectra tab
   - Create HSI images
   - Define ROIs
   - Generate averaged spectra
   - Fit and analyze

3. **Save Regularly**
   - Load Data tab
   - Save HSI State
   - Verify in console

4. **Session End**
   - Final save
   - Note filename and location
   - Close application

5. **Next Session**
   - Load Data tab
   - Load HSI State
   - Continue analysis

### Best Practices

1. **Descriptive filenames**
   ```
   Good: HSI_sample_A_550nm_2024-02-02.pkl
   Bad: save1.pkl
   ```

2. **Descriptive ROI names**
   ```
   Good: bright_spot_center, edge_defect_3
   Bad: roi1, test
   ```

3. **Save before closing**
   - Always save final state
   - Don't rely on autosave
   - Verify save success in console

4. **Keep backups**
   - Save different versions
   - Use dates in filenames
   - Keep copies of important analyses

5. **Document your work**
   - Keep notes separate from SpecMap
   - Record what ROIs represent
   - Note analysis parameters

---

## Additional Resources

- **Main Documentation**: `DATA_SAVE_LOAD_ENHANCEMENT.md`
- **Technical Details**: `ROI_COMPRESSION_IMPLEMENTATION.md`
- **API Reference**: `SAVE_LOAD_FIT_RESULTS.md`
- **Program Structure**: `PROGRAM_STRUCTURE.md`

---

**Document Version:** 1.0  
**Last Updated:** 2024-02-02  
**For SpecMap Version:** 9.x and later
