import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageFont
import os

def obtainmagnification(imagename):
    magnification = 5
    scaling = 0.69444444
    if "5x" in imagename:
        magnification = 5
        scaling = 0.69444444
    elif "20x" in imagename:
        magnification = 20
        scaling = 0.17452007
    elif "50x" in imagename:
        magnification = 50
        scaling = 0.06978367
    return magnification, scaling

class ScaleBarApp:
    def __init__(self, root):
        # Initialize the magnification variable as a Tkinter StringVar to store magnification value
        self.root = root
        self.magnification_var = tk.StringVar()
        self.scaling_var = tk.StringVar()
    
    def find_magnification(self, image_path):
        # Find the magnification ("5x", "20x", "50x") in the filename
        mag, scaling = obtainmagnification(image_path)
        if mag:
            self.magnification_var.set(mag)  # Set the magnification value in the entry box
            self.scaling_var.set(scaling)
        else:
            self.magnification_var.set("")  # Clear if no magnification is found
            self.scaling_var.set("")
    
    def open_image(self):
        # Open a file dialog for selecting an image file
        self.file_path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[("Image files", "*.bmp *.jpg *.jpeg *.png")]
        )
        if self.file_path:
            # Run the find_magnification function with the selected file path
            self.find_magnification(self.file_path)

        self.addscalebarbutton()
    
    def build(self):
        # Create the main Tkinter window
        self.root.title("Scale Bar Application")
        
        # Add an "Open Image" button
        open_button = tk.Button(root, text="Open Image", command=self.open_image)
        open_button.pack(pady=10)
        
        # Create an entry box to display and allow editing of the magnification
        magnification_label = tk.Label(root, text="Magnification:")
        magnification_label.pack()
        magnification_entry = tk.Entry(root, textvariable=self.magnification_var)
        magnification_entry.pack(pady=5)
        scaling_label = tk.Label(root, text="Scaling:")
        scaling_label.pack()
        scaling_entry = tk.Entry(root, textvariable=self.scaling_var)
        scaling_entry.pack(pady=5)
        
        root.mainloop()

    def addscalebarbutton(self):
        # Add a button to call the addscalebar function
        add_scale_bar_button = tk.Button(root, text="Add Scale Bar to image", command=lambda: add_scale_bar(self.magnification_var.get(), self.file_path))
        add_scale_bar_button.pack(pady=10)
        # add checkbox to plot image if set true, otherwise only save image
        self.plot_image = tk.BooleanVar()
        self.plot_image.set(False)
        plot_image_checkbox = tk.Checkbutton(root, text="Plot Image", variable=self.plot_image)
        plot_image_checkbox.pack(pady=5)

def add_scale_bar(magnification, image_path):
    # Open the image
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    
    # Define the scale bar dimensions and position
    bar_length = 500  # pixels
    bar_height = 50   # pixels
    margin = 50      # margin from the top-right corner
    
    # Calculate scale bar position
    bar_x = image.width - bar_length - margin
    bar_y = margin
    
    # Draw the scale bar
    draw.rectangle([bar_x, bar_y, bar_x + bar_length, bar_y + bar_height], fill="white", outline="black")
    
    # Add the scale text under the bar
    text = "5 μm"
    text_x = bar_x
    text_y = bar_y + bar_height + 5
    
    # Select font size based on image size
    try:
        font = ImageFont.truetype("arial.ttf", 50)
    except IOError:
        font = ImageFont.load_default()
    
    # Draw the text
    draw.text((text_x, text_y), text, fill="white", font=font)
    
    # Create the new filename
    base, ext = os.path.splitext(image_path)
    new_image_path = f"{base}_scaled{ext}"
    
    # Save the edited image
    image.save(new_image_path)
    print(f"Image saved as {new_image_path}")

# Example usage
# add_scale_bar(20, 'path/to/image.jpg')



# Create an instance of the application and build the GUI
# create tkinter root
root = tk.Tk()
# create an instance of the ScaleBarApp class
app = ScaleBarApp(root)
app.build()
