import numpy as np
from scipy.ndimage import median_filter

# comment how cremove_cosmics works

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