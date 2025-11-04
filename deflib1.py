import numpy as np
from scipy.ndimage import median_filter
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from scipy.ndimage import median_filter
import pandas as pd
from scipy.interpolate import UnivariateSpline
import os, csv
from matplotlib.path import Path
import matplotlib.pyplot as plt
import copy

Notebooks = ['Load Data', 'Hyperspectra', 'Clara Image', 'Export', 'Newton Spectrum', 'TCSPC', 'Settings']
# dir of this file
DIR = os.path.dirname(os.path.abspath(__file__))
# Default values for the application
DEFAULTS_FILE = f'{DIR}/defaults.txt'

# load defaults
def initdefaults():
    loadeddefaults = load_defaults()
    reqdefaults = defaults.copy()
    for i in loadeddefaults.keys():
        try:
            reqdefaults[i] = defaulttypes[i](loadeddefaults[i])
        except Exception as Error:
            if loadeddefaults[i] == 'None':
                pass
            else:
                print(f'Error: {Error} while loading Entries. Using default value: {i}={reqdefaults[i]}')
    return reqdefaults

def save_defaults(variables):
    """Save default values to a file."""
    with open(DEFAULTS_FILE, 'w') as file:
        for name, value in variables.items():
            file.write(f'{name} = {value}\n')

def load_defaults():
    """Load default values from a file."""
    variables = {}
    if os.path.exists(DEFAULTS_FILE):
        with open(DEFAULTS_FILE, 'r') as file:
            for line in file:
                # Split each line into name and value
                if '=' in line:
                    name, value = line.split('=', 1)
                    name = name.strip()
                    value = value.strip()
                    # Handle basic types
                    if value.isdigit():
                        value = int(value)
                    elif value.replace('.', '', 1).isdigit():
                        value = float(value)
                    elif value.lower() in ('true', 'false'):
                        value = value.lower() == 'true'
                    variables[name] = value
    return variables

# correlation methods for read data interpolation

def matrix_image_correction_Matrix(SpectrumDataMatrix, thresh, width):
    SpectrumDataMatrix_correlated = copy.copy(SpectrumDataMatrix)

    # Apply matrix image correction to the SpectrumData's XYMap data
    if SpectrumDataMatrix is not None:
        # if len(SpectrumData) < 3 or len(SpectrumData[0]) < 3: just pass
        if len(SpectrumDataMatrix) < 3 or len(SpectrumDataMatrix[0]) < 3:
            return SpectrumDataMatrix

        correctionweighting = gaussian_weight_matrix(dx=1.0, dy=1.0, sigma_x=1.0, sigma_y=1.0, size=3)
        print('Correctionweighting: ', correctionweighting)
        #return SpectrumDataMatrix_correlated # first testing

        # iterate over each spectrum in the XYMap and identify cosmics
        for i in range(len(SpectrumDataMatrix)-2):
            for j in range(len(SpectrumDataMatrix[i])-2):
                if hasattr(SpectrumDataMatrix[i][j], 'PLB'):
                    existingmatrix = [[0,0,0],[0,0,0],[0,0,0]]
                    # check if surrounding pixels exist
                    for k in range(len(SpectrumDataMatrix[i][j].PLB)):
                        # fill existingmatrix
                        # iterate over surrounding pixels
                        for l in range(-1, 2):
                            for m in range(-1, 2):
                                # check if surrounding pixels exist
                                if SpectrumDataMatrix[i+l][j+m] is not None:
                                    existingmatrix[l+1][m+1] = 1
                    # if more than 80% of surrounding pixels exist, apply correction
                    if np.sum(existingmatrix) <= 0.8 * np.prod(np.array(existingmatrix).shape):
                        break
                        

                    for k in range(len(SpectrumDataMatrix[i][j].PLB)):
                        # correction, weight each pixel with the average of the surrounding pixels
                        local_matrix = np.array([[SpectrumDataMatrix[i-1][j-1].PLB[k], SpectrumDataMatrix[i-1][j].PLB[k], SpectrumDataMatrix[i-1][j+1].PLB[k]],
                                                  [SpectrumDataMatrix[i][j-1].PLB[k], SpectrumDataMatrix[i][j].PLB[k], SpectrumDataMatrix[i][j+1].PLB[k]],
                                                  [SpectrumDataMatrix[i+1][j-1].PLB[k], SpectrumDataMatrix[i+1][j].PLB[k], SpectrumDataMatrix[i+1][j+1].PLB[k]]])
                        # Apply a simple average filter
                        SpectrumDataMatrix_correlated[i][j].PLB[k] = np.mean(local_matrix)
        
    else:
        return SpectrumDataMatrix

    return SpectrumDataMatrix_correlated

