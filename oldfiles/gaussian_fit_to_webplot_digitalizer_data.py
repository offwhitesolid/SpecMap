import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Define the Gaussian function
def gaussian(x, a, b, c):
    return a * np.exp(-((x - b) ** 2) / (2 * c ** 2))


d = 'data.txt'
with open(d) as f:
    data = f.readlines()

x_data = []
y_data = []

for i in range(len(data)):
    data[i] = data[i].split('\n')[0].split(';')
    x_data.append(float(data[i][0].replace(',', '.')))
    y_data.append(float(data[i][1].replace(',', '.')))

print(x_data, y_data)

x_data = np.asarray(x_data)
y_data = np.asarray(y_data)

# Fit the Gaussian function to the data
initial_guess = [max(y_data), np.mean(x_data), np.std(x_data)]
popt, _ = curve_fit(gaussian, x_data, y_data, p0=initial_guess)

# Generate x values for plotting the fit
x_fit = np.linspace(min(x_data), max(x_data), 1000)
y_fit = gaussian(x_fit, *popt)

# Calculate 1/e points
a, b, c = popt
y_e = a / np.exp(1)
x1 = b - c * np.sqrt(2)
x2 = b + c * np.sqrt(2)

# Calculate and print the distance
distance = round(x2 - x1, 3)
print(f"The distance between the points where the fit is equal to 1/e is: {distance}")

# Plot the data and the fit
plt.plot(x_data, y_data, 'bo', label='Data')
plt.plot(x_fit, y_fit, 'r-', label='Gaussian Fit')
plt.axhline(y=y_e, color='g', linestyle='--', label='y = 1/e')
plt.scatter([x1, x2], [y_e, y_e], color='black', zorder=5, label='1/e points')
plt.legend()
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.title('Gaussian Fit')
plt.show()
