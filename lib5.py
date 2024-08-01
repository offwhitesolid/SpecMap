import numpy as np
from PIL import Image
from matplotlib.figure import Figure
import sys
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,  
NavigationToolbar2Tk)
import matplotlib.patches as mpatches
from scipy.optimize import curve_fit
from scipy.special import wofz
import mathlib3 as matl # type: ignore
import deflib1 as deflib # type: ignore

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
    def __init__(self, filename, WL, BG, loadeachbg = False, linearbg=False, removecosmics=False, cosmicthreshold=20, cosmicpixels=3, removecosmicmethod=list(deflib.cosmicfuncts.keys())[0]):
        self.removecosmicsmethod = removecosmicmethod
        self.loadeachbg = loadeachbg
        self.linearbg = linearbg
        self.removecosmics = removecosmics
        self.cosmicthreshold = cosmicthreshold
        self.cosmicpixels = cosmicpixels
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
        self.PL = []
        self._read_file()

        # init fit data
        self.fwhm = np.nan
        self.fitmaxX = np.nan
        self.fitmaxY = np.nan
        self.fitdata = [None]

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

        if self.removecosmics == True:
            try:
                self.PLB = deflib.cosmicfuncts[self.removecosmicsmethod](self.PLB, self.cosmicthreshold, self.cosmicpixels)
            except Exception as e:
                print('Cosmic removal failed. {}'.format(str(e)))

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
            print(f"Attribute {attr_name} not found in class SpectrumData.")


