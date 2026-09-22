import bpy

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
