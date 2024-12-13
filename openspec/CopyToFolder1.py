import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox

def copy_txt_files(search_dir, target_dir, exclude_dir_name):
    """
    Copies all .txt files from all folders in the specified search directory (except the exclude folder)
    to the target directory.

    Args:
        search_dir (str): The directory to search for .txt files.
        target_dir (str): The directory to copy the .txt files to.
        exclude_dir_name (str): The folder name to exclude from the search.
    """
    # Ensure the target directory exists
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    for root, dirs, files in os.walk(search_dir):
        # Skip the exclude folder
        if os.path.basename(root) == exclude_dir_name:
            continue

        for file in files:
            if file.endswith('.txt'):
                source_path = os.path.join(root, file)
                dest_path = os.path.join(target_dir, file)

                # Copy the file
                shutil.copy2(source_path, dest_path)

    messagebox.showinfo("Success", f".txt files copied successfully to {target_dir}")

# GUI Functionality
def select_search_dir():
    """Opens a directory selection dialog to choose the search directory."""
    dir_path = filedialog.askdirectory(title="Select Search Directory")
    if dir_path:
        search_dir_var.set(dir_path)

def select_target_dir():
    """Opens a directory selection dialog to choose the target directory."""
    dir_path = filedialog.askdirectory(title="Select Target Directory")
    if dir_path:
        target_dir_var.set(dir_path)

def start_copy():
    """Starts the copy process after validating input."""
    search_dir = search_dir_var.get()
    target_dir = target_dir_var.get()
    exclude_dir = exclude_dir_var.get()

    if not search_dir or not target_dir:
        messagebox.showerror("Error", "Please select both search and target directories.")
        return

    if not os.path.exists(search_dir):
        messagebox.showerror("Error", "Search directory does not exist.")
        return

    if exclude_dir and os.path.basename(search_dir) == exclude_dir:
        messagebox.showerror("Error", "The search directory cannot be the excluded directory.")
        return

    copy_txt_files(search_dir, target_dir, exclude_dir)

# Initialize GUI
root = tk.Tk()
root.title("Copy .txt Files")
root.geometry("500x350")

# Variables to hold directory paths
search_dir_var = tk.StringVar()
target_dir_var = tk.StringVar()
exclude_dir_var = tk.StringVar()

# Create Widgets
tk.Label(root, text="Search Directory:").pack(pady=5)
tk.Entry(root, textvariable=search_dir_var, width=50).pack(pady=5)
tk.Button(root, text="Browse", command=select_search_dir).pack(pady=5)

tk.Label(root, text="Target Directory:").pack(pady=5)
tk.Entry(root, textvariable=target_dir_var, width=50).pack(pady=5)
tk.Button(root, text="Browse", command=select_target_dir).pack(pady=5)

tk.Label(root, text="Exclude Folder Name (Optional):").pack(pady=5)
tk.Entry(root, textvariable=exclude_dir_var, width=50).pack(pady=5)

tk.Button(root, text="Copy .txt Files", command=start_copy, bg="green", fg="white").pack(pady=20)

# Run the GUI loop
root.mainloop()
