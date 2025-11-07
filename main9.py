import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from matplotlib.figure import Figure
#from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import os, sys, pickle
from PIL import Image, ImageTk
import lib9 as lib # type: ignore
import numpy as np
import deflib1 as deflib
import claralib1 as claralib
import export1 as xplib
import newtonspeclib1 as newtonlib
import threading as thr
import matplotlib.pyplot as plt
import HSI_debugger as DBG
import TCSPClib as tcspclib
import shutil

class FileProcessorApp:
    def __init__(self, root, defaults):
        self.defaults = defaults
        self.root = root
        self.root.title("File Processor")
        self.multiple_BG = tk.IntVar()
        self.linearBG = tk.IntVar()
        self.removecosmicsBool = tk.IntVar()
        self.createmenue()
        self.windownotebook(deflib.Notebooks)
        self.createbuttons(self.nodeframes['Load Data'])

    def createmenue(self):
        # Create the menu bar
        menu_bar = tk.Menu(root)
        self.root.config(menu=menu_bar)
        deflib.create_menu(self.root, menu_bar)
    
    def windownotebook(self, notebookentries):
        # Create a notebook widget
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        # Create the frames for the notebook
        self.nodeframes = {}
        for i in range(len(notebookentries)):
            # add a new frame to the notebook and store it by its name in the frames dictionary
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=notebookentries[i])
            self.nodeframes[notebookentries[i]] = frame

    def createbuttons(self, Notebook):
        # Specmap Load Frame
        self.open_frame = tk.Frame(Notebook, width=100, height=100, borderwidth=5, relief="ridge")
        self.open_frame.grid(row=0, column=0)
        # Folder selection
        self.SpecMapLoad_label = tk.Label(self.open_frame, text="Select folder with spectra for Hyperspectral processing", width=100)
        self.SpecMapLoad_label.pack()
        self.folder_label = tk.Label(self.open_frame, text="Select Folder")
        self.folder_label.pack()
        
        self.folder_entry = tk.Entry(self.open_frame)
        self.folder_entry.pack(fill=tk.X)
        self.folder_entry.insert(0, defaults['data_file'])
        self.folder_button = tk.Button(self.open_frame, text="Browse", command=lambda: deflib.browse_folder(self.folder_entry))
        self.folder_button.pack()
        # Filename input
        self.filename_label = tk.Label(self.open_frame, text="Enter Filename")
        self.filename_label.pack()
        self.filename_entry = tk.Entry(self.open_frame)
        self.filename_entry.pack(fill=tk.X)
        self.filename_entry.insert(0, defaults['filename'])
        # File format
        self.fileformat_label = tk.Label(self.open_frame, text="Enter File format")
        self.fileformat_label.pack()
        self.fileformat_entry = tk.Entry(self.open_frame)
        self.fileformat_entry.pack(fill=tk.X)
        self.fileformat_entry.insert(0, defaults['file_extension'])
        # Process button
        self.process_button = tk.Button(self.open_frame, text="Load HSI data", command=self.init_spec_loadfiles)
        self.process_button.pack()
        # space between frames
        tk.Frame(self.open_frame, height=10).pack()

        # Load frame for background selection and cosmic removal place subframes inside
        self.loadframe = tk.Frame(self.open_frame)
        self.loadframe.pack()
        # BG selection
        # add extra frame for background selection onto loadframe
        self.bgframe = tk.Frame(self.loadframe, borderwidth=2, relief="sunken")
        self.bgframe.grid(row=0, column=0)
        self.multiple_BG.set(defaults['multiple_Background'])
        self.chkmultiple = tk.Checkbutton(self.bgframe, text="Multiple Backgrounds", variable=self.multiple_BG)
        self.chkmultiple.grid(row=0, column=0)
		# linear background
        self.linearBG.set(defaults['linear_Background'])
        self.linearBGcheck = tk.Checkbutton(self.bgframe, text="Linear Background", variable=self.linearBG)
        self.linearBGcheck.grid(row=1, column=0)
        self.linearBG.set(defaults['linear_Background'])
        # perform power correction 
        self.powercorrectionBool = tk.IntVar()
        self.powercorrectionBool.set(defaults['power_correction'])
        self.powercorrectioncheck = tk.Checkbutton(self.bgframe, text="Power Correction", variable=self.powercorrectionBool)
        self.powercorrectioncheck.grid(row=2, column=0)
        # below the frame add another frame for making multiple HSIs
        # spacings
        self.multiple_HSIs_inp_frame = tk.Frame(self.loadframe)
        self.multiple_HSIs_inp_frame.grid(row=4, column=0, columnspan=2)
        tk.Label(self.multiple_HSIs_inp_frame, text="Make Multiple HSIs from folders in selected dir").grid(row=0, column=0, columnspan=2)
        self.make_multiple_HSIsbool = tk.IntVar()
        self.make_multiple_HSIsbool.set(defaults['process_multiple_HSIs_bool'])
        self.process_multiple_HSIs = tk.Checkbutton(self.multiple_HSIs_inp_frame, text="Process Multiple HSIs", variable=self.make_multiple_HSIsbool).grid(row=1, column=0)
        # main directory for multiple HSIs entry
        tk.Label(self.multiple_HSIs_inp_frame, text="File Main Directory:").grid(row=2, column=0)
        self.multiple_HSIs_dir_entry = tk.Entry(self.multiple_HSIs_inp_frame, width=80)
        self.multiple_HSIs_dir_entry.grid(row=2, column=1)
        self.multiple_HSIs_dir_entry.insert(0, defaults['hsifilesorter_maindir'])
        self.Browse_multiple_HSIs_dir_button = tk.Button(self.multiple_HSIs_inp_frame, text="Browse", command=lambda: deflib.browse_folder(self.multiple_HSIs_dir_entry))
        self.Browse_multiple_HSIs_dir_button.grid(row=2, column=2)
        # save directory to save the HSI output images
        tk.Label(self.multiple_HSIs_inp_frame, text="Save Directory:").grid(row=3, column=0)
        self.multiple_HSIs_save_dir_entry = tk.Entry(self.multiple_HSIs_inp_frame, width=80)
        self.multiple_HSIs_save_dir_entry.grid(row=3, column=1)
        self.multiple_HSIs_save_dir_entry.insert(0, defaults['hsifilesorter_savedir'])
        self.Browse_multiple_HSIs_save_dir_button = tk.Button(self.multiple_HSIs_inp_frame, text="Browse", command=lambda: deflib.browse_folder(self.multiple_HSIs_save_dir_entry))
        self.Browse_multiple_HSIs_save_dir_button.grid(row=3, column=2)

        # Cosmic removal
        # add extra frame for cosmic removal onto loadframe
        self.cosmicframe = tk.Frame(self.loadframe, borderwidth=2, relief="sunken")
        self.cosmicframe.grid(row=0, column=1)

        self.removecosmicsBool.set(defaults['remove_cosmics'])
        self.removecosmics = tk.Checkbutton(self.cosmicframe, text="Remove Cosmics", variable=self.removecosmicsBool)
        self.removecosmics.grid(row=0, column=0)
        tk.Label(self.cosmicframe, text="Cosmic Removal function:").grid(row=1, column=0)
        self.cosmicremoval = ttk.Combobox(self.cosmicframe, values=list(deflib.cosmicfuncts.keys()), width=20)
        self.cosmicremoval.grid(row=1, column=1)
        self.cosmicremoval.set(list(deflib.cosmicfuncts.keys())[0])
        tk.Label(self.cosmicframe, text="Cosmic Threshold:").grid(row=2, column=0)
        self.cosmicthresholdentry = tk.Entry(self.cosmicframe, width=10)
        self.cosmicthresholdentry.grid(row=3, column=0)
        self.cosmicthresholdentry.insert(0, defaults['cosmic_threshold'])
        tk.Label(self.cosmicframe, text="Cosmic Width:").grid(row=2, column=1)
        self.cosmicwidthentry = tk.Entry(self.cosmicframe, width=10)
        self.cosmicwidthentry.grid(row=3, column=1)
        self.cosmicwidthentry.insert(0, defaults['cosmic_width'])
        tk.Label(self.cosmicframe, text="Laser Spotsize (nm):").grid(row=2, column=2)
        self.laserspotsizeentry = tk.Entry(self.cosmicframe, width=10)
        self.laserspotsizeentry.grid(row=3, column=2)
        self.laserspotsizeentry.insert(0, defaults['laser_spotsize_nm'])
    
        # Clara load frame  
        self.claraloadframe = tk.Frame(Notebook, width=60, height=100, borderwidth=5, relief="ridge")
        self.claraloadframe.grid(row=1, column=0)
        # Folder selection
        self.clara_label = tk.Label(self.claraloadframe, text="Select folder with spectra for Clara processing", width=100)
        self.clara_label.pack()
        self.clara_file_label = tk.Label(self.claraloadframe, text="Select File")
        self.clara_file_label.pack()

        # Clara process frame
        self.cl_file_entrystr = tk.StringVar()
        self.cl_file_entry = tk.Entry(self.claraloadframe, textvariable=self.cl_file_entrystr, width=113)
        self.cl_file_entry.pack()
        self.cl_file_entry.insert(0, defaults['clara_image'])
        self.cl_process_button = tk.Button(self.claraloadframe, text="Load Clara data", command=self.cl_loadfiles)
        self.cl_process_button.pack(side=tk.RIGHT, anchor='center')
        spacer = tk.Frame(self.claraloadframe, width=10)
        spacer.pack(side=tk.RIGHT, anchor='center')
        # add combobox to select the clara scaling factors (20x, 50x, 100x)
        self.cl_scaling_label = tk.Label(self.claraloadframe, text="Scaling Factor").pack(side=tk.LEFT, anchor='center')
        self.cl_scaling = ttk.Combobox(self.claraloadframe, values=list(claralib.cl_scalings.keys()), width=10)
        self.cl_scaling.pack(side=tk.LEFT, anchor='center')
        self.cl_scaling.set(list(claralib.cl_scalings.keys())[0])
        # Process button
        self.cl_folder_button = tk.Button(self.claraloadframe, text="Browse", command= lambda: deflib.select_file(self.cl_file_entrystr))
        self.cl_folder_button.pack(side=tk.RIGHT, anchor='center')

        # frame to save the current hsi object
        self.saveframe = tk.Frame(Notebook, width=100, height=100, borderwidth=5, relief="ridge")
        self.saveframe.grid(row=2, column=0)
        # save the current hsi object
        self.save_label = tk.Label(self.saveframe, text="Save the current Data object")
        self.save_label.pack()
        self.savehsipath = tk.StringVar()
        self.save_entry = tk.Entry(self.saveframe, textvariable=self.savehsipath, width=117)
        self.save_entry.pack()
        self.save_entry.insert(0, defaults['save_hsi'])
        self.save_button = tk.Button(self.saveframe, text="Save", command=lambda: self.saveNanomap(self.savehsipath.get()))
        self.save_button.pack()
        # load saved spectra to current object
        self.load_label = tk.Label(self.saveframe, text="Load a saved Data object")
        self.load_label.pack()
        self.loadhsipath = tk.StringVar()
        self.load_entry = tk.Entry(self.saveframe, textvariable=self.loadhsipath, width=117)
        self.load_entry.pack()
        self.load_entry.insert(0, defaults['load_hsi_saved'])
        self.load_button = tk.Button(self.saveframe, text="Load", command=lambda: self.loadhsisaved(self.loadhsipath.get()))
        self.load_button.pack()

        # frame to load Newton spectrum
        self.newtonframe = tk.Frame(Notebook, width=100, height=100, borderwidth=5, relief="ridge")
        self.newtonframe.grid(row=3, column=0)
        # Newton spectrum load
        self.newton_label = tk.Label(self.newtonframe, text="Select Newton spectrum file", width=85)
        self.newton_label.grid(row=0, column=1)
        self.newton_file_label = tk.Label(self.newtonframe, text="Select File")
        self.newton_file_label.grid(row=1, column=0)
        self.newton_file_entrystr = tk.StringVar()
        self.newton_file_entry = tk.Entry(self.newtonframe, textvariable=self.newton_file_entrystr, width=97)
        self.newton_file_entry.grid(row=1, column=1)
        self.newton_file_entry.insert(0, defaults['newton_spectrum'])
        self.newton_process_button = tk.Button(self.newtonframe, text="Load Newton data", command=self.newtonloadfiles)
        self.newton_process_button.grid(row=2, column=1)
        self.newton_folder_button = tk.Button(self.newtonframe, text="Browse", command= lambda: deflib.select_file(self.newton_file_entrystr))
        self.newton_folder_button.grid(row=1, column=3)

        # frame to load TCSPC data
        self.tcspcframe = tk.Frame(Notebook, width=100, height=100, borderwidth=5, relief="ridge")
        self.tcspcframe.grid(row=4, column=0)
        # TCSPC load
        self.tcspc_label = tk.Label(self.tcspcframe, text="Select TCSPC directory", width=86)
        self.tcspc_label.grid(row=0, column=1)
        self.tcspc_file_label = tk.Label(self.tcspcframe, text="TCSPC dir")
        self.tcspc_file_label.grid(row=1, column=0)
        self.tcspc_maindir_entrystr = tk.StringVar()
        self.tcspc_maindir_entry = tk.Entry(self.tcspcframe, textvariable=self.tcspc_maindir_entrystr, width=90)
        self.tcspc_maindir_entry.grid(row=1, column=1)
        self.tcspc_maindir_entry.insert(0, defaults['tcspc_maindir'])
        self.tcspc_subdir_label = tk.Label(self.tcspcframe, text="save dir")
        self.tcspc_subdir_label.grid(row=2, column=0)
        self.tcspc_subdir_entrystr = tk.StringVar()
        self.tcspc_subdir_entry = tk.Entry(self.tcspcframe, textvariable=self.tcspc_subdir_entrystr, width=90)
        self.tcspc_subdir_entry.grid(row=2, column=1)
        self.tcspc_process_button = tk.Button(self.tcspcframe, text="Load TCSPC data", command=self.tcspcloadfiles)
        self.tcspc_process_button.grid(row=3, column=1)
        self.tcspc_folder_button = tk.Button(self.tcspcframe, text="Browse", command= lambda: deflib.select_folder(self.tcspc_maindir_entrystr))
        self.tcspc_folder_button.grid(row=1, column=3)

        self.TCSPC_Processor = tcspclib.TCSPCprocessor(self.nodeframes['TCSPC'], self.tcspc_maindir_entry, self.tcspc_subdir_entry)
        self.TCSPC_Processor.build_frame()

        # load HSI on start ater constructing the GUI
        if defaults['loadonstart'] == True:
            self.spec_loadfiles()
        
        # build specfilesorter frame on the specfilesorter notebook
        self.specfilesorterframe = specfilesorter(
            self.nodeframes['HSI File Sorter'], 
            defaults['hsifilesorter_maindir'], 
            defaults['hsifilesorter_filename'], 
            defaults['hsifilesorter_fileend'], 
            defaults['hsifilesorter_savedir'], 
            defaults['hsifilesorter_processdir']
            )
    
    def tcspcloadfiles(self):
        file = self.tcspc_maindir_entry.get()
        # check, if file is valid
        if not file:
            print('Please select a TCSPC main directory')
            return
        else: 
            # check if file exists
            if not os.path.exists(file):
                print('TCSPC main directory does not exist:', file)
                return
        
        self.TCSPC_Processor.filepath = file
        self.TCSPC_Processor.load_tcspc()

    def newtonloadfiles(self):
        file = self.newton_file_entry.get()        
        self.newtonclass = newtonlib.newtonspecopener(self.nodeframes['Newton Spectrum'], file)

    def init_spec_loadfiles(self):
        if self.make_multiple_HSIsbool.get() == True:
            # try to get File main directory
            filemaindir = self.multiple_HSIs_dir_entry.get()
            savedir = self.multiple_HSIs_save_dir_entry.get()
            if not filemaindir:
                print("Error while loading HSI data, please select a main directory for multiple HSIs")
                self.spec_loadfiles()
            if not savedir:
                print("Error while loading HSI data, please select a save directory for multiple HSIs")
                self.spec_loadfiles()
            else:
                foldersinmaindir = [f for f in os.listdir(filemaindir) if os.path.isdir(os.path.join(filemaindir, f))]
                for folder in foldersinmaindir:
                    fullfolderpath =  os.path.join(filemaindir, folder)
                    self.folder_entry.delete(0, tk.END)
                    self.folder_entry.insert(0, fullfolderpath)
                    filename = str(folder+"_HSI.png")
                    imagesavefolder = os.path.join(savedir, filename)
                    try:
                        self.spec_loadfiles()
                        # create intensity colormap and save spectra
                        self.Nanomap.buildandPlotIntCmap(savetoimage=imagesavefolder)
                    except:
                        print("Error processing folder:", fullfolderpath)
                        continue
                
        else:
            self.spec_loadfiles()
        
    # testcomment
    def spec_loadfiles(self):
        # close all open matplotlib windows        # close all running threads
        plt.close('all')
        for thread in thr.enumerate():
            if thread.name != 'MainThread':
                if hasattr(thread, 'stop_event'):
                    thread.stop_event.set()
		
        # kill any existing Nanomap object
        try:
            self.Nanomap.on_close()
            del self.Nanomap
            self.cmapframe.destroy()
            self.specframe.destroy()
            del self.Exporter
        except:
             pass
        self.defaults = deflib.initdefaults()
        folder = self.folder_entry.get()
        filename = self.filename_entry.get()
        fileend = self.fileformat_entry.get()
        
        if not folder:
            print("Error while loading HSI data, please select a folder")
            return
        if not filename:
            print("Error while loading HSI data, please select a folder")
            return
        files_processed = []
        for dirpath, _, filenames in os.walk(folder):
            for i in self.filter_substring(filenames, filename):
                if fileend in i:
                    file_path = os.path.join(dirpath, i)
                    files_processed.append(file_path) # can be accessed to process the files
        # frames for the colormap and spectral buttons
        if files_processed:
            try:
                self.cmapframe.destroy()
                self.specframe.destroy()
                del self.Nanomap
            except:
                pass
            self.cmapframe = tk.Frame(self.nodeframes['Hyperspectra'], width=100, height=50, borderwidth=5, relief="raised")
            self.cmapframe.pack(fill=tk.BOTH)
            self.specframe = tk.Frame(self.nodeframes['Hyperspectra'], borderwidth=5, relief="sunken")#, width=400, height=400)
            self.specframe.pack(fill=tk.BOTH, expand=True)
            
            # get the cosmic threshold and width
            try:
                self.cosmicthreshold = int(self.cosmicthresholdentry.get())
            except:
                self.cosmicthreshold = 20
                self.cosmicthresholdentry.insert(0, '20')
            try:
                self.cosmicwidth = int(self.cosmicwidthentry.get())
            except:
                self.cosmicwidth = 3
                self.cosmicwidthentry.insert(0, '3')

            self.Nanomap = lib.XYMap(
                files_processed, self.cmapframe, self.specframe, 
                bool(self.multiple_BG.get()), bool(self.linearBG.get()), bool(self.removecosmicsBool.get()), 
                self.cosmicthreshold, self.cosmicwidth, self.cosmicremoval.get(), 
                self.defaults,
                )
            if self.powercorrectionBool.get() == 1:
                self.Nanomap.powercorrection()
            self.Exporter = xplib.Exportframe(self.nodeframes['Export'], self.Nanomap)
                
            print("Success, Found and loaded {} files.".format(len(files_processed)))
        else:
            print("No files found with the specified name.")

    def filter_substring(self, a, b):
        return [element for element in a if b in element]
    
    def cl_loadfiles(self):
        file = self.cl_file_entry.get()
        if not file:
            print("Error", "Please select a file")
            return
        try:
            # clara 100x scaling factor 56.8 nm /pixel
            # adjust dx and dy for different scaling factors
            dx = 0.0568*2#0.0568 
            dy = 0.0568*2#0.0568
            scaling = self.cl_scaling.get()
            if scaling in claralib.cl_scalings.keys():
                dx = claralib.cl_scalings[scaling]
                dy = claralib.cl_scalings[scaling]
            self.claraimage = claralib.imageprocessor(self.nodeframes['Clara Image'], file, deflib.loadclaraimage, None, dx, dy)# 0.568, 0.568) 100x scaling
        except Exception as error:
            print("Error", "Could not load Clara image. {}".format(error))
    
    def on_closing(self):
        pass

    # pickle the Nanomap object, all subobjects and all their attributes
    def saveNanomap(self, filename):
        # check if the filename is empty
        if not filename:
            print("Error", "Please enter a filename")
            return
        # check if the Nanomap object exists
        try:
            self.Nanomap
        except:
            print("Error", "No Nanomap object to save")
            return
        # check if filename is a valid path
        canopen = False
        while os.path.exists(filename):
                filename = deflib.increment_filename(filename)
                canopen = True
                with open(filename, 'wb') as output: # clear the file
                    pass
        else:
            # check if / is in the filename
            if '/' in filename:
                # create the path
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                canopen = True

        if canopen:
            savearray = []
            for i in self.Nanomap.specs:
                savearray.append(i)
            with open(filename, 'ab') as output:
                pickle.dump(savearray, output)
        else:
            print(canopen, filename)
            print('Invalid filename to save HSI data')
    
    def loadhsisaved(self, filename):
        # check if the filename is empty
        if not filename:
            print('Please enter a filename to load')
            return 
        # check if filename is a valid path
        if os.path.exists(filename):
            with open(filename, 'rb') as input:
                specs = pickle.load(input)
            # check if the Nanomap object exists
            try:
                self.Nanomap
                self.Nanomap.specs = specs  
                self.Nanomap.SpecdataintoMatrix(True)                
            except:
                print('No Nanomap object to load data into')
                return

