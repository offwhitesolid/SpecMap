import numpy as np
import json

class PMclass(): # PixMatrix class
    def __init__(self, PixMatrix, xax, yax, metadata):
        self.PixMatrix = PixMatrix
        self.xax = xax
        self.yax = yax
        self.metadata = metadata
        self.gdx = self.xax[1] - self.xax[0]
        self.gdy = self.yax[1] - self.yax[0]

class Spectra():
    def __init__(self, yax, xax, metadata, parenthsiname):
        self.WL = xax
        self.Spec = yax
        self.metadata = metadata
        self.parenthsi = parenthsiname
        self.gdx = self.WL[1] - self.WL[0]
        self.header = dict_to_string(self.metadata, format="lines")
        # add to header: "wavelength in nm" \t "intensity in counts"
        self.header = self.header + "\n wavelenth in nm \t intensity in counts"
    
    def save(self, filename):
        np.savetxt(filename, np.column_stack((self.WL, self.Spec)), delimiter='\t', header=self.header)

def dict_to_string(header_dict, format="json"):
    """
    Convert a dictionary to a string format suitable for np.savetxt headers.

    Parameters:
    - header_dict (dict): Dictionary to convert.
    - format (str): "json" for compact JSON, "lines" for human-readable lines.

    Returns:
    - str: Formatted string representation of the dictionary.
    """
    if not isinstance(header_dict, dict):
        raise TypeError("Input must be a dictionary")

    if format == "json":
        return json.dumps(header_dict)  # Compact JSON format
    elif format == "lines":
        return "\n".join([f"{k}: {v}" for k, v in header_dict.items()])  # Human-readable format
    else:
        raise ValueError("Invalid format. Choose 'json' or 'lines'.")