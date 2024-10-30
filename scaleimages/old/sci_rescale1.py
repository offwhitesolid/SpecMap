import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk
import os

class ScaleBarApp:
    def __init__(self, root, magnification=20, max_display_size=(800, 600)):
        self.root = root
        self.root.title("Draggable Scale Bar")
        self.magnification = magnification
        self.max_display_size = max_display_size
        
        # Initialize variables
        self.image_path = None
        self.image = None
        self.display_image = None
        self.tk_image = None
        self.scale_ratio = 1  # Ratio to scale back to the original size when saving
        
        # Create a Canvas placeholder for displaying the image
        self.canvas = tk.Canvas(root, bg="gray")
        self.canvas.pack()
        
        # Create file selection button
        self.select_button = tk.Button(root, text="Select Image (.bmp)", command=self.select_image)
        self.select_button.pack(pady=10)
        
        # Save button (initially disabled)
        self.save_button = tk.Button(root, text="Save Image", state="disabled", command=self.save_image)
        self.save_button.pack(pady=10)

    def select_image(self):
        # Open file dialog to select .bmp image
        self.image_path = filedialog.askopenfilename(filetypes=[("BMP files", "*.bmp")])
        if self.image_path:
            # Load the original image
            self.image = Image.open(self.image_path)
            
            # Resize the image to fit within the max display size
            self.display_image = self.resize_image(self.image, self.max_display_size)
            self.scale_ratio = self.image.width / self.display_image.width
            
            # Convert for Tkinter display
            self.tk_image = ImageTk.PhotoImage(self.display_image)
            self.canvas.config(width=self.tk_image.width(), height=self.tk_image.height())
            self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
            
            # Enable the draggable scale bar
            self.create_draggable_scale_bar()
            
            # Enable the Save button
            self.save_button.config(state="normal")

    def resize_image(self, image, max_size):
        # Rescale the image to fit within max_size while maintaining aspect ratio
        image.thumbnail(max_size, Image.LANCZOS)
        return image

    def create_draggable_scale_bar(self):
        # Scale bar dimensions and initial position (based on scaled display image)
        self.bar_length = 30
        self.bar_height = 5
        self.text = "5 μm"
        
        # Default position of the scale bar on the resized display image
        self.bar_x = self.display_image.width - self.bar_length - 10
        self.bar_y = 10
        
        # Draw initial scale bar and text
        self.bar = self.canvas.create_rectangle(
            self.bar_x, self.bar_y, self.bar_x + self.bar_length, self.bar_y + self.bar_height, fill="black"
        )
        self.text_id = self.canvas.create_text(
            self.bar_x, self.bar_y + self.bar_height + 10, anchor="nw", text=self.text, fill="black"
        )
        
        # Bind mouse events for dragging
        self.canvas.tag_bind(self.bar, "<ButtonPress-1>", self.on_press)
        self.canvas.tag_bind(self.text_id, "<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)

    def on_press(self, event):
        # Record the initial position of the mouse
        self.start_x = event.x
        self.start_y = event.y
    
    def on_drag(self, event):
        # Calculate new position
        dx = event.x - self.start_x
        dy = event.y - self.start_y
        self.start_x = event.x
        self.start_y = event.y
        
        # Move the scale bar and text
        self.canvas.move(self.bar, dx, dy)
        self.canvas.move(self.text_id, dx, dy)
        
        # Update bar position
        coords = self.canvas.coords(self.bar)
        self.bar_x, self.bar_y = coords[0], coords[1]
    
    def save_image(self):
        # Check if image is loaded
        if not self.image:
            messagebox.showerror("Error", "No image selected.")
            return
        
        # Calculate position in original image coordinates
        original_bar_x = int(self.bar_x * self.scale_ratio)
        original_bar_y = int(self.bar_y * self.scale_ratio)
        original_bar_length = int(self.bar_length * self.scale_ratio)
        original_bar_height = int(self.bar_height * self.scale_ratio)
        
        # Draw scale bar and text onto a copy of the original image
        edited_image = self.image.copy()
        draw = ImageDraw.Draw(edited_image)
        
        # Draw the scale bar in the user-defined position
        draw.rectangle(
            [original_bar_x, original_bar_y, original_bar_x + original_bar_length, original_bar_y + original_bar_height],
            fill="black"
        )
        
        # Load font for the text
        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except IOError:
            font = ImageFont.load_default()
        
        # Draw the text below the scale bar
        draw.text(
            (original_bar_x, original_bar_y + original_bar_height + 5), self.text, fill="black", font=font
        )
        
        # Save the image with "_saved" in the filename
        base, ext = os.path.splitext(self.image_path)
        new_image_path = f"{base}_saved{ext}"
        edited_image.save(new_image_path)
        messagebox.showinfo("Image Saved", f"Image saved as {new_image_path}")

# Run the app
root = tk.Tk()
app = ScaleBarApp(root, magnification=20)
root.mainloop()
