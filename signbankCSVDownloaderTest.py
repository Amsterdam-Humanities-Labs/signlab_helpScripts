


#download signbank JSON format every hour from this url: https://signbank.cls.ru.nl/dictionary/package/?extended_fields=true
#after downloading it, unzip the file
#then convert JSON with function to adapted JSON format


import json
import requests
import zipfile
import os
import time
import urllib3
from requests.packages.urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)
from collections import defaultdict
import time

cookies = {
        'cookie_notification': 'functional',
        'cookies_consent': '-1',
        'sessionid': os.environ.get('SIGNBANK_SESSIONID', ''),
        'csrftoken': os.environ.get('SIGNBANK_CSRFTOKEN', ''),
    }
    
def download_signbank_json():
    
    current_time = time.time()

    # Subtract 30 minutes (1800 seconds) from the current time
    half_hour_ago = current_time - 300

    url = "https://signbank.cls.ru.nl/dictionary/package/?extended_fields=true&since_timestamp=" + str(int(half_hour_ago))
    print(url)


    r = requests.get(url, cookies=cookies)
    with open("signbank.zip", "wb") as file:
        file.write(r.content)
    with zipfile.ZipFile("signbank.zip", 'r') as zip_ref:
        zip_ref.extractall("signbank")
    os.remove("signbank.zip")
    
    
def convert_signbank_json():
    with open("/web/helpScripts/signbank/glosses.json", "r") as file:
         data = json.load(file)

    # Transforming the data
    transformed_data = [{key: value} for key, value in data.items()]

    # Converting the transformed data back to JSON
    transformed_json = json.dumps(transformed_data, indent=4)


    # Writing the transformed data to a new file
    with open("/web/helpScripts/signbank/glosses_converted.json", "w") as file:
        file.write(transformed_json)
    print("done")
    
    #we also want to convert deleted glosses
    with open("/web/helpScripts/signbank/deleted_glosses.json", "r") as file:
        data = json.load(file)
            
    # Transforming the data
    transformed_data = [{"id": item[0], "name": item[1]} for item in data]

    # Converting the transformed data back to JSON
    transformed_json = json.dumps(transformed_data, indent=4)
    
    
    with open("/web/helpScripts/signbank/deleted_converted_glosses.json", "w") as file:
        file.write(transformed_json)
    
def update_signbank_json():
    with open("/web/helpScripts/signbank/glosses_converted.json", "r") as file:
        data = json.load(file)
    
    with open("/web/helpScripts/test/glosses_transformed_test.json", "r") as file:
        transformed_data = json.load(file)
        
    with open("/web/helpScripts/signbank/deleted_converted_glosses.json", "r") as file:
        deleted_data = json.load(file)
        
        
    #now we want to update glosses_transformed.json with glosses_converted.json
    for item in data:
        for item2 in transformed_data:
            if list(item.keys())[0] == list(item2.keys())[0]:
                item2[list(item.keys())[0]] = item[list(item.keys())[0]]
                
    #then we look for deleted glosses and remove them from glosses_transformed.json
    for item in deleted_data:
        for item2 in transformed_data:
            if list(item.values())[0] == list(item2.keys())[0]:
                print(list(item.values())[0], list(item2.keys())[0])
                print("found")
                transformed_data.remove(item2)
    
    # Writing the transformed data to a new file
    with open("/web/helpScripts/test/glosses_transformed_test.json", "w") as file:
        json.dump(transformed_data, file, indent=4)
    print("done")
    


