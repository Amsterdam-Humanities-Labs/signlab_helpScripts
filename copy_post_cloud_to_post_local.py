#!/usr/bin/env python3
import os
import shutil
import re
import glob
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Define source and destination directories
SOURCE_BASE_DIR = "/web/gebarenoverleg_media/studioFiles"
DEST_DIR = "/web/gebarenoverleg_media/studioFilesMini/post"

def ensure_dest_dir_exists():
    """Ensure the destination directory exists."""
    if not os.path.exists(DEST_DIR):
        logging.info(f"Creating destination directory: {DEST_DIR}")
        os.makedirs(DEST_DIR)

def find_post_directories():
    """Find all directories from 2024 or 2025 that contain a 'post' subdirectory."""
    post_dirs = []
    
    # Find all directories in the source base directory
    try:
        all_dirs = [d for d in os.listdir(SOURCE_BASE_DIR) 
                  if os.path.isdir(os.path.join(SOURCE_BASE_DIR, d))]
    except FileNotFoundError:
        logging.error(f"Source directory not found: {SOURCE_BASE_DIR}")
        return []
    
    # Filter for directories with '2024' or '2025' in the name
    year_pattern = re.compile(r'202[45]')
    year_dirs = [d for d in all_dirs if year_pattern.search(d)]
    
    # Check each year directory for a 'post' subdirectory
    for year_dir in year_dirs:
        full_path = os.path.join(SOURCE_BASE_DIR, year_dir)
        post_path = os.path.join(full_path, "post")
        
        if os.path.isdir(post_path):
            post_dirs.append(post_path)
            logging.info(f"Found post directory: {post_path}")
    
    return post_dirs

def copy_mp4_files(post_dirs):
    """Copy all MP4 files from the post directories to the destination."""
    file_count = 0
    
    for post_dir in post_dirs:
        # Get all MP4 files in the post directory
        mp4_files = glob.glob(os.path.join(post_dir, "*.mp4"))
        
        for source_file in mp4_files:
            # Get just the filename
            filename = os.path.basename(source_file)
            
            # Remove '_h264' from the filename if present
            dest_filename = filename.replace("_h264", "")
            dest_path = os.path.join(DEST_DIR, dest_filename)
            
            try:
                shutil.copy2(source_file, dest_path)
                file_count += 1
                logging.info(f"Copied {filename} → {dest_filename}")
            except Exception as e:
                logging.error(f"Failed to copy {source_file}: {str(e)}")
    
    return file_count

def main():
    """Main function to run the script."""
    logging.info("Starting MP4 file copy process")
    
    # Ensure destination directory exists
    ensure_dest_dir_exists()
    
    # Find all relevant post directories
    post_dirs = find_post_directories()
    logging.info(f"Found {len(post_dirs)} post directories to process")
    
    # Copy files
    if post_dirs:
        copied_files = copy_mp4_files(post_dirs)
        logging.info(f"Successfully copied {copied_files} MP4 files to {DEST_DIR}")
    else:
        logging.warning("No post directories found matching the criteria")
    
    logging.info("Script execution completed")

if __name__ == "__main__":
    main()
