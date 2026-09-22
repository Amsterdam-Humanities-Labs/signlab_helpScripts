import os
import shutil

# Define the patterns for restored files and directories
RESTORED_FILE_SUFFIX = " (restored)."
RESTORED_DIR_SUFFIX = " (restored)"

def get_original_filename(restored_filename):
    """
    Converts a restored filename like 'file (restored).ext' to 'file.ext'.
    Returns None if the pattern is not matched.
    """
    idx = restored_filename.rfind(RESTORED_FILE_SUFFIX)
    if idx == -1:
        return None  # Not a recognized restored file pattern

    base_name = restored_filename[:idx]
    extension_part = restored_filename[idx + len(RESTORED_FILE_SUFFIX):]
    
    # Handles cases like " (restored).txt" -> ".txt"
    # or "name (restored)." -> "name."
    return f"{base_name}.{extension_part}"

def get_original_dirname(restored_dirname):
    """
    Converts a restored dirname like 'folder (restored)' to 'folder'.
    Returns None if the pattern is not matched or if the original name would be empty.
    """
    if restored_dirname.endswith(RESTORED_DIR_SUFFIX):
        original_name = restored_dirname[:-len(RESTORED_DIR_SUFFIX)]
        if not original_name:  # Original name would be empty
            return None
        return original_name
    return None

def process_directory_recursively(root_dir):
    """
    Scans the directory tree starting from root_dir and processes restored files/folders.
    Uses topdown=False to process contents of directories before the directories themselves.
    """
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        # --- Process files in the current directory ---
        for filename in filenames:
            # Only process .mp4 files (case-insensitive)
            if filename.endswith(".MP4"):
                original_name = get_original_filename(filename)
                if original_name:
                    restored_filepath = os.path.join(dirpath, filename)
                    original_filepath = os.path.join(dirpath, original_name)

                    if not os.path.exists(original_filepath):
                        try:
                            os.rename(restored_filepath, original_filepath)
                            print(f"Renamed MP4 file: '{restored_filepath}' to '{original_filepath}'")
                        except OSError as e:
                            print(f"Error renaming MP4 file '{restored_filepath}' to '{original_filepath}': {e}")
                    else:
                        print(f"Original MP4 file '{original_filepath}' already exists. Kept '{restored_filepath}'.")
            elif RESTORED_FILE_SUFFIX in filename: # Log if other restored files are skipped
                print(f"Skipping non-MP4 restored file: '{os.path.join(dirpath, filename)}'")


        # --- Process subdirectories in the current directory ---
        # dirnames are the names of subdirectories within dirpath.
        # These subdirectories' contents have already been processed due to topdown=False.
        for dirname_to_check in list(dirnames): # Iterate over a copy in case dirnames is modified by os.walk internals (though less likely with topdown=False)
            original_dir_name = get_original_dirname(dirname_to_check)
            
            if not original_dir_name:
                if dirname_to_check.endswith(RESTORED_DIR_SUFFIX): # Matched suffix but resulted in empty original name
                    print(f"Skipping directory '{os.path.join(dirpath, dirname_to_check)}' as its original name would be empty.")
                continue

            restored_dir_fullpath = os.path.join(dirpath, dirname_to_check)
            original_dir_fullpath = os.path.join(dirpath, original_dir_name)

            # Ensure it's actually a directory we're about to process
            if not os.path.isdir(restored_dir_fullpath):
                continue 

            if os.path.isdir(original_dir_fullpath):
                # Original directory exists, merge content from restored_dir into original_dir
                print(f"Merging '{restored_dir_fullpath}' into '{original_dir_fullpath}'...")
                try:
                    for item in os.listdir(restored_dir_fullpath):
                        source_item_path = os.path.join(restored_dir_fullpath, item)
                        dest_item_path = os.path.join(original_dir_fullpath, item)

                        if os.path.exists(dest_item_path):
                            print(f"  Item '{item}' already exists in '{original_dir_fullpath}'. Skipping move from restored.")
                        else:
                            shutil.move(source_item_path, dest_item_path)
                            print(f"  Moved '{source_item_path}' to '{dest_item_path}'.")
                    
                    shutil.rmtree(restored_dir_fullpath)
                    print(f"Successfully merged contents and removed '{restored_dir_fullpath}'.")
                except OSError as e:
                    print(f"Error during merge for directory '{restored_dir_fullpath}': {e}")
            
            elif not os.path.exists(original_dir_fullpath):
                # Original directory does not exist (and no file/other FS object with that name), rename restored_dir
                try:
                    os.rename(restored_dir_fullpath, original_dir_fullpath)
                    print(f"Renamed directory: '{restored_dir_fullpath}' to '{original_dir_fullpath}'")
                except OSError as e:
                    print(f"Error renaming directory '{restored_dir_fullpath}' to '{original_dir_fullpath}': {e}")
            else:
                # An item (e.g. a file) exists with the original directory name, cannot proceed.
                print(f"Cannot rename/merge '{restored_dir_fullpath}': Path '{original_dir_fullpath}' exists and is not a directory.")

if __name__ == "__main__":
    target_scan_directory = "/web/gebarenoverleg_media/studioFiles"
    
    if not os.path.isdir(target_scan_directory):
        print(f"Error: Target directory '{target_scan_directory}' does not exist or is not a directory.")
    else:
        print(f"Starting processing for directory: '{target_scan_directory}'")
        process_directory_recursively(target_scan_directory)
        print("Processing complete.")
