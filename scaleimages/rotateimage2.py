import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class ImageRotatorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Image Rotator")

        # Create a frame for the canvas and scrollbars
        self.frame = tk.Frame(master)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Create a canvas widget
        self.canvas = tk.Canvas(self.frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create vertical and horizontal scrollbars
        self.v_scrollbar = tk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.h_scrollbar = tk.Scrollbar(master, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.config(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Create a frame to hold the image
        self.image_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.image_frame, anchor='nw')

        self.image_label = tk.Label(self.image_frame, text="No image selected")
        self.image_label.pack(pady=10)

        self.open_button = tk.Button(master, text="Open Image", command=self.open_image)
        self.open_button.pack(pady=5)

        self.degree_entry = tk.Entry(master)
        self.degree_entry.pack(pady=5)
        self.degree_entry.insert(0, "Enter degrees")

        self.rotate_button = tk.Button(master, text="Rotate Image", command=self.rotate_image)
        self.rotate_button.pack(pady=5)

        # Bind the configure event to update scroll region
        self.image_frame.bind("<Configure>", self.on_frame_configure)

    def open_image(self):
        # Updated file dialog filter to include BMP files
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.gif;*.bmp")])
        if file_path:
            self.original_image = Image.open(file_path)
            self.image_label.config(text=file_path)
            self.display_image(self.original_image)

    def display_image(self, img):
        # Display the image
        self.img = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.img)

    def rotate_image(self):
        try:
            degrees = float(self.degree_entry.get())
            rotated_image = self.original_image.rotate(degrees, expand=True)

            # Save the rotated image with the specified name format
            original_filename = self.image_label.cget("text")
            filename_parts = original_filename.rsplit('.', 1)
            if len(filename_parts) == 2:
                new_filename = f"{filename_parts[0]}_{int(degrees)}.{filename_parts[1]}"
            else:
                new_filename = f"{filename_parts[0]}_{int(degrees)}.jpg"  # Default to .jpg if no extension

            rotated_image.save(new_filename)
            messagebox.showinfo("Success", f"Image saved as: {new_filename}")
            self.display_image(rotated_image)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for degrees.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def on_frame_configure(self, event):
        # Update the scroll region of the canvas
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageRotatorApp(root)
    root.mainloop()