def cosmic_correlation_Matrix(SpectrumDataMatrix, thresh, width):
    """
    Identify and correct cosmic rays in a 2D spectrum matrix using Gaussian-weighted interpolation.
    
    This function detects pixels that differ from their surroundings more than expected 
    based on a Gaussian laser profile, then interpolates them using Gaussian-weighted 
    neighboring pixels.
    
    Parameters
    ----------
    SpectrumDataMatrix : 2D array of SpectrumData objects
        Matrix containing spectral data at each spatial position
    thresh : float
        Threshold multiplier for cosmic detection (e.g., 3.0 for 3-sigma)
    width : int
        Not used in this implementation, kept for compatibility
        
    Returns
    -------
    SpectrumDataMatrix_corrected : 2D array of SpectrumData objects
        Corrected spectrum matrix with cosmics interpolated
    """
    SpectrumDataMatrix_corrected = copy.deepcopy(SpectrumDataMatrix)
    
    # Check if matrix is large enough
    if SpectrumDataMatrix is None or len(SpectrumDataMatrix) < 3 or len(SpectrumDataMatrix[0]) < 3:
        return SpectrumDataMatrix
    
    # Generate 3x3 Gaussian weighting kernel (normalized)
    gaussian_weights, _, _ = gaussian_weight_matrix(dx=1.0, dy=1.0, sigma_x=1.0, sigma_y=1.0, size=3)
    
    # Pre-compute weights without center
    weights_no_center = gaussian_weights.copy()
    weights_no_center[1, 1] = 0
    
    # Pre-compute neighbor mask (all except center)
    neighbor_mask = np.ones((3, 3), dtype=bool)
    neighbor_mask[1, 1] = False
    
    # Iterate over interior pixels (avoid edges)
    for i in range(1, len(SpectrumDataMatrix) - 1):
        for j in range(1, len(SpectrumDataMatrix[i]) - 1):
            # Check if center pixel has spectral data
            if not hasattr(SpectrumDataMatrix[i][j], 'PLB'):
                continue
            
            # Check which surrounding pixels exist and build spectral cube
            valid_neighbors = np.ones((3, 3), dtype=bool)
            spectral_cube = []  # Will hold 3x3 arrays, one per wavelength
            
            # Build the spectral cube for all wavelengths at once
            for di in range(-1, 2):
                for dj in range(-1, 2):
                    neighbor = SpectrumDataMatrix[i+di][j+dj]
                    if neighbor is None or not hasattr(neighbor, 'PLB'):
                        valid_neighbors[di+1, dj+1] = False
            
            # Need at least 80% of neighbors to be valid
            if np.sum(valid_neighbors) < 0.8 * 9:
                continue
            
            # Extract all spectra into a 3D array [3, 3, n_wavelengths]
            n_wl = len(SpectrumDataMatrix[i][j].PLB)
            spectral_cube = np.zeros((3, 3, n_wl))
            
            for di in range(-1, 2):
                for dj in range(-1, 2):
                    if valid_neighbors[di+1, dj+1]:
                        spectral_cube[di+1, dj+1, :] = SpectrumDataMatrix[i+di][j+dj].PLB
            
            # Vectorized operations over all wavelengths
            center_spectrum = spectral_cube[1, 1, :]  # Shape: (n_wl,)
            
            # Calculate valid weights for neighbors (excluding center)
            valid_weights_neighbors = weights_no_center * valid_neighbors
            weight_sum = np.sum(valid_weights_neighbors)
            
            if weight_sum > 0:
                valid_weights_neighbors = valid_weights_neighbors / weight_sum
                
                # Expected values for all wavelengths at once: shape (n_wl,)
                expected_spectrum = np.sum(spectral_cube * valid_weights_neighbors[:, :, np.newaxis], axis=(0, 1))
                
                # Calculate std of neighbors across all wavelengths
                # Extract only valid neighbor values
                neighbor_valid_mask = neighbor_mask & valid_neighbors  # Exclude center and invalid
                neighbor_values = spectral_cube[neighbor_valid_mask, :]  # Shape: (n_neighbors, n_wl)
                
                if neighbor_values.shape[0] > 0:
                    neighbor_std = np.std(neighbor_values, axis=0)  # Shape: (n_wl,)
                    
                    # Detect cosmics: vectorized deviation check
                    deviations = np.abs(center_spectrum - expected_spectrum)
                    cosmic_mask = deviations > (thresh * neighbor_std)  # Boolean array
                    
                    # If any cosmics detected, interpolate them
                    if np.any(cosmic_mask):
                        # Calculate weights for all valid neighbors (including center position)
                        weights_all = gaussian_weights * valid_neighbors
                        weight_sum_all = np.sum(weights_all)
                        
                        if weight_sum_all > 0:
                            weights_all = weights_all / weight_sum_all
                            
                            # Corrected values for all wavelengths
                            corrected_spectrum = np.sum(spectral_cube * weights_all[:, :, np.newaxis], axis=(0, 1))
                            
                            # Replace only the cosmic-affected wavelengths
                            # Convert PLB to numpy array if it's a list, apply correction, convert back
                            plb_array = np.array(SpectrumDataMatrix_corrected[i][j].PLB)
                            plb_array[cosmic_mask] = corrected_spectrum[cosmic_mask]
                            SpectrumDataMatrix_corrected[i][j].PLB = plb_array.tolist() if isinstance(SpectrumDataMatrix_corrected[i][j].PLB, list) else plb_array
    
    return SpectrumDataMatrix_corrected

