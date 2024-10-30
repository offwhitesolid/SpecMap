import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class ImageRotatorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Image Rotator")
        
        self.image_label = tk.Label(master, text="No image selected")
        self.image_label.pack(pady=10)

        self.open_button = tk.Button(master, text="Open Image", command=self.open_image)
        self.open_button.pack(pady=5)

        self.degree_entry = tk.Entry(master)
        self.degree_entry.pack(pady=5)
        self.degree_entry.insert(0, "Enter degrees")

        self.rotate_button = tk.Button(master, text="Rotate Image", command=self.rotate_image)
        self.rotate_button.pack(pady=5)

    def open_image(self):
        # Updated file dialog filter to include BMP files
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.gif;*.bmp")])
        if file_path:
            self.original_image = Image.open(file_path)
            self.image_label.config(text=file_path)
            self.display_image(self.original_image)

    def display_image(self, img):
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

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageRotatorApp(root)
    root.mainloop()
