import os
import re
import numpy as np
import matplotlib.pyplot as plt
from tkinter import messagebox
import tkinter as tk
from tkinter import filedialog, messagebox

SpectDataFloats = ['Slit Width (µm)', 'Central Wavelength (nm)',
                   'Cooling Temperature (°C)',
                   'Exposure Time (s)',
                   #'Wavelength First Pixel (nm)', # is obtained from WL
                   #'Wavelength Last Pixel (nm)',
                   'Delta Wavelength (nm)',
                   'x-position',
                   'y-position',
                   'z-position',
                   'Short Wavelength (nm)',
                   'Long Wavelength (nm)',
                   'magnification']

class SpectrumData:
    def __init__(self, filename, WL, BG, loadeachbg = False, linearbg=False, powernW=0):
        self.loadeachbg = loadeachbg
        self.linearbg = linearbg
        self.WL = WL
        if self.loadeachbg == True:
            self.BG = []
        else:
            self.BG = BG
        self.filename = filename
        self.readinkeys = ['BG', 'PL'] # WL is defined in XYMap
        self.openFstate = [] # open floats state from metadata
        self.openDstate = [] # open Data from spectrometer
        self.dataokay = False    # set True if everything openend properly
        self.data = {}
        self.roistore = {}
        self.PL = []
        self.powernW = powernW
        self._read_file()

    def _read_file(self):
        with open(self.filename, 'r') as file:
            lines = file.readlines()

        # Process lines to store variables
        startreaddata = False
        for line in lines:
            if ':' in line:
                key, value = map(str.strip, line.split(':', 1))
                if key in SpectDataFloats:
                    try:
                        self.data[key] = float(value)
                    except:
                        self.data[key] = value
                        self.openFstate.append(False)
                else:
                    self.data[key] = value
            elif '\t' in line:  # Data lines with tabs
                parts = line.split()
                if startreaddata == False:
                    count = 0
                    # start reading if at least two keys in the line
                    for i in parts:
                        if i in self.readinkeys:
                            count += 1
                    if count > 1:
                        startreaddata = True
                elif startreaddata == True:
                    try:
                        if self.loadeachbg == True:
                            self.BG.append(int(parts[1]))
                        #self.WL.append(float(parts[0]))  WL is only read once by XYMap since each SpectrumData has the same WL-axis
                        self.PL.append(int(parts[2]))
                    except Exception as e:
                        messagebox.showerror("Error", str(e))
        if self.loadeachbg == True and self.linearbg == True:
            av = np.mean(self.BG)
            for i in range(len(self.BG)):
                self.BG[i] = av

        try:
            self.PLB = np.subtract(self.PL, self.BG).tolist() # add PLB = PL-BG
        except Exception as e:
            messagebox.showerror("Error", str(e))
        # write openstate list
        for i in SpectDataFloats:
            if i not in list(self.data.keys()):
                self.openFstate.append(False)
        if len(self.WL) == 0:
            self.openDstate.append(None)
        if len(self.BG) == 0:
            self.openDstate.append(None)
        if len(self.PL) == 0:
            self.openDstate.append(None)
        self.setOK()

    def setOK(self):
        if False in self.openFstate:
            pass
        elif None in self.openDstate:
            pass
        else:
            self.dataokay = True

    # return a specific attribute of this class
    def get_attribute(self, attr_name:str):
        try:
            return getattr(self, attr_name)
        except AttributeError as e:
            print("Attribute {} not found in class SpectrumData.".format(attr_name))