def updateFormData():
    # Load the JSON data from the file
    with open("/web/test/glosses_transformed.json", "r") as file:
        data = json.load(file)

    # Iterate through each item in the JSON data
    for itema in data:
        for itemp, item in itema.items():
            # Initialize all the necessary variables for the current item
            #  if item.get("Annotation ID Gloss: Dutch") == "AARDAPPEL-A":
                
                handedness = item.get("Handedness", "")
                strong_hand = item.get("Strong Hand", "")
                weak_hand = item.get("Weak Hand", "")
                handshape_change = item.get("Handshape Change", "")
                hand_location = item.get("Location", "")
                relation_articulators = item.get("Relation Between Articulators", "")
                rel_orientation_move = item.get("Relative Orientation: Movement", "")
                rel_orientation_loc = item.get("Relative Orientation: Location", "")
                orientation_change = item.get("Orientation Change", "")
                contact_type = item.get("Contact Type", "")
                movement_shape = item.get("Movement Shape", "")
                movement_direction = item.get("Movement Direction", "")
                repeated_movement = item.get("Repeated Movement", "")
                alternating_movement = item.get("Alternating Movement", "")
                senses = item.get("Senses: Dutch", "")
                glos = item.get("Annotation ID Gloss: Dutch", "")
                glos_engels = item.get("Annotation ID Gloss: English", "")
                signbank_id = itemp

                # Convert senses from array to string
                senseString = []
                

                if isinstance(senses, dict):
                    # If senses is a dictionary, iterate over its items
                    for key, value in senses.items():
                        senseString = [value]
                elif isinstance(senses, list):
                    # If senses is a list, iterate over its elements
                    for value in senses:
                        senseString = [value]

                # Prepare the formData dictionary
                formData = {
                    'glos': glos,
                    'signbank': itemp,
                    'glos_engels': glos_engels
                }
                # Prepare the requestData dictionary for the GET request
                #check if glos is not empty
                #trim the glos
                glos = glos.strip()
                if glos != "":
                    
                    requestData = {'glos': glos}

                    #print(glos)
                    try:
                        formData = json.dumps(formData)

                        update_url = "https://leffe.science.uva.nl:8043/update_field.php"
                        update_response = requests.post(update_url, data={'updatedData': formData}, verify=False)
                        print(update_response.text)
                        
                        # if check_response_data['status'] == "notfound":
                        #     print(check_response_data.message)
                        

                        

                    except requests.exceptions.RequestException as e:
                        # Handle any errors that occur during the HTTP requests
                        print(f"HTTP Request failed: {e}")


def countSignbank(filepath, output_filepath):
    # Load the JSON data
    with open(filepath, 'r') as file:
        data = json.load(file)
    
    fields = [
        'Weak Hand', 'Handshape Change', 'Relation Between Articulators',
        'Location', 'Contact Type', 'Movement Shape', 'Movement Direction',
        'Relative Orientation: Movement', 'Relative Orientation: Location',
        'Orientation Change', 'Repeated Movement', 'Alternating Movement',
        'Virtual Object', 'Phonology Other', 'Mouth Gesture', 'Mouthing',
        'Phonetic Variation', 'Handedness', 'Strong Hand'
    ]
    
    # Count occurrences of each unique value for specified fields
    counts = defaultdict(lambda: defaultdict(int))
    for item in data:
        gloss_data = next(iter(item.values()))
        for field in fields:
            value = gloss_data.get(field)
            if value:
                counts[field][value] += 1

    # Write the counts to a new JSON file
    with open(output_filepath, 'w') as file:
        json.dump(counts, file, indent=4)
        
def callAutoUpdate():
    #here we are going to call autoUpdater.php 
    url = "https://leffe.science.uva.nl:8043/helpScripts/autoUpdater.php"
    try:
        r = requests.get(url, verify=False)
        # print(r.text)
    except requests.RequestException as e:
        print(f"Error calling autoUpdater.php: {e}")

def writeToJson():
    file_path = "/web/servicesRecords.json"
    
    # Load the JSON data from the file
    with open(file_path, "r") as file:
        data = json.load(file)
    
    # Define the service name
    service_name = "signBankCSVDownloader"
    
    # Search for an existing entry with the same service name
    found = False
    for entry in data:
        if entry['service'] == service_name:
            # Update the date for the existing entry
            entry['date'] = time.strftime("%Y-%m-%d %H:%M:%S")
            found = True
            break
    
    # If no existing entry found, append a new one
    if not found:
        data.append({"service": service_name, "date": time.strftime("%Y-%m-%d %H:%M:%S")})
    
    # Write to JSON file
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
        
download_signbank_json()
convert_signbank_json()
update_signbank_json()
# countSignbank("/web/glosses_transformed.json", "/web/helpScripts/signbank_field_counts.json")
# callAutoUpdate()
# download_videos()
# updateFormData()
        
