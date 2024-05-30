import os
import shutil
import struct
import imghdr
import tkinter as tk
from tkinter import filedialog, messagebox

def extract_spotlight_images(output_dir, aspect_ratios):
    # Define paths
    user_profile = os.getenv('USERPROFILE')
    spotlight_dir = os.path.join(user_profile, r'AppData\Local\Packages\Microsoft.Windows.ContentDeliveryManager_cw5n1h2txyewy\LocalState\Assets')

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Iterate over files in the Spotlight directory
    for file_name in os.listdir(spotlight_dir):
        file_path = os.path.join(spotlight_dir, file_name)
        
        # Only consider files larger than 100 KB (these are likely images)
        if os.path.isfile(file_path) and os.path.getsize(file_path) > 100 * 1024:
            # Determine the new file path with .jpg extension
            new_file_name = file_name + '.jpg'
            new_file_path = os.path.join(output_dir, new_file_name)

            # Copy the file to the output directory with the new name
            # shutil.copyfile(file_path, new_file_path)
            
            # Filter by aspect ratio and copy the file to the output directory with the new name
            try:
                if aspect_ratios["landscape"].get() and is_landscape(file_path):
                    shutil.copyfile(file_path, new_file_path)
                elif aspect_ratios["portrait"].get() and is_portrait(file_path):
                    shutil.copyfile(file_path, new_file_path)
                else:
                    continue
            except Exception as e:
                print(f"Error processing file {file_name}: {e}")

    messagebox.showinfo("Success", f"Spotlight images have been copied to {output_dir}")

def get_image_size(filepath):
    """Determine the image type of fhandle and return its size.
    from draco"""
    with open(filepath, 'rb') as fhandle:
        head = fhandle.read(24)
        if len(head) != 24:
            return
        if imghdr.what(filepath) == 'png':
            check = struct.unpack('>i', head[4:8])[0]
            if check == 0x0d0a1a0a:
                width, height = struct.unpack('>ii', head[16:24])
                return width, height
        elif imghdr.what(filepath) == 'gif':
            width, height = struct.unpack('<HH', head[6:10])
            return width, height
        elif imghdr.what(filepath) == 'jpeg':
            try:
                fhandle.seek(0)  # Read 0xff next
                size = 2
                ftype = 0
                while not 0xc0 <= ftype <= 0xcf:
                    fhandle.seek(size, 1)
                    byte = fhandle.read(1)
                    while ord(byte) == 0xff:
                        byte = fhandle.read(1)
                    ftype = ord(byte)
                    size = struct.unpack('>H', fhandle.read(2))[0] - 2
                fhandle.seek(1, 1)  # `precision' byte.
                height, width = struct.unpack('>HH', fhandle.read(4))
            except Exception as e:
                return
            return width, height

def is_landscape(filepath):
    size = get_image_size(filepath)
    if size:
        width, height = size
        return width > height
    return False

def is_portrait(filepath):
    size = get_image_size(filepath)
    if size:
        width, height = size
        return height > width
    return False

def select_output_folder(aspect_ratios):
    if aspect_ratios["landscape"].get() or aspect_ratios["portrait"].get():
        output_dir = filedialog.askdirectory(title="Select Output Folder")
    else:
        messagebox.showwarning("Select aspect ratios", "Select at least one aspect ratio to extract.")
    if output_dir:
        extract_spotlight_images(output_dir, aspect_ratios)

def main():
    # Create the root window
    root = tk.Tk()
    root.title("Windows Spotlight Image Extractor")
    root.resizable(False, False)  # Make the window non-resizable

    # Create a frame for padding and alignment
    frame = tk.Frame(root, padx=20, pady=20)
    frame.pack(fill=tk.BOTH, expand=True)

    # Create a title label
    label = tk.Label(frame, text="Select Aspect Ratios:")
    label.grid(row=0, column=0, sticky=tk.W, padx=5)

    # Variables to store the aspect ratio choices
    aspect_ratios = {
        "landscape": tk.BooleanVar(value=False),
        "portrait": tk.BooleanVar(value=False)
    }

    # Create checkboxes for aspect ratio selection on the same line as the label
    chk_landscape = tk.Checkbutton(frame, text="Landscape", variable=aspect_ratios["landscape"])
    chk_landscape.grid(row=0, column=1, sticky=tk.W, padx=5)

    chk_portrait = tk.Checkbutton(frame, text="Portrait", variable=aspect_ratios["portrait"])
    chk_portrait.grid(row=0, column=2, sticky=tk.W, padx=5)

    # Create a button to select the output folder
    btn_select_folder = tk.Button(frame, text="Select Output Folder", command=lambda: select_output_folder(aspect_ratios))
    btn_select_folder.grid(row=1, column=0, columnspan=3, pady=(10,0))

    # Run the Tkinter event loop
    root.eval('tk::PlaceWindow . center')
    root.mainloop()

if __name__ == '__main__':
    main()
