import numpy as np

arr = np.array([10, 20, 30, 40, 50, 30])

# Find index of the value 30
index = np.where(arr == 30)[0][0]
print(np.where(arr == 30))
print(f"Index of 30: {index}")
