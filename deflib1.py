import numpy as np

# comment how cremove_cosmics works

def remove_cosmics(data, threshold=0.5):
    # Find the median of the data
    median = np.median(data)
    # Find the standard deviation of the data
    std = np.std(data)
    # Find the cosmic rays
    cosmic_rays = np.where(data > median + threshold * std)
    # Relace the cosmic ray with the 
    # Replace the cosmic rays with the median value
    data[cosmic_rays] = median
    return data

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