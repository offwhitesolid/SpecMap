import numpy as np
from PIL import Image
from matplotlib.figure import Figure
import sys, pickle, copy
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,  
NavigationToolbar2Tk)
from matplotlib.widgets import Cursor
from matplotlib.widgets import Button
import matplotlib.patches as mpatches
from scipy.optimize import curve_fit
from scipy.special import wofz
from tkinter import filedialog
import mathlib3 as matl # type: ignore
import deflib1 as deflib # type: ignore
import PMclasslib1 as PMlib # type: ignore

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
        self.roistore = {}
        self.PL = []
        self._read_file()

        # init fit data
        self.fwhm = np.nan
        self.fitmaxX = np.nan
        self.fitmaxY = np.nan
        self.fitdata = [None] # only fit parameter are stored, not the fit itself
        self.fitparams = matl.buildfitparas() # store all fit parameters

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
            print("Attribute {} not found in class SpectrumData.".format(attr_name))


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
        self.countthreshv = self.defentries['colormap_threshold']
        self.loadfiles()
        self.disspecs = {}                                                  # displayed spectra Objects contains [spec][wl]{metadata}
        self.cmapframe = cmapframe                                          # Colormap Frame
        self.specframe = specframe                                          # Spectrum Frame
        self.DataSpecMin = np.amin(self.WL)                                 # Spectrum Start
        self.DataSpecMax = np.amax(self.WL[-1])                             # Spectrum End
        self.DataSpecdL = self.specs[0].data['Delta Wavelength (nm)']       # delta Lambda
        self.allfpnames = matl.getlistofallFitparameters()
        self.allfpnamesinone = matl.getlistofallFitparaminone()
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
        #if self.defentries['enable_buttonmatrix'] == True:
        self.build_PixMatrix_frame(self.cmapframe)                          # build Pixel Matrix GUI
        self.buildselectboxes(self.cmapframe, list(self.speckeys.keys()))

        self.updatewl()
        self.PMmetadata['HSI0'] = {'wlstart': self.wlstart, 'wlend': self.wlend, 'countthresh': self.countthreshv, 'aqpixstart': self.aqpixstart, 'aqpixend': self.aqpixend}
        self.UpdateHSIselect()

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
    
    def updateproc_spec_max(self):
        try:
            self.proc_spec_min.delete(0, tk.END)
            self.proc_spec_min.insert(0, self.wlstart)
            self.proc_spec_max.delete(0, tk.END)
            self.proc_spec_max.insert(0, self.wlend)
        except Exception as e:
            messagebox.showerror("Error", '{} Insert valid spectral Borders of type float.'.format(str(e)))
        self.updatewl()

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

    def build_roi_frame(self, parframe, PMname='HSI0'):
        self.roihandler = Roihandler()#self)
        self.roisel = tk.StringVar()

        frame = tk.Frame(parframe, border=5, relief="raised")
        frame.grid(row=0, column=5, rowspan=6, sticky=tk.NW)
        tk.Label(frame, text="Select ROI").grid(row=0, column=0)
        self.roiselgui = ttk.Combobox(frame, textvariable=self.roisel)
        self.roiselgui.grid(row=1, column=0)
        try:
            b1 = tk.Button(frame, text="ROI Editing last Selection", command= lambda: self.roihandler.construct(self.PMdict[self.hsiselect.get()].PixMatrix, self.roiselgui))
        except: # select first HSI
            print('HSI selection failed. Selecting first HSI.')
            self.hsiselect.set(self.PMdict.keys()[0])
            b1 = tk.Button(frame, text="ROI Editing last Selection", command= lambda: self.roihandler.construct(self.PMdict[self.hsiselect.get()].PixMatrix, self.roiselgui))
        b1.grid(row=2, column=0)
        b2 = tk.Button(frame, text="plot ROI", command= lambda: self.roihandler.plotroi())
        b2.grid(row=3, column=0)
        b3 = tk.Button(frame, text="delete ROI", command= lambda: self.roihandler.delete_roi())
        b3.grid(row=4, column=0)     
    
        # build second clumn for ROI
        tk.Label(frame, text="Select HSI Image").grid(row=0, column=1)
        self.hsiselect = ttk.Combobox(frame)
        self.hsiselect.grid(row=1, column=1)
        b4 = tk.Button(frame, text="Plot HSI", command= lambda: self.plotPixelMatrix(self.hsiselect.get())) # original command
                       # test
                       #command = lambda: [self.plotPixelMatrix(i) for i in range(len(self.PMdict.keys()))]) # test command
        b4.grid(row=2, column=1)
        b5 = tk.Button(frame, text="Multiply HSI with ROI", command= lambda: self.multiroitopixmatrix())
        b5.grid(row=3, column=1)
        b6 = tk.Button(frame, text="Delete selected HSI", command= lambda: self.delHSI())
        b6.grid(row=4, column=1)

        # build third column for Spectral Data
        tk.Label(frame, text="Select Spectral Data").grid(row=0, column=2)
        self.specselect = ttk.Combobox(frame)
        self.specselect.grid(row=1, column=2)
        b7 = tk.Button(frame, text="Plot Spectrum", command= lambda: self.plotSpectral(self.specselect.get()))
        b7.grid(row=2, column=2)
        b8 = tk.Button(frame, text="Save Spectrum to .txt", command= lambda: self.saveSpectrum(self.specselect.get()))
        b8.grid(row=3, column=2)
        b9 = tk.Button(frame, text="average hsi to spectrum", command= lambda: self.averageHSItoSpecData())
        b9.grid(row=5, column=2)
        b10 = tk.Button(frame, text="Delete selected Spectral Data", command= lambda:
                          self.delSpecData(self.specselect.get()))
        b10.grid(row=4, column=2)
        # add entry for a correction spectrum
        tk.Label(frame, text="Correction Spectrum").grid(row=6, column=2)

        # Button to select correction spectrum file
        b11 = tk.Button(frame, text="Select Correction Spec File", command=self.select_correction_spectrum_file)
        b11.grid(row=7, column=2)
        b11 = tk.Button(frame, text="Correct Spectrum", command= lambda: self.correctSpectrum(self.specselect.get()))
        b11.grid(row=8, column=2)
    
    def select_correction_spectrum_file(self):
        self.correctionspecname = filedialog.askopenfilename(filetypes=[("Correction spectrum", "*")])

    def correctSpectrum(self, specname):
        # correct the selected spectrum with the entered correction spectrum
        try:
            correctionname = self.correctionspecname
        except Exception as e:
            print('Error correcting spectrum.', e)
        # load the correction spectrum
        #self.loadcorrectionSpectrum(correctionname)
        self.correctionWL, self.correctionSpec = deflib.loadexpspec(correctionname)

        # plot the correction spectrum
        plt.plot(self.correctionWL, self.correctionSpec)
        plt.plot(self.disspecs[specname].WL, self.disspecs[specname].Spec)
        plt.show()

        # correct the selected spectrum with the correction spectrum. Make sure to match the WL by interpolation
        corrected_spec = deflib.correct_spectrum(self.disspecs[specname].Spec, self.disspecs[specname].WL, self.correctionSpec, self.correctionWL)
        spname = '{}_corrected'.format(self.createdisspecname())
        self.disspecs[spname] = copy.deepcopy(self.disspecs[specname])
        self.disspecs[spname].Spec = corrected_spec
        # update the combobox with the new spectrum name
        # todo: fix this
        self.specselect['values'] = list(self.disspecs.keys())
        self.specselect.set(list(self.disspecs.keys())[-1])
        #self.disspecs['{}_corrected'.format(self.createdisspecname())].Spec = corrected_spec
    
    def loadcorrectionSpectrum(self, specname):
        try: 
            correctionname = self.correctionspecname
        except Exception as e:
            print('Error loading correction spectrum.', e)
            return
        # load a correction spectrum
        with open(correctionname, 'r') as file:
            _ = file.readline()
            lines = file.readlines()
        WL = []
        spec = []
        for line in lines:
            line = line.strip()
            if line:
                parts = line.split('\n')[0].split('\t')
                WL.append(float(parts[0]))
                spec.append(float(parts[1]))
        self.correctionWL = WL
        self.correctionSpec = spec
    
    def averageHSItoSpecData(self):
        # average all HSI to a single SpectrumData
        self.hsiselected = self.hsiselect.get()
        # get wlstart and wlend from self.hsiselected
        self.updatewl()
        # update wlstart and wlend entries on GUI
        metadata = {'wlstart': self.wlstart, 'wlend': self.wlend, 'countthresh': self.countthreshv, 'aqpixstart': self.aqpixstart, 'aqpixend': self.aqpixend}
        WL = self.WL[self.aqpixstart: self.aqpixend]
        PLB = WL.copy()
        speccount = 0
        print('wlstart, wlend', 'aqpixstart, aqpixend', self.wlstart, self.wlend, self.aqpixstart, self.aqpixend)
        for i in range(len(self.SpecDataMatrix)):
            for j in range(len(self.SpecDataMatrix[i])):
                if np.isnan(self.PMdict[self.hsiselected].PixMatrix[i][j]) == False:
                    speccount += 1
                    for k in range(self.aqpixstart, self.aqpixend):
                        # average HSI to spec for all pixels that are not NaN in the selected HSI
                        PLB[k-self.aqpixstart] += self.SpecDataMatrix[i][j].PLB[k]
        PLB = np.divide(PLB, speccount)
        self.disspecs[self.createdisspecname()] = PMlib.Spectra(PLB, WL, metadata, self.hsiselected)
        # update the selectbox for spectral data
        self.specselect['values'] = list(self.disspecs.keys())
        self.specselect.set(list(self.disspecs.keys())[-1])
    
    def createdisspecname(self): # create a new spectral data name
        if len(self.disspecs) == 0:
            specname = 'SpectrumData0'
        else:
            i = 0
            while 'SpectrumData{}'.format(i) in self.disspecs.keys():
                i += 1
            specname = 'SpectrumData' + str(i)
        return specname 
    
    def saveSpectrum(self, specname):
        savename = tk.filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text files', '*.txt')])
        if savename:
            self.disspecs[specname].save(savename)
    
    def delSpecData(self, specname): # self.disspecs is type dict
        # delete the selected spectral data
        try:
            del self.disspecs[specname]
            if len(self.disspecs) == 0:
                pass
            else:
                self.specselect['values'] = list(self.disspecs.keys())
                self.specselect.set(list(self.disspecs.keys())[-1])
        except Exception as e:
            print('Error deleting spectral data.', e)
    
    def plotSpectral(self, specname):
        # plot the selected spectral data
        try:
            selspec = self.specselect.get()
            selspecdataclass = self.disspecs[specname]
            # plot the selected spectral data
            self.PlotSpectrum(selspecdataclass.Spec, selspecdataclass.WL, 'Averaged HSI Spectrum')
        except Exception as e:
            print('Error plotting spectral data.', e)
    
    def pltoselspecvsselWL(self):
        # plot the selected spectral data vs the selected WL
        fig, ax = plt.subplots()
        ax.plot(self.selWL, self.selspecdata)
        ax.set_xlabel('Wavelength [nm]')
        ax.set_ylabel('Intensity [counts]')
        ax.set_title('Spectral Data')
        plt.show()
    
    def build_plotfitparamframe(self, parframe):
        frame = tk.Frame(parframe, border=5, relief="sunken")
        frame.grid(row=0, column=6, rowspan=6, sticky=tk.NW)
        tk.Label(frame, text="Plot Fit Parameters".format(self.DataSpecMin)).grid(row=0, column=0)
        updatefitparamsbutton = tk.Button(frame, text="Update Fit Parameters", command= lambda: self.updatefitparamplot())
        # add selectbox for fit parameters
        self.selectfitparambox = ttk.Combobox(frame, values=['FWHM', 'Center X', 'Center Y'])
    
    def updatefitplotparamplots(self):
        # obtain parameters from all fits that can be obtain and update self.selectfitparambox with them
        #self.selectfitparambox.set('FWHM')
        pass

    def fit2dgausstopixmatrix(self):
        try: 
            self.maxiter = int(self.fitmaxiter.get())
        except:
            print('Maxiter must be type int. Using default 1000.')
            self.maxiter = 1000
        try:
            PMselect = self.getPixMatrixSelection(self.hsiselect.get())
            matl.fitgaussian2dtomatrix(self.PMdict[PMselect].PixMatrix, True, self.gdx, self.gdy, self.colormap.get(), maxfev=self.maxiter)
        except:
            print('2D Gaussian Fit failed.')
            
    def fit2drotgausstopixmatrix(self):
        try: 
            self.maxiter = int(self.fitmaxiter.get())
        except:
            print('Maxiter must be type int. Using default 1000.')
            self.maxiter = 1000
        try:
            PMselect = self.getPixMatrixSelection(self.hsiselect.get())
            matl.fitgaussiand2dtomatrixrot(self.PMdict[PMselect].PixMatrix, True, self.gdx, self.gdy, self.colormap.get(), maxfev=self.maxiter)
        except Exception as Error:
            print('2D rotational Gaussian Fit failed.', Error)
        
    # Matrix with Pixels to obtain spectrum
    def build_button_frame(self, placeframe, width=600, height=600):
        # create new subframe

        parframe = tk.Frame(placeframe)
        #parframe.pack(side=tk.TOP, anchor=tk.W, expand=False)#, fill=tk.Y)
        parframe.grid(row=0, column=0, sticky=tk.NW)

        # create input GUI, ButtonMatrix is created in buildButtonMatrix in seperate frame
        firstPM = list(self.PMdict.keys())[0]
        n = len(firstPM)
        m = len(firstPM[0])
        plotframe = tk.Frame(parframe, border=5, relief="raised")
        plotframe.grid(row=0, column=0, sticky=tk.NW)
        tk.Label(plotframe, text='Press Plot Spectrum\nto plot selected Pixel\nPixel Loaded: {} x {}'.format(len(self.SpecDataMatrix[0]), len(self.SpecDataMatrix))).pack(side=tk.TOP, anchor=tk.W)
        tk.Label(plotframe, text='selected Pixel: ').pack(side=tk.TOP, anchor=tk.W)
        xyframe = tk.Frame(plotframe)
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
        # inside xyframe
        self.newselx = 0
        self.newsely = 0

        tk.Label(plotframe, text="Select Data Set".format(self.DataSpecMax)).pack(side=tk.TOP, anchor=tk.W)
        self.selectspecpixbox = ttk.Combobox(plotframe, values=list(self.speckeys.keys()))
        self.selectspecpixbox.set(list(self.speckeys.keys())[-1])
        self.selectspecpixbox.pack(side=tk.TOP, anchor=tk.W)

        b1 = tk.Button(plotframe, text="Plot Spectrum", command=self.PlotPixelSpectrum)
        b1.pack(side=tk.TOP, anchor=tk.W)

        if self.defentries['enable_buttonmatrix'] == True:
            b2 = tk.Button(parframe, text="Create Button Matrix", command= lambda: self.buildButtonMatrix(parframe, n, m)) # do not use the buttonmatrix !!!
            b2.pack(side=tk.BOTTOM, anchor=tk.W)

        # add new frame for Fit Parameters
        fitframe = tk.Frame(placeframe, border=5, relief="raised")
        fitframe.grid(row=0, column=1, sticky=tk.NW)

        # fit to spectrum
        tk.Label(fitframe, text="Select Fit function".format(self.DataSpecMax)).pack(side=tk.TOP, anchor=tk.W)
        self.selectwindowbox = ttk.Combobox(fitframe, values=list(self.windowfunctions))
        self.selectwindowbox.set(self.defentries['selected_fit_function'])
        self.selectwindowbox.pack(side=tk.TOP, anchor=tk.W)
        b3 = tk.Button(fitframe, text="Fit Window to Spectrum", command=lambda: self.fitwindowtospec('fitmaxX', newfit=True))
        b3.pack(side=tk.TOP, anchor=tk.W)
        self.sepfitfunct = tk.IntVar()
        b4 = tk.Button(fitframe, text="plot existing fit and spectrum", command=lambda: self.fitwindowtospec('fitmaxX', newfit=False))
        b4.pack(side=tk.TOP, anchor=tk.W)
        self.sepfitfunct.set(0)
        self.sepfitfunctsbut = tk.Checkbutton(fitframe, text="Separate Fit Functions", variable=self.sepfitfunct)
        self.sepfitfunctsbut.pack(side=tk.TOP, anchor=tk.W)

        # create a select box for the parameters of each fit
        tk.Label(fitframe, text="HSI from Fit Parameter").pack(side=tk.TOP, anchor=tk.W)
        self.selectfitparambox = ttk.Combobox(fitframe, values=self.allfpnamesinone)
        self.selectfitparambox.pack(side=tk.TOP, anchor=tk.W)
        self.selectfitparambox.set(self.allfpnamesinone[0]) # set default value
        b3 = tk.Button(fitframe, text="Plot HSI from Fit Parameter", command= lambda: self.plotHSIfromfitparam())
        b3.pack(side=tk.TOP, anchor=tk.W)

        self.build_roi_frame(placeframe)
        buttons = []
        self.SpecButtons = []
        return buttons
        
        # fram = Tkinter frame, n = len(self.PMdict[i].PixMatrix), m = len(self.PMdict[i].PixMatrix[0])
    def buildButtonMatrix(self, frame, n, m):
        # create new subframe
        butmatframe = tk.Frame(frame)
        butmatframe.pack(side=tk.TOP, anchor=tk.W, fill=tk.BOTH, expand=True)

        # create buttons
        buttons = []
        self.vvars = []
        for row in range(n):
            row_buttons = []
            row_vars = []
            for col in range(m):
                var = [col, row]
                button = tk.Button(butmatframe, bg="red", command=lambda v=var: self.button_click(v))
                button.grid(row=row+1, column=col+1, sticky=tk.NSEW)
                row_buttons.append(button)
                row_vars.append(var)
            buttons.append(row_buttons)
            self.vvars.append(row_vars)
        # Configure row and column weights to make buttons fill the butmatframe
        for row in range(1, n+1):
            butmatframe.rowconfigure(row, weight=1)
        for col in range(1, m+1):
            butmatframe.columnconfigure(col, weight=1)
        # Add row axis
        for row in range(n):
            label = tk.Label(butmatframe, text=str(round(row*self.gdx, 10)), relief=tk.RAISED)
            label.grid(row=row+1, column=0, sticky=tk.NSEW)
        # Add column axis
        for col in range(m):
            label = tk.Label(butmatframe, text=str(round(col*self.gdy, 10)), relief=tk.RAISED)
            label.grid(row=0, column=col+1, sticky=tk.NSEW)
        self.SpecButtons = buttons
        self.buttonframe_updateColor()
        #return buttons

    def button_click(self, var):
        self.newselx = var[0]
        self.newsely = var[1]
        self.updateselectionentries()
    
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

    def updateselectionentries(self):
        self.selectPixX.delete(0, tk.END)
        self.selectPixX.insert(0, self.newselx)
        self.selectPixY.delete(0, tk.END)
        self.selectPixY.insert(0, self.newsely)

    # Max Counts Colormap
    def buildandPlotIntCmap(self):
        self.readfontsize()
        self.updatecountthresh()
        # update spec min and max values
        self.updatewl()
        # create a new colormap by copying the selected HSI
        lastpm = copy.deepcopy(self.PMdict[self.hsiselect.get()].PixMatrix)
        newpm = self.writetopixmatrix(lastpm, None)
        self.getPLpixelIntervalMaxIndex(self.PMdict[newpm].PixMatrix, False)
        self.plotPixelMatrix(self.hsiselect.get())
        self.UpdateHSIselect()
        
    # Spectral Maximum Colormap
    def buildandPlotSpecCmap(self):
        self.updatewl()
        self.updatecountthresh()
        self.readfontsize()
        lastpm = copy.deepcopy(self.PMdict[self.hsiselect.get()].PixMatrix)
        newpm = self.writetopixmatrix(lastpm, None)#str(self.selectspecpixbox.get()))
        self.fittoMatrixfitparams(self.PMdict[newpm].PixMatrix, 'fitmaxX') # new
        self.getPLpixelSpecMax(self.PMdict[newpm].PixMatrix)
        self.UpdateHSIselect()
    
        try:
            self.plotPixelMatrix(self.hsiselect.get())
        except Exception as e:
            print('Plot failed. {}'.format(str(e)))
            plt.cla()
    
    def updateandPlotSpecCmap(self, variable):
        #self.updatePixelMatrix(variable)
        self.plotPixelMatrix(self.hsiselect.get())
        self.UpdateHSIselect()

    def fitwindowtospec(self, variable, newfit=False):
        PixMatrix = self.PMdict[self.getPixMatrixSelection(self.hsiselect.get())].PixMatrix
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
                            self.SpecDataMatrix[y][x].fitmaxX, self.SpecDataMatrix[y][x].fitmaxY = self.fitkeys[self.selectwindowboxVari][2](self.aqpixstart, self.aqpixstart, *self.SpecDataMatrix[y][x].fitdata[:-1])
                            self.SpecDataMatrix[y][x].fitmaxX = self.SpecDataMatrix[y][x].fitmaxX*self.DataSpecdL+self.DataSpecMin
                            PixMatrix = self.SpecDataMatrix[y][x].get_attribute(variable)
                            print('Fit worked, {} {}'.format(self.SpecDataMatrix[y][x].fitmaxX, self.SpecDataMatrix[y][x].fitmaxY))
                        
                            #plt.scatter(self.SpecDataMatrix[y][x].fitmaxX, self.SpecDataMatrix[y][x].fitmaxY, color='red')
                        self.PlotFitSpectrum(self.SpecDataMatrix[y][x].WL[self.aqpixstart: self.aqpixend], data, ['Spectrometer counts', self.fitkeys[self.selectwindowboxVari][3]], [self.SpecDataMatrix[y][x].fitdata[:-1]], [self.fitkeys[self.selectwindowboxVari][0]])
                        
                    except Exception as e:
                        print('Fit filed. {}'.format(str(e)))
        else:
            print(self.SpecDataMatrix[y][x])  

    def fittoMatrixfitparams(self, PixMatrix, variable='fitmaxX', incmin=2, incmax=-2, nmin=20, nmax=20):
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
                            #try:
                            if True: # debug start
                                if self.speckeys[self.selectspecboxVari] == 'PLB': #Spectrum
                                    if np.sum(self.SpecDataMatrix[i][j].PLB[self.aqpixstart:self.aqpixend]) < self.countthreshv:
                                        PixMatrix[i][j] = np.nan
                                    else:
                                        try:
                                            self.maxiter = int(self.fitmaxiter.get())
                                        except:
                                            print('Maxiter must be int. Using default 1000.')
                                            self.maxiter = 1000
                                        self.SpecDataMatrix[i][j].fitdata = self.fitkeys[self.selectwindowboxVari][1](self.aqpixstart, self.aqpixend, self.SpecDataMatrix[i][j].WL, self.SpecDataMatrix[i][j].PLB, self.maxiter)
                                        self.SpecDataMatrix[i][j].fitmaxX, self.SpecDataMatrix[i][j].fitmaxY = self.fitkeys[self.selectwindowboxVari][2](self.aqpixstart, self.aqpixend, *self.SpecDataMatrix[i][j].fitdata[:-1])#[1]
                                        r_squared, ss_res, ss_tot = matl.calc_r_squared(self.SpecDataMatrix[i][j].PLB[self.aqpixstart:self.aqpixend], self.fitkeys[self.selectwindowboxVari][0](self.SpecDataMatrix[i][j].WL[self.aqpixstart:self.aqpixend], *self.SpecDataMatrix[i][j].fitdata[:-1]))
                                        a =  list(matl.fitkeys.keys()).index(self.selectwindowbox.get())
                                        # put fitdata into fitparams
                                        try:
                                            for k in range(matl.fitkeys[list(matl.fitkeys.keys())[a]][4]):
                                                self.SpecDataMatrix[i][j].fitparams[a][k] = self.SpecDataMatrix[i][j].fitdata[k]
                                            # store fitmaxX and fitmaxY in fitparams[-1] and [-2]
                                            self.SpecDataMatrix[i][j].fitparams[a][-1] = self.SpecDataMatrix[i][j].fitmaxX
                                            self.SpecDataMatrix[i][j].fitparams[a][-2] = self.SpecDataMatrix[i][j].fitmaxY
                                            # store aqpixstart and aqpixend in fitparams[-3] and [-4]
                                            self.SpecDataMatrix[i][j].fitparams[a][-3] = self.aqpixstart
                                            self.SpecDataMatrix[i][j].fitparams[a][-4] = self.aqpixend
                                            # store r_squared in fitparams [-7], [-8], [-9]
                                            self.SpecDataMatrix[i][j].fitparams[a][matl.addtofitparms.index('r_squared')-len(matl.addtofitparms)+1] = r_squared
                                            self.SpecDataMatrix[i][j].fitparams[a][matl.addtofitparms.index('ss_res')-len(matl.addtofitparms)+1] = ss_res
                                            self.SpecDataMatrix[i][j].fitparams[a][matl.addtofitparms.index('ss_tot')-len(matl.addtofitparms)+1] = ss_tot
                                        except Exception as e:
                                            print('Fit parameter update failed in new fitline. {}'.format(str(e)))

                                if self.SpecDataMatrix[i][j].fitdata == [None]:
                                    PixMatrix[i][j] = np.nan
                                else:
                                    # check if maximum is within the window and set to Intmatrix
                                    if self.SpecDataMatrix[i][j].fitmaxX >= self.wlstart and self.SpecDataMatrix[i][j].fitmaxX <= self.wlend:
                                        worked = True
                                        PixMatrix[i][j] = self.SpecDataMatrix[i][j].get_attribute(variable)
                                    else:
                                        pass
                                        #print(self.SpecDataMatrix[i][j].fitmaxX, self.SpecDataMatrix[i][j].fitmaxY)
                            #except Exception as e: # debug end
                                try:
                                    if adjmin == True:
                                        self.aqpixstart += incmin
                                        adjmin = False
                                    else:
                                        self.aqpixend += incmax
                                        adjmin = True
                                except:
                                    print("Fit Window ran out of Data. Fit to Matrix Failed at element {}, {} in exc1 function {}.\n{}".format(i, j, 'XYMap.fittoMatrixfitparams', str(e)))
                                    worked = True
                            print("Fit to Matrix Failed at element {}, {} in function {} \n{}".format(i, j, 'XYMap.fittoMatrixfitparams', 'not converged')) # print name of function
                            self.updatewl()

    # function currently not in use
    def fittoSpecfitparams(self, PixMatrix, variable='fitmaxX', incmin=2, incmax=-2, nmin=20, nmax=20):
        # fill matrix with data of the selected enry
        self.updatewl()
        x, y, valid = self.validpixelinput()
        if valid[0] == True and valid[1] == True:
            if type(self.SpecDataMatrix[y][x]) == SpectrumData:
                if self.SpecDataMatrix[y][x].dataokay == True:
                    self.selectwindowboxVari = self.selectwindowbox.get()
                    self.selectspecboxVari = self.selectspecbox.get()
                    tries = 1
                    worked = False
                    adjmin = True
                    # if fit does not work, adjust the window size
                    while tries < nmin+nmax and worked == False:
                        tries += 1
                        try:
                            if self.speckeys[self.selectspecboxVari] == 'PLB': #Spectrum
                                if np.sum(self.SpecDataMatrix[y][x].PLB[self.aqpixstart:self.aqpixend]) < self.countthreshv:
                                    PixMatrix[y][x] = np.nan
                                else:
                                    try:
                                        self.maxiter = int(self.fitmaxiter.get())
                                    except:
                                        print('Maxiter must be int. Using default 1000.')
                                        self.maxiter = 1000
                                    self.SpecDataMatrix[y][x].fitdata = self.fitkeys[self.selectwindowboxVari][1](self.aqpixstart, self.aqpixend, self.SpecDataMatrix[y][x].WL, self.SpecDataMatrix[y][x].PLB, self.maxiter)
                                    self.SpecDataMatrix[y][x].fitmaxX, self.SpecDataMatrix[y][x].fitmaxY = self.fitkeys[self.selectwindowboxVari][2](self.aqpixstart, self.aqpixend, *self.SpecDataMatrix[y][x].fitdata[:-1])#[1]
                                    r_squared, ss_res, ss_tot = matl.calc_r_squared(self.SpecDataMatrix[y][x].PLB[self.aqpixstart:self.aqpixend], self.fitkeys[self.selectwindowboxVari][0](self.SpecDataMatrix[y][x].WL[self.aqpixstart:self.aqpixend], *self.SpecDataMatrix[y][x].fitdata[:-1]))
                                    a =  list(matl.fitkeys.keys()).index(self.selectwindowbox.get())
                                    # put fitdata into fitparams
                                    try:
                                        for k in range(matl.fitkeys[list(matl.fitkeys.keys())[a]][4]):
                                            self.SpecDataMatrix[y][x].fitparams[a][k] = self.SpecDataMatrix[y][x].fitdata[k]
                                        # store fitmaxX and fitmaxY in fitparams[-1] and [-2]
                                        self.SpecDataMatrix[y][x].fitparams[a][-1] = self.SpecDataMatrix[y][x].fitmaxX
                                        self.SpecDataMatrix[y][x].fitparams[a][-2] = self.SpecDataMatrix[y][x].fitmaxY
                                        # store aqpixstart and aqpixend in fitparams[-3] and [-4]
                                        self.SpecDataMatrix[y][x].fitparams[a][-3] = self.aqpixstart
                                        self.SpecDataMatrix[y][x].fitparams[a][-4] = self.aqpixend
                                        # store r_squared, ss_res, ss_tot in fitparams[-5] and [-6] and [-7]
                                        self.SpecDataMatrix[y][x].fitparams[a][matl.addtofitparms.index('r_squared')-len(matl.addtofitparms)+1] = r_squared
                                        self.SpecDataMatrix[y][x].fitparams[a][matl.addtofitparms.index('ss_res')-len(matl.addtofitparms)+1] = ss_res
                                        self.SpecDataMatrix[y][x].fitparams[a][matl.addtofitparms.index('ss_tot')-len(matl.addtofitparms)+1] = ss_tot
                                    except Exception as e:
                                        print('Fit parameter update failed in new fitline in function {}. {}'.format(self.__name__, str(e)))
                        
                                if self.SpecDataMatrix[y][x].fitdata == [None]:
                                    PixMatrix[y][x] = np.nan 
                                else:
                                    # check if maximum is within the window and set to Intmatrix
                                    if self.SpecDataMatrix[y][x].fitmaxX >= self.wlstart and self.SpecDataMatrix[y][x].fitmaxX <= self.wlend:
                                        worked = True
                                        PixMatrix[y][x] = self.SpecDataMatrix[y][x].get_attribute(variable)
                                    else:
                                        pass
                                        #print(self.SpecDataMatrix[y][x].fitmaxX, self.SpecDataMatrix[y][x].fitmaxY)
                        except Exception as e:
                            try:
                                if adjmin == True:
                                    self.aqpixstart += incmin
                                    adjmin = False
                                else:
                                    self.aqpixend += incmax
                                    adjmin = True
                            except:
                                print("Fit Window ran out of Data. Fit to Matrix Failed at element {}, {}.\n{}".format(i, j, self.__name__, str(e)))
                                worked = True
                            print("Fit Window ran out of Data. Fit to Matrix Failed at element {}, {}.\n{}".format(i, j, str(e)))
                        self.updatewl()   

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
                                if self.speckeys[self.selectspecboxVari] == 'PLB': #Spectrum
                                    if np.sum(self.SpecDataMatrix[i][j].PLB[self.aqpixstart:self.aqpixend]) < self.countthreshv:
                                        PixMatrix[i][j] = np.nan
                                    else:
                                        try:
                                            self.maxiter = int(self.fitmaxiter.get())
                                        except:
                                            print('Maxiter must be int. Using default 1000.')
                                            self.maxiter = 1000
                                        self.SpecDataMatrix[i][j].fitdata = self.fitkeys[self.selectwindowboxVari][1](self.aqpixstart, self.aqpixend, self.SpecDataMatrix[i][j].WL, self.SpecDataMatrix[i][j].PLB, self.maxiter)
                                        self.SpecDataMatrix[i][j].fitmaxX, self.SpecDataMatrix[i][j].fitmaxY = self.fitkeys[self.selectwindowboxVari][2](self.aqpixstart, self.aqpixend, *self.SpecDataMatrix[i][j].fitdata[:-1])#[1]
                                        r_squared, ss_res, ss_tot = matl.calc_r_squared(self.SpecDataMatrix[i][j].PLB[self.aqpixstart:self.aqpixend], self.fitkeys[self.selectwindowboxVari][0](self.SpecDataMatrix[i][j].WL[self.aqpixstart:self.aqpixend], *self.SpecDataMatrix[i][j].fitdata[:-1]))
                                        a =  list(matl.fitkeys.keys()).index(self.selectwindowbox.get())
                                        # put fitdata into fitparams
                                        try:
                                            for k in range(matl.fitkeys[list(matl.fitkeys.keys())[a]][4]):
                                                self.SpecDataMatrix[i][j].fitparams[a][k] = self.SpecDataMatrix[i][j].fitdata[k]
                                            # store fitmaxX and fitmaxY in fitparams[-1] and [-2]
                                            self.SpecDataMatrix[i][j].fitparams[a][-1] = self.SpecDataMatrix[i][j].fitmaxX
                                            self.SpecDataMatrix[i][j].fitparams[a][-2] = self.SpecDataMatrix[i][j].fitmaxY
                                            # store aqpixstart and aqpixend in fitparams[-3] and [-4]
                                            self.SpecDataMatrix[i][j].fitparams[a][-3] = self.aqpixstart
                                            self.SpecDataMatrix[i][j].fitparams[a][-4] = self.aqpixend
                                            # store r_squared in fitparams [-7], [-8], [-9]
                                            self.SpecDataMatrix[i][j].fitparams[a][matl.addtofitparms.index('r_squared')-len(matl.addtofitparms)+1] = r_squared
                                            self.SpecDataMatrix[i][j].fitparams[a][matl.addtofitparms.index('ss_res')-len(matl.addtofitparms)+1] = ss_res
                                            self.SpecDataMatrix[i][j].fitparams[a][matl.addtofitparms.index('ss_tot')-len(matl.addtofitparms)+1] = ss_tot
                                        except Exception as e:
                                            print('Fit parameter update failed in new fitline. {}'.format(str(e)))

                                if self.SpecDataMatrix[i][j].fitdata == [None]:
                                    PixMatrix[i][j] = np.nan 
                                else:
                                    # check if maximum is within the window and set to Intmatrix
                                    if self.SpecDataMatrix[i][j].fitmaxX >= self.wlstart and self.SpecDataMatrix[i][j].fitmaxX <= self.wlend:
                                        worked = True
                                        PixMatrix[i][j] = self.SpecDataMatrix[i][j].get_attribute(variable)
                                    else:
                                        pass
                                        #print(self.SpecDataMatrix[i][j].fitmaxX, self.SpecDataMatrix[i][j].fitmaxY)
                            except Exception as e:
                                try:
                                    if adjmin == True:
                                        self.aqpixstart += incmin
                                        adjmin = False
                                    else:
                                        self.aqpixend += incmax
                                        adjmin = True
                                except:
                                    print("Fit Window ran out of Data. Fit to Matrix Failed at element {}, {} in function {}.\n{}".format(i, j, 'XYMap.updatecountthresh', str(e)))
                                    worked = True
                                print("Fit to Matrix Failed at element {}, {} in function {}.\n{}".format(i, j, 'XYMap.updatecountthresh', str(e)))     
                            self.updatewl()
    
    def fittoMatrix(self, PixMatrix, variable='fitmaxX', incmin=1, incmax=-1, nmin=20, nmax=20):
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
                                if self.speckeys[self.selectspecboxVari] == 'PLB': #Spectrum
                                    if np.sum(self.SpecDataMatrix[i][j].PLB[self.aqpixstart:self.aqpixend]) < self.countthreshv:
                                        PixMatrix[i][j] = np.nan
                                    else:
                                        try:
                                            self.maxiter = int(self.fitmaxiter.get())
                                        except:
                                            print('Maxiter must be int. Using default 1000.')
                                            self.maxiter = 1000
                                        self.SpecDataMatrix[i][j].fitdata = self.fitkeys[self.selectwindowboxVari][1](self.aqpixstart, self.aqpixend, self.SpecDataMatrix[i][j].WL, self.SpecDataMatrix[i][j].PLB, self.maxiter)
                                        self.SpecDataMatrix[i][j].fitmaxX, self.SpecDataMatrix[i][j].fitmaxY = self.fitkeys[self.selectwindowboxVari][2](self.aqpixstart, self.aqpixend, *self.SpecDataMatrix[i][j].fitdata[:-1])#[1]
                
                                if self.SpecDataMatrix[i][j].fitdata == [None]:
                                    PixMatrix[i][j] = np.nan 
                                else:
                                    # check if maximum is within the window and set to Intmatrix
                                    if self.SpecDataMatrix[i][j].fitmaxX >= self.wlstart and self.SpecDataMatrix[i][j].fitmaxX <= self.wlend:
                                        worked = True
                                        PixMatrix[i][j] = self.SpecDataMatrix[i][j].get_attribute(variable)
                                    else:
                                        pass
                                        #print(self.SpecDataMatrix[i][j].fitmaxX, self.SpecDataMatrix[i][j].fitmaxY)
                            except Exception as e:
                                try:
                                    if adjmin == True:
                                        self.aqpixstart += incmin
                                        adjmin = False
                                    else:
                                        self.aqpixend += incmax
                                        adjmin = True
                                except:
                                    print("Fit Window ran out of Data. Fit to Matrix Failed at element {}, {} in function {}.\n{}".format(i, j, 'XYMap.fittoMatrix', str(e)))
                                    worked = True
                                print("Fit to Matrix Failed at element {}, {} in function {}.\n{}".format(i, j, 'XYMap.fittoMatrix', str(e)))    
                                
    # function curently not in use
    def updatePixelMatrix(self, PixMatrix, variable, nonecase=np.nan):
        for i in range(len(self.SpecDataMatrix)):
            for j in range(len(self.SpecDataMatrix[i])):
                try:
                    PixMatrix[i][j] = self.SpecDataMatrix[i][j].get_attribute(variable)
                except Exception as e:
                    PixMatrix[i][j] = nonecase
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

    # Function to handle click events of the image
    def on_click(self, event, image):
        # Check if the click was within the axes
        if event.inaxes:
            # Get the coordinates of the click in pixel space
            self.newselx = int(event.xdata)
            self.newsely = int(event.ydata)
            #print("Clicked pixel: ({0}, {1}) - Value: {2}".format(self.newselx, self.newsely, image[self.newsely][self.newselx]))
            self.selectPixX.insert(0, self.newselx)
            self.selectPixY.insert(0, self.newsely)
            self.updateselectionentries()

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
                        self.PlotSpectrum(data, self.SpecDataMatrix[y][x].WL, 'PL Spectrum')
                    else:
                        print('No valid Data set selected for the Plot.')

    def PlotSpectrum(self, x, y, label):
        self.readfontsize()
        plt.figure(figsize=(10, 6))
        plt.plot(y, x, label=label, color='blue')       
        plt.xlabel('Wavelength / nm', fontsize=self.fontsize)
        plt.ylabel('Intensity / counts', fontsize=self.fontsize)
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
            try:
                for i in range(len(fitdata)):
                    plt.plot(x, fitfunc[i](x, *fitdata[i]), label=label[i+1], color='red')  
            except:
                plt.show()
        plt.xlabel('Wavelength / nm', fontsize=self.fontsize)
        plt.ylabel('Intensity', fontsize=self.fontsize)
        plt.title('Spectrograph Data', fontsize=self.fontsize)
        plt.legend(fontsize=self.fontsize)
        plt.tick_params(axis='both', which='major', labelsize=self.fontsize)
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def plotPixelMatrix(self, HSIname, cmapticks=6):
        fig, ax = plt.subplots()
        HSIimage = self.PMdict[HSIname].PixMatrix       
        # Display the data as an image with a colormap
        cax = ax.imshow(HSIimage, cmap=self.colormap.get()) # aspect='auto' for cubic image
        # Add a colorbar to the image
        cbar = fig.colorbar(cax, ax=ax)
        # Set the colorbar label
        cbar.set_label('Spectrometer Counts', fontsize=self.fontsize)
        # Set the ticks of the colormap
        #cbar_ticks=np.linspace(np.amin(self.PMdict[self.getPixMatrixSelection(self.hsiselect.get())].PixMatrix), np.amax(self.PMdict[self.getPixMatrixSelection(self.hsiselect.get())].PixMatrix), cmapticks)
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

        # click event
        cid = fig.canvas.mpl_connect('button_press_event', lambda event: self.on_click(event, self.PMdict[self.getPixMatrixSelection(self.hsiselect.get())].PixMatrix))
        self.updateselectionentries()
        fig.canvas.mpl_connect('motion_notify_event', lambda event: deflib.fig_on_hoverevent(event, ax, fig, self.PMdict[self.getPixMatrixSelection(self.hsiselect.get())].PixMatrix, (self.PixAxX[0], self.PixAxX[-1]), (self.PixAxY[0], self.PixAxY[-1])))

        plt.show()

    def getPixMatrixSelection(self, PMname=None):
        if PMname == None:
            PMname = self.hsiselect.get()
        try:
            if PMname not in list(self.PMdict.keys()):
                print('No Pixel Matrix with the given name for PlotPixelMatrixSpectral.')
                PMname = list(self.PMdict.keys())[0]
        except Exception as e:
            print('No Pixel Matrix with the given name for PlotPixelMatrixSpectral. {}'.format(str(e)))
            PMname = list(self.PMdict.keys())[0]
        return PMname


    def plotPixelMatrixSpectral(self):
        PMname = self.getPixMatrixSelection(self.hsiselect.get())
        fig, ax = plt.subplots()
        # Display the data as an image with a colormap
        cax = ax.imshow(self.PMdict[PMname].PixMatrix, cmap=self.colormap.get())#'viridis')
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

        # automatic displayed ticks
        ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
        ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
        # Set the font size of the ticks on both axes
        ax.tick_params(axis='both', which='major', labelsize=self.fontsize)
        # Create a legend
        plt.tight_layout()

        # click event
        cid = fig.canvas.mpl_connect('button_press_event', lambda event: deflib.on_click(event, self.PMdict[self.getPixMatrixSelection(self.hsiselect.get())].PixMatrix))
        self.updateselectionentries()

        plt.show()

    def getPLpixelIntervalMaxIndex(self, PixMatrix, makenan=False):
        # fill matrix with data of the selected enry:
        self.updatewl()
        for i in range(len(self.SpecDataMatrix)):
            for j in range(len(self.SpecDataMatrix[i])):
                if type(self.SpecDataMatrix[i][j]) == SpectrumData:
                    try:
                        self.selectspecboxVari = self.selectspecbox.get()
                        if self.speckeys[self.selectspecboxVari] == 'WL': #Wavelength
                            PixMatrix[i][j] = np.sum(self.SpecDataMatrix[i][j].WL[self.aqpixstart:self.aqpixend])
                        elif self.speckeys[self.selectspecboxVari] == 'BG': #Background
                            PixMatrix[i][j] = np.sum(self.SpecDataMatrix[i][j].BG[self.aqpixstart:self.aqpixend])
                        elif self.speckeys[self.selectspecboxVari] == 'PL': # Counts
                            PixMatrix[i][j] = np.sum(self.SpecDataMatrix[i][j].PL[self.aqpixstart:self.aqpixend])
                        elif self.speckeys[self.selectspecboxVari] == 'PLB': #Spectrum
                            PixMatrix[i][j] = np.sum(self.SpecDataMatrix[i][j].PLB[self.aqpixstart:self.aqpixend])
                        if PixMatrix[i][j] < self.countthreshv:
                            if makenan == True:
                                PixMatrix[i][j] = np.nan
                    except Exception as e:
                        print(str(e), 'Error in getPLpixelIntervalMaxIndex')
                if PixMatrix[i][j] == np.nan:
                    PixMatrix[i][j] = 0
                        
    def getPLpixelSpecMax(self, PixMatrix):
        # fill matrix with data of the selected enry:
        self.updatewl()
        self.updatecountthresh()
        for i in range(len(self.SpecDataMatrix)):
            for j in range(len(self.SpecDataMatrix[i])):
                if type(self.SpecDataMatrix[i][j]) == SpectrumData:
                    try:
                        self.selectspecboxVari = self.selectspecbox.get()
                        print('SelectSpecBoxVari', self.selectspecboxVari)
                        if self.speckeys[self.selectspecboxVari] == 'WL': #Wavelength
                            if np.sum(self.SpecDataMatrix[i][j].WL[self.aqpixstart:self.aqpixend]) < self.countthreshv:
                                PixMatrix[i][j] = np.nan
                            else:
                                PixMatrix[i][j] = self.SpecDataMatrix[i][j].fitmaxX
                        elif self.speckeys[self.selectspecboxVari] == 'BG': #Background
                            if np.sum(self.SpecDataMatrix[i][j].BG[self.aqpixstart:self.aqpixend]) < self.countthreshv:
                                PixMatrix[i][j] = np.nan
                            else:
                                PixMatrix[i][j] = self.SpecDataMatrix[i][j].fitmaxX
                        elif self.speckeys[self.selectspecboxVari] == 'PL': # Counts
                            if np.sum(self.SpecDataMatrix[i][j].PL[self.aqpixstart:self.aqpixend]) < self.countthreshv:
                                PixMatrix[i][j] = np.nan
                            else:
                                PixMatrix[i][j] = self.SpecDataMatrix[i][j].fitmaxX
                        elif self.speckeys[self.selectspecboxVari] == 'PLB': #Spectrum
                            if np.sum(self.SpecDataMatrix[i][j].PLB[self.aqpixstart:self.aqpixend]) < self.countthreshv:
                                PixMatrix[i][j] = np.nan
                            else:
                                PixMatrix[i][j] = self.SpecDataMatrix[i][j].fitmaxX
                    except Exception as e:
                        print('Error in getPLpixelSpecMax', str(e))
                        sys.exit()
                else:
                    PixMatrix[i][j] = np.nan

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
        self.PMdict = {}
        self.PMmetadata = {}
        if len(self.specs) == 0:
            messagebox.showerror("Error", 'No valid Data found. Check Data Files.')
        elif len(self.specs) == 1:
            self.mxcoords.append(self.specs[0].data['x-position'])
            self.mycoords.append(self.specs[0].data['y-position'])
            self.PixAxX = [0]
            self.PixAxY = [0]
            self.SpecDataMatrix = [[self.specs[0]]]
            PixMatrix = [[0]]
            self.gdx = 0
            self.gdy = 0
        else:
            #self.PMmetadata[self.hsiselect.get()] = {'wlstart': self.wlstart, 'wlend': self.wlend, 'countthresh': self.countthreshv, 'aqpixstart': self.aqpixstart, 'aqpixend': self.aqpixend}
            for i in self.specs:
                if i is not None:
                    if i.data['x-position'] not in self.mxcoords:
                        self.mxcoords.append(i.data['x-position'])
                    if i.data['y-position'] not in self.mycoords:
                        self.mycoords.append(i.data['y-position'])
            self.mxcoords = sorted(self.mxcoords)
            self.mycoords = sorted(self.mycoords)
            PixMatrix, self.SpecDataMatrix, self.PixAxX, self.PixAxY = self.genmatgrid(self.mxcoords, self.mycoords)
            PixMatrixc = PMlib.PMclass(np.asarray(PixMatrix, dtype=float), self.PixAxX, self.PixAxY, self.PMmetadata)
            self.PMdict['HSI0'] = PixMatrixc
            self.SpecdataintoMatrix()
    
    def UpdateHSIselect(self):
        self.hsiselect['values'] = list(self.PMdict.keys())
        self.hsiselect.current(0)
        # select the last HSI
        self.hsiselect.set(list(self.PMdict.keys())[-1])

    def multiroitopixmatrix(self):
        fig, ax = plt.subplots()
        if len(self.roihandler.roilist) == 0:
            print('No ROI found. Cannot create HSI.')
            return
        else: 
            roi = self.roihandler.roilist[self.roiselgui.get()]
            newroiname = "{}{}".format(self.hsiselect.get(), self.roiselgui.get())
        # Generate a copy of the selected PixMatrix class
        lastpixmatrix = copy.deepcopy(self.PMdict[self.hsiselect.get()])
        for i in range(len(lastpixmatrix.PixMatrix)):
            for j in range(len(lastpixmatrix.PixMatrix[i])):
                if np.isnan(roi[i][j]) == True:
                    lastpixmatrix.PixMatrix[i][j] = np.nan
        self.PMdict[newroiname] = lastpixmatrix
        #fig.imshow(self.PMdict[newroiname].PixMatrix) error
        ax.imshow(self.PMdict[newroiname].PixMatrix)
        fig.show()
        self.UpdateHSIselect()
    
    def delHSI(self):
        if len(self.PMdict) == 1:
            messagebox.showerror("Error", 'Cannot delete last HSI.')
        else:
            del self.PMdict[self.hsiselect.get()]
            #del self.PMmetadata[self.hsiselect.get()]
        self.UpdateHSIselect()

    # set the spectra into the array
    def SpecdataintoMatrix(self, overwrite=False):
        # sorting function
        for i in self.specs:
            x = i.data['x-position']
            y = i.data['y-position']
            xind, yind = deflib.closest_indices(self.PixAxX, self.PixAxY, x, y)
            if type(self.SpecDataMatrix[yind][xind]) == SpectrumData:
                if overwrite == True:
                    self.SpecDataMatrix[yind][xind] = i
                else:
                    print('Point neglected of index {} {}. Its pos is {} {}. Occupiing pos is {} {}'.format(
                        xind, yind, x, y, self.SpecDataMatrix[yind][xind].data['x-position'], self.SpecDataMatrix[yind][xind].data['y-position']))
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
    
    def writetopixmatrix(self, matrix, name=None):
        if name == None or name not in self.PMdict.keys():
            pmi = 0
            for i in range(len(list(self.PMdict.keys()))+1):
                newpmname = '{}{}'.format('HSI', i) # create name of new HSI
                if newpmname in list(self.PMdict.keys()):
                    pmi += 1
                else:
                    newpmname = '{}{}'.format('HSI', pmi) # create name of new HSI
                    break
        else: 
            newpmname = name
        # add ne PixMatrix to the dictionary with its metadata
        self.PMdict[newpmname] = PMlib.PMclass(np.asarray(matrix), self.PixAxX, self.PixAxY, self.PMmetadata)
        self.PMdict[newpmname].metadata = {'wlstart': self.wlstart, 'wlend': self.wlend, 'countthresh': self.countthreshv, 'aqpixstart': self.aqpixstart, 'aqpixend': self.aqpixend}
        return newpmname

    def plotHSIfromfitparam(self):
        self.updatewl()
        self.updatecountthresh()
        # test
        lastpm = copy.deepcopy(self.PMdict[self.hsiselect.get()].PixMatrix)
        newpm = self.writetopixmatrix(lastpm, None)
        self.getPLpixelIntervalMaxIndex(self.PMdict[newpm].PixMatrix, False)
        fitvari = self.allfpnamesinone.index(self.selectfitparambox.get())
        
        # get index of fitvari in self.allfitparams
        for i in range(len(self.SpecDataMatrix)):
            for j in range(len(self.SpecDataMatrix[i])):
                if type(self.SpecDataMatrix[i][j]) == SpectrumData:
                    if self.SpecDataMatrix[i][j].dataokay == True:
                        try:
                            pari, parj = matl.getindexofFitparameter(self.allfpnames, self.selectfitparambox.get())
                            if pari == None or parj == None:
                                raise Exception('Parameter not found in fitparams.')
                            pari = int(pari)
                            parj = int(parj)
                            if pari != -1 and parj != -1:
                                lastpm[i][j] = self.SpecDataMatrix[i][j].fitparams[pari][parj]
                            else:
                                lastpm[i][j] = np.nan
                                raise Exception('Parameter not found in fitparams.')
                        except Exception as e:
                            print('Error in plotHSIfromfitparam. {}'.format(str(e)))
                    else:
                        lastpm[newpm][i][j] = np.nan
                        print('No Data found in Pixel {}, {}'.format(i, j))
                else:
                    lastpm[newpm][i][j] = np.nan
                    print('No Data found in Pixel {}, {}'.format(i, j))
        # test
        self.plotPixelMatrix(newpm)
        #self.plotPixelMatrix(self.PMdict[newpm].PixMatrix)
        self.UpdateHSIselect()
        
