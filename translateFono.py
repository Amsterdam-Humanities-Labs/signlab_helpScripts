from bs4 import BeautifulSoup
import json

def extract_data(filename):
    # Load the HTML content from the file
    with open(filename, 'r') as file:
        html_content = file.read()

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract relevant data from each 'li' element within each 'ul'
    extracted_data = []
    ul_elements = soup.find_all('ul', id=lambda x: x)
    for ul in ul_elements:
        for li in ul.find_all('li'):
            item = {
                'id': li.get('id'),
                'text': li.get_text(strip=True)
            }
            extracted_data.append(item)
    
    return extracted_data

# Extract data from both files
data_fono = extract_data('fono.html')
data_fono_eng = extract_data('fono_eng.html')

# Assuming both files have the same structure and number of elements,
# bind the data together
combined_data = []
for item_fono, item_fono_eng in zip(data_fono, data_fono_eng):
    combined_item = {
        'id': item_fono['id'],  # Assuming IDs are the same and can be used as a reference
        'text_fono': item_fono['text'],
        'text_fono_eng': item_fono_eng['text']
    }
    combined_data.append(combined_item)

# Convert the combined data to JSON
combined_json = json.dumps(combined_data, indent=4)

# Output or save the JSON data
print(combined_json)

# Save to file
with open('combined_fono.json', 'w') as file:
    file.write(combined_json)
