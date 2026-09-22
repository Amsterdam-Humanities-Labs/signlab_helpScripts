from bs4 import BeautifulSoup
import json

def extract_column_data_with_id(html_file_path, column_name):
    with open(html_file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'lxml')
    
    table = soup.find('table')
    headers = []
    for th in table.find('tr').find_all('th'):
        headers.append(th.text.strip())
    
    column_index = headers.index(column_name)
    column_data = {}
    
    for row in table.find_all('tr')[1:]:  # skip the header row
        cells = row.find_all('td')
        if len(cells) > column_index:
            anchor = cells[column_index].find('a')
            if anchor:
                handshape_id = anchor['href'].split('/')[-2]  # assuming URL format /dictionary/handshape/21/
                handshape_name = anchor.text.strip()
                column_data[handshape_id] = handshape_name

    return column_data

# Paths to your HTML files
html_file_path_nl = 'fonoTableNL.html'
html_file_path_en = 'fonoTableEN.html'

# Column to extract (contains the URLs and names)
column_name = 'Naam'

# Extract the data from both Dutch and English files
naam_column_data_nl = extract_column_data_with_id(html_file_path_nl, "Naam")
naam_column_data_en = extract_column_data_with_id(html_file_path_en, "Name")
# Combine the data using handshape IDs
combined_data = []
for handshape_id in naam_column_data_nl.keys():
    if handshape_id in naam_column_data_en:
        combined_data.append({
            "id": handshape_id,
            "NL": naam_column_data_nl[handshape_id],
            "EN": naam_column_data_en[handshape_id]
        })

# Output to JSON file
with open('combined_data.json', 'w', encoding='utf-8') as f:
    json.dump(combined_data, f, ensure_ascii=False, indent=4)

# Print or process the extracted data
print(json.dumps(combined_data, indent=4))