class Roihandler():
    def __init__(self, roilist={}, pixmatrix=[[]]):
        self.roi_mode = True
        self.roi_points = []
        self.roi_lines = []
        self.fig = None
        self.roilist = roilist
        self.pixmatrix = pixmatrix
        self.pixmatrix = np.transpose(self.pixmatrix)

    def construct(self, pixmatrix, roiselgui):
        self.pixmatrix = pixmatrix
        self.pixmatrix = np.transpose(self.pixmatrix)
        self.roiselgui = roiselgui
        self.fig, self.ax = plt.subplots()
        self.fig.subplots_adjust(right=0.89)# distance on right side for buttons
        self.ax.imshow(pixmatrix, cmap='viridis')
        # plt.axess([left, bottom, width, height])
        self.ax_button_toggle = plt.axes([0.89, 0.95, 0.1, 0.05])
        self.button_toggle = Button(self.ax_button_toggle, 'Save ROI')
        self.button_toggle.on_clicked(self.toggle_roi)
        self.ax_button_clear = plt.axes([0.89, 0.89, 0.1, 0.05])
        self.button_clear = Button(self.ax_button_clear, 'Clear ROI')
        self.button_clear.on_clicked(self.clear_roi)
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        plt.show()
        self.selnewestroi()

    def toggle_roi(self, event):
        if self.roi_mode == True:
            fig, ax = plt.subplots()
            self.button_toggle.label.set_text('Edit ROI')
            if len(self.roi_points) > 2:
                nrois = len(list(self.roilist.keys()))
                for i in range(len(self.roi_points)):
                    self.roi_points[i] = [float(self.roi_points[i][0]), float(self.roi_points[i][1])]
                newroi = deflib.highlight_roi(self.pixmatrix, self.roi_points)
                # transpose newroi
                #newroi = np.transpose(newroi)
                self.roilist[str('roi'+str(nrois+1))] = newroi
                cax = ax.imshow(newroi, cmap='viridis')
                # add colorbar to the plot
                cbar = fig.colorbar(cax, ax=ax)

                plt.show()
                self.roiselgui['values'] = list(self.roilist.keys())
                self.roi_points.clear()
            self.roi_mode = False
            print(len(self.roilist))
        else:
            self.button_toggle.label.set_text('Save ROI')
            self.roi_points.clear()
            self.clear_roi_lines()
            self.roi_mode = True
            plt.draw()

    def clear_roi(self, event):
        self.clear_roi_points()
        self.clear_roi_lines()
        plt.draw()
            
    def on_click(self, event):
        if self.roi_mode and event.inaxes == self.ax:
            x, y = event.xdata, event.ydata
            self.roi_points.append((x, y))
            point_plot, = self.ax.plot(x, y, 'ro')
            self.roi_lines.append(point_plot)
            if len(self.roi_points) > 1:
                line_plot, = self.ax.plot([self.roi_points[-2][0], x],
                                            [self.roi_points[-2][1], y], 'r-')
                self.roi_lines.append(line_plot)
            plt.draw()

    def clear_roi_points(self):
        self.roi_points.clear()

    def clear_roi_lines(self):
        for line in self.roi_lines:
            line.remove()
        self.roi_lines.clear()
    
    def plotroi(self, fontsize=12):
        # get selection of self.roiselgui
        roi = self.roilist[self.roiselgui.get()]
        fig, ax = plt.subplots()
        cax = ax.imshow(roi, cmap='viridis')
        cbar = fig.colorbar(cax, ax=ax)
        cbar.set_label('ROI', fontsize=fontsize)
        cbar.ax.tick_params(labelsize=fontsize)
        ax.set_title('Region of Interest')
        ax.set_xlabel('Nanostage X Axis in \u03bcm', fontsize=fontsize)
        ax.set_ylabel('Nanostage Y Axis in \u03bcm', fontsize=fontsize)
        plt.show()
    
    def delete_roi(self):
        if self.roiselgui.get() != '':
            del self.roilist[self.roiselgui.get()]
            self.roiselgui['values'] = list(self.roilist.keys())
            self.selnewestroi()
            plt.show()
        else:
            pass
    
    def selnewestroi(self):
        if len(self.roilist) > 0:
            self.roiselgui.set(list(self.roilist.keys())[-1])
        else:
            self.roiselgui.set('')