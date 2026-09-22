#!/bin/bash

base_dir="/web/gebarenoverleg_media/studioFiles"
temp_dir="$base_dir/temp_mismatched_files"

# Create the temp directory if it doesn't exist
mkdir -p "$temp_dir"

# Function to move files in the background
move_file() {
    local src="$1"
    local dest="$2"
    mv "$src" "$dest" &
}

# Loop through all directories that match the date pattern
for folder in $(find "$base_dir" -maxdepth 1 -type d -regextype posix-extended -regex ".*/[0-9]{4}-[0-9]{2}-[0-9]{2}"); do
    folder_date=$(basename "$folder" | sed 's/-//g') # Extract folder date and remove dashes
    raw_dir="$folder/raw"

    # Check if the raw directory exists
    if [ -d "$raw_dir" ]; then
        echo "Checking folder: $folder_date"

        # Loop through the files in the raw directory
        for file in "$raw_dir"/*; do
            # Skip if it's not a file
            [ -f "$file" ] || continue

            filename=$(basename "$file")
            
            # Check if filename contains the folder date
            if [[ "$filename" != *"$folder_date"* ]]; then
                echo "File mismatch: $file"
                
                # Target directory where the file should be moved
                target_dir="$base_dir/$(echo "$filename" | grep -oP '[0-9]{4}[0-9]{2}[0-9]{2}')/raw"

                # Check if the target directory exists
                if [ -d "$target_dir" ]; then
                    # Check if the file already exists in the target directory
                    if [ -f "$target_dir/$filename" ]; then
                        echo "File already exists in $target_dir. Moving $file to temp directory."
                        move_file "$file" "$temp_dir/"
                    else
                        echo "Moving $file to $target_dir"
                        move_file "$file" "$target_dir/"
                    fi
                else
                    echo "Target directory $target_dir does not exist. Moving $file to temp directory."
                    move_file "$file" "$temp_dir/"
                fi
            fi
        done
    fi
done

# Wait for all background moves to finish
wait
echo "All moves completed."
