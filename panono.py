from bs4 import BeautifulSoup
import json
import os

def extract_values_with_ids(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'lxml')
    
    values_with_ids = {}
    list_items = soup.find_all('li', class_='select2-results__option')
    for li in list_items:
        span = li.find('span')
        if span:
            id_part = li['id'].split('-')[-1]
            text = span.text.strip()
            values_with_ids[id_part] = text
    
    return values_with_ids

def find_matching_files(directory):
    nl_files = {}
    # Scan the directory for html files
    for filename in os.listdir(directory):
        if filename.endswith('.html') and 'NL' in filename:
            # Assuming the English file replaces 'NL' with 'EN'
            en_filename = filename.replace('NL', 'EN')
            if en_filename in os.listdir(directory):  # Check if English file exists
                nl_files[filename] = en_filename
    return nl_files

# Specify the directory containing your HTML files
directory = './'  # Adjust the path as necessary
file_pairs = find_matching_files(directory)

all_combined_data = []  # List to hold all combined translation data

# Process each pair of NL and EN files
for nl_file, en_file in file_pairs.items():
    values_nl = extract_values_with_ids(os.path.join(directory, nl_file))
    values_en = extract_values_with_ids(os.path.join(directory, en_file))

    # Combine the Dutch and English values based on IDs
    for id_key in values_nl:
        if id_key in values_en:
            all_combined_data.append({"ID": id_key, "NL": values_nl[id_key], "EN": values_en[id_key]})

# Output all combined data to one JSON file
json_filename = 'all_combined_translations.json'
with open(json_filename, 'w', encoding='utf-8') as f:
    json.dump(all_combined_data, f, ensure_ascii=False, indent=4)

print(f"Data for all translations written to {json_filename} with {len(all_combined_data)} entries.")
