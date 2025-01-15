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
    def __init__(self, filename, WL, BG, loadeachbg = False, linearbg=False, powernW=0, tint=2):
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
        self.tint = tint
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
    def __init__(self, path, linearbg=False, loadeachbg=False):
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
            powernW, tint = getpowerbyname(i)
            specobj = SpectrumData(i, self.WL, self.BG, self.loadeachbg, self.linearbg, powernW, tint)
            if specobj.dataokay == True:
                #self.specs.append(specobj)
                self.specs[i] = specobj

def getpowerbyname(name):
    power = '0'
    tint = 2
    if 'nW' in name:
        try:
            power = name.split('nW')[0].split('_')[-1]
            if power[0] == '0':
                power = float(power[1:])/10
            else:
                power = float(power)
        except Exception as e:
            print('Error while trying to get power from filename: {}'.format(str(e)))
            power = 0
    if 'sec' in name:
        try:
            tint = name.split('sec')[0].split('_')[-1]
            if tint[0] == '0':
                tint = float(tint[1:])/10
            else:
                tint = float(tint)  
        except Exception as e:
            print('Error while trying to get tint from filename: {}'.format(str(e)))
            tint = 2
    return power, tint

def savefig(fig, filename, dpi=600):
    # try to get savedir
    try:
        save_dir = save_dir_var.get()
        print('Save Directory: {}'.format(save_dir))
    except:
        # set savedir to current directory
        save_dir = os.getcwd()
        print('No savedir selected. Saving to current directory: {}'.format(save_dir))
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    fig.savefig(os.path.join(save_dir, filename), dpi=dpi)
    print('Figure saved as: {}'.format(os.path.join(save_dir, filename)))
    

