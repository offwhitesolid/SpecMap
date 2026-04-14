# Quick Reference: ROI and Averaged Spectra Save/Load

##  Quick Start

### Saving Your Work
1. Go to **Load Data** tab
2. Enter filename in "Save HSI State" field
3. Click **"Save HSI State"** button
4. Done! ROIs and spectra are saved.

### Loading Your Work
1. Go to **Load Data** tab
2. Click **"Load HSI State"** or use file browser
3. Select your `.pkl` file
4. Done! Everything is restored.

---

##  What Gets Saved

When you save HSI state:

All spectral data  
All HSI images  
**All ROI masks** (with names)  
**All averaged spectra** (all types)  
Fit results and parameters  
Processing settings  
GUI configuration  

---

##  ROI Workflow

### Creating ROIs

1. **Hyperspectra tab** → Select HSI
2. Click **"ROI Editing last Selection"**
3. Draw region on plot
4. Name your ROI (be descriptive!)
5. **Load Data tab** → **Save HSI State**

### Using Loaded ROIs

After loading a `.pkl` file:
- ROIs appear in ROI dropdown
- Check "Use ROI" to apply
- All ROI names preserved
- Ready to use immediately

---

##  Averaged Spectra Workflow

### Creating Averaged Spectra

**Method 1: Single Type**
1. Select HSI from dropdown
2. Select data type (PLB, Specdiff1, etc.)
3. Click **"average hsi to spectrum"**

**Method 2: All Types at Once** Recommended
1. Select HSI from dropdown
2. Click **"Export All Averaged Spectra"**
3. All 5 types generated instantly

### Using Loaded Spectra

After loading a `.pkl` file:
- Spectra appear in spectra dropdown
- Names format: `HSI0_PLB_avg`, `HSI0_Specdiff1_avg`, etc.
- Click to view and analyze
- Ready to export or process

---

##  File Locations

### Default Save Location
- Current working directory
- Where you launched SpecMap

### Recommended File Naming
```
Good Examples:
  HSI_Sample_A_550nm_2024-02-02.pkl
  Analysis_Bright_Spot_2024-02-02.pkl
  
Avoid:
  save.pkl
  test1.pkl
  data.pkl
```

---

## Verification Checklist

### After Saving
Check console for:
```
Successfully saved XYMap state to: filename.pkl
  - Saved X spectra
  - Saved Y HSI images
  - Saved Z ROI masks
    ROI names: [...]
  - Saved N averaged spectra
    Averaged spectra names: [...]
```

### After Loading
Check console for:
```
Successfully loaded XYMap state from: filename.pkl
  - Loaded X spectra
  - Loaded Y HSI images
  - Loaded Z ROI masks
    ROI names: [...]
  ROI dimensions validated
  - Loaded N averaged spectra
    Averaged spectra names: [...]
```

---

##  Data Types Available

### Averaged Spectra Types

1. **PLB** - Background-corrected spectrum  
   *Use for: Peak positions, overall signal*

2. **Specdiff1** - First derivative  
   *Use for: Transitions, peak identification*

3. **Specdiff2** - Second derivative  
   *Use for: Fine features, overlapping peaks*

4. **Specdiff1_norm** - Normalized first derivative  
   *Use for: Shape comparison*

5. **Specdiff2_norm** - Normalized second derivative  
   *Use for: Feature detection*

All types are generated with **"Export All Averaged Spectra"**

---

##  Common Tasks

### Task: Start New Analysis
```
1. Load Data tab
2. Load raw files (.txt)
3. Hyperspectra tab → Create HSI
4. Define ROIs
5. Generate averaged spectra
6. Load Data tab → Save HSI State
```

### Task: Continue Previous Analysis
```
1. Load Data tab
2. Load HSI State → Select .pkl file
3. Hyperspectra tab → Continue work
4. Save when done
```

### Task: Export Everything
```
1. For each HSI:
   - Export All Averaged Spectra (CSV)
   - Export HSI with Spectra (2 files)
2. Save HSI State (.pkl for SpecMap)
3. Now you have both analysis and export
```

---

##  Important Notes

### ROI Names
- Use descriptive names: `bright_spot_center`
- Avoid generic: `roi1`, `test`
- Names are preserved exactly

### Save Frequency
- Save after creating important ROIs
- Save after generating spectra
- Save before closing SpecMap
- No autosave - manual save required

### File Size
- Automatically optimized (10x smaller)
- NaN compression applied
- Typical size: 50-500 MB
- Depends on data amount

---

##  Troubleshooting

### ROIs Not Visible After Load
- Check console - were they loaded?
- Switch to Hyperspectra tab
- Look in ROI dropdown

### Spectra Not in Dropdown
- Check console - were they loaded?
- Were they generated before saving?
- Click dropdown to refresh

### Dimension Mismatch Warning
```
Warning: ROI dimensions don't match HSI
```
- ROI from different HSI size
- Can still load but may not work
- Create new ROI for current HSI

---

##  More Information

Detailed documentation:
- `GUI_SAVE_LOAD_WORKFLOW.md` - Complete GUI guide
- `DATA_SAVE_LOAD_ENHANCEMENT.md` - Technical details
- `ROI_COMPRESSION_IMPLEMENTATION.md` - How compression works

---

## Pro Tips

1. **Name things well** - Future you will thank you
2. **Save often** - After each major step
3. **Keep backups** - Use dated filenames
4. **Verify saves** - Check console output
5. **Test loads** - Reload to verify before closing

---

**Quick Reference Version:** 1.0  
**Last Updated:** 2024-02-02
