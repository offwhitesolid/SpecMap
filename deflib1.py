import numpy as np
from scipy.ndimage import median_filter
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from scipy.ndimage import median_filter
import pandas as pd
from scipy.interpolate import UnivariateSpline
import os, csv

# comment how cremove_cosmics works

Notebooks = ['Load Data', 'Hyperspectra', 'Clara Image', 'Export']
DEFAULTS_FILE = 'defaults.txt'

# load defaults
def initdefaults():
    loadeddefaults = load_defaults()
    reqdefaults = defaults.copy()
    for i in loadeddefaults.keys():
        try:
            reqdefaults[i] = defaulttypes[i](loadeddefaults[i])
        except Exception as Error:
            print(f'Error: {Error} while loading Entries. Using default value: {reqdefaults[i]}')
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
    cosmic_indices = np.where(np.abs(diff) > thresh)[0]
    
    # Copy the data to avoid modifying the original array
    interpolated_data = np.copy(data)
    
    for start in cosmic_indices:
        end_range = min(start + width, len(data) - 1)
        
        # Identify the end of the cosmic within the given width
        for end in range(start + 1, end_range + 1):
            if np.abs(data[end] - data[start]) < thresh:
                break
        
        # Replace cosmic rays with the nearest neighbor value
        interpolated_data[start:end+1] = data[end]
    
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
    most_frequent = None
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

def select_file(entry_var):
    file_path = filedialog.askopenfilename()
    if file_path:
        entry_var.set(file_path)

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

cosmicfuncts = {'Linear Interpolation': remove_cosmics_linear, 
                'Median Filter': remove_cosmics_median_filter, 
                #'Rolling Mean': remove_cosmics_rolling_mean, 
                #'Spline Interpolation': remove_cosmics_spline,
                'Nearest Neighbor': remove_cosmics_nearest_neighbor
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
    'remove_cosmics': False,
    'cosmic_threshold': 100,
    'cosmic_width': 10,
    'cosmic_method': 'Linear Interpolation',
    # Clara Image Frame
    'clara_image': 'C:/Users/mol95ww/Desktop/Evaluation/data/2024/qdot_100fach/Laser_in_zpos/145_0.asc',

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
    'load_hsi_saved': "hsidata/hsi.txt"
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
    'load_hsi_saved': str
}