# uncorrelated spectra methods

# Matrix image correction method
def matrix_image_correction(data, thresh, width):
    return data # placeholder, no correction applied

def cosmic_correlation(data, thresh, width):
    return data # placeholder, no correction applied

# Linear interpolation provides a simple and fast method for filling in missing values.
def remove_cosmics_linear(data, thresh, width):
    # Calculate the finite differences (first derivative)
    diff = np.diff(data)
    
    # Identify where the absolute value of the difference is greater than the threshold
    cosmic_starts = np.where(np.abs(diff) > thresh)[0]
    
    # Copy the data to avoid modifying the original array
    interpolated_data = np.copy(data)
    
    for start in cosmic_starts:
        # Define the range to look for the end of the cosmic
        end_range = min(start + width, len(data) - 1)
        
        # Identify the end of the cosmic within the given width
        for end in range(start + 1, end_range + 1):
            if np.abs(data[end] - data[start]) < thresh:
                # Perform linear interpolation between start and end
                interpolated_data[start:end+1] = np.linspace(data[start], data[end], end - start + 1)
                break
    
    return interpolated_data

#Median filtering is good for robust outlier removal.
def remove_cosmics_median_filter(data, thresh, width):
    # Apply a median filter with size `width`
    filtered_data = median_filter(data, size=width)
    
    # Replace cosmic rays with median values
    diff = np.abs(data - filtered_data)
    cosmic_indices = np.where(diff > thresh)[0]
    interpolated_data = np.copy(data)
    interpolated_data[cosmic_indices] = filtered_data[cosmic_indices]
    
    return interpolated_data

#Rolling mean is good for preserving the overall trend of the data.            
def remove_cosmics_rolling_mean(data, thresh, width):
    # Compute the rolling mean
    rolling_mean = pd.Series(data).rolling(window=width, center=True).mean().to_numpy()
    
    # Replace cosmic rays with rolling mean values
    diff = np.abs(data - rolling_mean)
    cosmic_indices = np.where(diff > thresh)[0]
    interpolated_data = np.copy(data)
    interpolated_data[cosmic_indices] = rolling_mean[cosmic_indices]
    
    return interpolated_data

