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

# Enable the Rigify add-on
if "rigify" not in bpy.context.preferences.addons:
    bpy.ops.preferences.addon_enable(module="rigify")
    print("Rigify add-on enabled.")

# Ensure the add-on is enabled
if "rigify" in bpy.context.preferences.addons:
    print("Rigify is enabled.")

    # Add a basic human metarig
    bpy.ops.object.armature_human_metarig_add()
    print("Added human metarig.")

    # You can now proceed to generate the rig or perform further operations
    # For example, you could set up the rig or customize it before generating
else:
    print("Rigify could not be enabled.")

# List all enabled add-ons
print("Enabled Add-ons:")
for addon in bpy.context.preferences.addons.keys():
    print(f"Plugin: {addon}")
    

# List of add-ons to enable
addons_to_enable = [
    "pose_library",                       # Animation: Pose Library
    "io_anim_bvh",                        # Import-Export: BioVision Motion Capture (BVH) format
    "io_scene_fbx",                       # Import-Export: FBX format    "io_curve_svg",                       # Import-Export: Scalable Vector Graphics (SVG) 1.1 format
    "io_mesh_uv_layout",                  # Import-Export: UV Layout
    "io_scene_gltf2",                     # Import-Export: glTF 2.0 format
    "object_boolean_tools",               # Object: Bool Tool
    "cycles",                             # Render: Cycles Render Engine
    "expykit",                            # Rigging: Expy Kit
    "rigify",                             # Rigging: Rigify
]

# Enable each add-on
for addon in addons_to_enable:
    if addon not in bpy.context.preferences.addons:
        bpy.ops.preferences.addon_enable(module=addon)
        print(f"Enabled Addon: {addon}")
    else:
        print(f"Addon already enabled: {addon}")

print("All specified add-ons have been enabled.")

