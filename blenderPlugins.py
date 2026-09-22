import bpy
import os
import sys

def load_addons_from_directory(addons_directory):
    # Ensure the directory exists
    if not os.path.exists(addons_directory):
        print(f"Directory does not exist: {addons_directory}")
        return
    
    # Add the directory to the system path so that Python can find the modules
    sys.path.append(addons_directory)

    # Get the list of all directories (which are add-ons)
    addon_folders = [name for name in os.listdir(addons_directory) if os.path.isdir(os.path.join(addons_directory, name))]

    for addon_folder in addon_folders:
        addon_name = os.path.basename(addon_folder)
        
        # Check if the addon is already enabled
        if addon_name not in bpy.context.preferences.addons:
            # Try to load and enable the addon
            try:
                bpy.ops.preferences.addon_enable(module=addon_name)
                print(f"Enabled Addon: {addon_name}")
            except Exception as e:
                print(f"Failed to enable addon: {addon_name}, Error: {e}")
        else:
            print(f"Addon already enabled: {addon_name}")

# Specify the directory containing the add-ons
addons_directory = "/home/signcollect/.config/blender/4.2/scripts/addons"

# Load the add-ons from the directory
load_addons_from_directory(addons_directory)

# List all enabled add-ons
print("Enabled Add-ons:")
for addon in bpy.context.preferences.addons.keys():
    print(f"Plugin: {addon}")
