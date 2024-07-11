import numpy as np
from scipy.ndimage import median_filter
import tkinter as tk
from tkinter import ttk

# comment how cremove_cosmics works

Notebooks = ['Load Data', 'Process Data', 'Export Data']

def remove_cosmics(data, max_width=3, threshold=5):
    """
    Remove cosmics (outliers) from a 1D numpy array if they span up to a given width.
    Parameters:
    -----------
    data : numpy array
        Input data array from which cosmics are to be removed.
    max_width : int, optional
        Maximum width of cosmic rays (in pixels). Default is 3.
    threshold : float, optional
        Threshold value in units of standard deviations. Default is 5.
    Returns:
    --------
    cleaned_data : numpy array
        Cleaned data array with cosmics removed.
    """

    # Apply median filtering to smooth out extreme values
    filtered_data = median_filter(data, size=max_width)

    # Calculate median and standard deviation of filtered data
    median = np.median(filtered_data)
    std = np.std(filtered_data)

    # Initialize cleaned data as a copy of original data
    cleaned_data = data.copy()

    # Loop over the data to identify and remove cosmics
    for i in range(len(data)):
        # Check if the absolute deviation is greater than threshold * std
        if np.abs(data[i] - filtered_data[i]) > threshold * std:
            # Replace the cosmic ray with the median value
            cleaned_data[i] = median
    return cleaned_data

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


