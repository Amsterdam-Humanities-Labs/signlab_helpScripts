#!/bin/bash

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

    # Process each video file in the directory for .mp4, .mov, and .webm extensions
    for video in *.{mp4,MP4,mov,MOV,webm}; do
      # Check if the file actually exists since the pattern could find no matches
      if [ -f "$video" ]; then
        # Define the absolute thumbnail filename, removing the file extension
        thumbnail="${PWD}/${video%.*}.jpg"
        
        # Check if the thumbnail already exists
        if [ ! -f "$thumbnail" ]; then

          # Determine the total number of frames in the video
          frame_count=$(ffprobe -v error -select_streams v:0 -count_frames -show_entries stream=nb_read_frames -of default=nokey=1:noprint_wrappers=1 "$video")

          echo "Frame count of the video is: $frame_count frames"

          if [ -z "$frame_count" ] || [ "$frame_count" == "N/A" ]; then
              echo "Unable to determine frame count of the video: $video"
              # Set a default frame count if unable to determine
              frame_count=1
          fi

          # Calculate the midpoint frame
          midpoint_frame=$(echo "$frame_count / 2" | bc)

          # Generate the thumbnail from the midpoint frame
          echo "Generating thumbnail for $video at frame $midpoint_frame"
          nice -n 19 ffmpeg -loglevel quiet -vf "select=eq(n\,$midpoint_frame)" -vsync vfr -i "$video" -frames:v 1 "$thumbnail" -y 2>/dev/null

          if [ $? -eq 0 ]; then
              echo "Thumbnail generated successfully: $thumbnail"
          else
              echo "Failed to generate thumbnail for $video"
          fi
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