#Spline interpolation is good for preserving the overall trend of the data.
def remove_cosmics_spline(data, thresh, width):
    # Create an array of indices
    x = np.arange(len(data))
    
    # Identify cosmic indices
    diff = np.diff(data)
    cosmic_indices = np.where(np.abs(diff) > thresh)[0]
    
    # Create a spline interpolation of the data
    spline = UnivariateSpline(x, data, s=width)
    
    # Replace cosmic rays with spline values
    interpolated_data = np.copy(data)
    for idx in cosmic_indices:
        end_range = min(idx + width, len(data) - 1)
        interpolated_data[idx:end_range+1] = spline(x[idx:end_range+1])
    
    return interpolated_data

#Nearest neighbor interpolation is good for preserving the overall trend of the data.
def remove_cosmics_nearest_neighbor(data, thresh, width):
    # Identify where the absolute value of the difference is greater than the threshold
    diff = np.diff(data)
    #cosmic_indices = np.where(np.abs(diff) > thresh)[0]

    cosmic_indices = np.where(np.abs(data) > thresh)[0]
    # Identify the start and end of cosmic rays
    start_indices = np.where(np.diff(cosmic_indices) != 1)[0]
    end_indices = np.append(start_indices[1:], len(cosmic_indices) - 1)
    cosmic_ranges = [(cosmic_indices[start], cosmic_indices[end]) for start, end in zip(start_indices, end_indices)]

    # Copy the data to avoid modifying the original array
    interpolated_data = np.copy(data)

    #print(cosmic_ranges)
    #print(interpolated_data)

    #print(len(interpolated_data), print(len(interpolated_data[0])))

    
    return interpolated_data

# get grid dx and dy
def most_freq_element(arr):
    # Use a dictionary to count occurrences of each element
    count_dict = {}
    for value in arr:
        if value in count_dict:
            count_dict[value] += 1
        else:
            count_dict[value] = 1
    # Find the element with the highest count
    max_count = 0
    most_frequent = 1
    for key, count in count_dict.items():
        if count > max_count:
            max_count = count
            most_frequent = key
    return most_frequent

def remove_duplicates(arr):
    # Use a set to track unique elements
    seen = set()
    unique_arr = []
    for value in arr:
        if value not in seen:
            unique_arr.append(value)
            seen.add(value)
    return unique_arr

def findif(a):
    find = []
    for i in range(len(a)-1):
        find.append(a[i+1]-a[i])
    return find   

# Function stubs for menu commands
def file_new():
    print("New File")

def file_open():
    print("Open File")

def file_save():
    print("Save File")

def edit_undo():
    print("Undo")

def edit_redo():
    print("Redo")

def select_all():
    print("Select All")

def view_toggle():
    print("Toggle View")

def create_menu(root, menu_bar):
    # Create File menu
    file_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="New", command=file_new)
    file_menu.add_command(label="Open", command=file_open)
    file_menu.add_command(label="Save", command=file_save)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)

    # Create Edit menu
    edit_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Edit", menu=edit_menu)
    edit_menu.add_command(label="Undo", command=edit_undo)
    edit_menu.add_command(label="Redo", command=edit_redo)

    # Create Selection menu
    selection_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Selection", menu=selection_menu)
    selection_menu.add_command(label="Select All", command=select_all)

    # Create View menu
    view_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="View", menu=view_menu)
    view_menu.add_command(label="Toggle View", command=view_toggle)

def on_click(event, PixMatrix):
    """
    Handles mouse click events on a matplotlib figure.
    Prints the coordinates and value at the clicked position in PixMatrix.
    """
    if event.inaxes:
        try:
            x = int(round(event.xdata))
            y = int(round(event.ydata))
            if 0 <= y < len(PixMatrix) and 0 <= x < len(PixMatrix[0]):
                value = PixMatrix[y][x]
                print(f"Clicked at (x={x}, y={y}), value: {value}")
            else:
                print(f"Clicked at (x={x}, y={y}), but out of bounds.")
        except Exception as e:
            print(f"Error handling click event: {e}")

