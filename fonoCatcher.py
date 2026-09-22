import requests
from bs4 import BeautifulSoup
import json
import time

def writeToJson():
    file_path = "/web/servicesRecords.json"
    
    # Load the JSON data from the file
    with open(file_path, "r") as file:
        data = json.load(file)
    
    # Define the service name
    service_name = "fonoCatcher"
    
    # Search for an existing entry with the same service name
    found = False
    for entry in data:
        if entry['service'] == service_name:
            # Update the date for the existing entry
            entry['date'] = time.strftime("%Y-%m-%d %H:%M:%S")
            found = True
            print(entry)
            break
    
    # If no existing entry found, append a new one
    if not found:
        data.append({"service": service_name, "date": time.strftime("%Y-%m-%d %H:%M:%S")})
    
    # Write to JSON file
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
        
        
def scrape_select_options(url, select_ids, language):
    headers = {
        'Cookie': f'django_language={language}; Path=/'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    selects_data = {}
    
    for select_id in select_ids:
        select = soup.find('select', id=select_id)
        if select:
            options = select.find_all('option')
            options_list = [{"value": option['value'], "name": option.text.strip()} for option in options]
            
            #convert the select_id to select_convert
            if select_id in select_convert:
                select_id = select_convert[select_id]
            selects_data[select_id] = options_list
            
    
    
    return selects_data

def save_to_json(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

# List of select IDs you want to scrape
select_ids = [
    "id_handedness", "id_domhndsh", "id_subhndsh",
    "id_handCh", "id_relatArtic", "id_locprim", "id_contType", "id_movSh", "id_movDir",
    "id_repeat", "id_altern", "id_relOriMov", "id_relOriLoc", "id_oriCh"
]
select_convert = {
    "id_handedness" : "Handeness",
    "id_domhndsh" : "strongHand",
    "id_subhndsh" : "weakHand",
    "id_handCh" : "HandshapeChange",
    "id_relatArtic" : "RelationArticulators",
    "id_locprim" : "handLocation",
    "id_contType" : "ContactType",
    "id_movSh" : "MovementShape",
    "id_movDir" : "MovementDirection",
    "id_repeat" : "RepeatedMovement",
    "id_altern" : "AlternatingMovement",
    "id_relOriMov" : "relativeOrienationMovement",
    "id_relOriLoc" : "relativeOrienationLocation",
    "id_oriCh" : "orientationChange"}


# URL of the page to scrape
url = "https://signbank.cls.ru.nl/signs/search/"

# Scrape the data for "en" language
select_data_en = scrape_select_options(url, select_ids, "en")
# Save data to JSON
save_to_json(select_data_en, '/web/helpScripts/selects_data_en.json')

# Scrape the data for "nl" language
select_data_nl = scrape_select_options(url, select_ids, "nl")
# Save data to JSON
save_to_json(select_data_nl, '/web/helpScripts/selects_data_nl.json')

# Assuming select_data_nl and select_data_en are already defined

combined_data = {}
# Iterate over each select field
for key in select_data_nl:
    if key in select_data_en:  # Ensure the key exists in the English data as well
        combined_options = []
        # Iterate over options in the Dutch data
        for nl_option in select_data_nl[key]:
            # Find the corresponding English option
            en_option = next((item for item in select_data_en[key] if item["value"] == nl_option["value"]), None)
            if en_option:  # Ensure that a matching English option was found
                # Create new dict for combined info
                combined_option = {
                    "value": nl_option["value"],
                    "NL": nl_option["name"],
                    "EN": en_option["name"]
                }
                combined_options.append(combined_option)
        combined_data[key] = combined_options

# Save the combined data to a JSON file
save_to_json(combined_data, '/web/helpScripts/selects_data_combined.json')