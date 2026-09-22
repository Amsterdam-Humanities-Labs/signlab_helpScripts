import csv

# Replace 'yourfile.csv' with the path to your CSV file
csv_file_path = 'oline.csv'

with open(csv_file_path, newline='') as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=';')
    next(csv_reader, None)  # Skip the header row if there is one
    for row in csv_reader:
        # Extracting the necessary fields
        folder_prefix = row[0].strip()
        video_left = row[1].strip()
        video_center = row[2].strip()
        video_right = row[3].strip()

        # Generating and printing the commands
        print(f'cp {video_left} /web/gebarenoverleg_media/studioFiles/3DLEX/videoLeft')
        print(f'cp {video_right} /web/gebarenoverleg_media/studioFiles/3DLEX/videoRight')
        print(f'cp {video_center} /web/gebarenoverleg_media/studioFiles/3DLEX/videoCenter')