def select_file(entry_var):
    file_path = filedialog.askopenfilename()
    if file_path:
        entry_var.set(file_path)

def select_folder(entry_var):
    folder_path = filedialog.askdirectory()
    if folder_path:
        entry_var.set(folder_path)

def browse_folder(folder_entry):
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, folder_selected)
    
def loadclaraimage(file):
    with open(file) as f:
        for i in range(34):
            f.readline()
        fload = f.readlines()
    x = []
    y = []
    data = []
    for i in fload:
        isplit = i.split('\n')[0].split('\t')
        x.append(float(isplit[0]))
        for j in range(1, len(isplit)):
            if isplit[j] == '':
                pass
            else:
                y.append(float(isplit[j]))
        data.append(y)
        y = []  
    return np.asarray(data)

# check if file ends with a number before the file extension
# increment the number by 1 and return the new filename
def increment_filename(file):
    fnoext = file.split('.')[-2]
    fext = file.split('.')[-1]
    num = 1
    # check if the file ends with a number and increment it by 1
    if fnoext[-1].isdigit():
        num = int(fnoext[-1]) + 1
        fnoext = fnoext[:-1]
    return fnoext + str(num) + '.' + fext

def closest_indices(X, Y, px, py):
    X = np.asarray(X)
    Y = np.asarray(Y)
    # Calculate the absolute differences between px and all elements in X
    diff_x = np.abs(X - px)
    # Calculate the absolute differences between py and all elements in Y
    diff_y = np.abs(Y - py)
    # Find the index of the minimum difference in X
    i = np.argmin(diff_x)
    # Find the index of the minimum difference in Y
    j = np.argmin(diff_y)
    return i, j

#roi = region of interest, returns a matrix with 1s in the region of interest and NaNs elsewhere
def highlight_roi(Mat, points):
    Mat = np.asarray(Mat)
    # Create a copy of the matrix initialized with NaN
    result = np.full_like(Mat, np.nan, dtype=float)
    # Get grid of all pixel coordinates in the matrix
    y, x = np.meshgrid(np.arange(Mat.shape[1]), np.arange(Mat.shape[0]))
    points_grid = np.vstack((x.ravel(), y.ravel())).T
    # Create a Path object from the points (closed polygon)
    polygon_path = Path(points)
    # Find which points are inside the polygon
    inside_mask = polygon_path.contains_points(points_grid)
    inside_mask = inside_mask.reshape(Mat.shape)
    # Set inside points to 1, leaving the rest as NaN
    result[inside_mask] = 1
    return np.transpose(result)

