import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import os, sys, pickle
from PIL import Image, ImageTk
import lib9 as lib # type: ignore
import numpy as np
import deflib1 as deflib
import claralib1 as claralib
import export1 as xplib
import newtonspeclib1 as newtonlib

# default values for GUI
defaults = deflib.initdefaults()

print('Starting...')
class FileProcessorApp:
    def __init__(self, root, defaults):
        self.defaults = defaults
        self.root = root
        self.root.title("File Processor")
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
        self.open_frame = tk.Frame(Notebook, width=60, height=100, borderwidth=5, relief="ridge")
        self.open_frame.grid(row=0, column=0)
        # Folder selection
        self.SpecMapLoad_label = tk.Label(self.open_frame, text="Select folder with spectra for Hyperspectral processing")
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
        self.process_button = tk.Button(self.open_frame, text="Load data", command=self.spec_loadfiles)
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
        self.multiple_BG = tk.IntVar()
        self.multiple_BG.set(defaults['multiple_Background'])
        self.chkmultiple = tk.Checkbutton(self.bgframe, text="Multiple Backgrounds", variable=self.multiple_BG)
        self.chkmultiple.grid(row=0, column=0)

        self.linearBG = tk.IntVar()
        self.linearBG.set(defaults['linear_Background'])
        self.linearBGcheck = tk.Checkbutton(self.bgframe, text="Linear Background", variable=self.linearBG)
        self.linearBGcheck.grid(row=1, column=0)
        self.linearBG.set(defaults['linear_Background'])

        # Cosmic removal
        # add extra frame for cosmic removal onto loadframe
        self.cosmicframe = tk.Frame(self.loadframe, borderwidth=2, relief="sunken")
        self.cosmicframe.grid(row=0, column=1)

        self.removecosmicsBool = tk.IntVar()
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
    
        # Clara load frame  
        self.claraloadframe = tk.Frame(Notebook, width=60, height=100, borderwidth=5, relief="ridge")
        self.claraloadframe.grid(row=1, column=0)
        # Folder selection
        self.clara_label = tk.Label(self.claraloadframe, text="Select folder with spectra for Clara processing")
        self.clara_label.pack()
        self.clara_file_label = tk.Label(self.claraloadframe, text="Select File")
        self.clara_file_label.pack()

        # Clara process frame
        self.cl_file_entrystr = tk.StringVar()
        self.cl_file_entry = tk.Entry(self.claraloadframe, textvariable=self.cl_file_entrystr, width=60)
        self.cl_file_entry.pack()
        self.cl_file_entry.insert(0, defaults['clara_image'])
        self.cl_process_button = tk.Button(self.claraloadframe, text="Load data", command=self.cl_loadfiles)
        self.cl_process_button.pack(side=tk.RIGHT, anchor='center')
        spacer = tk.Frame(self.claraloadframe, width=10)
        spacer.pack(side=tk.RIGHT, anchor='center')
        # Process button
        self.cl_folder_button = tk.Button(self.claraloadframe, text="Browse", command= lambda: deflib.select_file(self.cl_file_entrystr))
        self.cl_folder_button.pack(side=tk.RIGHT, anchor='center')

        # frame to save the current hsi object
        self.saveframe = tk.Frame(Notebook, width=60, height=100, borderwidth=5, relief="ridge")
        self.saveframe.grid(row=2, column=0)
        # save the current hsi object
        self.save_label = tk.Label(self.saveframe, text="Save the current Data object")
        self.save_label.pack()
        self.savehsipath = tk.StringVar()
        self.save_entry = tk.Entry(self.saveframe, textvariable=self.savehsipath, width=60)
        self.save_entry.pack()
        self.save_entry.insert(0, defaults['save_hsi'])
        self.save_button = tk.Button(self.saveframe, text="Save", command=lambda: self.saveNanomap(self.savehsipath.get()))
        self.save_button.pack()
        # load saved spectra to current object
        self.load_label = tk.Label(self.saveframe, text="Load a saved Data object")
        self.load_label.pack()
        self.loadhsipath = tk.StringVar()
        self.load_entry = tk.Entry(self.saveframe, textvariable=self.loadhsipath, width=60)
        self.load_entry.pack()
        self.load_entry.insert(0, defaults['load_hsi_saved'])
        self.load_button = tk.Button(self.saveframe, text="Load", command=lambda: self.loadhsisaved(self.loadhsipath.get()))
        self.load_button.pack()

        # frame to load Newton spectrum
        self.newtonframe = tk.Frame(Notebook, width=60, height=100, borderwidth=5, relief="ridge")
        self.newtonframe.grid(row=0, column=1)
        # Newton spectrum load
        self.newton_label = tk.Label(self.newtonframe, text="Select Newton spectrum file")
        self.newton_label.grid(row=0, column=0)
        self.newton_file_label = tk.Label(self.newtonframe, text="Select File")
        self.newton_file_label.grid(row=1, column=0)
        self.newton_file_entrystr = tk.StringVar()
        self.newton_file_entry = tk.Entry(self.newtonframe, textvariable=self.newton_file_entrystr, width=60)
        self.newton_file_entry.grid(row=1, column=1)
        self.newton_file_entry.insert(0, defaults['newton_spectrum'])
        self.newton_process_button = tk.Button(self.newtonframe, text="Load data", command=self.newtonloadfiles)
        self.newton_process_button.grid(row=1, column=2)
        self.newton_folder_button = tk.Button(self.newtonframe, text="Browse", command= lambda: deflib.select_file(self.newton_file_entrystr))
        self.newton_folder_button.grid(row=1, column=3)
    
        if defaults['loadonstart'] == True:
            self.spec_loadfiles()

    def newtonloadfiles(self):
        file = self.newton_file_entry.get()
        self.newtonclass = newtonlib.newtonspecopener(self.nodeframes['Newton Spectrum'], file)

    # testcomment
    def spec_loadfiles(self):
        self.defaults = deflib.initdefaults()
        folder = self.folder_entry.get()
        filename = self.filename_entry.get()
        fileend = self.fileformat_entry.get()
        
        if not folder:
            messagebox.showerror("Error", "Please select a folder")
            return
        if not filename:
            messagebox.showerror("Error", "Please enter a filename")
            return
        files_processed = []
        for dirpath, _, filenames in os.walk(folder):
            for i in self.filter_substring(filenames, filename):
                if fileend in i:
                    file_path = os.path.join(dirpath, i)
                    files_processed.append(file_path) # can be accessed to process the files
        print('Files to process:' , len(files_processed))
        # frames for the colormap and spectral buttons
        if files_processed:
            try:
                self.cmapframe.destroy()
                self.specframe.destroy()
                del Nanomap
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
                self.multiple_BG.get(), self.linearBG.get(), self.removecosmicsBool.get(), 
                self.cosmicthreshold, self.cosmicwidth, self.cosmicremoval.get(), 
                self.defaults,
                )
            self.Exporter = xplib.Exportframe(self.nodeframes['Export'], self.Nanomap)
                
            print("Success", "Found and loaded {} files.".format(len(files_processed)))
        else:
            messagebox.showinfo("No Files", "No files found with the specified name.")

    def filter_substring(self, a, b):
        return [element for element in a if b in element]
    
    def cl_loadfiles(self):
        file = self.cl_file_entry.get()
        if not file:
            messagebox.showerror("Error", "Please select a file")
            return
        try:
            # clara 100x scaling factor 56.8 nm /pixel
            # adjust dx and dy for different scaling factors
            dx = 0.0568*2#0.0568 
            dy = 0.0568*2#0.0568
            self.claraimage = claralib.imageprocessor(self.nodeframes['Clara Image'], file, deflib.loadclaraimage, None, dx, dy)# 0.568, 0.568) 100x scaling
        except Exception as error:
            messagebox.showerror("Error", "Could not load Clara image. {}".format(error))
    
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()

    # pickle the Nanomap object, all subobjects and all their attributes
    def saveNanomap(self, filename):
        # check if the filename is empty
        if not filename:
            messagebox.showerror("Error", "Please enter a filename")
            return
        # check if the Nanomap object exists
        try:
            self.Nanomap
        except:
            messagebox.showerror("Error", "No Nanomap object to save")
            return
        # check if filename is a valid path
        canopen = False
        exists = False
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


if __name__ == "__main__":
    # Create the main window
    root = tk.Tk()
    root.geometry('{}x{}'.format(int(defaults['windowsize_X']), int(defaults['windowsize_Y'])))
    frame = tk.Frame(root)
    app = FileProcessorApp(root, defaults)

    # Run the application
    root.mainloop()