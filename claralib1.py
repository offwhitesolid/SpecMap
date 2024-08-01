import numpy as np
import os, sys
from scipy.optimize import curve_fit
from scipy.special import jv
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import tkinter as tk

class imageprocessor():
    def __init__(self, Notebook, imagefile, loadfunct, metadata, dx, dy):
        self.Notebook = Notebook
        self.imagefile = imagefile
        self.loadfunct = loadfunct
        self.metadata = metadata
        self.dx = dx
        self.dy = dy
        self.buildnotebook()
    
    def buildnotebook(self):
        # load the image 
        self.imagedata = self.loadfunct(self.imagefile)
        # create a new frame for the image processing
        self.image_frame = tk.Frame(self.Notebook, borderwidth=5, relief="ridge")
        self.image_frame.grid(row=0, column=0, sticky='nsew')

        # create a new frame for the image processing
        self.image_frame = tk.Frame(self.Notebook, borderwidth=5, relief="ridge")
        self.image_frame.grid(row=0, column=0, sticky='nsew')
        self.plotimage = tk.Button(self.image_frame, text='Plot Image', command=self.plotimage)
        self.plotimage.grid(row=0, column=0)

    def plotimage(self):
        fig, ax = plt.subplots()
        fig.imshow(self.imagedata, cmap='viridis')
        fig.colorbar()
        # Get current ticks
        current_xticks = np.arange(self.imagedata.shape[1])
        current_yticks = np.arange(self.imagedata.shape[0])
        # Multiply ticks by constants
        new_xticks = np.multiply(current_xticks, self.dx).round(2)
        new_yticks = np.multiply(current_yticks, self.dy).round(2)
        # Set new ticks
        ax.set_xticks(current_xticks)  # Set the ticks to be at the indices of the current ticks
        ax.set_yticks(current_yticks)
        # Set tick labels to the new values
        ax.set_xticklabels(new_xticks)
        ax.set_yticklabels(new_yticks)
        # Set the axis labels auto adjust
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.yaxis.set_major_locator(MaxNLocator(nbins=6))  # Adjust the number of bins to fit the plot size
    