def correct_spectrum(spec, wl, speccorrect, wlcorrect):
    """
    Corrects a spectrum by interpolating a correction spectrum to match the original wavelength axis.

    Parameters:
    - spec (array-like): The original spectrum values.
    - wl (array-like): The wavelength axis of the original spectrum.
    - speccorrect (array-like): The correction spectrum values.
    - wlcorrect (array-like): The wavelength axis of the correction spectrum.

    Returns:
    - corrected_spec (np.ndarray): The corrected spectrum.
    """
    # check if the wavelength axes are sorted
    if not np.all(np.diff(wl) > 0):
        raise ValueError("Wavelength axis is not sorted.")
    if not np.all(np.diff(wlcorrect) > 0):
        raise ValueError("Correction wavelength axis is not sorted.")
    
    if wl[0] < wlcorrect[0]:
        # insert one element at the beginning of wlcorrect
        wlcorrect = np.insert(wlcorrect, 0, wlcorrect[0]-0.001)
        speccorrect = np.insert(speccorrect, 0, 0)
    if wl[-1] > wlcorrect[-1]:
        # append one element at the end of wlcorrect
        wlcorrect = np.append(wlcorrect, wlcorrect[-1]+0.001)
        speccorrect = np.append(speccorrect, 0)
    
    # Ensure wl and wlcorrect are numpy arrays
    wl = np.array(wl)
    wlcorrect = np.array(wlcorrect)
    dwlcorrect = np.diff(wlcorrect)
    dwl = np.diff(wl)
    # get the most frequent element of dwl
    dwlv = most_freq_element(dwl)
    
    # append dwl to dwlcorrect
    dwlcorrect = np.append(dwlcorrect, dwlv)

    # calculate smallest common divisor
    gcd = np.gcd.reduce(dwlcorrect.astype(int))
    # create a new wlcorrect with kgv
    wlcorrectinter = np.arange(wlcorrect[0], wlcorrect[-1], gcd)

    # interpolate speccorrect to match the new wlcorrect
    corrected_interp_spec = np.interp(wlcorrectinter, wlcorrect, speccorrect)
    # interpolate the original spectrum to match the new wlcorrect
    spec_wlc = np.interp(wlcorrectinter, wl, spec)
    # subtract the interpolated correction spectrum from the interpolated original spectrum
    corrected_spec = spec_wlc - corrected_interp_spec

    # interpolate the correction spectrum to match the original wavelength axis
    specc = np.interp(wl, wlcorrect, speccorrect)
    
    # Interpolate the correction spectrum to match the original wavelength axis
    #interpolated_correction = np.interp(wl, wlcorrect, speccorrect)

    # Subtract the interpolated correction spectrum from the original spectrum
    corrected_spec = np.array(spec) - specc #interpolated_correction

    return corrected_spec

def loadexpspec(fname):
    #Loads a spectrum from a file.
    wavelengths = []
    intensities = []
    
    with open(fname, 'r') as file:
        for line in file:
            # Skip comment lines
            if line.startswith('#'):
                continue
            
            # Parse data lines
            parts = line.strip().split()
            if len(parts) == 2:
                try:
                    wavelength = float(parts[0])
                    intensity = float(parts[1])
                    wavelengths.append(wavelength)
                    intensities.append(intensity)
                except ValueError:
                    continue  # Skip lines that can't be parsed
    return wavelengths, intensities

def testcorrect_spectrum():
    # spec in "C:\Users\volib\Documents\spectra\spect1.txt"
    wl, spec = loadexpspec("C:/Users/volib/Documents/spectra/spect1.txt")
    # corectspec in "C:\Users\volib\Documents\spectra\correctspec_t2.txt"
    wlcorrect, speccorrect = loadexpspec("C:/Users/volib/Documents/spectra/correctionspec_t2.txt")
    # Correct the spectrum
    corrected_spec = correct_spectrum(spec, wl, speccorrect, wlcorrect)
    # plot the corrected spectrum and the original spectrum
    plt.figure(figsize=(10, 6))
    plt.plot(wl, spec, label='Original Spectrum')
    plt.plot(wl, corrected_spec, label='Corrected Spectrum')
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Intensity')
    plt.title('Spectrum Correction')
    plt.legend()
    plt.show()

def remove_nan(arr):
    # Remove NaN values from the array and return it
    reta = []
    return reta

def fig_on_hoverevent(event, ax, fig, Z, x_range, y_range):
 def on_hover(event, ax, fig, Z, x_range, y_range):
    """
    Handles mouse hover event to display x, y, and z values dynamically for a 2D list or array.

    Parameters:
    - event: The mouse motion event.
    - ax: The axes of the plot.
    - fig: The matplotlib figure object.
    - Z: The 2D list (or array) of values.
    - x_range: Tuple (x_min, x_max) representing the x-coordinate range.
    - y_range: Tuple (y_min, y_max) representing the y-coordinate range.
    """
    if event.inaxes == ax:
        x_min, x_max = x_range
        y_min, y_max = y_range

        # Check if Z is a 2D list (list of lists)
        if not (isinstance(Z, list) and all(isinstance(row, list) for row in Z)):
            raise ValueError("Z must be a 2D list.")

        # Get the number of rows and columns
        num_rows = len(Z)
        num_cols = len(Z[0])

        # Calculate indices based on cursor position and plot extent
        x_idx = int((event.xdata - x_min) / (x_max - x_min) * (num_cols - 1))
        y_idx = int((event.ydata - y_min) / (y_max - y_min) * (num_rows - 1))

        if 0 <= x_idx < num_cols and 0 <= y_idx < num_rows:
            z_value = Z[y_idx][x_idx]  # Access the element in the 2D list
            ax.set_title(f"x: {event.xdata:.2f}, y: {event.ydata:.2f}, z: {z_value:.2f}")
            fig.canvas.draw_idle()

