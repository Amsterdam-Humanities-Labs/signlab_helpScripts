#!/bin/bash

error_log="conversion_errors.log"
lockfile="/tmp/process_files.lock"
skipped_files="skipped_files.log"

# List directories starting with 2024 in /web/gebarenoverleg_media/studioFiles
folders=$(find /web/gebarenoverleg_media/studioFiles -mindepth 1 -maxdepth 1 -type d -name '2024*')

# Generate a list of files in these directories
file_list=$(mktemp)
dir_list=$(mktemp)
for folder in $folders; do
    find "$folder" -type f \( -name '*.MP4' -o -name '*.mp4' \) >> "$file_list"
    echo "$folder" >> "$dir_list"
done





# Check for lockfile
if [ -e "$lockfile" ]; then
    echo "Lockfile exists. Another instance is running or the previous instance didn't exit cleanly."
    exit 1
else
    # Create a lockfile
    touch "$lockfile"
    # Ensure the lockfile is removed on script exit or interruption
    trap "rm -f '$lockfile' '$file_list' '$dir_list'; exit" INT TERM EXIT

    # Call the function to process files

for item in $(cat $file_list); do
    #now we want to check if the file exists in the output directory
     if [[ "$item" == *raw* ]]; then
            output_dir="/web/gebarenoverleg_media/studioFilesMini/raw"
        elif [[ "$item" == *post* ]]; then
            output_dir="/web/gebarenoverleg_media/studioFilesMini/post"
        else
            echo "$name does not contain 'raw' or 'post', skipping."
            echo "$item" >> "$skipped_files"
            continue
        fi

    extension="${item##*.}"
    name=$(basename "$item" .$extension)
    echo "$name"
    # Now we know the directory, then we check if the file exists in the output dir
if [[ -f "$output_dir/$name.mp4" || -f "$output_dir/$name.MP4" ]]; then
        lala="lala"

        #then we are going to process with ffmpeg
    else
        echo "File does not exist: $output_dir/$name.mp4\n"
        # nice -n 19 ffmpeg -nostdin -an -i "$item" -vcodec libx264 -pix_fmt yuv420p -profile:v baseline -level 3 "$output_dir/$name.MP4" -n 
        nice -n 19 ffmpeg -loglevel quiet -nostdin -i "$item" -c:v libx264 -c:a aac -pix_fmt yuv420p -profile:v baseline -level 3 "$output_dir/$name.mp4" -n 2>/dev/null

    fi

done

    # Remove the lockfile and temporary file lists on successful completion
    rm -f "$lockfile" "$file_list" "$dir_list"
fi

# Define your directories in an array
directories=(
  "/web/gebarenoverleg_media/studioFilesMini/raw"
  "/web/gebarenoverleg_media/studioFilesMini/post"
  "/web/uploads"
)

# Loop through each directory
for dir in "${directories[@]}"; do
  echo "Processing directory: $dir"
  # Check if the directory exists
  if [ -d "$dir" ]; then
    # Navigate to the directory
    cd "$dir" || exit  # Exit if changing directory fails
    
    # Enable case-insensitive globbing
    shopt -s nocaseglob

    # Process each video file in the directory for .mp4 and .mov extensions
    for video in *.{mp4,MP4,mov,MOV,webm}; do
      # Check if the file actually exists since the pattern could find no matches
      if [ -f "$video" ]; then
        # Define the absolute thumbnail filename, removing the file extension
        thumbnail="${PWD}/${video%.*}.jpg"
        
        # Check if the thumbnail already exists
        if [ ! -f "$thumbnail" ]; then

          #we want to determine duration from the video:
          frame_count=$(ffprobe -v error -select_streams v:0 -count_frames -show_entries stream=nb_read_frames -of default=nokey=1:noprint_wrappers=1 "$video")

          echo "Frame count of the video is: $frame_count frames"

          if [ -z "$frame_count" ] || [ "$frame_count" == "N/A" ]; then
              echo "Unable to determine frame count of the video: $video"
              # Set a default frame count if unable to determine
              frame_count=5
          fi
           # Calculate the midpoint frame
          midpoint_frame=$(echo "$frame_count / 2" | bc)

          # Generate the thumbnail from the midpoint frame
          echo "Generating thumbnail for $video at frame $midpoint_frame"
          nice -n 19 ffmpeg -loglevel quiet -i "$video" -vf "select=eq(n\,$midpoint_frame)" -vsync vfr -frames:v 1 "$thumbnail" -y 2>/dev/null
        fi
      fi
    done

    # Disable case-insensitive globbing after processing
    shopt -u nocaseglob

    # Navigate back to the original directory
    cd - > /dev/null
  else
    echo "Directory not found: $dir"
  fi
done

filePath="/web/servicesRecords.json"
service_name="Convert Script"
current_date=$(date "+%Y-%m-%d %H:%M:%S")

# Check if the service entry exists
found=$(jq --arg service_name "$service_name" '.[] | select(.service == $service_name)' "$filePath")

if [[ -z $found ]]; then
    # Append new record if not found
    jq --arg service_name "$service_name" --arg date "$current_date" \
       '. += [{"service": $service_name, "date": $date}]' "$filePath" > tmp.json
else
    # Update existing record if found
    jq --arg service_name "$service_name" --arg date "$current_date" \
       'map(if .service == $service_name then .date = $date else . end)' "$filePath" > tmp.json
fi

# Safely move the temporary file back to the original file
mv tmp.json "$filePath"
