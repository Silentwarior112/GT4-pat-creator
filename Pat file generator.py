import tkinter as tk
from tkinter import filedialog, messagebox
import struct

# Function to compare two files and generate a patch list
def generate_patch():
    file1_path = filedialog.askopenfilename(title="Select the first MDLS (MainModel). Select the modified file first to write original Tex1 data to the .pat")
    if not file1_path:
        messagebox.showwarning("Process aborted", "No file selected.")
        return
    
    file2_path = filedialog.askopenfilename(title="Select the second MDLS (MainModel). Select the original file second to write original Tex1 data to the .pat")
    if not file2_path:
        messagebox.showwarning("Process aborted", "No file selected.")
        return

    save_path = filedialog.asksaveasfilename(defaultextension=".pat", filetypes=[("Patch files", "*.pat")])
    if not save_path:
        messagebox.showwarning("Process aborted", "No save path selected.")
        return

    try:
        with open(file1_path, 'rb') as f1, open(file2_path, 'rb') as f2:
            file1_data = f1.read()
            file2_data = f2.read()

            # Ensure both files are the same size, or limit to the smaller one
            max_size = min(len(file1_data), len(file2_data))
            patches = []
            
            i = 0
            while i < max_size:
                if file1_data[i] != file2_data[i]:
                    start_offset = i
                    patch_bytes = bytearray()
                    
                    # Collect bytes until the files match again or we hit the end
                    while i < max_size and file1_data[i] != file2_data[i]:
                        patch_bytes.append(file2_data[i])
                        i += 1
                    
                    # Round up patch length to the next multiple of 4
                    patch_length = len(patch_bytes)
                    padding_needed = (4 - (patch_length % 4)) % 4
                    padded_length = patch_length + padding_needed
                    
                    # Add extra matching bytes to make it a multiple of 4
                    if i + padding_needed <= max_size:
                        patch_bytes += file2_data[i:i + padding_needed]
                        
                    patches.append((start_offset, len(patch_bytes), patch_bytes))
                    i += padding_needed  # Skip those extra bytes we just added
                    
                else:
                    i += 1

        # Create the patch file content
        patch_content = bytearray()

        # Magic "Pat0"
        patch_content += b'Pat0'

        # 12 bytes of hard-coded 0x00
        patch_content += b'\x00' * 12

        # Hard-coded 0x01 0x00. Since we only need to create a .pat with one color we simply hardcode. Once generated the color adder script will handle adding more variations
        patch_content += b'\x01\x00'

        # Number of patches (2 bytes, little-endian)
        patch_content += struct.pack('<H', len(patches))

        # Another 12 bytes of hard-coded 0x00
        patch_content += b'\x00' * 12

        # Write the location table
        patch_locations = []
        current_offset = 0x30 + (len(patches) * 4)  # Initial offset after the location table
        for patch in patches:
            patch_locations.append(current_offset - 16)
            current_offset += 8 + patch[1]  # 8 bytes for offset + length, plus patch size

        # Write patch start locations (4 bytes for each patch location)
        for loc in patch_locations:
            patch_content += struct.pack('<I', loc)

        # For each patch: write the original file offset, patch size, and patch bytes
        for idx, patch in enumerate(patches):
            patch_offset, patch_length, patch_bytes = patch

            # Starting offset in the original file (4 bytes, little-endian)
            patch_content += struct.pack('<I', patch_offset)

            # Patch length (4 bytes, little-endian)
            patch_content += struct.pack('<I', patch_length)

            # Patch bytes
            patch_content += patch_bytes

        # Save the patch file
        with open(save_path, 'wb') as patch_file:
            patch_file.write(patch_content)

        messagebox.showinfo("Success", f"Patch file saved to {save_path}")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Create GUI window
root = tk.Tk()
root.title("Patch Generator")
root.geometry("260x60")

# Button to generate patch
patch_button = tk.Button(root, text="Generate .pat", command=generate_patch)
patch_button.pack(pady=10)

# Start the GUI loop
root.mainloop()