cosmicfuncts = {
                'Linear Interpolation': remove_cosmics_linear, 
                'Median Filter': remove_cosmics_median_filter, 
                #'Rolling Mean': remove_cosmics_rolling_mean, 
                #'Spline Interpolation': remove_cosmics_spline,
                'Nearest Neighbor average': remove_cosmics_nearest_neighbor, 
                'Matrix Image correction': matrix_image_correction, 
                'Cosmic Correlation Matrix': cosmic_correlation,
                } 

# Correlation functions for cosmic ray removal must be run by XYMap class instead of SpectrumData class only
correlationcosmicfuncts = {
                'Matrix Image correction': matrix_image_correction_Matrix,
                'Cosmic Correlation Matrix': cosmic_correlation_Matrix
                }
# Rolling Mean showed not to be good for cosmic removal
# Spline Interpolation showed not to be good for cosmic removal and took like forever to perform

speckeys = {'Wavelength axis': 'WL', 
            'Background (BG)': 'BG',
            'Counts (PL)': 'PL', 
            'Spectrum (PL-BG)': 'PLB'}

defaults={
    # General inits
    'Matrix_grid_dx': None,
    'Matrix_grid_dy': None,
    'windowsize_X': 900,
    'windowsize_Y': 900,
    # Load Data Notebook
    # Select Folder Frame
    'data_file': 'C:/Users/mol95ww/Desktop/Evaluation/data/VP/test7_MoS2_ML_2sec/test7_MoS2_ML_2sec',
    'filename': 'spectrum', 
    'file_extension': '.txt',
    # Background Subtraction Frame
    'multiple_Background': False,
    'linear_Background': True,
    # Cosmic Ray Removal Frame
    'remove_cosmics': True,
    'cosmic_threshold': 100,
    'cosmic_width': 10,
    'cosmic_method': 'Linear Interpolation',
    # Clara Image Frame
    'clara_image': 'C:/Users/mol95ww/Desktop/Evaluation/data/2024/qdot_100fach/Laser_in_zpos/145_0.asc',
    'newton_spectrum': 'C:/Users/mol95ww/Desktop/Evaluation/data/2024/Perovskite/N1_Sndoping/Pb-Sn_0_0625/PL_Sn_Image_0_0625_1250g_500lnm_470-1030nm.asc',
    # TCSPC Frame
    'tcspc_maindir': '',
    'tcspc_subdir': '',
    # Hyperspectra Notebook
    # cmap frame
    'lowest_wavelength': 500, 
    'highest_wavelength': 700,
    'colormap_threshold': 10000,
    'fontsize': 13,
    'maxfev': 2000,
    #speckeys
    'Wavelength axis': 'WL', 
    'Background (BG)': 'BG',
    'Counts (PL)': 'PL', 
    'Spectrum (PL-BG)': 'PLB',
    'data_set': 'Spectrum (PL-BG)',
    # buttonframe
    'selected_pixel_x': 0,
    'selected_pixel_y': 0,
    'selected_fit_function': 'gaussian',
    'seperate_fits': False,
    'save_hsi': "hsidata/hsi.txt", 
    'load_hsi_saved': "hsidata/hsi.txt",
    'enable_buttonmatrix': False, 
    'loadonstart': False, 
    'selected_WL_axis': 'Wavelength (nm)',
    'Fit_use_ROI_mask': True, 
    'HSI_from_fitparam_useROI': True, 
    'power_correction': False, 
    'laser_spotsize_nm': 1000.0,
}

