import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk
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
    def __init__(self, root, magnification=20):
        self.root = root
        self.root.title("Draggable Scale Bar")
        self.magnification = magnification

        # Create a frame for the canvas and scrollbars
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True)
        # Create a canvas widget
        self.canvas = tk.Canvas(self.frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Initialize variables
        self.image_path = None
        self.image = None
        self.tk_image = None
        
        # Create Canvas placeholder (will be updated with image)
        self.canvas = tk.Canvas(self.canvas)
        self.canvas.pack(pady=10)
        
        # Create file selection button
        self.select_button = tk.Button(self.frame, text="Select Image (.bmp)", command=self.select_image)
        self.select_button.pack(side=tk.LEFT, padx=(0, 10))

        # add entry to enter length of scale bar
        self.scalelength = tk.DoubleVar()
        self.scalelength.set(5)
        self.scalelength.trace_add("write", self.on_enterscale)
        self.scale_entry = tk.Entry(self.frame, width=20, textvariable=self.scalelength)
        self.scale_entry.pack(side=tk.LEFT)
        
        #self.scale_entry.insert(0, "Enter scale bar length in µm")
        
        # Save button (initially disabled)
        self.save_button = tk.Button(self.frame, text="Save Image", state="disabled", command=self.save_image)
        self.save_button.pack(side = tk.LEFT)

    def select_image(self):
        # delete the existing canvas if it exists
        self.canvas.delete("all")
        # delete the existing scale bar if it exists
        self.bar = None
        # delete existing self.v_scrollbar and self.h_scrollbar if they exist
        if hasattr(self, 'v_scrollbar'):
            self.v_scrollbar.destroy()
        if hasattr(self, 'h_scrollbar'):
            self.h_scrollbar.destroy()
        # Open file dialog to select .bmp image
        self.image_path = filedialog.askopenfilename(filetypes=[("BMP files", "*.bmp")])
        if self.image_path:
            # Load and display the image
            self.image = Image.open(self.image_path)
            self.tk_image = ImageTk.PhotoImage(self.image)
            #self.canvas.config(width=self.image.width, height=self.image.height)
            # set size of canvas to fill the window
            self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
            self.canvas.config(width=self.root.winfo_screenwidth(), height=self.root.winfo_screenheight())
            # set canvas to expand with window
            self.canvas.pack(fill=tk.BOTH, expand=True)

            # Create vertical and horizontal scrollbars
            self.v_scrollbar = tk.Scrollbar(self.canvas, orient=tk.VERTICAL, command=self.canvas.yview)
            self.h_scrollbar = tk.Scrollbar(self.canvas, orient=tk.HORIZONTAL, command=self.canvas.xview)
            self.canvas.config(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

            self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
            
            # Enable the draggable scale bar
            self.magnification, self.scalepixels = obtainmagnification(self.image_path)
            self.create_draggable_scale_bar()
            
            # Enable the Save button
            self.save_button.config(state="normal")
            # Bind the configure event to update scroll region
            self.canvas.bind("<Configure>", self.on_frame_configure)

    def create_draggable_scale_bar(self):
        # Scale bar dimensions and initial position
        self.bar_length_mum = self.scalelength.get()
        self.bar_height_mum = 1
        self.bar_length = self.bar_length_mum/self.scalepixels
        self.bar_height = self.bar_height_mum/self.scalepixels
        self.text = f"{self.bar_length_mum} µm"
        
        # Default position of the scale bar
        self.bar_x = self.image.width - self.bar_length - 10
        self.bar_y = 10
        
        # Draw initial scale bar and text
        self.bar = self.canvas.create_rectangle(self.bar_x, self.bar_y, self.bar_x + self.bar_length, self.bar_y + self.bar_height, fill="white")
        self.text_id = self.canvas.create_text(self.bar_x, self.bar_y + self.bar_height + 10, anchor="nw", text=self.text, fill="white", font=("Arial", 20))
        
        # Bind mouse events for dragging
        self.canvas.tag_bind(self.bar, "<ButtonPress-1>", self.on_press)
        self.canvas.tag_bind(self.text_id, "<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)

    def on_enterscale(self, *args):
        # update scale bar length
        if self.image:
            self.bar_length_mum = self.scalelength.get()
            self.bar_length = self.bar_length_mum/self.scalepixels
            self.text = f"{self.bar_length_mum} µm"
            self.canvas.coords(self.bar, self.bar_x, self.bar_y, self.bar_x + self.bar_length, self.bar_y + self.bar_height)
            self.canvas.itemconfig(self.text_id, text=self.text)


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
        
        # Draw scale bar and text onto a copy of the image
        edited_image = self.image.copy()
        draw = ImageDraw.Draw(edited_image)
        
        # Draw the scale bar at the final position chosen by the user
        draw.rectangle([self.bar_x, self.bar_y, self.bar_x + self.bar_length, self.bar_y + self.bar_height], fill="white")
        
        # Load font for the text
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except IOError:
            font = ImageFont.load_default()
        
        # Draw the text below the scale bar
        draw.text((self.bar_x, self.bar_y + self.bar_height + 5), self.text, fill="white", font=font)
        
        # Save the image with "_saved" in the filename
        base, ext = os.path.splitext(self.image_path)
        new_image_path = f"{base}_saved{ext}"
        edited_image.save(new_image_path)
        messagebox.showinfo("Image Saved", f"Image saved as {new_image_path}")
    
    def on_frame_configure(self, event):
        # Update the scroll region of the canvas
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

# Run the app
root = tk.Tk()
app = ScaleBarApp(root, magnification=20)
root.mainloop()
