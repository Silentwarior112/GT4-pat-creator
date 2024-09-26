import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import struct
import os

# Function to apply masking logic
def apply_mask_logic(pixels):
    mask_pixels = bytearray(pixels)
    for i in range(0, len(pixels), 4):
        r, g, b, a = pixels[i:i+4]

        if a == 0: # Overrides pixels with no opacity as red, although some pixels will be relevant if they are adjacent to relevant pixels despite having 0 opacity, should probably change
            mask_pixels[i:i+4] = b'\xFF\x00\x00\xFF' # Red = No opacity, should ignore for the most part
        elif a > 128: # Overrides pixels with opacity greater than 128 as green. Green = Completely invalid
            mask_pixels[i:i+4] = b'\x00\xFF\x00\xFF'
        elif r != g or g != b: # Overrides pixels that are valid but not shades as blue. Blue = Valid Colors
            mask_pixels[i:i+4] = b'\x00\x00\xFF\xFF'
        else: # Overrides pixels that are valid shades as black. Each channel is changed to make pat file generation easy.
            mask_pixels[i:i+4] = b'\x00\x00\x00\xFF'

    return bytes(mask_pixels)

# Function to extract Tex1 data and convert to PNG and Masked PNG
def extract_and_convert_to_png():
    file_path = filedialog.askopenfilename(title="Select Tex1 file to extract")
    
    if not file_path:
        messagebox.showwarning("No file selected", "Please select a valid file.")
        return
    
    try:
        with open(file_path, 'rb') as f:
            f.seek(0xC)
            total_bytes = struct.unpack('I', f.read(4))[0]
            f.seek(0x12)
            block_size = struct.unpack('H', f.read(2))[0]
            block_size_bytes = block_size * 256
            pixel_data_start = total_bytes - block_size_bytes
            f.seek(pixel_data_start)
            pixel_bytes = f.read(block_size_bytes)
            image_width = 64
            num_pixels = len(pixel_bytes) // 4
            image_height = (num_pixels + image_width - 1) // image_width
            total_pixels = image_width * image_height
            padding_needed = total_pixels - num_pixels
            if padding_needed > 0: # To account for byte counts that don't result in even multiple of 64
                pixel_bytes += b'\xFF\xFF\xFF\xFF' * padding_needed
            image = Image.frombytes('RGBA', (image_width, image_height), pixel_bytes)
            save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
            if save_path:
                image.save(save_path)
                messagebox.showinfo("Success", f"PNG saved to {save_path}")
            else:
                messagebox.showwarning("No save path", "File not saved.")
                return
            mask_pixels = apply_mask_logic(pixel_bytes)
            mask_image = Image.frombytes('RGBA', (image_width, image_height), mask_pixels)
            base_name, ext = os.path.splitext(save_path)
            mask_save_path = f"{base_name}_mask.png"
            mask_image.save(mask_save_path)
            messagebox.showinfo("Success", f"Mask PNG saved to {mask_save_path}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Function to import a PNG into the file as bytes
def import_png_as_bytes():
    file_path = filedialog.askopenfilename(title="Select Tex1 to import PNG into")
    
    if not file_path:
        messagebox.showwarning("No file selected", "Please select a valid file.")
        return
    
    png_path = filedialog.askopenfilename(title="Select PNG file to import", filetypes=[("PNG files", "*.png")])
    
    if not png_path:
        messagebox.showwarning("No PNG selected", "Please select a valid PNG file.")
        return
    
    try:
        # Open the main file to modify
        with open(file_path, 'r+b') as f:
            f.seek(0xC)
            total_bytes = struct.unpack('I', f.read(4))[0]
            f.seek(0x12)
            block_size = struct.unpack('H', f.read(2))[0]
            block_size_bytes = block_size * 256
            pixel_data_start = total_bytes - block_size_bytes

            # Load the PNG
            image = Image.open(png_path)
            png_bytes = bytearray(image.tobytes())
            
            if len(png_bytes) > block_size_bytes:
                png_bytes = png_bytes[:block_size_bytes]  # Cut off excess data
            
            ignored_bytes = len(png_bytes) - block_size_bytes if len(png_bytes) > block_size_bytes else 0
            
            # Write pixel bytes to the main file
            f.seek(pixel_data_start)
            f.write(png_bytes[:block_size_bytes])
            
            messagebox.showinfo("Success", f"PNG imported into the file! {ignored_bytes} excess bytes were detected.")
    
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Create GUI window
root = tk.Tk()
root.title("Tex1 to byte map")
root.geometry("320x100")

# Button to extract PNG and create Mask PNG
convert_button = tk.Button(root, text="Tex1 to PNG with mask", command=extract_and_convert_to_png)
convert_button.pack(pady=10)

# New button to import PNG into the file as bytes
import_button = tk.Button(root, text="Import PNG into Tex1", command=import_png_as_bytes)
import_button.pack(pady=10)

# Start the GUI loop
root.mainloop()