defaulttypes = {
    # General inits
    'windowsize_X': int,
    'windowsize_Y': int,
    # Load Data Notebook
    'data_file': str,
    'filename': str,
    'file_extension': str,
    'multiple_Background': bool,
    'linear_Background': bool,
    'remove_cosmics': bool,
    'cosmic_threshold': int,
    'cosmic_width': int,
    'cosmic_method': str,
    'clara_image': str,
    'newton_spectrum': str,
    'tcspc_maindir': str,
    'tcspc_subdir': str,
    # Hyperspectra Notebook
    'lowest_wavelength': float,
    'highest_wavelength': float,
    'colormap_threshold': int,
    'fontsize': int,
    'maxfev': int,
    'Wavelength axis': str,
    'Background (BG)': str,
    'Counts (PL)': str,
    'Spectrum (PL-BG)': str,
    'data_set': str,
    'selected_pixel_x': int,
    'selected_pixel_y': int,
    'selected_fit_function': str,
    'seperate_fits': bool,
    'save_hsi': str,
    'load_hsi_saved': str, 
    'Matrix_grid_dx': float,
    'Matrix_grid_dy': float,
    'enable_buttonmatrix': bool, 
    'loadonstart': bool,
    'selected_WL_axis': str,
    'Fit_use_ROI_mask': bool,
    'HSI_from_fitparam_useROI': bool, 
    'power_correction': bool,
    'laser_spotsize_nm': float,

}

def testdefaults():
    for i in list(defaults.keys()):
        if i not in list(defaulttypes.keys()):
            print(f'{i} not in defaulttypes')
        if i not in list(defaults.keys()):
            print(f'{i} not in defaults')
        if defaulttypes[i] != type(defaults[i]):
            print(f'{i} not the same type')

def newton_loadfiles(file):
    data = None
    if not file:
        messagebox.showerror("Error", "Please select a file")
        return
    try:
        data = np.loadtxt(file, skiprows=34)
    except Exception as Error:
        print(f'Error: {Error}')
    
    return data

# WL Axis stuff
WL_values = ['Wavelength (nm)', 'Energy (eV)']

def wl_array_to_ev(wl):
    """
    Convert wavelength in nm to energy in eV.
    
    Parameters:
    - wl: Wavelength in nm.
    
    Returns:
    - Energy in eV.
    """
    h = 4.135667696e-15  # Planck's constant in eV·s
    c = 299792458e9      # Speed of light in nm/s
    for i in range(len(wl)): 
        wl[i] = h * c / wl[i]
    return wl  # Energy in eV

def gaussian_weight_matrix(dx=1.0, dy=1.0, sigma_x=None, sigma_y=None, size=3):
    """
    Generate a normalized 2D Gaussian weighting matrix.
    
    Parameters
    ----------
    dx, dy : float
        Sampling spacing along x and y axes (distance between spectra).
    sigma_x, sigma_y : float
        Standard deviations (beam waist) along x and y.
        If sigma_y is None, isotropic Gaussian is assumed.
    size : int
        Matrix dimension (must be odd). Default is 3 for 3x3.
        
    Returns
    -------
    w_norm : 2D numpy array
        Normalized Gaussian weights that sum to 1.
    x_grid, y_grid : 2D numpy arrays
        Coordinate grids (for reference).
    """
    if sigma_y is None:
        sigma_y = sigma_x

    # ensure odd size (so we have a center)
    if size % 2 == 0:
        raise ValueError("Matrix size must be odd (e.g. 3, 5, 7).")

    half = size // 2
    x = np.arange(-half, half + 1) * dx
    y = np.arange(-half, half + 1) * dy
    X, Y = np.meshgrid(x, y)

    # 2D Gaussian weights
    w = np.exp(-((X**2)/(2*sigma_x**2) + (Y**2)/(2*sigma_y**2)))

    # normalize to sum = 1
    w_norm = w / np.sum(w)
    return w_norm, X, Y        

# check definitions 
if __name__ == '__main__':
    try:
        testdefaults()
        print('All definitions are correct')
    except Exception as Error:
        print('Error while loading defaults')
        print(f'Error: {Error}')
    
    #testcorrect_spectrum()