class OpenSpec:
    def __init__(self, path, linearbg=False, loadeachbg=False):#, removecosmics=False, cosmicthreshold=20, cosmicpixels=3, remcosmicfunc='median'):
        self.path = path
        self.spectra = {}
        self.readinkeys = ['WL']
        self.linearbg = linearbg
        self.loadeachbg = loadeachbg
        os.chdir(self.path)
        self.fnames = os.listdir(self.path)
        imax = len(self.fnames)
        i = 0
        while i < imax: 
            if '.txt' not in self.fnames[i]:
                self.fnames.pop(i)
                imax -= 1
            i+=1
        self.specs = {}

    def loadfiles(self):
        # read WL axis once for all files (must be same for all datafiles)
        gotWL = False
        gotBG = False
        i = 0
        self.WL = []
        self.BG = []
        while gotWL == False or gotBG == False:
            try:
                with open(self.fnames[i], 'r') as file:
                    lines = file.readlines()
            except Exception as e:
                print('Error While trying to read WL axis. No WL found in {} Files. {}'.format(i, str(e)))
            # Process lines to store variables
            startreaddata = False 
            for line in lines:
                if '\t' in line:  # Data lines with tabs
                    parts = line.split()
                    if startreaddata == False:
                        count = 0
                        # start reading if at least two keys in the line
                        for j in parts:
                            if j in self.readinkeys:
                                count += 1
                        if count > 0:
                            startreaddata = True
                    elif startreaddata == True:
                        if gotWL == False:
                            try:
                                self.WL.append(float(parts[0]))
                            except Exception as e:
                                print('Error While trying to read WL axis from {}. {}'.format(self.fnames[i], str(e)))
                        if gotBG == False or self.loadeachbg == False:
                            try:
                                self.BG.append(float(parts[1]))
                            except Exception as e:
                                print('Error While trying to read WL axis from {}. {}'.format(self.fnames[i], str(e)))

            i += 1
            if len(self.WL) > 1:
                gotWL = True
            if len(self.BG) > 1:
                gotBG = True
        
        if self.loadeachbg == False:
            if self.linearbg == True:
                av = np.mean(self.BG)
                for i in range(len(self.BG)):
                    self.BG[i] = av

        for i in self.fnames:
            powernW = getpowerbyname(i)
            specobj = SpectrumData(i, self.WL, self.BG, self.loadeachbg, self.linearbg, powernW)
            if specobj.dataokay == True:
                #self.specs.append(specobj)
                self.specs[i] = specobj

def getpowerbyname(name):
    power = '0'
    if 'nw' in name:
        try:
            power = name.split('nw')[0].split('_')[-1]
            if power[0] == '0':
                power = float(power[1:])/10
            else:
                power = float(power)
        except Exception as e:
            print('Error while trying to get power from filename: {}'.format(str(e)))
            power = 0
    return power

# GUI Functionality
def select_search_dir():
    """Opens a directory selection dialog to choose the search directory."""
    dir_path = filedialog.askdirectory(title="Select Search Directory")
    if dir_path:
        search_dir_var.set(dir_path)

def loadfiles():
    """Loads the files from the selected search directory."""
    search_dir = search_dir_var.get()
    if not search_dir:
        messagebox.showerror("Error", "Please select a search directory.")
        return
    open_spec = OpenSpec(search_dir)
    open_spec.loadfiles()
    for i in range(len(list(open_spec.specs.keys()))):
        print(list(open_spec.specs.keys())[i], open_spec.specs[list(open_spec.specs.keys())[i]].powernW)
    
    # Plot power vs maximum intensity
    pltpowermaxint(open_spec)

def pltpowermaxint(open_spec):
    """Plots the power vs maximum intensity."""
    power = []
    maxint = []
    for i in range(len(list(open_spec.specs.keys()))):
        power.append(open_spec.specs[list(open_spec.specs.keys())[i]].powernW)
        maxint.append(max(open_spec.specs[list(open_spec.specs.keys())[i]].PL))

    plt.scatter(power, maxint)
    plt.xlabel("Power (nW)")
    plt.ylabel("Maximum Intensity")
    plt.title("Power vs Maximum Intensity")

    # fit a linear regression line to the data
    m, b = np.polyfit(power, maxint, 1)
    plt.plot(power, m*np.array(power) + b, color='red')

    plt.show()

# Example usage:
# Assuming the text files are located in a folder named "testfiles":
open_spec = OpenSpec("C:/Users/volib/Desktop/Evaluation/code/SpecMap/SpecMap1/openspec/testfiles".replace('\\', '/'))
# Initialize GUI
root = tk.Tk()
root.title("Plot Power vs PL Maximum (2sec Integration)")
root.geometry("200x100")

# Variables to hold directory paths
search_dir_var = tk.StringVar()
tk.Button(root, text="Select Search Directory", command=select_search_dir).pack()
tk.Button(root, text="Load Files", command=loadfiles).pack()

root.mainloop()