import numpy as np
from scipy.ndimage import median_filter
import tkinter as tk
from tkinter import ttk

# comment how cremove_cosmics works

Notebooks = ['Load Data', 'Process Data', 'Export Data']


def remove_cosmics(data, max_width=3, threshold=5):
    # Calculate the difference array
    c = max_width
    abl = np.diff(data[c:-c])
    # Find indices where elements of abl are greater than b
    indicesp =  np.where(abl > threshold)[0]
    indicesm = np.where(abl < -threshold)[0]
    print(indicesp, indicesm)
    indices = np.concatenate((indicesp, indicesm))
    print(indices)
    indices = filter_peaks_start_end(remove_pairs_within_distance(indices, c), len(abl), c)
    print('filterd', indices)
    cosmiccl = clasifycosmics(abl, indices, max_width, threshold)
    print('clasified', cosmiccl)
    # reconvert into the original indices
    # Perform element-wise addition
    cosmiccl = [np.add(arr, c) for arr in cosmiccl]
    # single_cosmics (cosmiccl[0]):
    # interpolate between data[-1] and data [1]
    data = interpolate_cosmics(data, cosmiccl[0], 0, 2)
    # threashold_cosmics (cosmiccl[1]):
    # interpolate between data[-c] and data [c]
    data = interpolate_cosmics(data, cosmiccl[1], -c, c)
    return data

# c = max_width, indices = indices, abl = abl, thresh = threshold
# clasisfy the cosmic rays into single peaks [0], threashold peaks [1] and big peaks [2]
def clasifycosmics(abl, indices, max_width, thresh):
    singcs = []
    threcs = []
    bigcs = []
    print('max_width', max_width, 'thresh', thresh)
    for i in indices:
        if abs(abl[i]+abl[i+1]) < thresh:
            print('single', abl[i], abl[i+1])
            singcs.append(i)
        elif abs(np.sum(abl[i-max_width:i+max_width])) < thresh:
            print('threashold', abs(np.sum(abl[i-max_width:i+max_width])))
            threcs.append(i)
        else:
            print('big', abs(np.sum(abl[i-max_width:i+max_width])))
            bigcs.append(i)
    return [singcs, threcs, bigcs]

def interpolate_cosmics(data, cosmic_indices, start_index, stop_index):
    print('cosmic_indices', cosmic_indices, 'start_index', start_index, 'stop_index', stop_index)
    # Interpolate the cosmic rays
    for i in cosmic_indices:
        # Interpolate the cosmic ray
        data[i+start_index:i+stop_index] = np.linspace(data[i+start_index], data[i+stop_index], stop_index - start_index)
    return data
            
# peaks = cosmic indices, lenabl = len(abl), c = max_width
def filter_peaks_start_end(peaks, lenabl, c):
    # Calculate the length of abl
    # Filter peaks based on the conditions
    filtered_peaks = [peak for peak in peaks if (peak >= c and peak <= lenabl - c)]
    return filtered_peaks

# a = derivative, c = max width of the peak
def remove_pairs_within_distance(a, c):
    # Convert input list to a NumPy array
    n = len(a)
    # Sort the array to ensure we only check adjacent pairs
    sorted_indices = np.argsort(a)
    a_sorted = a[sorted_indices]
    # List to store indices to remove
    remove_indices = set()
    # Iterate through the sorted array and find pairs
    i = 0
    while i < n - 1:
        if abs(a_sorted[i + 1] - a_sorted[i]) <= c:
            # Add the index of the second element of the pair to remove list
            remove_indices.add(sorted_indices[i + 1])
            # Skip the next element as it forms a pair with the current element
            i += 1
        i += 1
    # Remove the elements
    a = np.delete(a, list(remove_indices))
    return a.tolist()

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


