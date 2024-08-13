import matplotlib.pyplot as plt
import numpy as np

# Create a sample image using numpy
image = np.random.rand(10, 10)

# Function to handle click events
def on_click(event):
    # Check if the click was within the axes
    if event.inaxes:
        # Get the coordinates of the click in pixel space
        x = int(event.xdata)
        y = int(event.ydata)
        print(f"Clicked pixel: ({x}, {y}) - Value: {image[y, x]}")

# Create the figure and display the image
fig, ax = plt.subplots()
ax.imshow(image, cmap='viridis')

# Connect the click event to the handler function
cid = fig.canvas.mpl_connect('button_press_event', on_click)

plt.show()
