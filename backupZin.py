#!/usr/bin/env python3

import os
import shutil
import datetime
import logging

def setup_logging():
    """Setup logging configuration"""
    log_dir = "/web/gebarenoverleg_media/studioFiles/zinBackup/logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"backup_{datetime.datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def backup_files():
    """Backup files from source to destination directory"""
    # Define source and destination directories
    source_dir = "/web/zin/eaf/zin"
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dest_base = "/web/gebarenoverleg_media/studioFiles/zinBackup"
    dest_dir = os.path.join(dest_base, f"backup_{timestamp}")
    
    # Create destination directory if it doesn't exist
    try:
        os.makedirs(dest_dir, exist_ok=True)
        logging.info(f"Created backup directory: {dest_dir}")
    except Exception as e:
        logging.error(f"Failed to create backup directory: {e}")
        return False
    
    # Check if source directory exists
    if not os.path.exists(source_dir):
        logging.error(f"Source directory does not exist: {source_dir}")
        return False
    
    # Copy files from source to destination
    try:
        files_copied = 0
        for item in os.listdir(source_dir):
            src_path = os.path.join(source_dir, item)
            dst_path = os.path.join(dest_dir, item)
            
            if os.path.isfile(src_path):
                shutil.copy2(src_path, dst_path)
                files_copied += 1
                logging.info(f"Copied: {src_path} -> {dst_path}")
            elif os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path)
                files_copied += 1
                logging.info(f"Copied directory: {src_path} -> {dst_path}")
        
        logging.info(f"Backup completed successfully. Total items copied: {files_copied}")
        return True
    except Exception as e:
        logging.error(f"Error during backup: {e}")
        return False

if __name__ == "__main__":
    setup_logging()
    logging.info("Starting backup process...")
    
    success = backup_files()
    
    if success:
        logging.info("Backup completed successfully")
    else:
        logging.error("Backup failed")