class PowerWLplot:
    def __init__(self, Laserspotarea=4.27): # laserspotarea in µm²
        self.openspec = []
        self.colors = ['red', 'blue', 'green', 'orange', 'purple', 'black', 'brown', 'pink', 'gray', 'cyan']
        self.powernW = []
        self.maxint = []
        self.maxinterror = []
        self.countsint = []
        self.countsinterror = []
        self.tint = []
        self.Laserspotarea = Laserspotarea
    def getpowermaxint(self):
        print(len(self.powernW))
        powerN = []
        maxintN = []
        countsintN = []
        tintN = []
        maxintNerror = []
        countsintNerrorx = []
        countsintNerrory = []
        for i in [-1]:#range(len(self.openspec)):
            for j in range(len(list(self.openspec[i].specs.keys()))):
                powerN.append(self.openspec[i].specs[list(self.openspec[i].specs.keys())[j]].powernW)
                maxintN.append(max(self.openspec[i].specs[list(self.openspec[i].specs.keys())[j]].PL))
                # X-Error power error: 0.005+2*3/powerN[-1]
                # Y-Error counts error: time 0.0005 counts 0.1 = 0.0005+0.1
                powererror = (0.005+2*3/powerN[-1])*powerN[-1]
                maxintNerror.append([
                    powererror,                 # X-Error                                                                       
                    np.std(self.openspec[i].specs[list(self.openspec[i].specs.keys())[j]].PL)+maxintN[-1]*(0.0005+0.05) # Y-Error
                    ])
                countsintN.append(sum(self.openspec[i].specs[list(self.openspec[i].specs.keys())[j]].PL))
                countsintNerrorx.append(powererror)
                countsintNerrory.append(np.sqrt(sum(self.openspec[i].specs[list(self.openspec[i].specs.keys())[j]].PL)))
                tintN.append(self.openspec[i].specs[list(self.openspec[i].specs.keys())[j]].tint)
        # correction factors for all numbers
        for i in range(len(maxintN)):
            maxintN[i] /= tintN[i]
            #maxintN[i] /= self.Laserspotarea
            # powerN[i] /= self.Laserspotarea divide power by Laser spotarea if needed
            powerN[i] /= 3 # 3 is the factor that gets lost by the beam splitter and 4 mirrors
        self.powernW.append(powerN)
        self.maxint.append(maxintN)
        #self.maxinterror.append(maxintNerror)
        self.maxinterror = maxintNerror
        self.countsint.append(countsintN)
        self.countsinterror.append([countsintNerrorx, countsintNerrory])
        self.tint.append(tintN)
        print(self.powernW)
        print(self.maxint)
        print(self.tint)
        print(self.maxinterror)
        for i in range(len(self.maxinterror)):
            print('i = {}'.format(i), self.maxinterror[i], "\n")

    def pltpowermaxintlinear(self):
        """Plots the power vs maximum intensity."""
        fig, ax = plt.subplots()
        labels = ['Increasing Power', 'Decreasing Power']
        for i in range(len(self.powernW)):
            print(i)
            ax.scatter(self.powernW[i], self.maxint[i], color=self.colors[i], label=labels[i])#'Counts {}'.format(i+1))
            # add error bars of maxint[i] to the plot
            ax.errorbar(self.powernW[i], self.maxint[i], yerr=self.maxinterror[i][1], xerr=self.maxinterror[i][0], fmt='o', color=self.colors[i])
            # fit a linear regression line to the data
            m, b = np.polyfit(self.powernW[i], self.maxint[i], 1)
            ax.plot(self.powernW[i], m*np.array(self.powernW[i]) + b, color=self.colors[i], label='Fit {}'.format(i+1))
            print("Slope: {:.2f}, Intercept: {:.2f}".format(m, b))

        ax.legend()
        ax.set_xlabel('Power in nW')#/$\mu m^2$')
        ax.set_ylabel('Counts per second')
        ax.set_title('$N_1$ Perovskites Excitation Power vs PL counts')
        plt.tight_layout()
        plt.show()
        # save fig with 600 dpi
        savefig(fig, 'PowerMaxIntlinear.png', 600)
    
    def plotpowercountsintlinear(self):
        """Plots the power vs counts per second."""
        fig, ax = plt.subplots()
        labels = ['Increasing Power', 'Decreasing Power']

        for i in range(len(self.powernW)):
            ax.scatter(self.powernW[i], self.countsint[i], color=self.colors[i], label=labels[i])#'Counts {}'.format(i+1))
            # add error bars of countsint[i] to the plot
            ax.errorbar(self.powernW[i], self.countsint[i], yerr=self.countsinterror[i], fmt='o', color=self.colors[i])
            # fit a linear regression line to the data
            m, b = np.polyfit(self.powernW[i], self.countsint[i], 1)
            ax.plot(self.powernW[i], m*np.array(self.powernW[i]) + b
                    , color=self.colors[i], label='Fit {}'.format(i+1))
            print("Slope: {:.2f}, Intercept: {:.2f}".format(m, b))
        
        ax.legend()
        ax.set_xlabel('Power in nW')#/$\mu m^2$')
        ax.set_ylabel('Counts per second')
        ax.set_title('$N_1$ Perovskites Excitation Power vs PL counts')
        plt.tight_layout()
        plt.show()
        savefig(fig, 'PowerCountsIntlinear.png', 600)
    
    def pltpowermaxintzerofit(self):
        """Plots the power vs maximum intensity."""
        fig, ax = plt.subplots()
        labels = ['Increasing Power', 'Decreasing Power']
        for i in range(len(self.powernW)):
            print(i)
            ax.scatter(self.powernW[i], self.maxint[i], color=self.colors[i], label=labels[i])#'Measurement {}'.format(i+1))
            # add error bars of maxint[i] to the plot
            ax.errorbar(self.powernW[i], self.maxint[i], yerr=self.maxinterror[i][1], xerr=self.maxinterror[i][0], fmt='o', color=self.colors[i])
            # fit a linear regression line to the data
            # fit a line to the data that goes through the origin
            m = np.sum(np.multiply(self.powernW[i], self.maxint[i])) / np.sum(np.square(self.powernW[i]))
            ax.plot(self.powernW[i], m*np.array(self.powernW[i]), color=self.colors[i], label='Fit {}'.format(i+1))
            print("fit Slope: {:.2f}".format(m))

        ax.legend()
        ax.set_xlabel('Power in nW')#/$\mu m^2$')
        ax.set_ylabel('Counts per second')
        ax.set_title('$N_1$ Perovskites Excitation Power vs PL counts')
        plt.tight_layout()
        plt.show()
        savefig(fig, 'PowerMaxIntzerofit.png', 600)

    def pltpowercountsintzerofit(self):
        """Plots the power vs counts per second with a fit line through the origin."""
        fig, ax = plt.subplots()
        labels = ['Increasing Power', 'Decreasing Power']
        for i in range(len(self.powernW)):
            ax.scatter(self.powernW[i], self.countsint[i], color=self.colors[i],
                       label=labels[i])#'Counts {}'.format(i+1))
            # fit a fit line to the data that goes through the origin
            m = np.sum(np.multiply(self.powernW[i], self.countsint[i])) / np.sum(np.square(self.powernW[i]))
            ax.plot(self.powernW[i], m*np.array(self.powernW[i]), color=self
                    .colors[i], label='Fit {}'.format(i+1))
            print("fit Slope: {:.2f}".format(m))
        
        ax.legend()
        ax.set_xlabel('Power in nW')#/$\mu m^2$')
        ax.set_ylabel('Counts per second')
        ax.set_title('$N_1$ Perovskites Excitation Power vs PL counts')
        plt.tight_layout()
        plt.show()
        savefig(fig, 'PowerCountsIntzerofit.png', 600)
    
    def plotpowermaxintonlypoints(self):
        """Plots the power vs maximum intensity."""
        fig, ax = plt.subplots()
        labels = ['Increasing Power', 'Decreasing Power']
        for i in range(len(self.powernW)):
            print(i)
            ax.scatter(self.powernW[i], self.maxint[i], color=self.colors[i], label=labels[i])#'Measurement {}'.format(i+1))
            # add error bars of maxint[i] to the plot
            ax.errorbar(self.powernW[i], self.maxint[i], yerr=self.maxinterror[i][1], xerr=self.maxinterror[i][0], fmt='o', color=self.colors[i])

        ax.legend()
        ax.set_xlabel('Power in nW')#/$\mu m^2$')
        ax.set_ylabel('Counts per second')
        ax.set_title('$N_1$ Perovskites Excitation Power vs PL counts')
        plt.tight_layout()
        plt.show()
        savefig(fig, 'PowerMaxIntonlypoints.png', 600)
    
    def plotpowercountsintonlypoints(self):
        """Plots the power vs counts per second."""
        fig, ax = plt.subplots()
        labels = ['Increasing Power', 'Decreasing Power']
        for i in range(len(self.powernW)):
            ax.scatter(self.powernW[i], self.countsint[i], color=self.colors[i],
                       label=labels[i])
        ax.legend()
        ax.set_xlabel('Power in nW')#/$\mu m^2$')
        ax.set_ylabel('Counts per second')
        ax.set_title('$N_1$ Perovskites Excitation Power vs PL counts')
        plt.tight_layout()
        plt.show()
        savefig(fig, 'PowerCountsIntonlypoints.png', 600)
    
