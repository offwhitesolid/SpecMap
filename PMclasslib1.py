import numpy as np

class PMclass(): # PixMatrix class
    def __init__(self, PixMatrix, xax, yax, metadata):
        self.PixMatrix = PixMatrix
        self.xax = xax
        self.yax = yax
        self.metadata = metadata
        self.gdx = self.xax[1] - self.xax[0]
        self.gdy = self.yax[1] - self.yax[0]

class Spectra():
    def __init__(self, xax, yax, metadata):
        self.xax = xax
        self.yax = yax
        self.metadata = metadata
        self.gdx = self.xax[1] - self.xax[0]
        self.gdy = self.yax[1] - self.yax[0]
