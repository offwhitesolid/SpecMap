import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import os, sys
from PIL import Image, ImageTk
import lib1 as lib # type: ignore
import numpy as np
import deflib1 as deflib

# defautl entries
defopdir = 'E:\\Promotion\\VP\\20240523\\scandata2_121'
    #'C:\\Users\\s368855\\Desktop\\PLEM\\Setup\\data\\test8_MoS2_ML_1sec_02mumsteps'
    #'C:\\Users\\s368855\\Desktop\\PLEM\\Setup\\data\\test3\\Data\\scan1'
    #'C:\\Users\\s368855\\Desktop\\PLEM\\Setup\\data\\test1\\scandata2_121'
    #'C:\\Users\\s368855\\Desktop\\PLEM\\Setup\\data\\test6_Mos2_ML_2sec'
defopnam = 'spectrum'
defopend = '.txt'
windowsize = [900, 900]

print('Starting...')
class FileProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Processor")
        self.createmenue()
        self.windownotebook(deflib.Notebooks)
        self.createbuttons(self.noteframes['Load Data'])

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
        self.noteframes = {}
        for i in range(len(notebookentries)):
            # add a new frame to the notebook and store it by its name in the frames dictionary
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=notebookentries[i])
            self.noteframes[notebookentries[i]] = frame

    def createbuttons(self, Notebook):
        # Frame
        self.open_frame = tk.Frame(Notebook, width=60, height=100, borderwidth=5, relief="ridge")
        self.open_frame.pack(anchor='nw')#fill='both', expand=True)
        # Folder selection
        self.folder_label = tk.Label(self.open_frame, text="Select Folder:")
        self.folder_label.pack()
        
        self.folder_entry = tk.Entry(self.open_frame, width=60)
        self.folder_entry.pack()
        self.folder_entry.insert(0, defopdir)
        self.folder_button = tk.Button(self.open_frame, text="Browse", command=self.browse_folder)
        self.folder_button.pack()
        # Filename input
        self.filename_label = tk.Label(self.open_frame, text="Enter Filename:")
        self.filename_label.pack()
        self.filename_entry = tk.Entry(self.open_frame, width=60)
        self.filename_entry.pack()
        self.filename_entry.insert(0, defopnam)
        # File format
        self.fileformat_label = tk.Label(self.open_frame, text="Enter File format:")
        self.fileformat_label.pack()
        self.fileformat_entry = tk.Entry(self.open_frame, width=60)
        self.fileformat_entry.pack()
        self.fileformat_entry.insert(0, defopend)
        # Process button
        self.process_button = tk.Button(self.open_frame, text="Load data", command=self.process_files)
        self.process_button.pack()
        self.multiple_BG = tk.IntVar()
        self.loadframe = tk.Frame(self.open_frame)
        self.loadframe.pack()
        self.chkmultiple = tk.Checkbutton(self.loadframe, text="Multiple Backgrounds", variable=self.multiple_BG)
        self.chkmultiple.grid(row=0, column=0)
        self.removecosmicsBool = tk.IntVar()
        self.removecosmicsBool.set(0)
        self.removecosmics = tk.Checkbutton(self.loadframe, text="Remove Cosmics", variable=self.removecosmicsBool)
        self.removecosmics.grid(row=0, column=1)
        tk.Label(self.loadframe, text="Cosmic Threshold:").grid(row=1, column=1)
        self.cosmicthresholdentry = tk.Entry(self.loadframe, width=10)
        self.cosmicthresholdentry.grid(row=2, column=1)
        self.cosmicthresholdentry.insert(0, '20')
        tk.Label(self.loadframe, text="Cosmic Width:").grid(row=1, column=2)
        self.cosmicwidthentry = tk.Entry(self.loadframe, width=3)
        self.cosmicwidthentry.grid(row=2, column=2)
        self.cosmicwidthentry.insert(0, '3')

        # spectrum frame
        #self.specplot = self.plotimage([320, 20], 'Pixel Image')
        #self.specplot.openimage("random_image.png", [50, 50])

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder_selected)

    def process_files(self):
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
            self.cmapframe = tk.Frame(self.noteframes['Process Data'], width=100, height=50, borderwidth=5, relief="raised")
            self.cmapframe.pack(fill=tk.BOTH)
            self.specframe = tk.Frame(self.noteframes['Process Data'], borderwidth=5, relief="sunken")#, width=400, height=400)
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

            self.Nanomap = lib.XYMap(files_processed, self.cmapframe, self.specframe, self.multiple_BG.get(), self.removecosmicsBool.get(), self.cosmicthreshold, self.cosmicwidth)
            print("Success", f"Found and loaded {len(files_processed)} files.")
        else:
            messagebox.showinfo("No Files", "No files found with the specified name.")

    def filter_substring(self, a, b):
        return [element for element in a if b in element]
    
if __name__ == "__main__":
    # Create the main window
    root = tk.Tk()
    root.geometry('{}x{}'.format(windowsize[0], windowsize[1]))
    frame = tk.Frame(root)
    app = FileProcessorApp(root)

    # Run the application
    root.mainloop()