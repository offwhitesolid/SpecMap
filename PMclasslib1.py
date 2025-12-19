import numpy as np
import json

class PMclass(): # PixMatrix class
    def __init__(self, PixMatrix, xax, yax, metadata, name='', units='', description='', data_type=''):
        self.PixMatrix = PixMatrix
        self.xax = xax
        self.yax = yax
        self.metadata = metadata
        if len(self.xax) < 2:
            self.gdx = 1
        else:
            self.gdx = self.xax[1] - self.xax[0]
        if len(self.yax) < 2:
            self.gdy = 1
        else:
            self.gdy = self.yax[1] - self.yax[0]
        self.units = units
        self.name = name
        self.description = description
        self.data_type = data_type

class Spectra():
    def __init__(self, yax, xax, metadata, parenthsiname):
        self.WL = xax
        self.Spec = yax
        self.metadata = metadata
        self.parenthsi = parenthsiname
        self.gdx = self.WL[1] - self.WL[0]
        self.header = dict_to_string(self.metadata, format="lines")
        # add to header: "wavelength in nm" \t "intensity in counts"
        self.header = self.header + "\nWL / nm\tCounts"
        self.Spec_d1 = None  # first derivative
        self.Spec_d2 = None  # second derivative
    
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

def calc_derivative(spec_obj, derivative_polynomarray):
    """
    Calculates derivatives using sliding window polynomial fit.
    spec_obj: Spectra object
    derivative_polynomarray: [calc_d1 (bool), calc_d2 (bool), poly_order (int), window_size (int)]
    """
    calc_d1 = derivative_polynomarray[0]
    calc_d2 = derivative_polynomarray[1]
    poly_order = derivative_polynomarray[2]
    window_size = derivative_polynomarray[3]
    
    wl = spec_obj.WL
    y = spec_obj.Spec
    n_points = len(wl)
    
    if calc_d1:
        spec_obj.Spec_d1 = np.zeros(n_points)
    if calc_d2:
        spec_obj.Spec_d2 = np.zeros(n_points)
        
    half_window = window_size // 2
    
    for i in range(n_points):
        # Determine window indices
        start_idx = max(0, i - half_window)
        end_idx = min(n_points, i + half_window + 1)
        
        # If window is too small at edges, we can either skip or use what we have
        # For consistency with typical implementations, we use what we have if it's enough points for the order
        if end_idx - start_idx <= poly_order:
            continue
            
        x_window = wl[start_idx:end_idx]
        y_window = y[start_idx:end_idx]
        
        # Fit polynomial
        try:
            p = np.polyfit(x_window, y_window, poly_order)
            
            # Evaluate derivatives at the center point (wl[i])
            if calc_d1:
                dp = np.polyder(p, 1)
                spec_obj.Spec_d1[i] = np.polyval(dp, wl[i])
                
            if calc_d2:
                ddp = np.polyder(p, 2)
                spec_obj.Spec_d2[i] = np.polyval(ddp, wl[i])
        except np.linalg.LinAlgError:
            pass
