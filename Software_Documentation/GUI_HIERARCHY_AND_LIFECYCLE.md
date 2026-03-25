# SpecMap GUI Hierarchy & Lifecycle Documentation

**Version:** 1.0  
**Last Updated:** November 28, 2025  
**Purpose:** Tkinter root element propagation, error handling directions, and cleanup lifecycle

---

## Table of Contents
1. [GUI Hierarchy Tree](#gui-hierarchy-tree)
2. [Root Instance Propagation](#root-instance-propagation)
3. [Error Handling Flow (Directional)](#error-handling-flow-directional)
4. [Cleanup & Closing Flow (Directional)](#cleanup--closing-flow-directional)
5. [Potential Error Scenarios](#potential-error-scenarios)
6. [Best Practices & Recommendations](#best-practices--recommendations)

---

## GUI Hierarchy Tree

### Visual Representation with Ownership

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ROOT: tk.Tk()                                                  ┃
┃ Created: main9.py line 949: root = tk.Tk()                    ┃
┃ Owner: __main__ scope                                          ┃
┃ Lifecycle: Lives entire application runtime                   ┃
┃ Cleanup: root.destroy() called by pressclose()                ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
    │
    ├─▶ [PASSED TO]
    │
    ┌───┴──────────────────────────────────────────────────────────┐
    │ FileProcessorApp.__init__(root, defaults)                    │
    │ Stored: self.root = root                                     │
    │ Line: main9.py line 22                                       │
    └──┬───────────────────────────────────────────────────────────┘
       │
       ├─▶ [CREATES DIRECT CHILDREN]
       │
       ├──┬─▶ tk.Menu(root) → menu_bar
       │  │   ├─ Owner: FileProcessorApp
       │  │   ├─ Parent: root (attached via root.config(menu=...))
       │  │   └─ Cleanup: Automatic when root destroyed
       │  │
       │  └─▶ deflib.create_menu(self.root, menu_bar)
       │      └─ Adds menu items to menu_bar
       │
       └──┬─▶ ttk.Notebook(self.root) → self.notebook
          │   ├─ Owner: FileProcessorApp.notebook
          │   ├─ Parent: root
          │   ├─ Line: main9.py line 62
          │   └─ Cleanup: Automatic when root destroyed
          │
          └─▶ [CREATES NOTEBOOK TABS]
              │
              ├─────────────────────────────────────────────────────┐
              │ Tab 1: 'Load Data'                                  │
              │ ┌──────────────────────────────────────────────────┐│
              │ │ ttk.Frame(self.notebook)                         ││
              │ │ Stored: self.nodeframes['Load Data']             ││
              │ │ Owner: FileProcessorApp.nodeframes               ││
              │ │ Parent: self.notebook                            ││
              │ │ Cleanup: Automatic when notebook destroyed       ││
              │ └──────────────────────────────────────────────────┘│
              │      │                                               │
              │      ├─▶ self.open_frame → tk.Frame                 │
              │      │   ├─ Parent: nodeframes['Load Data']         │
              │      │   ├─ Contains: SpecMap load controls         │
              │      │   └─ Children:                               │
              │      │       ├─ self.loadframe → tk.Frame           │
              │      │       │   ├─ self.bgframe → tk.Frame         │
              │      │       │   │   └─ Checkbuttons (BG options)   │
              │      │       │   └─ self.cosmicframe → tk.Frame     │
              │      │       │       └─ Cosmic removal controls     │
              │      │       └─ self.multiple_HSIs_inp_frame        │
              │      │           └─ Multi-HSI processing controls   │
              │      │                                               │
              │      ├─▶ self.claraloadframe → tk.Frame             │
              │      │   ├─ Parent: nodeframes['Load Data']         │
              │      │   └─ Contains: Clara image load controls     │
              │      │                                               │
              │      ├─▶ self.saveframe → tk.Frame                  │
              │      │   ├─ Parent: nodeframes['Load Data']         │
              │      │   └─ Contains: Save/Load HSI state controls  │
              │      │                                               │
              │      ├─▶ self.newtonframe → tk.Frame                │
              │      │   ├─ Parent: nodeframes['Load Data']         │
              │      │   └─ Contains: Newton spectrum controls      │
              │      │                                               │
              │      └─▶ self.tcspcframe → tk.Frame                 │
              │          ├─ Parent: nodeframes['Load Data']         │
              │          └─ Contains: TCSPC data controls           │
              │                                                      │
              ├─────────────────────────────────────────────────────┘
              │
              ├─────────────────────────────────────────────────────┐
              │ Tab 2: 'Hyperspectra'                               │
              │ ┌──────────────────────────────────────────────────┐│
              │ │ ttk.Frame(self.notebook)                         ││
              │ │ Stored: self.nodeframes['Hyperspectra']          ││
              │ └──────────────────────────────────────────────────┘│
              │      │                                               │
              │      ├─▶ self.cmapframe → tk.Frame                  │
              │      │   ├─ Parent: nodeframes['Hyperspectra']      │
              │      │   ├─ Owner: FileProcessorApp.cmapframe       │
              │      │   ├─ Line: main9.py line 37                  │
              │      │   ├─ Purpose: Colormap visualization         │
              │      │   ├─ PASSED TO: XYMap.__init__()             │
              │      │   │   └─ Stored: XYMap.cmapframe             │
              │      │   ├─ Cleanup: self.cmapframe.destroy()       │
              │      │   │   Called: spec_loadfiles() before reload │
              │      │   └─ Children:                               │
              │      │       ├─ minmaxspecframe → tk.Frame          │
              │      │       │   ├─ Parent: cmapframe               │
              │      │       │   ├─ Owner: XYMap                    │
              │      │       │   ├─ Created: buildMinMaxSpec()      │
              │      │       │   └─ Children:                       │
              │      │       │       ├─ WLselframe → tk.Frame       │
              │      │       │       │   ├─ WLselection (Combobox)  │
              │      │       │       │   └─ WL_sel_button           │
              │      │       │       ├─ cmapselframe → tk.Frame     │
              │      │       │       │   ├─ cmapselection (Combobox)│
              │      │       │       │   └─ cmap_sel_button         │
              │      │       │       └─ fontframe → tk.Frame        │
              │      │       │           ├─ CMFont (Entry)          │
              │      │       │           └─ setfont_button          │
              │      │       │                                       │
              │      │       └─ PMframe → tk.Frame                  │
              │      │           ├─ Parent: cmapframe               │
              │      │           ├─ Owner: XYMap                    │
              │      │           ├─ Created: build_PixMatrix_frame()│
              │      │           └─ Children:                       │
              │      │               ├─ PMselframe → tk.Frame       │
              │      │               │   ├─ PMselection (Combobox)  │
              │      │               │   └─ PM_sel_button           │
              │      │               ├─ PMfitselframe → tk.Frame    │
              │      │               │   ├─ PMfitselection (Combobox)│
              │      │               │   ├─ useROI_button           │
              │      │               │   └─ PMfit_sel_button        │
              │      │               └─ PMcorrframe → tk.Frame      │
              │      │                   ├─ PMcorrselgui (Combobox) │
              │      │                   └─ PMcorr_button           │
              │      │                                               │
              │      └─▶ self.specframe → tk.Frame                  │
              │          ├─ Parent: nodeframes['Hyperspectra']      │
              │          ├─ Owner: FileProcessorApp.specframe       │
              │          ├─ Line: main9.py line 39                  │
              │          ├─ Purpose: Spectrum controls & plots      │
              │          ├─ PASSED TO: XYMap.__init__()             │
              │          │   └─ Stored: XYMap.specframe             │
              │          ├─ Cleanup: self.specframe.destroy()       │
              │          │   Called: spec_loadfiles() before reload │
              │          └─ Children:                               │
              │              ├─ plotframe → tk.Frame                │
              │              │   ├─ Parent: specframe               │
              │              │   ├─ Owner: XYMap                    │
              │              │   ├─ Created: build_button_frame()   │
              │              │   └─ Children:                       │
              │              │       ├─ b1 (Plot button)            │
              │              │       ├─ b3 (Plot Line button)       │
              │              │       ├─ b4 (Save Spec button)       │
              │              │       ├─ b5 (Plot AVspec button)     │
              │              │       ├─ spectralminentry (Entry)    │
              │              │       └─ spectralmaxentry (Entry)    │
              │              │                                       │
              │              ├─ fitframe → tk.Frame                 │
              │              │   ├─ Parent: specframe               │
              │              │   ├─ Owner: XYMap                    │
              │              │   ├─ Created: build_button_frame()   │
              │              │   └─ Children:                       │
              │              │       ├─ funcselgui (Combobox)       │
              │              │       ├─ b2 (Fit button)             │
              │              │       ├─ pstartentry (Entry)         │
              │              │       ├─ pendentry (Entry)           │
              │              │       ├─ chkplotfit (Checkbutton)    │
              │              │       └─ chkmanualfit (Checkbutton)  │
              │              │                                       │
              │              └─ ROI_frame → tk.Frame                │
              │                  ├─ Parent: specframe               │
              │                  ├─ Owner: XYMap                    │
              │                  ├─ Created: build_roi_frame()      │
              │                  └─ Children:                       │
              │                      ├─ roiselgui (Combobox)        │
              │                      ├─ HSI_fit_useROI_button       │
              │                      ├─ createroi_button            │
              │                      ├─ plotroi_button              │
              │                      ├─ deleteroi_button            │
              │                      └─ plot_options_frame          │
              │                                                      │
              ├─────────────────────────────────────────────────────┘
              │
              ├─────────────────────────────────────────────────────┐
              │ Tab 3: 'HSI Plot'                                   │
              │ ┌──────────────────────────────────────────────────┐│
              │ │ ttk.Frame(self.notebook)                         ││
              │ │ Stored: self.nodeframes['HSI Plot']              ││
              │ └──────────────────────────────────────────────────┘│
              │      │                                               │
              │      └─▶ PASSED TO: Exportframe.__init__()          │
              │          └─ export_frame → tk.Frame                 │
              │              ├─ Parent: nodeframes['HSI Plot']      │
              │              ├─ Owner: Exportframe.export_frame     │
              │              ├─ Created: buildframe()               │
              │              ├─ Cleanup: Automatic when parent dies │
              │              └─ Children:                           │
              │                  └─ save_button (Export button)     │
              │                                                      │
              ├─────────────────────────────────────────────────────┘
              │
              ├─────────────────────────────────────────────────────┐
              │ Tab 4: 'Clara Image'                                │
              │ ┌──────────────────────────────────────────────────┐│
              │ │ ttk.Frame(self.notebook)                         ││
              │ │ Stored: self.nodeframes['Clara Image']           ││
              │ └──────────────────────────────────────────────────┘│
              │      │                                               │
              │      └─▶ PASSED TO: imageprocessor.__init__()       │
              │          └─ image_frame → tk.Frame                  │
              │              ├─ Parent: nodeframes['Clara Image']   │
              │              ├─ Owner: imageprocessor.image_frame   │
              │              ├─ Created: On cl_loadfiles()          │
              │              ├─ Cleanup: Implicit, no explicit del  │
              │              └─ Children:                           │
              │                  ├─ plotimage (Button)              │
              │                  ├─ fitg2Dbutton (Button)           │
              │                  ├─ plotfitbutton (Button)          │
              │                  └─ area (Button)                   │
              │                                                      │
              ├─────────────────────────────────────────────────────┘
              │
              ├─────────────────────────────────────────────────────┐
              │ Tab 5: 'Newton Spectrum'                            │
              │ ┌──────────────────────────────────────────────────┐│
              │ │ ttk.Frame(self.notebook)                         ││
              │ │ Stored: self.nodeframes['Newton Spectrum']       ││
              │ └──────────────────────────────────────────────────┘│
              │      │                                               │
              │      └─▶ PASSED TO: newtonspecopener.__init__()     │
              │          └─ openframe → tk.Frame                    │
              │              ├─ Parent: nodeframes['Newton Spectrum']│
              │              ├─ Owner: newtonspecopener.openframe   │
              │              ├─ Created: On newtonloadfiles()       │
              │              ├─ Cleanup: Implicit, no explicit del  │
              │              └─ Children: (controls for Newton spec)│
              │                                                      │
              ├─────────────────────────────────────────────────────┘
              │
              ├─────────────────────────────────────────────────────┐
              │ Tab 6: 'TCSPC'                                      │
              │ ┌──────────────────────────────────────────────────┐│
              │ │ ttk.Frame(self.notebook)                         ││
              │ │ Stored: self.nodeframes['TCSPC']                 ││
              │ └──────────────────────────────────────────────────┘│
              │      │                                               │
              │      └─▶ PASSED TO: TCSPCprocessor.__init__()       │
              │          └─ plotframe → tk.Frame                    │
              │              ├─ Parent: nodeframes['TCSPC']         │
              │              ├─ Owner: TCSPCprocessor.plotframe     │
              │              ├─ Created: build_frame()              │
              │              ├─ Cleanup: Automatic when parent dies │
              │              └─ Children:                           │
              │                  ├─ load_button                     │
              │                  ├─ plot_tres_linear_button         │
              │                  └─ plot_tres_log_button            │
              │                                                      │
              ├─────────────────────────────────────────────────────┘
              │
              └─────────────────────────────────────────────────────┐
                Tab 7: 'HSI File Sorter'                            │
                ┌──────────────────────────────────────────────────┐│
                │ ttk.Frame(self.notebook)                         ││
                │ Stored: self.nodeframes['HSI File Sorter']       ││
                └──────────────────────────────────────────────────┘│
                     │                                               │
                     └─▶ PASSED TO: specfilesorter.__init__()       │
                         └─ sortframe → ttk.LabelFrame              │
                             ├─ Parent: nodeframes['HSI File Sorter']│
                             ├─ Owner: specfilesorter.sortframe     │
                             ├─ Created: buildGUI()                 │
                             ├─ Cleanup: Automatic when parent dies │
                             └─ Children:                           │
                                 ├─ left → tk.Frame                 │
                                 │   ├─ Input entries & buttons     │
                                 │   ├─ btnframe → tk.Frame         │
                                 │   │   └─ Control buttons         │
                                 │   └─ progressfame → tk.Frame     │
                                 │       └─ progress (Progressbar)  │
                                 └─ right → tk.Frame                │
                                     ├─ tree (Treeview)             │
                                     └─ vsb (Scrollbar)             │
                                                                     │
                ─────────────────────────────────────────────────────┘
```

---

## Root Instance Propagation

### Flow Chart: How Root is Passed Down

```
┌─────────────────────────────────────────────────────────────────┐
│ START: main9.py __main__ block                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │ root = tk.Tk() │
                    └────────┬───────┘
                             │
                             ▼
        ┌────────────────────────────────────────────┐
        │ app = FileProcessorApp(root, defaults)     │
        │ Method: __init__(self, root, defaults)     │
        │ Action: self.root = root                   │
        │ Storage: Instance variable                 │
        └────────────────┬───────────────────────────┘
                         │
                         ├─────────────────────┐
                         │                     │
                         ▼                     ▼
        ┌────────────────────────┐   ┌────────────────────────┐
        │ tk.Menu(root)          │   │ ttk.Notebook(self.root)│
        │ Direct parent: root    │   │ Direct parent: root    │
        │ Storage: menu_bar      │   │ Storage: self.notebook │
        └────────────────────────┘   └───────┬────────────────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                        │
                    ▼                        ▼                        ▼
        ┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
        │ ttk.Frame         │   │ ttk.Frame         │   │ ttk.Frame         │
        │ (notebook tab)    │   │ (notebook tab)    │   │ (notebook tab)    │
        │ Parent: notebook  │   │ Parent: notebook  │   │ Parent: notebook  │
        │ Storage:          │   │ Storage:          │   │ Storage:          │
        │ nodeframes[...]   │   │ nodeframes[...]   │   │ nodeframes[...]   │
        └─────────┬─────────┘   └─────────┬─────────┘   └─────────┬─────────┘
                  │                       │                       │
                  ▼                       ▼                       ▼
        ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
        │ tk.Frame        │   │ tk.Frame        │   │ tk.Frame        │
        │ (controls)      │   │ (controls)      │   │ (controls)      │
        │ Parent:         │   │ Parent:         │   │ Parent:         │
        │ nodeframes[...] │   │ nodeframes[...] │   │ nodeframes[...] │
        └─────────────────┘   └─────────────────┘   └─────────────────┘

SPECIAL CASE: Frames passed to external classes
        
        nodeframes['Hyperspectra']
                  │
                  ├──▶ cmapframe = tk.Frame(nodeframes['Hyperspectra'], ...)
                  │    └─ PASSED TO: XYMap.__init__(... cmapframe ...)
                  │       └─ Stored: XYMap.cmapframe
                  │          └─ Used by: buildMinMaxSpec(), build_PixMatrix_frame()
                  │
                  └──▶ specframe = tk.Frame(nodeframes['Hyperspectra'], ...)
                       └─ PASSED TO: XYMap.__init__(... specframe ...)
                          └─ Stored: XYMap.specframe
                             └─ Used by: build_button_frame(), build_roi_frame()
```

### Propagation Rules

1. **Direct Passing**: `root` is passed as constructor argument
   - Example: `FileProcessorApp(root, defaults)`
   
2. **Reference Storage**: Components store `root` for later use
   - Example: `self.root = root` in FileProcessorApp
   
3. **Implicit Parent**: Widgets inherit parent from constructor
   - Example: `tk.Frame(parent_frame, ...)` → parent is parent_frame
   
4. **Frame Delegation**: Frame references passed to subclasses
   - Example: `XYMap(..., cmapframe, specframe, ...)`
   
5. **No Direct Root Access**: Subclasses (XYMap, Exportframe, etc.) never access root directly
   - They only receive frame references to build inside

---

## Error Handling Flow (Directional)

### Error Propagation Direction: ⬆ UPWARD (Child → Parent → Root)

```
┌─────────────────────────────────────────────────────────────────┐
│ LEVEL 0: Root Window (tk.Tk)                                    │
│ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ │
│ ┃ Error Handler: pressclose()                                 ┃ │
│ ┃ Trigger: WM_DELETE_WINDOW protocol                          ┃ │
│ ┃ Action:                                                     ┃ │
│ ┃   1. Set all threads to daemon                              ┃ │
│ ┃   2. Call root.destroy()                                    ┃ │
│ ┃   3. Call app.on_closing()                                  ┃ │
│ ┃ Error Recovery: Force exit, terminate all children          ┃ │
│ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ │
└──────────────────────────────┬──────────────────────────────────┘
                               ▲ Errors propagate up
                               │
┌──────────────────────────────┴──────────────────────────────────┐
│ LEVEL 1: FileProcessorApp                                       │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Error Sources:                                              │ │
│ │ ✗ init_spec_loadfiles() → Folder not found                  │ │
│ │ ✗ spec_loadfiles() → No files matching pattern              │ │
│ │ ✗ saveNanomap() → File write permission denied              │ │
│ │ ✗ loadhsisaved() → Corrupted pickle file                    │ │
│ │ ✗ cl_loadfiles() → Image file not found                     │ │
│ │ ✗ newtonloadfiles() → Invalid spectrum format               │ │
│ │ ✗ tcspcloadfiles() → Directory not accessible               │ │
│ │                                                             │ │
│ │ Error Handling Strategy:                                    │ │
│ │ 1. try/except blocks around file operations                 │ │
│ │ 2. Validation checks before calling methods                 │ │
│ │ 3. Print to console: print("Error: message")                │ │
│ │ 4. User notification: messagebox.showerror(title, msg)      │ │
│ │ 5. Early return on error (prevents propagation)             │ │
│ │                                                             │ │
│ │ Error Recovery Actions:                                     │ │
│ │ → Empty folder: Print message, return early                 │ │
│ │ → Invalid file: Skip file, continue processing              │ │
│ │ → Save failure: Show error dialog, keep app running         │ │
│ │ → Load failure: Show error dialog, keep app running         │ │
│ └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────────┬──────────────────────────────────┘
                               ▲ Errors propagate up
                               │
┌──────────────────────────────┴──────────────────────────────────┐
│ LEVEL 2: XYMap (lib9.py)                                        │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ Error Sources:                                               │ │
│ │ ✗ loadfiles() → Thread pool exception                       │ │
│ │ ✗ on_spec_chosen() → Invalid spectrum index                 │ │
│ │ ✗ make_fit() → scipy.optimize.curve_fit failure             │ │
│ │ ✗ save_state() → pickle.dump() error                        │ │
│ │ ✗ load_state() → pickle.load() error                        │ │
│ │ ✗ PM_selected() → KeyError (invalid PMdict key)             │ │
│ │ ✗ PMfromfitparams() → Fit data not available                │ │
│ │ ✗ WL_selected() → Empty PMdict                              │ │
│ │ ✗ buildandPlotIntCmap() → Empty specs list                  │ │
│ │                                                               │ │
│ │ Error Handling Strategy:                                     │ │
│ │ 1. try/except with traceback.print_exc()                    │ │
│ │ 2. Return False on failure (save/load methods)              │ │
│ │ 3. Print detailed error messages                            │ │
│ │ 4. Continue processing (skip failed items)                  │ │
│ │                                                               │ │
│ │ Error Propagation:                                           │ │
│ │ → loadfiles() error: Caught, logged, continue with loaded   │ │
│ │ → save_state() error: Return False → FileProcessorApp shows │ │
│ │ → load_state() error: Return False → FileProcessorApp shows │ │
│ │ → fit error: Caught, print message, don't store fit         │ │
│ │ → GUI error: Caught, widget remains disabled                │ │
│ └──────────────────────────────────────────────────────────────┘ │
└──────────────────────────────┬──────────────────────────────────┘
                               ▲ Errors propagate up
                               │
┌──────────────────────────────┴──────────────────────────────────┐
│ LEVEL 3: SpectrumData (lib9.py)                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Error Sources:                                              │ │
│ │ ✗ _read_file() → FileNotFoundError                          │ │
│ │ ✗ _read_file() → ValueError (invalid data format)           │ │
│ │ ✗ _read_file() → IndexError (malformed file)                │ │
│ │ ✗ cosmic removal → deflib function exception                │ │
│ │ ✗ background subtraction → Array shape mismatch             │ │
│ │                                                             │ │
│ │ Error Handling Strategy:                                    │ │
│ │ 1. Flag-based error tracking: self.dataokay = False         │ │
│ │ 2. State arrays: self.openFstate[], self.openDstate[]       │ │
│ │ 3. try/except with print("Error", str(e))                   │ │
│ │ 4. Silent failure (parent checks dataokay flag)             │ │
│ │                                                             │ │
│ │ Error Propagation:                                          │ │
│ │ → File not found: Set dataokay=False, XYMap filters out     │ │
│ │ → Invalid format: Set dataokay=False, logged to console     │ │
│ │ → Cosmic removal fail: Print error, continue without        │ │
│ │ → BG subtract fail: Print error, continue without           │ │
│ └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────────┬──────────────────────────────────┘
                               ▲ Errors propagate up
                               │
┌──────────────────────────────┴──────────────────────────────────┐
│ LEVEL 4: Roihandler (lib9.py)                                   │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Error Sources:                                              │ │
│ │ ✗ construct() → Invalid pixmatrix shape                     │ │
│ │ ✗ toggle_roi() → Insufficient points (<3)                   │ │
│ │ ✗ plotroi() → Empty roilist                                 │ │
│ │ ✗ delete_roi() → KeyError (invalid ROI key)                 │ │
│ │ ✗ on_click() → matplotlib event handling error              │ │
│ │                                                             │ │
│ │ Error Handling Strategy:                                    │ │
│ │ 1. Validation checks: if len(roi_points) > 2                │ │
│ │ 2. Implicit matplotlib error handling                       │ │
│ │ 3. No explicit error propagation                            │ │
│ │ 4. Errors caught by caller (XYMap)                          │ │
│ │                                                             │ │
│ │ Error Propagation:                                          │ │
│ │ → Invalid points: Silently ignore, wait for more clicks     │ │
│ │ → Plot error: matplotlib handles, shows error dialog        │ │
│ │ → KeyError: Exception propagates to XYMap                   │ │
│ └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────────┬──────────────────────────────────┘
                               ▲ Errors propagate up
                               │
┌──────────────────────────────┴──────────────────────────────────┐
│ LEVEL 5: Component Classes (Exportframe, TCSPCprocessor, etc.)  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Exportframe:                                                │ │
│ │ ✗ save_file() → No data in PMdict                           │ │
│ │ ✗ save_file() → CSV write error                             │ │
│ │ Strategy: Check PMdict exists, try/except on write          │ │
│ │                                                             │ │
│ │ TCSPCprocessor:                                             │ │
│ │ ✗ load_tcspc() → Directory not found                        │ │
│ │ ✗ plot_tres_*() → No data loaded                            │ │
│ │ Strategy: Validation checks, print to console               │ │
│ │                                                             │ │
│ │ imageprocessor (claralib):                                  │ │
│ │ ✗ __init__() → Image file not found                         │ │
│ │ ✗ fit2dgaussian() → Fit failure                             │ │
│ │ Strategy: try/except, print error, propagate to FileProc    │ │
│ │                                                             │ │
│ │ newtonspecopener:                                           │ │
│ │ ✗ __init__() → Invalid spectrum file                        │ │
│ │ Strategy: Implicit error handling, print to console         │ │
│ │                                                             │ │
│ │ specfilesorter:                                             │ │
│ │ ✗ scan_maindir() → Directory access denied                  │ │
│ │ ✗ sort_and_process() → File copy failure                    │ │
│ │ ✗ _copy_worker() → Thread exception                         │ │
│ │ Strategy: try/except per file, continue, update progress    │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Error Handling Summary Table

| Component | Error Detection | Error Handling | Error Propagation | User Notification |
|-----------|----------------|----------------|-------------------|-------------------|
| **SpectrumData** | Flag-based (dataokay) | Silent failure | Checked by XYMap | None |
| **XYMap** | try/except + traceback | Return False/continue | Via return values | None (logged) |
| **FileProcessorApp** | Validation + try/except | Early return | Stops at this level | messagebox |
| **Roihandler** | Validation checks | Implicit matplotlib | Propagates up | matplotlib dialog |
| **Exportframe** | Pre-flight checks | try/except | Print to console | None |
| **TCSPCprocessor** | Validation checks | Print to console | No propagation | None |
| **specfilesorter** | Per-file try/except | Continue on error | No propagation | Progress bar |

---

## Cleanup & Closing Flow (Directional)

### Cleanup Direction: ⬇ DOWNWARD (Root → Parent → Child)

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ TRIGGER: User clicks window close button [X]                    ┃
┃ Protocol: root.protocol("WM_DELETE_WINDOW", pressclose)         ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: pressclose(root, app)                                   │
│ ┌──────────────────────────────────────────────────────────────┐│
│ │ def pressclose(root, app):                                   ││
│ │     # Terminate all non-main threads                         ││
│ │     for thread in thr.enumerate():                           ││
│ │         if thread is not thr.main_thread():                  ││
│ │             thread.daemon = True                             ││
│ │     # Destroy the root window                                ││
│ │     root.destroy()                                           ││
│ │     # Call app cleanup                                       ││
│ │     app.on_closing()                                         ││
│ └──────────────────────────────────────────────────────────────┘│
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ├──▶ Thread cleanup (daemon=True)
                                │    └─ Threads terminate when main exits
                                │
                                ├──▶ root.destroy() ──┐
                                │                     │
                                └──▶ app.on_closing() │
                                                      │
┌─────────────────────────────────────────────────────┼─────────┐
│ STEP 2: root.destroy()                              │         │
│ ┌──────────────────────────────────────────────────▼─────────┐│
│ │ Tkinter automatic cleanup cascade:                         ││
│ │                                                            ││
│ │ root (tk.Tk)                                               ││
│ │   └─▶ DESTROYS menu_bar (tk.Menu)                         ││
│ │   └─▶ DESTROYS notebook (ttk.Notebook)                    ││
│ │         └─▶ DESTROYS all nodeframes (ttk.Frame × 7)       ││
│ │               │                                            ││
│ │               ├─▶ DESTROYS nodeframes['Load Data']        ││
│ │               │     └─▶ open_frame                        ││
│ │               │           └─▶ loadframe                   ││
│ │               │                 ├─▶ bgframe               ││
│ │               │                 └─▶ cosmicframe           ││
│ │               │     └─▶ claraloadframe                    ││
│ │               │     └─▶ saveframe                         ││
│ │               │     └─▶ newtonframe                       ││
│ │               │     └─▶ tcspcframe                        ││
│ │               │                                            ││
│ │               ├─▶ DESTROYS nodeframes['Hyperspectra']     ││
│ │               │     └─▶ cmapframe                         ││
│ │               │           └─▶ minmaxspecframe             ││
│ │               │                 ├─▶ WLselframe            ││
│ │               │                 ├─▶ cmapselframe          ││
│ │               │                 └─▶ fontframe             ││
│ │               │           └─▶ PMframe                     ││
│ │               │                 ├─▶ PMselframe            ││
│ │               │                 ├─▶ PMfitselframe         ││
│ │               │                 └─▶ PMcorrframe           ││
│ │               │     └─▶ specframe                         ││
│ │               │           └─▶ plotframe                   ││
│ │               │           └─▶ fitframe                    ││
│ │               │           └─▶ ROI_frame                   ││
│ │               │                 └─▶ plot_options_frame    ││
│ │               │                                            ││
│ │               ├─▶ DESTROYS nodeframes['HSI Plot']         ││
│ │               │     └─▶ export_frame                      ││
│ │               │                                            ││
│ │               ├─▶ DESTROYS nodeframes['Clara Image']      ││
│ │               │     └─▶ image_frame                       ││
│ │               │                                            ││
│ │               ├─▶ DESTROYS nodeframes['Newton Spectrum']  ││
│ │               │     └─▶ openframe                         ││
│ │               │                                            ││
│ │               ├─▶ DESTROYS nodeframes['TCSPC']            ││
│ │               │     └─▶ plotframe                         ││
│ │               │                                            ││
│ │               └─▶ DESTROYS nodeframes['HSI File Sorter']  ││
│ │                     └─▶ sortframe                         ││
│ │                           ├─▶ left                        ││
│ │                           │     └─▶ btnframe              ││
│ │                           │     └─▶ progressfame          ││
│ │                           └─▶ right                       ││
│ │                                                            ││
│ │ Result: ALL GUI widgets destroyed automatically            ││
│ └────────────────────────────────────────────────────────────┘│
└───────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: app.on_closing()                                        │
│ ┌──────────────────────────────────────────────────────────────┐│
│ │ def on_closing(self):                                        ││
│ │     pass  # Currently empty - no cleanup needed              ││
│ │                                                              ││
│ │ Note: This method exists for future expansion                ││
│ └──────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ SPECIAL CASE: Manual cleanup during spec_loadfiles()            │
│ ┌──────────────────────────────────────────────────────────────┐│
│ │ def spec_loadfiles(self):                                    ││
│ │     plt.close('all')  # Close matplotlib windows             ││
│ │                                                              ││
│ │     # Stop all threads                                       ││
│ │     for thread in thr.enumerate():                           ││
│ │         if thread.name != 'MainThread':                      ││
│ │             if hasattr(thread, 'stop_event'):                ││
│ │                 thread.stop_event.set()                      ││
│ │                                                              ││
│ │     # Manual cleanup sequence                                ││
│ │     try:                                                     ││
│ │         self.Nanomap.on_close()       # Close Nanomap        ││
│ │         del self.Nanomap               # Delete object       ││
│ │         self.cmapframe.destroy()      # Destroy frame        ││
│ │         self.specframe.destroy()      # Destroy frame        ││
│ │         del self.Exporter              # Delete object       ││
│ │         gc.collect()                   # Force GC            ││
│ │     except:                                                  ││
│ │         pass                                                 ││
│ │                                                              ││
│ │     # Recreate frames and objects                            ││
│ │     self.cmapframe = tk.Frame(...)                           ││
│ │     self.specframe = tk.Frame(...)                           ││
│ │     self.Nanomap = lib.XYMap(...)                            ││
│ │     self.Exporter = xplib.Exportframe(...)                   ││
│ └──────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ XYMap.on_close() - Manual cleanup for matplotlib resources      │
│ ┌──────────────────────────────────────────────────────────────┐│
│ │ def on_close(self):                                          ││
│ │     """Clean up matplotlib resources"""                      ││
│ │     plt.close('all')                                         ││
│ │     # Close ROI handler plots                                ││
│ │     if hasattr(self, 'roihandler'):                          ││
│ │         self.roihandler.on_close()                           ││
│ │                                                              ││
│ │ Called by:                                                   ││
│ │ - spec_loadfiles() before creating new XYMap                 ││
│ │ - init_spec_loadfiles() when processing multiple HSIs        ││
│ └──────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Roihandler.on_close() - Matplotlib plot cleanup                 │
│ ┌──────────────────────────────────────────────────────────────┐│
│ │ def on_close(self):                                          ││
│ │     plt.close('all')                                         ││
│ └──────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### Cleanup Sequence Summary

| Stage | Component | Action | Method | Direction |
|-------|-----------|--------|--------|-----------|
| **1** | Main Thread | Set threads to daemon | pressclose() | N/A |
| **2** | Root Window | Destroy root | root.destroy() | ⬇ Downward |
| **3** | Notebook | Auto-destroy | Tkinter automatic | ⬇ Downward |
| **4** | Node Frames | Auto-destroy | Tkinter automatic | ⬇ Downward |
| **5** | Child Frames | Auto-destroy | Tkinter automatic | ⬇ Downward |
| **6** | Widgets | Auto-destroy | Tkinter automatic | ⬇ Downward |
| **7** | App Object | Cleanup hook | app.on_closing() | N/A |
| **Manual** | XYMap | Manual cleanup | on_close() | Called explicitly |
| **Manual** | Roihandler | Close plots | on_close() | Called by XYMap |

### Important Cleanup Notes

1. **Automatic Cleanup**: Tkinter automatically destroys child widgets when parent is destroyed
2. **Manual Cleanup**: Only needed for non-Tkinter resources (matplotlib, threads, file handles)
3. **Reload Scenario**: spec_loadfiles() performs manual cleanup before recreating objects
4. **Thread Safety**: Threads set to daemon mode ensure they don't block exit
5. **Garbage Collection**: Explicit `gc.collect()` called after deleting large objects
6. **Matplotlib**: `plt.close('all')` called to close all plot windows

---

## Potential Error Scenarios

### Critical Error Points & Mitigation

```
┌─────────────────────────────────────────────────────────────────┐
│ ERROR SCENARIO 1: Frame destroyed while child is using it       │
│ ┌──────────────────────────────────────────────────────────────┐│
│ │ Situation:                                                   ││
│ │ - User clicks "Load HSI" multiple times rapidly              ││
│ │ - spec_loadfiles() destroys cmapframe/specframe              ││
│ │ - XYMap still references old frames                          ││
│ │                                                              ││
│ │ Symptom:                                                     ││
│ │ - TclError: invalid command name ".!frame..."                ││
│ │                                                              ││
│ │ Current Mitigation:                                          ││
│ │ - spec_loadfiles() calls Nanomap.on_close() first            ││
│ │ - Deletes Nanomap before destroying frames                   ││
│ │ - gc.collect() forces immediate cleanup                      ││
│ │                                                              ││
│ │ Recommendation:                                              ││
│ │ Add button disabling during load                           ││
│ │ Check if Nanomap.cmapframe.winfo_exists() before use       ││
│ └──────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ ERROR SCENARIO 2: Thread accessing destroyed widget             │
│ ┌──────────────────────────────────────────────────────────────┐│
│ │ Situation:                                                   ││
│ │ - Background thread (e.g., _copy_worker) running             ││
│ │ - User closes application                                    ││
│ │ - Thread tries to update progress bar after widget destroyed ││
│ │                                                              ││
│ │ Symptom:                                                     ││
│ │ - RuntimeError: main thread is not in main loop              ││
│ │ - TclError: application has been destroyed                   ││
│ │                                                              ││
│ │ Current Mitigation:                                          ││
│ │ - pressclose() sets threads to daemon                        ││
│ │ - specfilesorter uses stop_event for cancellation            ││
│ │ - try/except around self.sortframe.after()                   ││
│ │                                                              ││
│ │ Recommendation:                                              ││
│ │ Add widget existence checks before updates                 ││
│ │ Implement graceful shutdown with thread.join(timeout)      ││
│ └──────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ ERROR SCENARIO 3: Matplotlib plot window prevents close         │
│ ┌──────────────────────────────────────────────────────────────┐│
│ │ Situation:                                                   ││
│ │ - User creates ROI with matplotlib window                    ││
│ │ - Closes main app but matplotlib window still open           ││
│ │ - Application hangs waiting for matplotlib                   ││
│ │                                                              ││
│ │ Symptom:                                                     ││
│ │ - Application doesn't exit cleanly                           ││
│ │ - Process remains in background                              ││
│ │                                                              ││
│ │ Current Mitigation:                                          ││
│ │ - plt.close('all') called in pressclose() path               ││
│ │ - XYMap.on_close() calls plt.close('all')                    ││
│ │ - Roihandler.on_close() calls plt.close('all')               ││
│ │                                                              ││
│ │ Recommendation:                                              ││
│ │ Already well mitigated                                     ││
│ │ Consider using matplotlib.use('TkAgg') backend             ││
│ └──────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ ERROR SCENARIO 4: Circular reference preventing GC              │
│ ┌──────────────────────────────────────────────────────────────┐│
│ │ Situation:                                                   ││
│ │ - XYMap stores reference to cmapframe/specframe              ││
│ │ - cmapframe contains widgets created by XYMap                ││
│ │ - Circular reference: XYMap ↔ Frame ↔ Widgets                ││
│ │                                                              ││
│ │ Symptom:                                                     ││
│ │ - Memory leak on repeated load/unload                        ││
│ │ - Objects not garbage collected                              ││
│ │                                                              ││
│ │ Current Mitigation:                                          ││
│ │ - Explicit del self.Nanomap                                  ││
│ │ - gc.collect() after deletion                                ││
│ │ - Frames destroyed explicitly                                ││
│ │                                                              ││
│ │ Recommendation:                                              ││
│ │ Use weak references for parent frame storage               ││
│ │ Implement proper __del__ method in XYMap                   ││
│ └──────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ ERROR SCENARIO 5: Save/Load state with active GUI references    │
│ ┌──────────────────────────────────────────────────────────────┐│
│ │ Situation:                                                   ││
│ │ - User saves XYMap state to pickle                           ││
│ │ - XYMap contains references to cmapframe/specframe           ││
│ │ - pickle tries to serialize Tkinter widgets                  ││
│ │                                                              ││
│ │ Symptom:                                                     ││
│ │ - pickle.PicklingError: cannot pickle tkinter objects        ││
│ │                                                              ││
│ │ Current Mitigation:                                          ││
│ │ - save_state() creates state_dict with selected attributes   ││
│ │ - Excludes cmapframe, specframe, GUI variables               ││
│ │ - Only saves data: specs, PMdict, roilist, config            ││
│ │ - load_state() rebuilds GUI after loading data               ││
│ │                                                              ││
│ │ Recommendation:                                              ││
│ │ Already well implemented                                   ││
│ │ Document which attributes are saved vs transient           ││
│ └──────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## Best Practices & Recommendations

### Current Good Practices

1. **Frame Ownership Clarity**
   - Frames created at FileProcessorApp level
   - Passed to child classes as parameters
   - Child classes don't create top-level frames

2. **Explicit Cleanup on Reload**
   - spec_loadfiles() manually destroys old objects
   - Calls on_close() before deletion
   - Forces garbage collection

3. **Thread Safety**
   - Daemon threads don't block exit
   - Stop events for controlled shutdown
   - try/except around GUI updates from threads

4. **Matplotlib Management**
   - plt.close('all') called at multiple points
   - Dedicated on_close() methods for plot cleanup

5. **Error Isolation**
   - Errors caught at appropriate levels
   - User notified via messageboxes
   - Console logging for developer debugging

###  Recommended Improvements

```python
# IMPROVEMENT 1: Add widget existence checks
def safe_update_widget(widget, value):
    """Safely update widget if it still exists"""
    try:
        if widget.winfo_exists():
            widget.set(value)
    except tk.TclError:
        pass  # Widget was destroyed

# IMPROVEMENT 2: Add button state management during operations
def spec_loadfiles(self):
    # Disable load button
    self.process_button.config(state='disabled')
    try:
        # ... existing code ...
    finally:
        # Re-enable load button
        self.process_button.config(state='normal')

# IMPROVEMENT 3: Implement proper cleanup in on_closing()
def on_closing(self):
    """Cleanup before application exit"""
    # Close all matplotlib windows
    plt.close('all')
    
    # Stop background threads gracefully
    for thread in threading.enumerate():
        if thread != threading.main_thread():
            if hasattr(thread, 'stop_event'):
                thread.stop_event.set()
    
    # Clean up Nanomap if exists
    if hasattr(self, 'Nanomap'):
        self.Nanomap.on_close()
    
    # Clean up ROI handler
    if hasattr(self, 'Nanomap') and hasattr(self.Nanomap, 'roihandler'):
        self.Nanomap.roihandler.on_close()

# IMPROVEMENT 4: Add context manager for XYMap
class XYMap:
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.on_close()
        return False

# Usage:
with lib.XYMap(...) as nanomap:
    # Use nanomap
    pass
# Automatically cleaned up

# IMPROVEMENT 5: Add weak references for parent frames
import weakref

class XYMap:
    def __init__(self, ..., cmapframe, specframe, ...):
        # Store weak references to frames
        self._cmapframe_ref = weakref.ref(cmapframe)
        self._specframe_ref = weakref.ref(specframe)
    
    @property
    def cmapframe(self):
        """Get cmapframe if it still exists"""
        frame = self._cmapframe_ref()
        if frame is None:
            raise RuntimeError("cmapframe has been destroyed")
        return frame
```

###  Cleanup Checklist

Use this checklist when modifying the code:

- [ ] Does the new component receive a parent frame parameter?
- [ ] Are all widgets children of the passed frame?
- [ ] Does the component avoid creating top-level windows?
- [ ] Are background threads set to daemon or properly joined?
- [ ] Is there a cleanup method (on_close) for non-Tkinter resources?
- [ ] Does the cleanup method close matplotlib windows?
- [ ] Are there try/except blocks around GUI updates from threads?
- [ ] Are widget existence checks in place for async updates?
- [ ] Does save_state exclude Tkinter objects from serialization?
- [ ] Is gc.collect() called after large object deletion?

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-28 | Initial documentation - GUI hierarchy, error flow, cleanup flow |

---

*This document provides directional analysis of GUI hierarchy, error propagation, and cleanup sequences for the SpecMap application, essential for debugging and maintaining application stability.*
