import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import os, sys
from PIL import Image, ImageTk
import lib1 as lib # type: ignore
import numpy as np

# defautl entries
defopdir = 'C:\\Users\\s368855\\Desktop\\PLEM\\Setup\\data\\test8_MoS2_ML_1sec_02mumsteps'
    #'C:\\Users\\s368855\\Desktop\\PLEM\\Setup\\data\\test3\\Data\\scan1'
    #'C:\\Users\\s368855\\Desktop\\PLEM\\Setup\\data\\test1\\scandata2_121'#'E:\\Promotion\\VP\\20240523\\scandata2_121'
    #'C:\\Users\\s368855\\Desktop\\PLEM\\Setup\\data\\test6_Mos2_ML_2sec'
defopnam = 'spectrum'
defopend = '.txt'
windowsize = [900, 900]

print('Starting...')
class FileProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Processor")
        self.createbuttons()

    def createbuttons(self):
        # Frame
        self.open_frame = tk.Frame(root, width=50, height=100, borderwidth=5, relief="ridge")
        self.open_frame.pack(anchor='nw')#fill='both', expand=True)
        # Folder selection
        self.folder_label = tk.Label(self.open_frame, text="Select Folder:")
        self.folder_label.pack()
        
        self.folder_entry = tk.Entry(self.open_frame, width=50)
        self.folder_entry.pack()
        self.folder_entry.insert(0, defopdir)
        self.folder_button = tk.Button(self.open_frame, text="Browse", command=self.browse_folder)
        self.folder_button.pack()
        # Filename input
        self.filename_label = tk.Label(self.open_frame, text="Enter Filename:")
        self.filename_label.pack()
        self.filename_entry = tk.Entry(self.open_frame, width=50)
        self.filename_entry.pack()
        self.filename_entry.insert(0, defopnam)
        # File format
        self.fileformat_label = tk.Label(self.open_frame, text="Enter File format:")
        self.fileformat_label.pack()
        self.fileformat_entry = tk.Entry(self.open_frame, width=50)
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
        self.cosmicthreshold = tk.Entry(self.loadframe, width=10)
        self.cosmicthreshold.grid(row=2, column=1)
        self.cosmicthreshold.insert(0, '20')
        tk.Label(self.loadframe, text="Cosmic Width:").grid(row=1, column=2)
        self.cosmicwidth = tk.Entry(self.loadframe, width=3)
        self.cosmicwidth.grid(row=2, column=2)
        self.cosmicwidth.insert(0, '3')


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
            self.cmapframe = tk.Frame(root, width=100, height=50, borderwidth=5, relief="raised")
            self.cmapframe.place(x=315, y=0)
            self.specframe = tk.Frame(root, borderwidth=5, relief="sunken")#, width=400, height=400)
            self.specframe.place(x=0, y=310)
            self.specframe.pack(fill=tk.BOTH, expand=True)

            self.Nanomap = lib.XYMap(files_processed, self.cmapframe, self.specframe, self.multiple_BG.get(), self.removecosmicsBool.get(), int(self.cosmicthreshold.get()), int(self.cosmicwidth.get())
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