# sort files and multiple HSI processings
# what is the taks of specfilesorter: 
# 1. Step:
# select a dir with multiple measurement days, on each day HSIs were measured, but some of them went for multiple days. Therefore find the "deepest" folder instance for each folder name. 
# then create a list of all days on which HSIs were measured. For each day, on which on the following day a measurement appears, check if they must be merged. Merge them into a single folder. If no measurement followed, just copy the folder to the savedir (no merge needed)
# 2. Step: 
# for each HSI in savedir, process the HSI with the FileProcessorApp class, create a HSI image, then save it to the savedir as a image. by the HSI name. 

class specfilesorter:
    def __init__(self, tkroot, maindir, filename, fileend, savedir, processdir):
        self.tkroot = tkroot
        self.maindir = maindir
        self.filename = filename
        self.fileend = fileend
        self.savedir = savedir
        self.maindir_entrystr = tk.StringVar()
        self.maindir_entrystr.set(maindir)
        self.filename_entrystr = tk.StringVar()
        self.filename_entrystr.set(filename)
        self.fileend_entrystr = tk.StringVar()
        self.fileend_entrystr.set(fileend)
        self.savedir_entrystr = tk.StringVar()
        self.savedir_entrystr.set(savedir)
        self.processdir_entrystr = tk.StringVar()
        self.processdir_entrystr.set(processdir)
        
        self.files_processed = []
        # UI state
        self.scan_results = []
        self.selected_items = []
        self.merge_var = tk.IntVar(value=0)
        self.buildGUI()

    def buildGUI(self):
        # Main container
        self.sortframe = ttk.LabelFrame(self.tkroot, text="HSI File Sorter", padding=(8, 8))
        self.sortframe.pack(fill='both', expand=True)

        # Left: inputs and controls
        left = tk.Frame(self.sortframe)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=6)

        # Main dir
        tk.Label(left, text="Main directory:").grid(row=0, column=0, sticky='w')
        self.maindir_entry = tk.Entry(left, textvariable=self.maindir_entrystr, width=63)
        self.maindir_entry.grid(row=1, column=0, columnspan=4, sticky='w')
        tk.Button(left, text="Browse...", command=lambda: deflib.browse_folder(self.maindir_entry)).grid(row=1, column=2, padx=4)

        # Filename pattern
        tk.Label(left, text="Filename contains:").grid(row=2, column=0, sticky='w', pady=(8, 0))
        self.filename_entry = tk.Entry(left, textvariable=self.filename_entrystr, width=20)
        self.filename_entry.grid(row=3, column=0, sticky='w')

        # Fileend pattern
        tk.Label(left, text="File extension contains:").grid(row=2, column=1, sticky='w', pady=(8, 0))
        self.fileend_entry = tk.Entry(left, textvariable=self.fileend_entrystr, width=12)
        self.fileend_entry.grid(row=3, column=1, sticky='w')

        # Save dir
        tk.Label(left, text="Save directory:").grid(row=4, column=0, sticky='w', pady=(8, 0))
        self.savedir_entry = tk.Entry(left, textvariable=self.savedir_entrystr, width=63)
        self.savedir_entry.grid(row=5, column=0, columnspan=4, sticky='w')
        tk.Button(left, text="Browse...", command=lambda: deflib.browse_folder(self.savedir_entry)).grid(row=5, column=2, padx=4)

        # Process dir (where merged/processed folders are written)
        tk.Label(left, text="Process directory:").grid(row=6, column=0, sticky='w', pady=(8, 0))
        self.processdir_entry = tk.Entry(left, textvariable=self.processdir_entrystr, width=63)
        self.processdir_entry.grid(row=7, column=0, columnspan=4, sticky='w')
        tk.Button(left, text="Browse...", command=lambda: deflib.browse_folder(self.processdir_entry)).grid(row=7, column=2, padx=4)

        # Options
        tk.Checkbutton(left, text="Merge consecutive days", variable=self.merge_var).grid(row=8, column=0, columnspan=2, sticky='w', pady=(8, 0))

        # Control buttons
        self.btnframe = tk.Frame(left)
        self.btnframe.grid(row=9, column=0, columnspan=3, pady=(12, 0), sticky='w')
        self.scan_button = tk.Button(self.btnframe, text="Scan", width=12, command=self.scan_maindir)
        self.scan_button.pack(side=tk.LEFT)
        self.preview_button = tk.Button(self.btnframe, text="Preview Selected", width=14, command=self.preview_selected)
        self.preview_button.pack(side=tk.LEFT, padx=6)
        self.process_button_sf = tk.Button(self.btnframe, text="Process Selected", width=14, command=self.sort_and_process)
        self.process_button_sf.pack(side=tk.LEFT)
        self.clear_button = tk.Button(self.btnframe, text="Clear", width=8, command=self.clear_list)
        self.clear_button.pack(side=tk.LEFT, padx=6)
        # cancel button for background copy (disabled until a job runs)
        self.cancel_button = tk.Button(self.btnframe, text="Cancel", width=8, command=self.cancel_copy, state='disabled')
        self.cancel_button.pack(side=tk.LEFT, padx=6)

        # Right: results treeview
        right = tk.Frame(self.sortframe)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=6)

        cols = ("#1", "#2", "#3")
        self.tree = ttk.Treeview(right, columns=cols, show='headings', selectmode='extended')
        self.tree.heading('#1', text='Folder')
        self.tree.heading('#2', text='Files')
        self.tree.heading('#3', text='Path')
        self.tree.column('#1', width=180)
        self.tree.column('#2', width=60, anchor='center')
        self.tree.column('#3', width=380)

        vsb = ttk.Scrollbar(right, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.LEFT, fill=tk.Y)

        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

        # Progress bar
        # below buttonframe, ad a progress barframe
        self.progressfame = tk.Frame(left)
        self.progressfame.grid(row=10, column=0, columnspan=3, pady=(12, 0), sticky='we')
        lablel = tk.Label(self.progressfame, text="Progress:").pack(side=tk.LEFT)
        self.progress = ttk.Progressbar(self.progressfame, orient='horizontal', mode='determinate')
        self.progress.pack(side=tk.LEFT, padx=8, pady=(0, 8), fill=tk.X, expand=True)
        #self.progress.pack(fill=tk.X, padx=8, pady=(0, 8))
        #self.progress.pack(side=tk.LEFT, padx=8, pady=(12, 0), fill=tk.X, expand=True)
    
    def sort_and_process(self):
        # Prepare processing tasks and launch background worker thread to copy files safely
        # Operate on the currently scanned folders (self.scan_results)
        # 1) For each unique folder name, create a folder with that name inside the Process directory
        # 2) If duplicates (same folder name) exist among scanned results, only the first instance is used
        # 3) Copy files matching filename and file extension filters into the created process folder
        # 4) leave a `pass` placeholder for further per-folder processing

        if not self.scan_results:
            print("No data", "No scanned folders available. Run Scan first.")
            return

        savedir = self.savedir_entry.get()
        if not savedir:
            print("No process directory", "Please select a Process directory before processing.")
            return
        # ensure processdir exists
        try:
            os.makedirs(savedir, exist_ok=True)
        except Exception as e:
            print("Error", f"Could not create/access Process directory: {e}")
            return

        # build a mapping of unique folder name -> first seen path
        unique = {}
        for name, count, path in self.scan_results:
            if name not in unique:
                unique[name] = path

    # collect files to copy per unique folder and compute total file count
        filename_filter = self.filename_entry.get()
        fileend_filter = self.fileend_entry.get()
        tasks = []  # list of (folder_name, src_path, [files])
        total_files = 0
        for name, src in unique.items():
            try:
                entries = os.listdir(src)
            except Exception as e:
                print('Could not list directory', src, e)
                continue
            matched = []
            for f in entries:
                full = os.path.join(src, f)
                if not os.path.isfile(full):
                    continue
                if (not filename_filter or filename_filter in f) and (not fileend_filter or fileend_filter in f):
                    matched.append(f)
            if matched:
                tasks.append((name, src, matched))
                total_files += len(matched)

        if not tasks:
            print("No files", "No files matching the filters were found in scanned folders.")
            return

        # perform copying with progress
        copied = 0
        self.progress['maximum'] = total_files
        for name, src, files in tasks:
            target_dir = os.path.join(savedir, name)
            os.makedirs(target_dir, exist_ok=True)
            # copy each matching file
            for f in files:
                srcfile = os.path.join(src, f)
                dstfile = os.path.join(target_dir, f)
                try:
                    shutil.copy2(srcfile, dstfile)
                except Exception as e:
                    print('Failed to copy', srcfile, '->', dstfile, e)
                copied += 1
                # update progress
                try:
                    self.progress['value'] = copied
                    self.sortframe.update_idletasks()
                except Exception:
                    if not tasks:
                        print("No files", "No files matching the filters were found in scanned folders.")
                        return

                    # store task info for worker
                    self._copy_tasks = tasks
                    self._savedir = savedir
                    self._total_files = total_files
                    self._copied_count = 0
                    self._stop_event = thr.Event()
                    self._lock = thr.Lock()

                    # disable controls that should not be used while copying
                    self.scan_button.config(state='disabled')
                    self.preview_button.config(state='disabled')
                    self.process_button_sf.config(state='disabled')
                    self.clear_button.config(state='disabled')
                    self.cancel_button.config(state='normal')

                    # prepare progress
                    self.progress['maximum'] = total_files
                    self.progress['value'] = 0

                    # launch background thread (daemon so it won't block exit)
                    self._copy_thread = thr.Thread(target=self._copy_worker, daemon=True)
                    self._copy_thread.start()

    def _copy_worker(self):
        """Background worker that copies files and updates progress via the main thread."""
        import shutil
        try:
            for name, src, files in self._copy_tasks:
                if self._stop_event.is_set():
                    break
                target_dir = os.path.join(self._savedir, name)
                os.makedirs(target_dir, exist_ok=True)
                for f in files:
                    if self._stop_event.is_set():
                        break
                    srcfile = os.path.join(src, f)
                    dstfile = os.path.join(target_dir, f)
                    try:
                        shutil.copy2(srcfile, dstfile)
                    except Exception as e:
                        print('Failed to copy', srcfile, '->', dstfile, e)
                    # increment counter in thread-safe manner
                    with self._lock:
                        self._copied_count += 1
                        copied = self._copied_count
                    # schedule a GUI update on the main thread
                    try:
                        self.sortframe.after(0, self._update_progress, copied)
                    except Exception:
                        pass
                # placeholder for further processing per folder
                # pass
        finally:
            # schedule finalizer on main thread
            self.sortframe.after(0, self._copy_finished)

    def _update_progress(self, value):
        try:
            self.progress['value'] = value
        except Exception:
            pass

    def cancel_copy(self):
        # signal worker to stop
        if hasattr(self, '_stop_event') and self._stop_event:
            self._stop_event.set()
            # disable cancel to avoid repeated clicks
            try:
                self.cancel_button.config(state='disabled')
            except Exception:
                pass

    def _copy_finished(self):
        # re-enable controls
        try:
            self.scan_button.config(state='normal')
            self.preview_button.config(state='normal')
            self.process_button_sf.config(state='normal')
            self.clear_button.config(state='normal')
            self.cancel_button.config(state='disabled')
        except Exception:
            pass
        # inform user
        copied = getattr(self, '_copied_count', 0)
        total = getattr(self, '_total_files', 0)
        if getattr(self, '_stop_event', None) and self._stop_event.is_set():
            print("Cancelled", f"Copy cancelled after {copied} of {total} files.")
        else:
            print("Done", f"Copied {copied} files into {getattr(self, '_savedir', '')}")
        # reset progress
        try:
            self.progress['value'] = 0
        except Exception:
            pass
        self.scan_results.sort()
        self.populate_list()
    
    def scan_maindir(self):
        folder = self.maindir_entry.get()
        filename_filter = self.filename_entry.get()
        fileend_filter = self.fileend_entry.get()

        if not folder:
            print("Error", "Please select a main directory to scan.")
            return
        if not os.path.exists(folder):
            print("Error", "The selected main directory does not exist.")
            return

        self.scan_results = []
        for dirpath, dirnames, filenames in os.walk(folder):
            matched_files = []
            for f in filenames:
                if (not filename_filter or filename_filter in f) and (not fileend_filter or fileend_filter in f):
                    matched_files.append(f)
            if matched_files:
                folder_name = os.path.basename(dirpath)
                file_count = len(matched_files)
                self.scan_results.append((folder_name, file_count, dirpath))

        self.scan_results.sort()
        self.populate_list()

    def populate_list(self):
        self.tree.delete(*self.tree.get_children())
        for name, count, path in self.scan_results:
            self.tree.insert('', 'end', values=(name, count, path))

    def on_tree_select(self, event):
        sel = self.tree.selection()
        self.selected_items = [self.tree.set(i, '#3') for i in sel]

    def preview_selected(self):
        # Open the folder(s) in file explorer where possible
        if not self.selected_items:
            print("No selection", "Please select a folder to preview.")
            return
        for p in self.selected_items:
            try:
                if sys.platform == 'win32':
                    os.startfile(p)
                else:
                    # cross-platform fallback
                    import subprocess
                    subprocess.run(['xdg-open', p], check=False)
            except Exception as e:
                print('Could not open folder', p, e)

    def clear_list(self):
        self.tree.delete(*self.tree.get_children())
        self.scan_results = []
        self.selected_items = []

    def make_HSI_from_folder(self, folder):
        # set self.folder_entry, self.filename_entry and self.fileformat_entry accordingly
        pass

        #self.folder_entry.delete(0, tk.END)
        #self.folder_entry.insert(0, folder)


def pressclose(root, app):
    # Get all running threads
    for thread in thr.enumerate():
        # Skip the main thread
        if thread is not thr.main_thread():
            # Set daemon to True so thread terminates when main program exits
            thread.daemon = True
    # Destroy the root window
    root.destroy()
    app.on_closing()

if __name__ == "__main__":
    # init debugger
    debugger = DBG.main_Debugger()

    # Create the main window

    # default values for GUI
    defaults = deflib.initdefaults()
    print('Starting...')

    root = tk.Tk()
    root.geometry('{}x{}'.format(int(defaults['windowsize_X']), int(defaults['windowsize_Y'])))
    frame = tk.Frame(root)
    app = FileProcessorApp(root, defaults)

    # Set the protocol for closing the window
    root.protocol("WM_DELETE_WINDOW", lambda: pressclose(root, app))

    # Run the application
    root.mainloop()