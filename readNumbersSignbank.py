import json
import csv


urls = 'video_urls.json'

# Read the JSON file
with open(urls, 'r') as file:
    json_data = json.load(file)

# Extract the numbers from the keys
numbers = [key.split('-')[-1] for key in json_data.keys()]

# remove everything after . in the numbers
numbers = [number.split('.')[0] for number in numbers]

# reove duplicates
numbers = list(set(numbers))


# Specify the path to your CSV file
csv_file_path = 'signbankUrls.csv'

# Write the numbers to a CSV file
with open(csv_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Number'])  # Writing the header
    for number in numbers:
        writer.writerow([number])

print(f"Numbers extracted and saved to {csv_file_path}")