# GUI Functionality
def select_search_dir():
    """Opens a directory selection dialog to choose the search directory."""
    dir_path = filedialog.askdirectory(title="Select Search Directory")
    if dir_path:
        search_dir_var.set(dir_path)

def loadfiles(PIplot):
    """Loads the files from the selected search directory."""
    search_dir = search_dir_var.get()
    if not search_dir:
        messagebox.showerror("Error", "Please select a search directory.")
        return
    openspec = OpenSpec(search_dir)
    openspec.loadfiles()
    PIplot.openspec.append(openspec)
    PIplot.getpowermaxint()

def plotpowermaxintaxpb(PIplot):
    PIplot.pltpowermaxintlinear()

def plotpowermaxnofit(PIplot):
    PIplot.plotpowermaxintonlypoints()

def select_save_dir(save_dir_var):
    print("Select Save Directory:", save_dir_var.get())
    """Opens a directory selection dialog to choose the save directory."""
    dir_path = filedialog.askdirectory(title="Select Save Directory")
    if dir_path:
        save_dir_var.set(dir_path)


# Example usage:
# Assuming the text files are located in a folder named "testfiles":
openspec = OpenSpec("C:/Users/volib/Desktop/Evaluation/code/SpecMap/SpecMap1/openspec/testfiles".replace('\\', '/'))
# Initialize GUI
root = tk.Tk()
root.title("Plot Power vs PL Maximum (2sec Integration)")
windowwidth = 400
windowheight = 450
root.geometry("{}x{}".format(windowwidth, windowheight))

# Variables to hold directory paths
PIplot = PowerWLplot(5.3)
# Load files from selected directory
save_dir_var = tk.StringVar()
# set to C:\Users\volib\Desktop\Promotion\Reports\2025\250114\images
save_dir_var.set('C:/Users/volib/Desktop/Promotion/Reports/2025/250114/images/rising'.replace('\\', '/'))
search_dir_var = tk.StringVar()

# Create Widgets
tk.Button(root, text="Select Search Directory", command=select_search_dir).pack()
tk.Button(root, text="Load Files", command=lambda: loadfiles(PIplot)).pack()
# add save directory selection
tk.Label(root, text="Save Directory:").pack()
# add save directory selection button
tk.Button(root, text="Select Save Directory", command=lambda: select_save_dir(save_dir_var)).pack()
saveentry = tk.Entry(root, textvariable=save_dir_var, width=windowwidth).pack()

# add spacing
tk.Label(root, text="Highest Intensity").pack()
tk.Button(root, text="Plot Power vs Max Intensity", command=lambda: plotpowermaxnofit(PIplot)).pack()
tk.Button(root, text="Plot Power vs PL Maximum Linear", command=lambda: plotpowermaxintaxpb(PIplot)).pack()
tk.Button(root, text="Plot Power vs PL Maximum Zero fit", command=lambda: PIplot.pltpowermaxintzerofit()).pack()
# add spacing
tk.Label(root, text="Full Spectrum integrated").pack()
tk.Button(root, text="Plot Power vs Counts per second", command=lambda: PIplot.plotpowercountsintonlypoints()).pack()
tk.Button(root, text="Plot Power vs Counts per second Linear", command=lambda: PIplot.plotpowercountsintlinear()).pack()
tk.Button(root, text="Plot Power vs Counts per second Zero fit", command=lambda: PIplot.pltpowercountsintzerofit()).pack()

root.mainloop()