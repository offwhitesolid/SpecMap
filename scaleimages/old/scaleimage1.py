import tkinter as tk
from tkinter import filedialog
from PIL import Image

def addscalebar(image_path):
    # This is a placeholder for your code.
    # Here, you could open the image, add a scale bar, and save or display the modified image.
    print(f"Scale bar function called for image: {image_path}")
    # Example of opening the image
    img = Image.open(image_path)
    print(image_path)
    # Add your scale bar code here
    img.show()  # Display the image with any modifications (for testing)

def obtainmagnification(imagename):
    magnification = 5
    if "5x" in imagename:
        magnification = 5
    elif "20x" in imagename:
        magnification = 20
    elif "50x" in imagename:
        magnification = 50
    return magnification

def select_file():
    # Open a file dialog to select a BMP image file
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(
        title="Select a BMP Image",
        filetypes=[("Bitmap files", "*.bmp")]
    )
    if file_path:
        addscalebar(file_path)

# Run the file selection dialog
select_file()