# create XY Map that contains the Pixels 
class XYMap:
    def __init__(self, fnames, cmapframe, specframe, loadbg=False, linearbg=False, removecosmics=False, cosmicthreshold=20, cosmicpixels=3, cosmicmethod=list(deflib.cosmicfuncts.keys())[0], defentries=deflib.defaults):
        self.defentries = defentries
        self.remcosmicfunc = cosmicmethod
        self.removecosmics = removecosmics
        self.linearbg = linearbg
        self.cosmicthreshold = cosmicthreshold
        self.cosmicpixels = cosmicpixels
        self.fnames = fnames
        self.readinkeys = ['WL']
        self.loadeachbg = loadbg
        self.specs = []                                                     # Spectral Objects
        self.fontsize = self.defentries['fontsize']                         # Default Plot Font Size
        self.colormap = tk.StringVar()                                      # Colormap
        self.fitkeys = matl.fitkeys
        # load files in hyperthreading
        self.loadfiles()
        self.cmapframe = cmapframe                                          # Colormap Frame
        self.specframe = specframe                                          # Spectrum Frame
        self.DataSpecMin = np.amin(self.WL)                                 # Spectrum Start
        self.DataSpecMax = np.amax(self.WL[-1])                             # Spectrum End
        self.DataSpecdL = self.specs[0].data['Delta Wavelength (nm)']       # delta Lambda
        self.speckeys = {'Wavelength axis': 'WL', 'Background (BG)': 'BG',
                         'Counts (PL)': 'PL', 'Spectrum (PL-BG)': 'PLB'} # WLB is BG corrected (=PL-BG)
        self.windowfunctions = ['gaussian', 'lorentz', 'voigt', 'double gaussian', 'double lorentz', 'double voigt', 'linear']  # Window Functions
        self.autogenmatrix()                                                # generate emty grid and fill Data obj into Matrix
        self.DataPixSt = len(self.specs[0].WL)                              # Number of WL Pixels                   
        self.DataPixDX = self.gdx                                           # Plot Pixel dx
        self.DataPixDY = self.gdy                                           # Plot Pixel dy
        self.aqpixstart = 0                                                 # evaluate window start dL
        self.aqpixend = -1                                                  # evaluate window end dL
        self.SpecButtons = self.build_button_frame(self.specframe)         # build Spec GUI
        self.buildMinMaxSpec(self.cmapframe)                                # build CMAP grid GUI
        self.build_PixMatrix_frame(self.cmapframe)                          # build Pixel Matrix GUI
        self.buildselectboxes(self.cmapframe, list(self.speckeys.keys()))
        #self.getPLpixelIntervalMax()                                        # build PL Matrix
        #self.plotPixelMatrix()                                              # Plot PL Matrix 
        self.updatewl()

    def buildselectboxes(self, frame, values):
        tk.Label(frame, text="Select Data Set".format(self.DataSpecMax)).grid(row=0, column=1)
        self.selectspecbox = ttk.Combobox(frame, values=values)
        self.selectspecbox.set(list(self.speckeys.keys())[-1])
        self.selectspecbox.grid(row=1, column=1)
        tk.Label(frame, text="Select Colormap".format(self.DataSpecMax)).grid(row=0, column=2)
        self.selectcolmapbox = ttk.Combobox(frame, values=plt.colormaps(), textvariable=self.colormap)
        self.selectcolmapbox.set(plt.colormaps()[0])
        self.selectcolmapbox.grid(row=1, column=2) 

    def updatecountthresh(self):
        try:
            self.countthreshv = int(self.countthresh.get())
        except Exception as e:
            messagebox.showerror("Error", '{} Insert valid threshold of type int.'.format(str(e)))

    # Spectral Plot Input Update
    def updatewl(self):
        try:
            self.wlstart = float(self.proc_spec_min.get())
            self.wlend = float(self.proc_spec_max.get())
        except Exception as e:
            messagebox.showerror("Error", '{} Insert valid spectral Borders of type float.'.format(str(e)))
        passt = False
        if self.wlstart > self.wlend:
            tk.messagebox.showerror('ERROR', 'Lowest Wavelength must be smaller than Highest Wavelength! Reconsider Input!')
            self.wlstart = self.DataSpecMin
            self.proc_spec_min.delete(0, tk.END)
            self.proc_spec_min.insert(0, self.DataSpecMin)
            self.wlend = self.DataSpecMax
            self.proc_spec_max.delete(0, tk.END)
            self.proc_spec_max.insert(0, self.DataSpecMax)
        elif self.wlstart < self.DataSpecMin:
            passt = True
            tk.messagebox.showwarning('ERROR', 'Lowest Wavelength is below data WL. Set WL to lowest datapoint.')
            self.wlstart = self.DataSpecMin
            self.proc_spec_min.delete(0, tk.END)
            self.proc_spec_min.insert(0, self.DataSpecMin)
            if self.wlend > self.DataSpecMax:
                tk.messagebox.showwarning('ERROR', 'Lowest Wavelength is below data WL. Set WL to highest datapoint.')
                self.wlend = self.DataSpecMax
                self.proc_spec_max.delete(0, tk.END)
                self.proc_spec_max.insert(0, self.DataSpecMax)
        elif self.wlend > self.DataSpecMax:
            passt = True
            tk.messagebox.showwarning('ERROR', 'Lowest Wavelength is below data WL. Set WL to highest datapoint.')
            self.wlend = self.DataSpecMax
            self.proc_spec_max.delete(0, tk.END)
            self.proc_spec_max.insert(0, self.DataSpecMax)
            if self.wlstart < self.DataSpecMin:
                tk.messagebox.showwarning('ERROR', 'Lowest Wavelength is below data WL. Set WL to lowest datapoint.')
                self.wlstart = self.DataSpecMin
                self.proc_spec_min.delete(0, tk.END)
                self.proc_spec_min.insert(0, self.DataSpecMin)
        else:
            passt = True
        if passt == True:
            # convert lambdamin and lambdamax into pixels
            self.aqpixstart = int((self.wlstart-self.DataSpecMin)/self.DataSpecdL)
            self.aqpixend = int((self.wlend-self.DataSpecMin)/self.DataSpecdL) #round

    # min and max wl can be inserted here for preceed window
    def buildMinMaxSpec(self, frame):
        # ProcSpecMin input field
        tk.Label(frame, text="Lowest wavelength \\ nm\nMinimum: {} nm".format(self.DataSpecMin)).grid(row=0, column=0)
        self.proc_spec_min = tk.Entry(frame)
        self.proc_spec_min.grid(row=1, column=0)
        self.proc_spec_min.insert(0, self.defentries['lowest_wavelength'])

        # ProcSpecMax input field
        tk.Label(frame, text="Highest wavelength \\ nm\nMaximum: {} nm".format(self.DataSpecMax)).grid(row=2, column=0)
        self.proc_spec_max = tk.Entry(frame)
        self.proc_spec_max.grid(row=3, column=0)
        self.proc_spec_max.insert(0, self.defentries['highest_wavelength'])

        # Button to create colormap
        tk.Label(frame, text="Press button below \nto update data matrix").grid(row=2, column=1)
        b1 = tk.Button(frame, text="Create intensity colormap", command= lambda: self.buildandPlotIntCmap())
        b1.grid(row=3, column=1)
        b2 = tk.Button(frame, text="Create spectral maximum colormap", command= lambda: self.buildandPlotSpecCmap())
        b2.grid(row=4, column=1)
        b3 = tk.Button(frame, text="Update spectral fit maxima", command= lambda: self.updateandPlotSpecCmap('fitmaxX'))
        b3.grid(row=5, column=1)

        # Plot Font size
        tk.Label(frame, text="Plot font size".format(self.DataSpecMin)).grid(row=2, column=2)
        self.CMFont = tk.Entry(frame)
        self.CMFont.grid(row=3, column=2)
        self.CMFont.insert(0, self.fontsize)

        # scipy fit maxiter
        tk.Label(frame, text="Max tries for fit").grid(row=4, column=2)
        self.fitmaxiter = tk.Entry(frame)
        self.fitmaxiter.grid(row=5, column=2)
        self.fitmaxiter.insert(0, self.defentries['maxfev'])

        # threshold for colormap
        tk.Label(frame, text="Colormap threshold \\ Counts").grid(row=4, column=0)
        self.countthresh = tk.Entry(frame)
        self.countthresh.grid(row=5, column=0)
        self.countthresh.insert(0, self.defentries['colormap_threshold'])

    def build_PixMatrix_frame(self, parframe):
        frame = tk.Frame(parframe, border=5, relief="sunken")
        frame.grid(row=0, column=4, rowspan=6, sticky=tk.NW)
        tk.Label(frame, text="Process Pixel Matrix".format(self.DataSpecMin)).grid(row=0, column=0)

        b1= tk.Button(frame, text="fit rotated 2D Gaussian to Matrix", command= lambda: self.fit2drotgausstopixmatrix())
        b1.grid(row=1, column=0)
        b2= tk.Button(frame, text="fit 2D Gaussian to Matrix", command= lambda: self.fit2dgausstopixmatrix())
        b2.grid(row=2, column=0)
    
    def buid_FitFrame(self, parframe):
        frame = tk.Frame(parframe, border=5, relief="sunken")
        frame.grid(row=0, column=5, rowspan=6, sticky=tk.NW)
    
    def fit2dgausstopixmatrix(self):
        try: 
            self.maxiter = int(self.fitmaxiter.get())
        except:
            print('Maxiter must be type int. Using default 1000.')
            self.maxiter = 1000
        try:
            matl.fitgaussian2dtomatrix(self.PixMatrix, True, self.gdx, self.gdy, self.colormap.get(), maxfev=self.maxiter)
        except:
            print('2D Gaussian Fit failed.')
            
    def fit2drotgausstopixmatrix(self):
        try: 
            self.maxiter = int(self.fitmaxiter.get())
        except:
            print('Maxiter must be type int. Using default 1000.')
            self.maxiter = 1000
        try:
            matl.fitgaussiand2dtomatrixrot(self.PixMatrix, True, self.gdx, self.gdy, self.colormap.get(), maxfev=self.maxiter)
            #fitdata, pcov, fwhmx, fwhmy = matl.fitgaussiand2dtomatrix(self.PixMatrix, maxfev=self.maxiter)
            #print(fitdata, pcov, fwhmx, fwhmy)
        except Exception as Error:
            print('2D rotational Gaussian Fit failed.', Error)
        


    # Matrix with Pixels to obtain spectrum
    def build_button_frame(self, parframe, width=600, height=600):
        n = len(self.PixMatrix)
        m = len(self.PixMatrix[0])
        frame = tk.Frame(parframe)
        frame.pack(side=tk.RIGHT, anchor=tk.N, fill=tk.BOTH, expand=True)
        tk.Label(parframe, text='Press Plot Spectrum\nto plot selected Pixel\nPixel Loaded: {} x {}'.format(len(self.SpecDataMatrix[0]), len(self.SpecDataMatrix))).pack(side=tk.TOP, anchor=tk.W)
        tk.Label(parframe, text='selected Pixel: ').pack(side=tk.TOP, anchor=tk.W)
        xyframe = tk.Frame(parframe)
        xyframe.pack(side=tk.TOP, anchor=tk.W)
        # inside xyframe
        tk.Label(xyframe, text='X =').grid(row=0, column=0)
        self.selectPixX = tk.Entry(xyframe)
        self.selectPixX.grid(row=0, column=1)
        self.selectPixX.insert(0, self.defentries['selected_pixel_x'])
        tk.Label(xyframe, text='Y =').grid(row=1, column=0)
        self.selectPixY = tk.Entry(xyframe)#, text="0")
        self.selectPixY.grid(row=1, column=1)
        self.selectPixY.insert(0, self.defentries['selected_pixel_y'])

        tk.Label(parframe, text="Select Data Set".format(self.DataSpecMax)).pack(side=tk.TOP, anchor=tk.W)
        self.selectspecpixbox = ttk.Combobox(parframe, values=list(self.speckeys.keys()))
        self.selectspecpixbox.set(list(self.speckeys.keys())[-1])
        self.selectspecpixbox.pack(side=tk.TOP, anchor=tk.W)

        b1 = tk.Button(parframe, text="Plot Spectrum", command=self.PlotPixelSpectrum)
        b1.pack(side=tk.TOP, anchor=tk.W)
        b2 = tk.Button(parframe, text="Create Button Matrix", command= lambda: self.buildButtonMatrix( frame, n, m))
        b2.pack(side=tk.BOTTOM, anchor=tk.W)

        # fit to spectrum
        tk.Label(parframe, text="Select Fit function".format(self.DataSpecMax)).pack(side=tk.TOP, anchor=tk.W)
        self.selectwindowbox = ttk.Combobox(parframe, values=list(self.windowfunctions))
        self.selectwindowbox.set(self.defentries['selected_fit_function'])
        self.selectwindowbox.pack(side=tk.TOP, anchor=tk.W)
        b3 = tk.Button(parframe, text="Fit Window to Spectrum", command=lambda: self.fitwindowtospec('fitmaxX', newfit=True))
        b3.pack(side=tk.TOP, anchor=tk.W)
        self.sepfitfunct = tk.IntVar()
        b4 = tk.Button(parframe, text="plot existing fit and spectrum", command=lambda: self.fitwindowtospec('fitmaxX', newfit=False))
        b4.pack(side=tk.TOP, anchor=tk.W)
        self.sepfitfunct.set(0)
        self.sepfitfunctsbut = tk.Checkbutton(parframe, text="Separate Fit Functions", variable=self.sepfitfunct)
        self.sepfitfunctsbut.pack(side=tk.TOP, anchor=tk.W)
        buttons = []
        self.SpecButtons = []
        #buttons = self.buildButtonMatrix(frame, n, m)
        return buttons
        
        # fram = Tkinter frame, n = len(self.PixMatrix), m = len(self.PixMatrix[0])
    def buildButtonMatrix(self, frame, n, m):
        # create buttons
        buttons = []
        self.vvars = []
        for row in range(n):
            row_buttons = []
            row_vars = []
            for col in range(m):
                var = [col, row]
                button = tk.Button(frame, bg="red", command=lambda v=var: self.button_click(v))
                button.grid(row=row+1, column=col+1, sticky=tk.NSEW)
                row_buttons.append(button)
                row_vars.append(var)
            buttons.append(row_buttons)
            self.vvars.append(row_vars)
        # Configure row and column weights to make buttons fill the frame
        for row in range(1, n+1):
            frame.rowconfigure(row, weight=1)
        for col in range(1, m+1):
            frame.columnconfigure(col, weight=1)
        # Add row axis
        for row in range(n):
            label = tk.Label(frame, text=str(round(row*self.gdx, 10)), relief=tk.RAISED)
            label.grid(row=row+1, column=0, sticky=tk.NSEW)
        # Add column axis
        for col in range(m):
            label = tk.Label(frame, text=str(round(col*self.gdy, 10)), relief=tk.RAISED)
            label.grid(row=0, column=col+1, sticky=tk.NSEW)
        self.SpecButtons = buttons
        self.buttonframe_updateColor()
        #return buttons

    def button_click(self, var):
        self.selectPixX.delete(0, tk.END)
        self.selectPixX.insert(0, var[0])
        self.selectPixY.delete(0, tk.END)
        self.selectPixY.insert(0, var[1])
    
    def buttonframe_updateColor(self):
        for i in range(len(self.SpecDataMatrix)):
            for j in range(len(self.SpecDataMatrix[i])):
                if type(self.SpecDataMatrix[i][j]) == SpectrumData:
                    if self.SpecDataMatrix[i][j].dataokay == True:
                        self.SpecButtons[i][j].config(bg="green")
                    else:
                        self.SpecButtons[i][j].config(bg="red")
                else:
                    self.SpecButtons[i][j].config(bg="red")

    # Max Counts Colormap
    def buildandPlotIntCmap(self):
        self.getPLpixelIntervalMaxIndex()
        self.readfontsize()
        self.plotPixelMatrixIntensity()
        
    # Spectral Maximum Colormap
    def buildandPlotSpecCmap(self):
        self.updatewl()
        self.getPLpixelSpecMax()
        self.readfontsize()
        self.fittoMatrix('fitmaxX')
        self.plotPixelMatrixSpectral()
    
    def updateandPlotSpecCmap(self, variable):
        #self.updatePixelMatrix(variable)
        self.plotPixelMatrixSpectral()

    def fitwindowtospec(self, variable, newfit=False):
        self.updatewl()
        x, y, valid = self.validpixelinput()
        if valid[0] == True and valid[1] == True:
            if type(self.SpecDataMatrix[y][x]) == SpectrumData:
                if self.SpecDataMatrix[y][x].dataokay == True:
                    self.selectwindowboxVari = self.selectwindowbox.get()
                    self.selectspecboxVari = self.selectspecbox.get()
                    if self.speckeys[self.selectspecboxVari] == 'WL': #Wavelength
                        data = self.SpecDataMatrix[y][x].WL
                        self.PlotSpectrum(data, self.SpecDataMatrix[y][x].WL, 'Wavelength')
                    elif self.speckeys[self.selectspecboxVari] == 'BG': #Background
                        data = self.SpecDataMatrix[y][x].BG
                        self.PlotSpectrum(data, self.SpecDataMatrix[y][x].WL, 'Background Counts')
                    elif self.speckeys[self.selectspecboxVari] == 'PL': # Counts
                        data = self.SpecDataMatrix[y][x].PL
                        self.PlotSpectrum(data, self.SpecDataMatrix[y][x].WL, 'Spectrometer Counts')
                    elif self.speckeys[self.selectspecboxVari] == 'PLB': #Spectrum
                        data = self.SpecDataMatrix[y][x].PLB[self.aqpixstart: self.aqpixend]
                    try: # fit function to spectrum  
                        if newfit == True or self.SpecDataMatrix[y][x].fitdata == [None]:
                            if self.SpecDataMatrix[y][x].fitdata == [None]:
                                print('No fit data found. Fitting new data.')
                            try: 
                                self.maxiter = int(self.fitmaxiter.get())
                            except:
                                print('Maxiter must be type int. Using default 1000.')
                                self.maxiter = 1000
                            self.SpecDataMatrix[y][x].fitdata = self.fitkeys[self.selectwindowboxVari][1](self.aqpixstart, self.aqpixend, self.SpecDataMatrix[y][x].WL, self.SpecDataMatrix[y][x].PLB, self.maxiter)
                            self.SpecDataMatrix[y][x].fitmaxY, self.SpecDataMatrix[y][x].fitmaxX = self.fitkeys[self.selectwindowboxVari][2](self.aqpixstart, self.aqpixstart, *self.SpecDataMatrix[y][x].fitdata[:-1])
                            # get maximum using mathlib.Newtonmax
                            #self.SpecDataMatrix[y][x].fitmaxX = matl.Newtonmax(self.fitkeys[self.selectwindowboxVari][0], self.SpecDataMatrix[y][x].fitdata[0], tol=1e-6, maxiter=1000)
                            #self.SpecDataMatrix[y][x].fitmaxY = self.fitkeys[self.selectwindowboxVari][0](self.SpecDataMatrix[y][x].fitmaxX, *self.SpecDataMatrix[y][x].fitdata[:-1])
                            self.PixMatrix[y][x] = self.SpecDataMatrix[y][x].get_attribute(variable)
                        
                            #plt.scatter(self.SpecDataMatrix[y][x].fitmaxX, self.SpecDataMatrix[y][x].fitmaxY, color='red')
                        self.PlotFitSpectrum(self.SpecDataMatrix[y][x].WL[self.aqpixstart: self.aqpixend], data, ['Spectrometer counts', self.fitkeys[self.selectwindowboxVari][3]], [self.SpecDataMatrix[y][x].fitdata[:-1]], [self.fitkeys[self.selectwindowboxVari][0]])
                        
                    except Exception as e:
                        print('Fit filed. {}'.format(str(e)))
        else:
            print(self.SpecDataMatrix[y][x])        
    
    def fittoMatrix(self, variable='fitmaxX', incmin=1, incmax=-1, nmin=10, nmax=10):
        # fill matrix with data of the selected enry:
        self.updatecountthresh()
        for i in range(len(self.SpecDataMatrix)):
            for j in range(len(self.SpecDataMatrix[i])):
                if type(self.SpecDataMatrix[i][j]) == SpectrumData:
                    if self.SpecDataMatrix[i][j].dataokay == True:
                        self.selectwindowboxVari = self.selectwindowbox.get()
                        self.selectspecboxVari = self.selectspecbox.get()
                        tries = 1
                        worked = False
                        adjmin = True
                        # if fit does not work, adjust the window size
                        while tries < nmin+nmax and worked == False:
                            tries += 1
                            try:
                                if self.speckeys[self.selectspecboxVari] == 'WL': #Wavelength
                                    if np.sum(self.SpecDataMatrix[i][j].WL[self.aqpixstart:self.aqpixend]) < self.countthreshv:
                                        self.PixMatrix[i][j] = np.nan
                                elif self.speckeys[self.selectspecboxVari] == 'BG': #Background
                                    if np.sum(self.SpecDataMatrix[i][j].BG[self.aqpixstart:self.aqpixend]) < self.countthreshv:
                                        self.PixMatrix[i][j] = np.nan
                                    else:
                                        self.PixMatrix[i][j] = self.SpecDataMatrix[i][j].WL[self.SpecDataMatrix[i][j].BG[self.aqpixstart:self.aqpixend].index(np.amax(self.SpecDataMatrix[i][j].BG[self.aqpixstart:self.aqpixend]))+self.aqpixstart]
                                elif self.speckeys[self.selectspecboxVari] == 'PL': # Counts
                                    if np.sum(self.SpecDataMatrix[i][j].PL[self.aqpixstart:self.aqpixend]) < self.countthreshv:
                                        self.PixMatrix[i][j] = np.nan
                                    else:
                                        self.PixMatrix[i][j] = self.SpecDataMatrix[i][j].WL[self.SpecDataMatrix[i][j].PL[self.aqpixstart:self.aqpixend].index(np.amax(self.SpecDataMatrix[i][j].PL[self.aqpixstart:self.aqpixend]))+self.aqpixstart]
                                elif self.speckeys[self.selectspecboxVari] == 'PLB': #Spectrum
                                    if np.sum(self.SpecDataMatrix[i][j].PLB[self.aqpixstart:self.aqpixend]) < self.countthreshv:
                                        self.PixMatrix[i][j] = np.nan
                                    else:
                                        try:
                                            self.maxiter = int(self.fitmaxiter.get())
                                        except:
                                            print('Maxiter must be int. Using default 1000.')
                                            self.maxiter = 1000
                                        self.SpecDataMatrix[i][j].fitdata = self.fitkeys[self.selectwindowboxVari][1](self.aqpixstart, self.aqpixend, self.SpecDataMatrix[i][j].WL, self.SpecDataMatrix[i][j].PLB, self.maxiter)
                                        self.SpecDataMatrix[i][j].fitmaxX, self.SpecDataMatrix[i][j].fitmaxY = self.fitkeys[self.selectwindowboxVari][2](self.aqpixstart, self.aqpixend, *self.SpecDataMatrix[i][j].fitdata[:-1])#[1]
                                        #_, self.SpecDataMatrix[i][j].fitmaxX, self.SpecDataMatrix[i][j].fitmaxY = matl.find_max_of_fit(self.SpecDataMatrix[i][j].fitdata, xmin=self.aqpixstart, xmax=self.aqpixend)
                                        self.PixMatrix[i][j] = self.SpecDataMatrix[i][j].get_attribute(variable)
                                worked = True
                            except Exception as e:
                                try:
                                    if adjmin == True:
                                        self.aqpixstart += incmin
                                        adjmin = False
                                    else:
                                        self.aqpixend += incmax
                                        adjmin = True
                                except:
                                    print("Fit Window ran out of Data. Fit to Matrix Failed at element {}, {}.\n{}".format(i, j, str(e)))
                                    worked = True
                                print("Fit to Matrix Failed at element {}, {}.\n{}".format(i, j, str(e)))
                                #messagebox.showerror("Error", "Fit to Matrix Failed at element {}, {}.\n{}".format(i, j, str(e)))
                            
    
    def updatePixelMatrix(self, variable):
        for i in range(len(self.SpecDataMatrix)):
            for j in range(len(self.SpecDataMatrix[i])):
                try:
                    self.PixMatrix[i][j] = self.SpecDataMatrix[i][j].get_attribute(variable)
                except Exception as e:
                    self.PixMatrix[i][j] = np.nan
                    print("Update Pixel Matrix Failed at element {}, {}.\n{}".format(i, j, str(e)))


    def readfontsize(self):
        try:
            self.fontsize =abs(float(self.CMFont.get()))
        except Exception as e:
            messagebox.showerror("Error", '{} Font Size must be Number.'.format(str(e)))

    def validpixelinput(self):
        x = self.selectPixX.get()
        y = self.selectPixY.get()
        valid = [False, False]
        try:
            x = int(x)
            if x < len(self.SpecDataMatrix[0]):
                valid[0] = True
            else:
                messagebox.showerror("Error", "No Pixel on X-Position.")
        except Exception as e:
            messagebox.showerror("Error", '{} Insert valid X-Position.'.format(str(e)))
        try:
            y = int(y)
            if y < len(self.SpecDataMatrix):
                valid[1] = True
            else:
                messagebox.showerror("Error", "No Pixel on Y-Position.")
        except Exception as e:
            messagebox.showerror("Error", '{} Insert valid Y-Position.'.format(str(e)))
        return(x, y, valid)

    def PlotPixelSpectrum(self):
        x, y, valid = self.validpixelinput()        
        if valid[0] == True and valid[1] == True:
            if type(self.SpecDataMatrix[y][x]) == SpectrumData:
                if self.SpecDataMatrix[y][x].dataokay == True:
                    self.selectdataboxVari = self.selectspecpixbox.get()
                    if self.speckeys[self.selectdataboxVari] == 'WL': #Wavelength
                        data = self.SpecDataMatrix[y][x].WL
                        self.PlotSpectrum(data, self.SpecDataMatrix[y][x].WL, 'Wavelength')
                    elif self.speckeys[self.selectdataboxVari] == 'BG': #Background
                        data = self.SpecDataMatrix[y][x].BG
                        self.PlotSpectrum(data, self.SpecDataMatrix[y][x].WL, 'Background Counts')
                    elif self.speckeys[self.selectdataboxVari] == 'PL': # Counts
                        data = self.SpecDataMatrix[y][x].PL
                        self.PlotSpectrum(data, self.SpecDataMatrix[y][x].WL, 'Spectrometer Counts')
                    elif self.speckeys[self.selectdataboxVari] == 'PLB': #Spectrum
                        data = self.SpecDataMatrix[y][x].PLB
                        self.PlotSpectrum(data, self.SpecDataMatrix[y][x].WL, 'Spectrum')
                    else:
                        print('No valid Data set selected for the Plot.')

    def PlotSpectrum(self, x, y, label):
        self.readfontsize()
        plt.figure(figsize=(10, 6))
        plt.plot(y, x, label=label, color='blue')       
        plt.xlabel('Wavelength / nm', fontsize=self.fontsize)
        plt.ylabel('Intensity', fontsize=self.fontsize)
        plt.title('Spectrograph Data', fontsize=self.fontsize)
        plt.legend(fontsize=self.fontsize)
        plt.tick_params(axis='both', which='major', labelsize=self.fontsize)
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def PlotFitSpectrum(self, x, y, label, fitdata, fitfunc):
        self.readfontsize()
        plt.figure(figsize=(10, 6))
        plt.plot(x, y, label=label[0], color='blue')
        #plt.plot(x, fitfunc(*fitdata), label='Fitted function', color='red')
        #plt.plot(x, fitfunc(x, *fitdata), label='Fitted function', color='red')
        self.selectwindowboxVari = self.selectwindowbox.get()
        if self.sepfitfunct.get() == 1:
            # plot double window function seperately
            if self.selectwindowboxVari == 'double gaussian':
                plt.plot(x, matl.gaussianwind(x, fitfunc[0][0], fitfunc[0][1], fitfunc[0][2]), label='Gaussian 1', color='red')
                plt.plot(x, matl.gaussianwind(x, fitfunc[0][3], fitfunc[0][4], fitfunc[0][5]), label='Gaussian 2', color='green')
            elif self.selectwindowboxVari == 'double lorentz':
                plt.plot(x, matl.lorentzwind(x, fitfunc[0][0], fitfunc[0][1], fitfunc[0][2]), label='Lorentz 1', color='red')
                plt.plot(x, matl.lorentzwind(x, fitfunc[0][3], fitfunc[0][4], fitfunc[0][5]), label='Lorentz 2', color='green')
            elif self.selectwindowboxVari == 'double voigt':
                plt.plot(x, matl.voigtwind(x, fitfunc[0][0], fitfunc[0][1], fitfunc[0][2]), label='Voigt 1', color='red')
                plt.plot(x, matl.voigtwind(x, fitfunc[0][3], fitfunc[0][4], fitfunc[0][5]), label='Voigt 2', color='green')
        else:  
            for i in range(len(fitdata)):
                plt.plot(x, fitfunc[i](x, *fitdata[i]), label=label[i+1], color='red')  
        plt.xlabel('Wavelength / nm', fontsize=self.fontsize)
        plt.ylabel('Intensity', fontsize=self.fontsize)
        plt.title('Spectrograph Data', fontsize=self.fontsize)
        plt.legend(fontsize=self.fontsize)
        plt.tick_params(axis='both', which='major', labelsize=self.fontsize)
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def plotPixelMatrixIntensity(self, cmapticks=6):
        fig, ax = plt.subplots()
        # Display the data as an image with a colormap
        cax = ax.imshow(self.PixMatrix, cmap=self.colormap.get()) # aspect='auto' for cubic image
        # Add a colorbar to the image
        cbar = fig.colorbar(cax, ax=ax)
        # Set the colorbar label
        cbar.set_label('Spectrometer Counts', fontsize=self.fontsize)
        # Set the ticks of the colormap
        #cbar_ticks=np.linspace(np.amin(self.PixMatrix), np.amax(self.PixMatrix), cmapticks)
        #cbar.set_ticks(cbar_ticks)
        # Set the font size of the colorbar ticks
        cbar.ax.tick_params(labelsize=self.fontsize)
        # Set the plot title
        ax.set_title('Integrated {0} pixels from {1} nm to {2} nm.'.format(int(self.aqpixend-self.aqpixstart+1), self.wlstart, self.wlend, fontsize=self.fontsize))
        # Set the x and y axis labels
        ax.set_xlabel('Nanostage X Axis in \u03bcm', fontsize=self.fontsize)
        ax.set_ylabel('Nanostage Y Axis in \u03bcm', fontsize=self.fontsize)
        # set the axis ticks
        xticks = np.arange(0, self.PixAxX[-1]-self.PixAxX[0], self.gdx)
        yticks = np.arange(0, self.PixAxY[-1]-self.PixAxY[0], self.gdy)
        ax.set_xticks(np.arange(len(xticks)))
        ax.set_yticks(np.arange(len(yticks)))
        ax.set_xticklabels(np.round(xticks, 4))
        ax.set_yticklabels(np.round(yticks, 4))
        # automatic displayed ticks
        ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
        ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
        # Set the font size of the ticks on both axes
        ax.tick_params(axis='both', which='major', labelsize=self.fontsize)
        plt.tight_layout()
        plt.show()

    def plotPixelMatrixSpectral(self):
        fig, ax = plt.subplots()
        # Display the data as an image with a colormap
        cax = ax.imshow(self.PixMatrix, cmap=self.colormap.get())#'viridis')
        # Add a colorbar to the image
        cbar = fig.colorbar(cax, ax=ax)
        # Set the colorbar label
        cbar.set_label('Highest Intensity in nm', fontsize=self.fontsize)
        # Set the font size of the colorbar ticks
        cbar.ax.tick_params(labelsize=self.fontsize)
        # Set the plot title
        ax.set_title('Nanostage Intensity {} nm to {} nm.'.format(self.wlstart , self.wlend), fontsize=self.fontsize)
        # Set the x and y axis labels
        ax.set_xlabel('Nanostage X Axis in \u03bcm', fontsize=self.fontsize)
        ax.set_ylabel('Nanostage Y Axis in \u03bcm', fontsize=self.fontsize)
        # set the axis ticks
                # set the axis ticks
        xticks = np.arange(0, self.PixAxX[-1]-self.PixAxX[0], self.gdx)
        yticks = np.arange(0, self.PixAxY[-1]-self.PixAxY[0], self.gdy)
        ax.set_xticks(np.arange(len(xticks)))
        ax.set_yticks(np.arange(len(yticks)))
        ax.set_xticklabels(np.round(xticks, 4))
        ax.set_yticklabels(np.round(yticks, 4))
        #ax.set_xticks(np.arange(0, len(self.PixAxX), 1))
        #ax.set_yticks(np.arange(0, len(self.PixAxY), 1))
        #ax.set_xticklabels(np.subtract(np.multiply(self.PixAxX, self.gdx), np.amin(self.PixAxX)), fontsize=self.fontsize)
        #ax.set_yticklabels(np.subtract(np.multiply(self.PixAxY, self.gdy), np.amin(self.PixAxY)), fontsize=self.fontsize)

        # automatic displayed ticks
        ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
        ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
        # Set the font size of the ticks on both axes
        ax.tick_params(axis='both', which='major', labelsize=self.fontsize)
        # Create a legend
        plt.tight_layout()
        plt.show()

    def getPLpixelIntervalMaxIndex(self):#getPLpixelSpecMax(self):
        # fill matrix with data of the selected enry:
        self.updatewl()
        for i in range(len(self.SpecDataMatrix)):
            for j in range(len(self.SpecDataMatrix[i])):
                if type(self.SpecDataMatrix[i][j]) == SpectrumData:
                    try:
                        self.selectspecboxVari = self.selectspecbox.get()
                        if self.speckeys[self.selectspecboxVari] == 'WL': #Wavelength
                            self.PixMatrix[i][j] = np.sum(self.SpecDataMatrix[i][j].WL[self.aqpixstart:self.aqpixend])
                        elif self.speckeys[self.selectspecboxVari] == 'BG': #Background
                            self.PixMatrix[i][j] = np.sum(self.SpecDataMatrix[i][j].BG[self.aqpixstart:self.aqpixend])
                        elif self.speckeys[self.selectspecboxVari] == 'PL': # Counts
                            self.PixMatrix[i][j] = np.sum(self.SpecDataMatrix[i][j].PL[self.aqpixstart:self.aqpixend])
                        elif self.speckeys[self.selectspecboxVari] == 'PLB': #Spectrum
                            self.PixMatrix[i][j] = np.sum(self.SpecDataMatrix[i][j].PLB[self.aqpixstart:self.aqpixend])
                    except Exception as e:
                        print(str(e))
                        
    def getPLpixelSpecMax(self):#getPLpixelIntervalMaxIndex(self):
        # fill matrix with data of the selected enry:
        self.updatewl()
        self.updatecountthresh()
        for i in range(len(self.SpecDataMatrix)):
            for j in range(len(self.SpecDataMatrix[i])):
                if type(self.SpecDataMatrix[i][j]) == SpectrumData:
                    try:
                        self.selectspecboxVari = self.selectspecbox.get()
                        if self.speckeys[self.selectspecboxVari] == 'WL': #Wavelength
                            if np.sum(self.SpecDataMatrix[i][j].WL[self.aqpixstart:self.aqpixend]) < self.countthreshv:
                                self.PixMatrix[i][j] = np.nan
                            else:
                                self.PixMatrix[i][j] = self.SpecDataMatrix[i][j].WL[self.SpecDataMatrix[i][j].WL[self.aqpixstart:self.aqpixend].index(np.amax(self.SpecDataMatrix[i][j].WL[self.aqpixstart:self.aqpixend]))+self.aqpixstart]
                        elif self.speckeys[self.selectspecboxVari] == 'BG': #Background
                            if np.sum(self.SpecDataMatrix[i][j].BG[self.aqpixstart:self.aqpixend]) < self.countthreshv:
                                self.PixMatrix[i][j] = np.nan
                            else:
                                self.PixMatrix[i][j] = self.SpecDataMatrix[i][j].WL[self.SpecDataMatrix[i][j].BG[self.aqpixstart:self.aqpixend].index(np.amax(self.SpecDataMatrix[i][j].BG[self.aqpixstart:self.aqpixend]))+self.aqpixstart]
                        elif self.speckeys[self.selectspecboxVari] == 'PL': # Counts
                            if np.sum(self.SpecDataMatrix[i][j].PL[self.aqpixstart:self.aqpixend]) < self.countthreshv:
                                self.PixMatrix[i][j] = np.nan
                            else:
                                self.PixMatrix[i][j] = self.SpecDataMatrix[i][j].WL[self.SpecDataMatrix[i][j].PL[self.aqpixstart:self.aqpixend].index(np.amax(self.SpecDataMatrix[i][j].PL[self.aqpixstart:self.aqpixend]))+self.aqpixstart]
                        elif self.speckeys[self.selectspecboxVari] == 'PLB': #Spectrum
                            if np.sum(self.SpecDataMatrix[i][j].PLB[self.aqpixstart:self.aqpixend]) < self.countthreshv:
                                self.PixMatrix[i][j] = np.nan
                            else:
                                self.PixMatrix[i][j] = self.SpecDataMatrix[i][j].WL[self.SpecDataMatrix[i][j].PLB[self.aqpixstart:self.aqpixend].index(np.amax(self.SpecDataMatrix[i][j].PLB[self.aqpixstart:self.aqpixend]))+self.aqpixstart]
                    except Exception as e:
                        print('Error in getPLpixelSpecMax', str(e))
                else:
                    self.PixMatrix[i][j] = np.nan

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
            specobj = SpectrumData(i, self.WL, self.BG, self.loadeachbg, self.linearbg, self.removecosmics,  self.cosmicthreshold, self.cosmicpixels, self.remcosmicfunc)
            if specobj.dataokay == True:
                self.specs.append(specobj)

    def autogenmatrix(self):
        self.mxcoords = []
        self.mycoords = []
        if len(self.specs) == 0:
            messagebox.showerror("Error", 'No valid Data found. Check Data Files.')
        elif len(self.specs) == 1:
            self.mxcoords.append(self.specs[0].data['x-position'])
            self.mycoords.append(self.specs[0].data['y-position'])
            self.PixAxX = [0]
            self.PixAxY = [0]
            self.SpecDataMatrix = [[self.specs[0]]]
            self.PixMatrix = [[0]]
            self.gdx = 0
            self.gdy = 0
        else:
            for i in self.specs:
                if i is not None:
                    if i.data['x-position'] not in self.mxcoords:
                        self.mxcoords.append(i.data['x-position'])
                    if i.data['y-position'] not in self.mycoords:
                        self.mycoords.append(i.data['y-position'])
            self.mxcoords = sorted(self.mxcoords)
            self.mycoords = sorted(self.mycoords)
            self.PixMatrix, self.SpecDataMatrix, self.PixAxX, self.PixAxY = self.genmatgrid(self.mxcoords, self.mycoords)
            self.SpecdataintoMatrix()

    # set the spectra into the array
    def SpecdataintoMatrix(self):
        # sorting function
        for i in self.specs:
            x = i.data['x-position']
            y = i.data['y-position']
            xind, yind = deflib.closest_indices(self.PixAxX, self.PixAxY, x, y)
            if type(self.SpecDataMatrix[yind][xind]) == SpectrumData:
                print('Matrix to small for pixel resolution. Point neglected. Retry with higher resolution. {} {}'.format(xind, yind))
            else:
                #self.SpecDataMatrix[xind][yind] = i
                self.SpecDataMatrix[yind][xind] = i
        
    def genmatgrid(self, xar, yar): # returns that must be filled with the SpectrumData Objects
        self.matstart = [np.amin(self.mxcoords), np.amin(self.mycoords)]
        self.matend = [np.amax(self.mxcoords), np.amax(self.mycoords)]
        dxa = deflib.findif(self.mxcoords)
        dya = deflib.findif(self.mycoords)
        self.dxanodup = deflib.remove_duplicates(dxa)
        self.dyanodup = deflib.remove_duplicates(dya)
        if len(self.dxanodup) == 1:
            self.gdx = dxa[0]
        else:
            self.gdx = deflib.most_freq_element(dxa)
        if len(self.dyanodup) == 1:
            self.gdy = dya[0]
        else:
            self.gdy = deflib.most_freq_element(dya)
        self.gdx = round(self.gdx, 10)
        self.gdy = round(self.gdy, 10)
        matpixax = []
        matpiyax = []
        PixelMatrix = []
        SpectralMatrix = []
        for i in range(int((self.matend[0]-self.matstart[0]+self.gdx)/self.gdx)):
            matpixax.append(round(i*self.gdx+self.matstart[0], 10))
        for i in range(int((self.matend[1]-self.matstart[1]+self.gdy)/self.gdy)):
            matpiyax.append(round(i*self.gdy+self.matstart[1], 10))
            fillmat = []
            pixmat = []
            for j in matpixax:
                fillmat.append(np.nan)#None)
                pixmat.append(0)
            SpectralMatrix.append(fillmat)
            PixelMatrix.append(pixmat)
        return(PixelMatrix, SpectralMatrix, matpixax, matpiyax)
