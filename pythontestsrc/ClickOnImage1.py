import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

def on_click(event):
    # Get the x and y coordinates of the click
    x, y = int(event.xdata), int(event.ydata)
    if x is not None and y is not None:
        print(f"Clicked pixel: ({x}, {y})")
        # Get the pixel value at the clicked coordinates
        pixel_value = img[y, x]
        print(f"Pixel value: {pixel_value}")

# Create a tkinter window
root = tk.Tk()
root.title("Image Click Example")

# Create a figure and axis for matplotlib
fig, ax = plt.subplots()

# Generate a random image
img = np.random.rand(100, 100, 3)
ax.imshow(img)

# Connect the click event to the on_click function
fig.canvas.mpl_connect('button_press_event', on_click)

# Embed the matplotlib figure into the tkinter window
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack()

# Start the tkinter main loop
root.mainloop()
