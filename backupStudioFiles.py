import os
import shutil
import sys

# Source and destination base directories
src_base_dir = "/web/gebarenoverleg_media/studioFilesMini"
dest_base_dir = "/web/gebarenoverleg_media/studioFiles/backupMini"

# Lock file path
lock_file = "/tmp/backup_script.lock"

# Check if lock file exists, indicating that the script is already running
# if os.path.exists(lock_file):
#     print("Backup is already running. Exiting.")
#     sys.exit()

# # Create a lock file to indicate that the script is running
# with open(lock_file, 'w') as lock:
#     lock.write("Running")

try:
    # Ensure destination base directory exists
    os.makedirs(dest_base_dir, exist_ok=True)

    # Loop through each directory in the source base directory
    for dir_name in os.listdir(src_base_dir):
        src_dir = os.path.join(src_base_dir, dir_name)
        dest_dir = os.path.join(dest_base_dir, dir_name)
        
        # Check if it's a directory
        if os.path.isdir(src_dir):
            # Recursively copy directory if it doesn't exist in destination
            for root, dirs, files in os.walk(src_dir):
                # Create corresponding destination directories
                for dir in dirs:
                    dest_path = os.path.join(dest_dir, os.path.relpath(os.path.join(root, dir), src_dir))
                    os.makedirs(dest_path, exist_ok=True)

                # Copy files
                for file in files:
                    src_file = os.path.join(root, file)
                    dest_file = os.path.join(dest_dir, os.path.relpath(src_file, src_dir))

                    # Ensure the parent directory of the destination file exists
                    os.makedirs(os.path.dirname(dest_file), exist_ok=True)

                    try:
                        # Copy the file if it doesn't already exist in the destination
                        if not os.path.exists(dest_file):
                            shutil.copy2(src_file, dest_file)
                            print(f"Copied {file} to {dest_file}")
                        else:
                            print(f"File {file} already exists in {dest_file}. Skipping...")
                    except Exception as e:
                        print(f"Error copying {file}: {e}. Continuing...")

        else:
            # If it's a file directly under the source base directory, copy it
            dest_file = os.path.join(dest_base_dir, dir_name)
            try:
                if not os.path.exists(dest_file):
                    shutil.copy2(src_dir, dest_file)
                    print(f"Copied {dir_name} to {dest_base_dir}")
                else:
                    print(f"File {dir_name} already exists in {dest_base_dir}. Skipping...")
            except Exception as e:
                print(f"Error copying {dir_name}: {e}. Continuing...")

    print("Backup complete.")

finally:
    # Remove the lock file to indicate that the script has finished
    if os.path.exists(lock_file):
        os.remove(lock_file)
