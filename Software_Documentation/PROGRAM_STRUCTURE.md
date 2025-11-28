# SpecMap Program Structure Documentation

**Version:** 1.0  
**Last Updated:** November 28, 2025  
**Purpose:** Complete software tree structure from main9.py root

---

## Table of Contents
1. [Program Structure Tree](#program-structure-tree)
2. [Module Hierarchy](#module-hierarchy)
3. [Class Instantiation Flow](#class-instantiation-flow)
4. [Error Propagation Paths](#error-propagation-paths)
5. [Module Dependencies](#module-dependencies)

---

## Program Structure Tree

```
main9.py (Entry Point)
│
├── if __name__ == "__main__":
│   │
│   ├── HSI_debugger.main_Debugger()
│   │   └── Creates debugger instance
│   │
│   ├── deflib1.initdefaults()
│   │   └── Returns: dict with default configuration
│   │
│   ├── tk.Tk() → root
│   │   └── Main Tkinter window instance
│   │
│   └── FileProcessorApp(root, defaults)
│       │
│       ├── [Initialization Phase]
│       │   ├── self.root = root (stores tk.Tk instance)
│       │   ├── self.defaults = defaults
│       │   ├── tk.IntVar() × 3 (multiple_BG, linearBG, removecosmicsBool)
│       │   │
│       │   ├── self.createmenue()
│       │   │   ├── tk.Menu(root) → menu_bar
│       │   │   └── deflib1.create_menu(root, menu_bar)
│       │   │       └── Adds menu items to menu_bar
│       │   │
│       │   └── self.windownotebook(deflib.Notebooks)
│       │       ├── ttk.Notebook(self.root) → self.notebook
│       │       └── Creates self.nodeframes{} dict:
│       │           ├── 'Load Data' → ttk.Frame
│       │           ├── 'Hyperspectra' → ttk.Frame
│       │           ├── 'HSI Plot' → ttk.Frame
│       │           ├── 'Clara Image' → ttk.Frame
│       │           ├── 'Newton Spectrum' → ttk.Frame
│       │           ├── 'TCSPC' → ttk.Frame
│       │           └── 'HSI File Sorter' → ttk.Frame
│       │
│       ├── [GUI Construction Phase]
│       │   │
│       │   ├── self.createbuttons(self.nodeframes['Load Data'])
│       │   │   │
│       │   │   ├── self.open_frame → tk.Frame (parent: nodeframes['Load Data'])
│       │   │   │   ├── [SpecMap Load Widgets]
│       │   │   │   │   ├── self.SpecMapLoad_label → tk.Label
│       │   │   │   │   ├── self.folder_label → tk.Label
│       │   │   │   │   ├── self.folder_entry → tk.Entry
│       │   │   │   │   ├── self.folder_button → tk.Button (Browse)
│       │   │   │   │   ├── self.filename_label → tk.Label
│       │   │   │   │   ├── self.filename_entry → tk.Entry
│       │   │   │   │   ├── self.fileformat_label → tk.Label
│       │   │   │   │   ├── self.fileformat_entry → tk.Entry
│       │   │   │   │   └── self.process_button → tk.Button (Load HSI)
│       │   │   │   │       └── command: self.init_spec_loadfiles
│       │   │   │   │
│       │   │   │   ├── self.loadframe → tk.Frame
│       │   │   │   │   │
│       │   │   │   │   ├── self.bgframe → tk.Frame (Background options)
│       │   │   │   │   │   ├── self.chkmultiple → tk.Checkbutton
│       │   │   │   │   │   ├── self.linearBGcheck → tk.Checkbutton
│       │   │   │   │   │   └── self.powercorrectioncheck → tk.Checkbutton
│       │   │   │   │   │
│       │   │   │   │   └── self.cosmicframe → tk.Frame (Cosmic removal)
│       │   │   │   │       ├── self.removecosmics → tk.Checkbutton
│       │   │   │   │       ├── self.cosmicremoval → ttk.Combobox
│       │   │   │   │       ├── self.cosmicthresholdentry → tk.Entry
│       │   │   │   │       ├── self.cosmicwidthentry → tk.Entry
│       │   │   │   │       └── self.laserspotsizeentry → tk.Entry
│       │   │   │   │
│       │   │   │   └── self.multiple_HSIs_inp_frame → tk.Frame
│       │   │   │       ├── self.make_multiple_HSIsbool → tk.IntVar
│       │   │   │       ├── self.process_multiple_HSIs → tk.Checkbutton
│       │   │   │       ├── self.multiple_HSIs_dir_entry → tk.Entry
│       │   │   │       ├── self.Browse_multiple_HSIs_dir_button → tk.Button
│       │   │   │       ├── self.multiple_HSIs_save_dir_entry → tk.Entry
│       │   │   │       └── self.Browse_multiple_HSIs_save_dir_button → tk.Button
│       │   │   │
│       │   │   ├── self.claraloadframe → tk.Frame (parent: nodeframes['Load Data'])
│       │   │   │   ├── self.clara_label → tk.Label
│       │   │   │   ├── self.cl_file_entrystr → tk.StringVar
│       │   │   │   ├── self.cl_file_entry → tk.Entry
│       │   │   │   ├── self.cl_process_button → tk.Button
│       │   │   │   │   └── command: self.cl_loadfiles
│       │   │   │   ├── self.cl_scaling_label → tk.Label
│       │   │   │   ├── self.cl_scaling → ttk.Combobox
│       │   │   │   └── self.cl_folder_button → tk.Button
│       │   │   │
│       │   │   ├── self.saveframe → tk.Frame (parent: nodeframes['Load Data'])
│       │   │   │   ├── [Save HSI Section]
│       │   │   │   │   ├── self.save_label → tk.Label
│       │   │   │   │   ├── self.savehsipath → tk.StringVar
│       │   │   │   │   ├── self.save_entry → tk.Entry
│       │   │   │   │   ├── Browse Button → tk.Button
│       │   │   │   │   │   └── command: self.browse_save_path
│       │   │   │   │   └── self.save_button → tk.Button
│       │   │   │   │       └── command: self.saveNanomap
│       │   │   │   │
│       │   │   │   └── [Load HSI Section]
│       │   │   │       ├── self.load_label → tk.Label
│       │   │   │       ├── self.loadhsipath → tk.StringVar
│       │   │   │       ├── self.load_entry → tk.Entry
│       │   │   │       ├── Browse Button → tk.Button
│       │   │   │       │   └── command: self.browse_load_path
│       │   │   │       └── self.load_button → tk.Button
│       │   │   │           └── command: self.loadhsisaved
│       │   │   │
│       │   │   ├── self.newtonframe → tk.Frame (parent: nodeframes['Load Data'])
│       │   │   │   ├── self.newton_label → tk.Label
│       │   │   │   ├── self.newton_file_entrystr → tk.StringVar
│       │   │   │   ├── self.newton_file_entry → tk.Entry
│       │   │   │   ├── self.newton_process_button → tk.Button
│       │   │   │   │   └── command: self.newtonloadfiles
│       │   │   │   └── self.newton_folder_button → tk.Button
│       │   │   │
│       │   │   └── self.tcspcframe → tk.Frame (parent: nodeframes['Load Data'])
│       │   │       ├── self.tcspc_label → tk.Label
│       │   │       ├── self.tcspc_maindir_entrystr → tk.StringVar
│       │   │       ├── self.tcspc_maindir_entry → tk.Entry
│       │   │       ├── self.tcspc_subdir_entrystr → tk.StringVar
│       │   │       ├── self.tcspc_subdir_entry → tk.Entry
│       │   │       ├── self.tcspc_process_button → tk.Button
│       │   │       │   └── command: self.tcspcloadfiles
│       │   │       └── self.tcspc_folder_button → tk.Button
│       │   │
│       │   ├── [Core Data Frames Creation]
│       │   │   ├── self.cmapframe → tk.Frame (parent: nodeframes['Hyperspectra'])
│       │   │   │   └── Purpose: Container for colormap visualization
│       │   │   └── self.specframe → tk.Frame (parent: nodeframes['Hyperspectra'])
│       │   │       └── Purpose: Container for spectrum controls & plots
│       │   │
│       │   ├── [Main Data Object Creation]
│       │   │   └── self.Nanomap → lib9.XYMap(...)
│       │   │       │   Parameters: ([], cmapframe, specframe, defaults...)
│       │   │       │
│       │   │       ├── [XYMap Initialization - lib9.py]
│       │   │       │   │
│       │   │       │   ├── Instance Variables (tk-related):
│       │   │       │   │   ├── self.HSI_fit_useROI → tk.BooleanVar()
│       │   │       │   │   ├── self.colormap → tk.StringVar()
│       │   │       │   │   ├── self.WL_selection → tk.StringVar()
│       │   │       │   │   ├── self.HSI_from_fitparam_useROI → tk.BooleanVar()
│       │   │       │   │   ├── self.cmapframe = cmapframe (reference to parent)
│       │   │       │   │   └── self.specframe = specframe (reference to parent)
│       │   │       │   │
│       │   │       │   ├── Data Structures:
│       │   │       │   │   ├── self.specs = [] (list of SpectrumData objects)
│       │   │       │   │   ├── self.PMdict = {} (Pixel Matrix dictionary)
│       │   │       │   │   ├── self.WL = [] (Wavelength axis)
│       │   │       │   │   ├── self.BG = [] (Background spectrum)
│       │   │       │   │   └── self.roihandler → Roihandler()
│       │   │       │   │
│       │   │       │   ├── self.build_gui() → Constructs GUI elements
│       │   │       │   │   │
│       │   │       │   │   ├── self.SpecButtons = self.build_button_frame(specframe)
│       │   │       │   │   │   │
│       │   │       │   │   │   ├── plotframe → tk.Frame (parent: specframe)
│       │   │       │   │   │   │   ├── b1 → tk.Button ("Plot")
│       │   │       │   │   │   │   │   └── command: self.on_spec_chosen
│       │   │       │   │   │   │   ├── b3 → tk.Button ("Plot Line")
│       │   │       │   │   │   │   │   └── command: self.PlotAllSpectraLine
│       │   │       │   │   │   │   ├── b4 → tk.Button ("Save Spec")
│       │   │       │   │   │   │   │   └── command: self.saveonespectrum
│       │   │       │   │   │   │   ├── b5 → tk.Button ("Plot AVspec")
│       │   │       │   │   │   │   │   └── command: self.averagespectrum
│       │   │       │   │   │   │   ├── wlmin_label → tk.Label
│       │   │       │   │   │   │   ├── self.spectralminentry → tk.Entry
│       │   │       │   │   │   │   ├── wlmax_label → tk.Label
│       │   │       │   │   │   │   └── self.spectralmaxentry → tk.Entry
│       │   │       │   │   │   │
│       │   │       │   │   │   ├── fitframe → tk.Frame (parent: specframe)
│       │   │       │   │   │   │   ├── self.funcselgui → ttk.Combobox (fit functions)
│       │   │       │   │   │   │   ├── b2 → tk.Button ("Fit")
│       │   │       │   │   │   │   │   └── command: self.make_fit
│       │   │       │   │   │   │   ├── self.pstartentry → tk.Entry (pixel start)
│       │   │       │   │   │   │   ├── self.pendentry → tk.Entry (pixel end)
│       │   │       │   │   │   │   ├── self.PlotFitbool → tk.IntVar
│       │   │       │   │   │   │   ├── self.chkplotfit → tk.Checkbutton
│       │   │       │   │   │   │   ├── self.ManualFitbool → tk.IntVar
│       │   │       │   │   │   │   └── self.chkmanualfit → tk.Checkbutton
│       │   │       │   │   │   │
│       │   │       │   │   │   └── self.build_roi_frame(specframe)
│       │   │       │   │   │       │
│       │   │       │   │   │       ├── ROI_frame → tk.Frame (parent: specframe)
│       │   │       │   │   │       │   ├── self.roiselgui → ttk.Combobox
│       │   │       │   │   │       │   ├── self.HSI_fit_useROI_button → tk.Checkbutton
│       │   │       │   │   │       │   ├── createroi_button → tk.Button
│       │   │       │   │   │       │   │   └── command: self.roihandler.construct
│       │   │       │   │   │       │   ├── plotroi_button → tk.Button
│       │   │       │   │   │       │   │   └── command: self.roihandler.plotroi
│       │   │       │   │   │       │   └── deleteroi_button → tk.Button
│       │   │       │   │   │       │       └── command: self.roihandler.delete_roi
│       │   │       │   │   │       │
│       │   │       │   │   │       └── self.build_plot_options_frame(specframe)
│       │   │       │   │   │           └── Plot options controls
│       │   │       │   │   │
│       │   │       │   │   ├── self.buildMinMaxSpec(cmapframe)
│       │   │       │   │   │   │
│       │   │       │   │   │   └── minmaxspecframe → tk.Frame (parent: cmapframe)
│       │   │       │   │   │       ├── self.WLselframe → tk.Frame
│       │   │       │   │   │       │   ├── self.WLselection → ttk.Combobox
│       │   │       │   │   │       │   └── WL_sel_button → tk.Button
│       │   │       │   │   │       │       └── command: self.WL_selected
│       │   │       │   │   │       │
│       │   │       │   │   │       ├── self.cmapselframe → tk.Frame
│       │   │       │   │   │       │   ├── self.cmapselection → ttk.Combobox
│       │   │       │   │   │       │   └── cmap_sel_button → tk.Button
│       │   │       │   │   │       │       └── command: self.cmap_selected
│       │   │       │   │   │       │
│       │   │       │   │   │       └── self.fontframe → tk.Frame
│       │   │       │   │   │           ├── self.CMFont → tk.Entry (font size)
│       │   │       │   │   │           └── setfont_button → tk.Button
│       │   │       │   │   │               └── command: self.setfont
│       │   │       │   │   │
│       │   │       │   │   └── self.build_PixMatrix_frame(cmapframe)
│       │   │       │   │       │
│       │   │       │   │       └── self.PMframe → tk.Frame (parent: cmapframe)
│       │   │       │   │           ├── self.PMselframe → tk.Frame
│       │   │       │   │           │   ├── self.PMselection → ttk.Combobox
│       │   │       │   │           │   └── PM_sel_button → tk.Button
│       │   │       │   │           │       └── command: self.PM_selected
│       │   │       │   │           │
│       │   │       │   │           ├── self.PMfitselframe → tk.Frame
│       │   │       │   │           │   ├── self.PMfitselection → ttk.Combobox
│       │   │       │   │           │   ├── self.HSI_from_fitparam_useROI_button → tk.Checkbutton
│       │   │       │   │           │   └── PMfit_sel_button → tk.Button
│       │   │       │   │           │       └── command: self.PMfromfitparams
│       │   │       │   │           │
│       │   │       │   │           └── self.PMcorrframe → tk.Frame
│       │   │       │   │               ├── self.PMcorrselgui → ttk.Combobox
│       │   │       │   │               └── PMcorr_button → tk.Button
│       │   │       │   │                   └── command: self.PMMatrixCorr
│       │   │       │   │
│       │   │       │   └── Data Loading (if fnames provided):
│       │   │       │       └── self.loadfiles() → Parallel file loading
│       │   │       │           ├── Creates SpectrumData objects for each file
│       │   │       │           └── Stores in self.specs[]
│       │   │       │
│       │   │       └── [Methods]
│       │   │           ├── self.on_close() → Cleanup method
│       │   │           ├── self.save_state(filename) → Serialize to file
│       │   │           └── self.load_state(filename) → Deserialize from file
│       │   │
│       │   ├── self.Exporter → export2.Exportframe(...)
│       │   │   │   Parameters: (nodeframes['HSI Plot'], Nanomap)
│       │   │   │
│       │   │   ├── [Exportframe Initialization - export2.py]
│       │   │   │   ├── self.Notebook = nodeframes['HSI Plot']
│       │   │   │   ├── self.Nanomap = Nanomap (reference)
│       │   │   │   └── self.buildframe()
│       │   │   │       │
│       │   │   │       └── self.export_frame → tk.Frame (parent: Notebook)
│       │   │   │           └── self.save_button → tk.Button ("Export Pixel Matrix")
│       │   │   │               └── command: self.save_file
│       │   │   │
│       │   │   └── [Methods]
│       │   │       └── self.save_file() → Exports PixMatrix to CSV
│       │   │
│       │   ├── self.TCSPC_Processor → TCSPClib.TCSPCprocessor(...)
│       │   │   │   Parameters: (nodeframes['TCSPC'], entries...)
│       │   │   │
│       │   │   ├── [TCSPCprocessor Initialization - TCSPClib.py]
│       │   │   │   ├── self.parentframe = nodeframes['TCSPC']
│       │   │   │   ├── self.filepath = filepath
│       │   │   │   ├── self.savedir = savedir
│       │   │   │   └── self.build_frame()
│       │   │   │       │
│       │   │   │       └── self.plotframe → tk.Frame (parent: parentframe)
│       │   │   │           ├── self.load_button → tk.Button
│       │   │   │           │   └── command: self.load_tcspc
│       │   │   │           ├── self.plot_tres_linear_button → tk.Button
│       │   │   │           │   └── command: self.plot_tres_linear
│       │   │   │           └── self.plot_tres_log_button → tk.Button
│       │   │   │               └── command: self.plot_tres_log
│       │   │   │
│       │   │   └── [Methods]
│       │   │       ├── self.load_tcspc() → Load TCSPC data
│       │   │       ├── self.plot_tres_linear() → Plot time-resolved
│       │   │       └── self.plot_tres_log() → Plot log scale
│       │   │
│       │   └── self.specfilesorterframe → specfilesorter(...)
│       │       │   Parameters: (nodeframes['HSI File Sorter'], defaults...)
│       │       │
│       │       ├── [specfilesorter Initialization - main9.py]
│       │       │   ├── self.tkroot = nodeframes['HSI File Sorter']
│       │       │   ├── self.maindir, filename, fileend, savedir... (config)
│       │       │   └── self.buildGUI()
│       │       │       │
│       │       │       ├── self.sortframe → ttk.LabelFrame (parent: tkroot)
│       │       │       │   │
│       │       │       │   ├── left → tk.Frame (controls)
│       │       │       │   │   ├── self.maindir_entry → tk.Entry
│       │       │       │   │   ├── Browse button → tk.Button
│       │       │       │   │   ├── self.filename_entry → tk.Entry
│       │       │       │   │   ├── self.fileend_entry → tk.Entry
│       │       │       │   │   ├── self.savedir_entry → tk.Entry
│       │       │       │   │   ├── self.processdir_entry → tk.Entry
│       │       │       │   │   ├── self.merge_var → tk.IntVar (Checkbutton)
│       │       │       │   │   │
│       │       │       │   │   ├── self.btnframe → tk.Frame
│       │       │       │   │   │   ├── self.scan_button → tk.Button
│       │       │       │   │   │   │   └── command: self.scan_maindir
│       │       │       │   │   │   ├── self.preview_button → tk.Button
│       │       │       │   │   │   │   └── command: self.preview_selected
│       │       │       │   │   │   ├── self.process_button_sf → tk.Button
│       │       │       │   │   │   │   └── command: self.sort_and_process
│       │       │       │   │   │   ├── self.clear_button → tk.Button
│       │       │       │   │   │   │   └── command: self.clear_list
│       │       │       │   │   │   └── self.cancel_button → tk.Button
│       │       │       │   │   │       └── command: self.cancel_copy
│       │       │       │   │   │
│       │       │       │   │   └── self.progressfame → tk.Frame
│       │       │       │   │       └── self.progress → ttk.Progressbar
│       │       │       │   │
│       │       │       │   └── right → tk.Frame (results display)
│       │       │       │       ├── self.tree → ttk.Treeview
│       │       │       │       └── vsb → ttk.Scrollbar
│       │       │       │
│       │       │       └── [Methods]
│       │       │           ├── self.scan_maindir() → Scan directories
│       │       │           ├── self.sort_and_process() → Copy files
│       │       │           ├── self._copy_worker() → Background thread
│       │       │           └── self.cancel_copy() → Cancel operation
│       │       │
│       │       └── [Data Structures]
│       │           ├── self.scan_results = [] (scanned folders)
│       │           ├── self.selected_items = [] (selected paths)
│       │           └── self._copy_thread → threading.Thread
│       │
│       └── [Optional: Load on Start]
│           └── if defaults['loadonstart'] == True:
│               └── self.spec_loadfiles()
│
├── [FileProcessorApp Methods - Data Loading]
│   │
│   ├── self.init_spec_loadfiles()
│   │   ├── Checks if multiple HSI processing is enabled
│   │   ├── If True: Iterate through folders
│   │   │   ├── For each folder: call self.spec_loadfiles()
│   │   │   └── Build and save HSI image
│   │   └── If False: call self.spec_loadfiles()
│   │
│   ├── self.spec_loadfiles()
│   │   ├── Close existing matplotlib windows
│   │   ├── Stop running threads
│   │   ├── Cleanup existing Nanomap
│   │   │   ├── self.Nanomap.on_close()
│   │   │   ├── del self.Nanomap
│   │   │   ├── self.cmapframe.destroy()
│   │   │   ├── self.specframe.destroy()
│   │   │   ├── del self.Exporter
│   │   │   └── gc.collect()
│   │   │
│   │   ├── Scan folder for files matching pattern
│   │   ├── Recreate frames (cmapframe, specframe)
│   │   ├── Create new XYMap instance
│   │   │   └── self.Nanomap = lib.XYMap(files_processed, ...)
│   │   │       └── Triggers XYMap.__init__ → loadfiles() → GUI build
│   │   │
│   │   └── Recreate Exporter
│   │       └── self.Exporter = xplib.Exportframe(...)
│   │
│   ├── self.cl_loadfiles()
│   │   ├── Get Clara image file path
│   │   ├── Get scaling factor from cl_scaling combobox
│   │   └── self.claraimage = claralib.imageprocessor(...)
│   │       │   Parameters: (nodeframes['Clara Image'], file, ...)
│   │       │
│   │       └── [imageprocessor Initialization - claralib1.py]
│   │           ├── self.Notebook = nodeframes['Clara Image']
│   │           ├── self.imagefile = file
│   │           ├── self.loadfunct = loadfunction
│   │           ├── Load image data
│   │           └── self.image_frame → tk.Frame (parent: Notebook)
│   │               ├── self.plotimage → tk.Button
│   │               │   └── command: self.plotimage
│   │               ├── self.fitg2Dbutton → tk.Button
│   │               │   └── command: self.fit2dgaussian
│   │               ├── self.plotfitbutton → tk.Button
│   │               │   └── command: plot2dfit
│   │               └── self.area → tk.Button
│   │                   └── command: area2dgaussian
│   │
│   ├── self.newtonloadfiles()
│   │   ├── Get Newton spectrum file path
│   │   └── self.newtonclass = newtonlib.newtonspecopener(...)
│   │       │   Parameters: (nodeframes['Newton Spectrum'], file)
│   │       │
│   │       └── [newtonspecopener Initialization - newtonspeclib1.py]
│   │           ├── self.root = nodeframes['Newton Spectrum']
│   │           ├── self.opennotebook = file
│   │           └── self.buildopenframe()
│   │               └── self.openframe → tk.Frame (parent: root)
│   │                   └── Newton spectrum controls
│   │
│   ├── self.tcspcloadfiles()
│   │   ├── Get TCSPC directory path
│   │   └── self.TCSPC_Processor.load_tcspc()
│   │
│   ├── self.saveNanomap(filename)
│   │   ├── Validates filename and Nanomap existence
│   │   ├── Calls self.Nanomap.save_state(filename)
│   │   └── Shows success/error message
│   │
│   └── self.loadhsisaved(filename)
│       ├── Validates filename exists
│       ├── Creates Nanomap if doesn't exist
│       ├── Calls self.Nanomap.load_state(filename)
│       └── Shows success/error message
│
├── [FileProcessorApp Methods - Utilities]
│   ├── self.browse_save_path() → Open save file dialog
│   ├── self.browse_load_path() → Open load file dialog
│   ├── self.filter_substring(a, b) → Filter files by substring
│   └── self.on_closing() → Cleanup on exit
│
└── [Application Lifecycle]
    ├── root.protocol("WM_DELETE_WINDOW", pressclose)
    │   └── pressclose(root, app)
    │       ├── Terminate all non-main threads
    │       ├── root.destroy()
    │       └── app.on_closing()
    │
    └── root.mainloop()
        └── Enter Tkinter event loop
```

---

## Module Hierarchy

### Primary Modules (Direct Imports in main9.py)

| Module | Purpose | Key Classes | Tkinter Usage |
|--------|---------|-------------|---------------|
| **lib9.py** | Core hyperspectral data handling | `SpectrumData`, `XYMap`, `Roihandler` | Heavy (creates frames, buttons, entries) |
| **deflib1.py** | Default configuration and utilities | None | Moderate (helper functions for dialogs) |
| **claralib1.py** | Clara image processing | `imageprocessor` | Heavy (creates frame with controls) |
| **export2.py** | Data export functionality | `Exportframe` | Light (single frame with button) |
| **newtonspeclib1.py** | Newton spectrum handling | `newtonspecopener` | Moderate (frame with controls) |
| **TCSPClib.py** | Time-correlated single photon counting | `TCSPCprocessor` | Moderate (frame with plot buttons) |
| **mathlib3.py** | Mathematical fitting functions | None | None |
| **PMclasslib1.py** | Pixel matrix classes | `SpectrumData`, `PMclass` | None |
| **HSI_debugger.py** | Debugging utilities | `main_Debugger` | None |

### Secondary Modules (Imported by lib9.py)

| Module | Purpose | Used By | Tkinter Usage |
|--------|---------|---------|---------------|
| **mathlib3.py** | Fit functions and parameters | lib9.XYMap | None |
| **deflib1.py** | Cosmic removal functions | lib9.SpectrumData | None |
| **PMclasslib1.py** | Pixel matrix operations | lib9.XYMap | None |

---

## Class Instantiation Flow

### Order of Object Creation

```
1. HSI_debugger.main_Debugger()
   └── Independent debugger instance

2. tk.Tk() → root
   └── Main window (owns all GUI elements)

3. FileProcessorApp(root, defaults)
   │
   ├── 4. tk.Menu(root) → menu_bar
   │
   ├── 5. ttk.Notebook(root) → self.notebook
   │   └── 6. ttk.Frame × 7 → self.nodeframes{}
   │       ├── 'Load Data'
   │       ├── 'Hyperspectra'
   │       ├── 'HSI Plot'
   │       ├── 'Clara Image'
   │       ├── 'Newton Spectrum'
   │       ├── 'TCSPC'
   │       └── 'HSI File Sorter'
   │
   ├── 7. GUI Components in 'Load Data' frame
   │   ├── tk.Frame (open_frame, loadframe, bgframe, cosmicframe, ...)
   │   ├── tk.Label, tk.Entry, tk.Button, ttk.Combobox
   │   └── tk.IntVar, tk.StringVar
   │
   ├── 8. tk.Frame(nodeframes['Hyperspectra']) → self.cmapframe
   │
   ├── 9. tk.Frame(nodeframes['Hyperspectra']) → self.specframe
   │
   ├── 10. lib9.XYMap([], cmapframe, specframe, ...) → self.Nanomap
   │   │
   │   ├── 11. tk.BooleanVar, tk.StringVar (multiple)
   │   │
   │   ├── 12. Roihandler() → self.roihandler
   │   │
   │   ├── 13. self.build_gui()
   │   │   │
   │   │   ├── 14. tk.Frame(specframe) → plotframe
   │   │   │   └── tk.Button × 5, tk.Label, tk.Entry
   │   │   │
   │   │   ├── 15. tk.Frame(specframe) → fitframe
   │   │   │   └── ttk.Combobox, tk.Button, tk.Entry, tk.Checkbutton
   │   │   │
   │   │   ├── 16. tk.Frame(specframe) → ROI_frame
   │   │   │   └── ttk.Combobox, tk.Checkbutton, tk.Button × 3
   │   │   │
   │   │   ├── 17. tk.Frame(cmapframe) → minmaxspecframe
   │   │   │   └── tk.Frame × 3 (WLselframe, cmapselframe, fontframe)
   │   │   │       └── ttk.Combobox, tk.Button, tk.Entry
   │   │   │
   │   │   └── 18. tk.Frame(cmapframe) → PMframe
   │   │       └── tk.Frame × 3 (PMselframe, PMfitselframe, PMcorrframe)
   │   │           └── ttk.Combobox, tk.Button, tk.Checkbutton
   │   │
   │   └── If data files provided: loadfiles()
   │       └── 19. SpectrumData × N → self.specs[]
   │
   ├── 20. export2.Exportframe(nodeframes['HSI Plot'], Nanomap) → self.Exporter
   │   └── 21. tk.Frame(nodeframes['HSI Plot']) → export_frame
   │       └── tk.Button
   │
   ├── 22. TCSPClib.TCSPCprocessor(...) → self.TCSPC_Processor
   │   └── 23. tk.Frame(nodeframes['TCSPC']) → plotframe
   │       └── tk.Button × 3
   │
   └── 24. specfilesorter(nodeframes['HSI File Sorter'], ...) → self.specfilesorterframe
       └── 25. ttk.LabelFrame(nodeframes['HSI File Sorter']) → sortframe
           ├── tk.Frame (left, right)
           ├── tk.Entry × 4, tk.Button × 7
           ├── ttk.Treeview, ttk.Scrollbar
           └── ttk.Progressbar
```

### Parent-Child Relationships Summary

```
root (tk.Tk)
│
├── menu_bar (tk.Menu)
│
└── notebook (ttk.Notebook)
    │
    ├── nodeframes['Load Data'] (ttk.Frame)
    │   ├── open_frame (tk.Frame)
    │   │   ├── loadframe (tk.Frame)
    │   │   │   ├── bgframe (tk.Frame)
    │   │   │   └── cosmicframe (tk.Frame)
    │   │   └── multiple_HSIs_inp_frame (tk.Frame)
    │   ├── claraloadframe (tk.Frame)
    │   ├── saveframe (tk.Frame)
    │   ├── newtonframe (tk.Frame)
    │   └── tcspcframe (tk.Frame)
    │
    ├── nodeframes['Hyperspectra'] (ttk.Frame)
    │   ├── cmapframe (tk.Frame)
    │   │   ├── minmaxspecframe (tk.Frame)
    │   │   │   ├── WLselframe (tk.Frame)
    │   │   │   ├── cmapselframe (tk.Frame)
    │   │   │   └── fontframe (tk.Frame)
    │   │   └── PMframe (tk.Frame)
    │   │       ├── PMselframe (tk.Frame)
    │   │       ├── PMfitselframe (tk.Frame)
    │   │       └── PMcorrframe (tk.Frame)
    │   │
    │   └── specframe (tk.Frame)
    │       ├── plotframe (tk.Frame)
    │       ├── fitframe (tk.Frame)
    │       └── ROI_frame (tk.Frame)
    │           └── plot_options_frame (tk.Frame)
    │
    ├── nodeframes['HSI Plot'] (ttk.Frame)
    │   └── export_frame (tk.Frame)
    │
    ├── nodeframes['Clara Image'] (ttk.Frame)
    │   └── image_frame (tk.Frame)
    │
    ├── nodeframes['Newton Spectrum'] (ttk.Frame)
    │   └── openframe (tk.Frame)
    │
    ├── nodeframes['TCSPC'] (ttk.Frame)
    │   └── plotframe (tk.Frame)
    │
    └── nodeframes['HSI File Sorter'] (ttk.Frame)
        └── sortframe (ttk.LabelFrame)
            ├── left (tk.Frame)
            │   ├── btnframe (tk.Frame)
            │   └── progressfame (tk.Frame)
            └── right (tk.Frame)
```

---

## Error Propagation Paths

### Error Flow Direction: Bottom-Up

Errors propagate from child components to parent components, eventually reaching the root window.

```
┌─────────────────────────────────────────────────────────────┐
│ Level 7: root (tk.Tk) - Main Window                         │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Exception Handler: pressclose() catches thread errors   │ │
│ │ Action: Sets all threads to daemon, calls root.destroy()│ │
│ └─────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────┘
                            │ Propagates upward
┌───────────────────────────┴─────────────────────────────────┐
│ Level 6: FileProcessorApp                                   │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Error Sources:                                          │ │
│ │ - init_spec_loadfiles() → File not found                │ │
│ │ - spec_loadfiles() → Invalid folder/file                │ │
│ │ - saveNanomap() → Write permission denied               │ │
│ │ - loadhsisaved() → Corrupted pickle file                │ │
│ │                                                         │ │
│ │ Error Handling:                                         │ │
│ │ - Print to console                                      │ │
│ │ - messagebox.showerror() → User notification            │ │
│ │ - try/except blocks catch and log errors                │ │
│ └─────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────┘
                            │ Propagates upward
┌───────────────────────────┴─────────────────────────────────┐
│ Level 5: Nanomap (lib9.XYMap)                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Error Sources:                                          │ │
│ │ - loadfiles() → Thread pool exception                   │ │
│ │ - on_spec_chosen() → Invalid spectrum index             │ │
│ │ - make_fit() → Curve fit failure                        │ │
│ │ - save_state() → Pickle serialization error             │ │
│ │ - load_state() → Pickle deserialization error           │ │
│ │ - PM_selected() → KeyError (invalid PM key)             │ │
│ │ - PMfromfitparams() → Fit data not available            │ │
│ │                                                         │ │
│ │ Error Handling:                                         │ │
│ │ - try/except with traceback.print_exc()                 │ │
│ │ - Returns False on failure (save/load methods)          │ │
│ │ - Prints error messages to console                      │ │
│ │ - Propagates to FileProcessorApp via return values      │ │
│ └─────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────┘
                            │ Propagates upward
┌───────────────────────────┴─────────────────────────────────┐
│ Level 4: SpectrumData (lib9.SpectrumData)                   │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Error Sources:                                          │ │
│ │ - _read_file() → FileNotFoundError                      │ │
│ │ - _read_file() → ValueError (invalid data format)       │ │
│ │ - cosmic removal → deflib function exceptions           │ │
│ │                                                         │ │
│ │ Error Handling:                                         │ │
│ │ - Sets self.dataokay = False                            │ │
│ │ - Populates self.openFstate[], self.openDstate[]        │ │
│ │ - try/except with print("Error", str(e))                │ │
│ │ - Silently fails, checked by parent XYMap               │ │
│ └─────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────┘
                            │ Propagates upward
┌───────────────────────────┴─────────────────────────────────┐
│ Level 3: Roihandler (lib9.Roihandler)                       │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Error Sources:                                          │ │
│ │ - construct() → Invalid pixmatrix shape                 │ │
│ │ - toggle_roi() → Insufficient points (<3)               │ │
│ │ - plotroi() → Empty roilist                             │ │
│ │ - delete_roi() → KeyError (invalid ROI key)             │ │
│ │                                                         │ │
│ │ Error Handling:                                         │ │
│ │ - Implicit: matplotlib handles plot errors              │ │
│ │ - Key checks: if len(roi_points) > 2                    │ │
│ │ - No explicit error propagation                         │ │
│ │ - Errors caught by XYMap caller                         │ │
│ └─────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────┘
                            │ Propagates upward
┌───────────────────────────┴─────────────────────────────────┐
│ Level 2: Exportframe (export2.Exportframe)                  │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Error Sources:                                          │ │
│ │ - save_file() → No data in Nanomap.PMdict               │ │
│ │ - save_file() → File write permission error             │ │
│ │                                                         │ │
│ │ Error Handling:                                         │ │
│ │ - Checks if PMdict exists and has data                  │ │
│ │ - try/except in file I/O operations                     │ │
│ │ - messagebox for user notification                      │ │
│ └─────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────┘
                            │ Propagates upward
┌───────────────────────────┴─────────────────────────────────┐
│ Level 1: Other Components (claralib, newtonlib, TCSPClib)   │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ claralib.imageprocessor:                                │ │
│ │ - Error: Image file not found, corrupt image            │ │
│ │ - Handling: try/except with print, propagate to caller  │ │
│ │                                                         │ │
│ │ newtonlib.newtonspecopener:                             │ │
│ │ - Error: Invalid spectrum file format                   │ │
│ │ - Handling: Implicit, errors printed to console         │ │
│ │                                                         │ │
│ │ TCSPClib.TCSPCprocessor:                                │ │
│ │ - Error: Invalid TCSPC directory, missing files         │ │
│ │ - Handling: Check in load_tcspc(), print to console     │ │
│ │                                                         │ │
│ │ specfilesorter:                                         │ │
│ │ - Error: Directory access denied, file copy failure     │ │
│ │ - Handling: try/except in _copy_worker(), stop_event    │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Critical Error Points

| Location | Error Type | Severity | Handling | Recovery |
|----------|-----------|----------|----------|----------|
| **SpectrumData._read_file()** | FileNotFoundError | HIGH | Sets dataokay=False | XYMap filters out bad spectra |
| **XYMap.loadfiles()** | Thread pool exception | HIGH | try/except, prints traceback | Continues with loaded spectra |
| **XYMap.save_state()** | pickle.PickleError | MEDIUM | Returns False, prints error | User notified, can retry |
| **XYMap.load_state()** | pickle.UnpickleError | MEDIUM | Returns False, prints error | User notified, can load different file |
| **FileProcessorApp.spec_loadfiles()** | No files found | LOW | Print message, return early | User adjusts search parameters |
| **specfilesorter.sort_and_process()** | shutil.copy2 error | MEDIUM | try/except per file, continue | Partial copy completes |
| **Roihandler.construct()** | matplotlib error | LOW | Implicit matplotlib handling | User recreates ROI |

---

## Module Dependencies

### Import Graph

```
main9.py
├── tkinter (tk, ttk, filedialog, messagebox)
├── matplotlib (Figure, pyplot)
├── PIL (Image, ImageTk)
├── numpy
├── threading
├── pickle
├── os, sys, shutil, gc, traceback
│
├── lib9 ⟶ lib9.py
│   ├── numpy
│   ├── matplotlib (pyplot, Figure, widgets, patches, ticker)
│   ├── tkinter (tk, ttk, filedialog)
│   ├── scipy (optimize, special)
│   ├── PIL (Image)
│   ├── threading
│   ├── concurrent.futures (ThreadPoolExecutor)
│   ├── pickle, copy, traceback, os, gc
│   │
│   ├── mathlib3 ⟶ mathlib3.py
│   │   ├── numpy
│   │   └── scipy (special.wofz)
│   │
│   ├── deflib1 ⟶ deflib1.py
│   │   ├── numpy
│   │   ├── tkinter (filedialog, messagebox)
│   │   ├── os, json
│   │   └── scipy.signal (medfilt)
│   │
│   └── PMclasslib1 ⟶ PMclasslib1.py
│       └── numpy
│
├── deflib1 ⟶ deflib1.py (same as above)
│
├── claralib1 ⟶ claralib1.py
│   ├── numpy
│   ├── tkinter (tk)
│   ├── matplotlib (pyplot)
│   ├── PIL (Image)
│   └── scipy (optimize, ndimage)
│
├── export2 ⟶ export2.py
│   ├── tkinter (tk, filedialog)
│   ├── csv
│   └── numpy
│
├── newtonspeclib1 ⟶ newtonspeclib1.py
│   ├── tkinter (tk)
│   ├── numpy
│   └── matplotlib (pyplot)
│
├── HSI_debugger ⟶ HSI_debugger.py
│   └── (implementation details not analyzed)
│
└── TCSPClib ⟶ TCSPClib.py
    ├── tkinter (tk)
    ├── numpy
    ├── matplotlib (pyplot)
    └── os

```

### Circular Dependencies

**None detected.** The architecture maintains a clean dependency hierarchy:

```
main9.py (top level)
    ↓
lib9.py, claralib1.py, export2.py, newtonspeclib1.py, TCSPClib.py (component level)
    ↓
deflib1.py, mathlib3.py, PMclasslib1.py (utility level)
    ↓
numpy, scipy, matplotlib, tkinter (library level)
```

---

## Data Flow Summary

### Loading Hyperspectral Data

```
User clicks "Load HSI data" button
    ↓
FileProcessorApp.init_spec_loadfiles()
    ↓
FileProcessorApp.spec_loadfiles()
    ↓
    ├── Scan folder for files (os.walk)
    ├── Destroy existing Nanomap (if exists)
    ├── Recreate cmapframe, specframe
    └── Create new XYMap(files_processed, ...)
        ↓
        XYMap.__init__()
        ├── Store frames and parameters
        ├── Initialize data structures
        └── Call loadfiles()
            ↓
            ThreadPoolExecutor.map()
            └── For each file:
                SpectrumData.__init__(file, ...)
                    ↓
                    _read_file()
                    ├── Parse metadata
                    ├── Read WL, BG, PL arrays
                    ├── Subtract background
                    ├── Remove cosmic rays (if enabled)
                    └── Set dataokay flag
                        ↓
                        If dataokay: Add to XYMap.specs[]
            ↓
        After loading: Call build_gui()
            └── Create all GUI components
                ↓
                User can now interact with data
```

### Saving/Loading State

```
Save:
    User enters filename → clicks "Save" button
        ↓
    FileProcessorApp.saveNanomap(filename)
        ↓
    XYMap.save_state(filename)
        ├── Collect state: specs, PMdict, roilist, config
        ├── pickle.dump(state_dict, file)
        └── Return success/failure
            ↓
    messagebox shows result

Load:
    User enters filename → clicks "Load" button
        ↓
    FileProcessorApp.loadhsisaved(filename)
        ↓
    XYMap.load_state(filename)
        ├── pickle.load(file) → state_dict
        ├── Restore specs, PMdict, roilist, config
        ├── Call build_gui() to recreate interface
        └── Return success/failure
            ↓
    messagebox shows result
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-28 | Initial documentation - Complete program structure from main9.py |

---

*This document provides a complete hierarchical view of the SpecMap program structure, suitable for understanding code organization, debugging, and future development.*
