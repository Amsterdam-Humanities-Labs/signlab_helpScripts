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
# import glosSyntaxChecker as gloss_module
import mysql.connector
import logging
import datetime
import pytz
import sys

logging.basicConfig(level=logging.DEBUG)

cookies = {
        'cookie_notification': 'functional',
        'cookies_consent': '-1',
        'sessionid': os.environ.get('SIGNBANK_SESSIONID', ''),
        'csrftoken': os.environ.get('SIGNBANK_CSRFTOKEN', ''),
    }

headers = {
        "Authorization": "Bearer UlerhGrfFpU03RD3",
    }
    
def download_signbank_json():
    
    #we want to remove old flies from signbank folder first
    signbankFolder = "/web/helpScripts/signbank"
    for filename in os.listdir(signbankFolder):
        os.remove(f"{signbankFolder}/{filename}")
    
    #we want to get last time when the function was called
    #so we get json file signBankCSVDownloader.json
    with open("/web/helpScripts/signBankCSVDownloader.json", "r") as file:
        data = json.load(file)
        
    #if the file doesnt have json, then we create new one
    if not data:
        data = []
        #we add service, date and first_today to the file
        data.append({"service": "signBankCSVDownloader", "date": 0, "first_today": time.strftime("")})
        
    
    #then we get the last time when the function was called, if its empty then we set it to 0
    last_time = 0
    print(data)
    for item in data:
        if item["service"] == "signBankCSVDownloader":
            last_time = item["date"]
            first_today = item["first_today"]
            break

    #if first_today has date of today, then we dont set last_time to 0
    #if first_today has date of yesterday, then we set last_time to 0
    if first_today != time.strftime("%Y-%m-%d"):
        last_time = 1262304000 #1 january 2024
    else:
        last_time = datetime.datetime.strptime(str(last_time), '%Y-%m-%d %H:%M:%S %Z')   # last_time_dt -= datetime.timedelta(seconds=30)
        last_time = int(last_time.timestamp())

    
    print(last_time, first_today)
    url = "https://signbank.cls.ru.nl/dictionary/package/?dataset_name=NGT&extended_fields=true&since_timestamp=" + str(last_time)
    print(url)
    r = requests.get(url, cookies=cookies, timeout=3600)
    with open("signbank.zip", "wb") as file:
        file.write(r.content)
    
    try:
        with zipfile.ZipFile("signbank.zip", 'r') as zip_ref:
            zip_ref.extractall(signbankFolder)
    except zipfile.BadZipFile:
        print("Error: Bad zip file. Operation stopped.")
        return  # Stop the operation

    
    # Get the current timestamp
    current_timestamp = time.time()

    # Convert timestamp to datetime object in UTC
    dt_utc = datetime.datetime.fromtimestamp(current_timestamp, tz=datetime.timezone.utc)

    # Convert UTC datetime to Amsterdam time
    dt_amsterdam = dt_utc.astimezone(pytz.timezone('Europe/Amsterdam'))
    amsterdam_time_str = dt_amsterdam.strftime('%Y-%m-%d %H:%M:%S %Z')

    #we also want to update the last time when the function was called
    # Search for an existing entry with the same service name
    found = False
    for entry in data:
        if entry['service'] == "signBankCSVDownloader":
            # Update the date for the existing entry
            entry['date'] = amsterdam_time_str
            found = True
            
            if last_time == 1262304000:
                entry['first_today'] = time.strftime("%Y-%m-%d")
            break
    print(data, last_time)
    #then we write last time to the file
    if not found:
        data.append({"service": "signBankCSVDownloader", "date": last_time})
    
    # Write to JSON file
    with open("/web/helpScripts/signBankCSVDownloader.json", "w") as file:
        json.dump(data, file, indent=4)
        
    print(last_time)
    return last_time
        
    
    
def convert_signbank_json(last_time):
    with open("/web/helpScripts/signbank/glosses.json", "r") as file:
         data = json.load(file)
         
    print(data)
    #we want to make backup of the file with unique name and timestamp
    with open(f"/web/helpScripts/signbank_backups/glosses_{time.strftime('%Y-%m-%d_%H-%M-%S')}.json", "w") as file:
        json.dump(data, file, indent=4)   
    

    #if last_time is 1704067200 then we can just move the json file, otherwise we just convert them
    
    if last_time == 1262304000:
        transformed_data = [{key: value} for key, value in data.items()]
        transformed_json = json.dumps(transformed_data, indent=4)
        with open("/web/glosses_transformed.json", "w") as file:
            file.write(transformed_json)
    else:
        # Transforming the data
        transformed_data = [{key: value} for key, value in data.items()]

        # Converting the transformed data back to JSON
        transformed_json = json.dumps(transformed_data, indent=4)


        # Writing the transformed data to a new file
        with open("/web/helpScripts/signbank/glosses_converted.json", "w") as file:
            file.write(transformed_json)
        print("done")

        # with open("/web/helpScripts/signbank/glosses_converted_test.json", "w") as file:
        #     file.write(transformed_json)
        # print("done")

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
            
    with open("/web/glosses_transformed.json", "r") as file:
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
    with open("/web/glosses_transformed.json", "w") as file:
        json.dump(transformed_data, file, indent=4)
    print("done")



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

def lookupGlos(glos):
    #we open /web/glosses_transformed.json
    with open("/web/glosses_transformed.json", "r") as file:
        data = json.load(file)

    for obj in data:
    # Get the keys of the object (e.g., "3808", "3809", etc.)
        keys = obj.keys()
        if len(keys) > 0:
            key = list(keys)[0]
            # Extract the desired fields from the object
            signbank_id = key
            annotation_id = obj[key].get("Annotation ID Gloss: Dutch")
            if annotation_id == glos:
                #we return glos id
                return signbank_id
    
    
def process_morphology(morphology):
    #we first check if morphology has any value
    if not morphology:
        return json.dumps([])
    # We split the morphology by + sign
    morphologies = morphology.split(" + ")
    # We create a list where we are going to store the morphologies
    morphologies_list = []
    # We loop through the morphologies
    for morph in morphologies:
        # We create a dictionary with glos and id
        lookup_result = lookupGlos(morph)
        morph_dict = {"glos": morph, "id": lookup_result}
        # We append the dictionary to the list
        morphologies_list.append(morph_dict)
    # We should decode to JSON for MySQL
    return json.dumps(morphologies_list)
    
def callAutoUpdate(last_time):
    
    glosses = {}

    # Load JSON data
    if last_time == 1262304000:
        with open("/web/glosses_transformed.json", "r") as file:
            glosses_data = json.load(file)    
    else:
        with open("/web/helpScripts/signbank/glosses_converted.json", "r") as file:
             glosses_data = json.load(file)


    # Function to get glosses from glosses data
    for gloss in glosses_data:
        for gloss_id, gloss_info in gloss.items():
            if gloss_id:
                glosses[gloss_id] = {
                    "gloss_dutch": gloss_info.get("Annotation ID Gloss: Dutch"),
                    "gloss_english": gloss_info.get("Annotation ID Gloss: English"),
                    "senses": gloss_info.get("Senses: Dutch"),
                    "senses_engels": gloss_info.get("Senses: English"),
                    "Handedness": gloss_info.get("Handedness"),
                    "Strong Hand": gloss_info.get("Strong Hand"),
                    "Weak Hand": gloss_info.get("Weak Hand"),
                    "Handshape Change": gloss_info.get("Handshape Change"),
                    "Location": gloss_info.get("Location"),
                    "Relation Between Articulators": gloss_info.get("Relation Between Articulators"),
                    "Relative Orientation: Movement": gloss_info.get("Relative Orientation: Movement"),
                    "Relative Orientation: location": gloss_info.get("Relative Orientation: Location"),
                    "orientation Change": gloss_info.get("Orientation Change"),
                    "Contact Type": gloss_info.get("Contact Type"),
                    "Movement Shape": gloss_info.get("Movement Shape"),
                    "Movement Direction": gloss_info.get("Movement Direction"),
                    "Repeated Movement": gloss_info.get("Repeated Movement"),
                    "Alternating Movement": gloss_info.get("Alternating Movement"),
                    "Virtual Object": gloss_info.get("Virtual Object"),
                    "Phonology Other": gloss_info.get("Phonology Other"),
                    "Mouth Gesture": gloss_info.get("Mouth Gesture"),
                    "Mouthing": gloss_info.get("Mouthing"),
                    "Phonetic Variation": gloss_info.get("Phonetic Variation"),
                    "Sequential Morphology": gloss_info.get("Sequential Morphology"),
                    "Affiliation": gloss_info.get("Affiliation")
                }
                    
                

    # Database connection details
    db_config = {
        'host': 'signlab-db',
        'user': 'user',
        'password': os.environ.get('DB_PASS', ''),
        'database': 'admin_gebarenoverleg'
    }

    # Connect to the MySQL database
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Query to fetch data from form_data table where glosZichtbaar is '0'
    query = "SELECT * FROM form_data WHERE extern IS NULL"
    cursor.execute(query)
    form_data = cursor.fetchall()


        # Then we update glosses from form_data to glosses
    for row in form_data:
        fd_glos = row[6]
        signbank = row[1]
        match_found = False  # Initialize the flag for each row
        # print(signbank)
        if signbank:
            match_found = False  # Initialize the flag for each row
            for gloss_id, gloss_info in glosses.items():
                try:
                    glos = gloss_info.get("gloss_dutch")
                    # print(signbank, gloss_id)

                    if signbank == gloss_id:
                        match_found = True  # Match found
                        print(glos)

                        glos_engels = gloss_info.get("gloss_english")
                        senses = gloss_info.get("senses")
                        senses_engels = gloss_info.get("senses_engels")
                        handeness = gloss_info.get("Handedness")
                        strong_hand = gloss_info.get("Strong Hand")
                        weak_hand = gloss_info.get("Weak Hand")
                        handshape_change = gloss_info.get("Handshape Change")
                        location = gloss_info.get("Location")
                        relation_articulators = gloss_info.get("Relation Between Articulators")
                        rel_orientation_move = gloss_info.get("Relative Orientation: Movement")
                        rel_orientation_loc = gloss_info.get("Relative Orientation: location")
                        orientation_change = gloss_info.get("orientation Change")
                        contact_type = gloss_info.get("Contact Type")
                        movement_shape = gloss_info.get("Movement Shape")
                        movement_direction = gloss_info.get("Movement Direction")
                        repeated_movement = gloss_info.get("Repeated Movement")
                        alternating_movement = gloss_info.get("Alternating Movement")
                        virtual_object = gloss_info.get("Virtual Object")
                        phonology_other = gloss_info.get("Phonology Other")
                        mouth_gesture = gloss_info.get("Mouth Gesture")
                        mouthing = gloss_info.get("Mouthing")
                        phonetic_variation = gloss_info.get("Phonetic Variation")
                        sequential_morphology = process_morphology(gloss_info.get("Sequential Morphology"))
                        origin = gloss_info.get("Affiliation")
                        
                        if not origin:
                            origin = ""
                        else:
                            origin = origin[0]

                        print(glos, gloss_id)
                        
                        #block when handeness is empty
                        if not handeness or handeness == "":
                            #also when sequential_morphology is empty
                            if not sequential_morphology or sequential_morphology == "":
                                continue

                        if isinstance(senses, dict):
                            senses = [s.strip(' "') for s in senses.values()]
                        else:
                            senses = [s.strip(' "') for s in senses] if senses else []
                        senses = json.dumps(senses)

                        if isinstance(senses_engels, dict):
                            senses_engels = [s.strip(' "') for s in senses_engels.values()]
                        else:
                            senses_engels = [s.strip(' "') for s in senses_engels] if senses_engels else []

                        try:
                            if any(value for value in gloss_info.values()):
                                senses_engels = json.dumps(senses_engels)
                                print(glos, signbank, gloss_id, phonology_other)

                                # Update signCollect database with the values from glosses
                                cursor.execute("""
                                    UPDATE form_data 
                                    SET glos = %s, glos_engels = %s, senses = %s, sensesEngels = %s, Handeness = %s, 
                                        strongHand = %s, weakHand = %s, HandshapeChange = %s, handLocation = %s, 
                                        RelationArticulators = %s, relativeOrienationMovement = %s, relativeOrienationLocation = %s, 
                                        orientationChange = %s, ContactType = %s, MovementShape = %s, MovementDirection = %s, 
                                        RepeatedMovement = %s, AlternatingMovement = %s, virtualObjectt = %s, phonologyOther = %s, 
                                        MouthGesture = %s, mouthing = %s, phoneticVariation = %s, morfologie = %s, origin = %s 
                                    WHERE signbank = %s AND extern IS NULL
                                """, (
                                    glos, glos_engels, senses, senses_engels, handeness, strong_hand, weak_hand, handshape_change, 
                                    location, relation_articulators, rel_orientation_move, rel_orientation_loc, orientation_change, 
                                    contact_type, movement_shape, movement_direction, repeated_movement, alternating_movement, 
                                    virtual_object, phonology_other, mouth_gesture, mouthing, phonetic_variation, sequential_morphology, origin, gloss_id 
                                ))

                                connection.commit()
                                
                                logging.info("Update committed successfully.")

                        except Exception as e:
                            logging.error(f"An error occurred during update: {e}")

                except Exception as e:
                    logging.error(f"An error occurred while processing gloss: {e}")

            # After checking all glosses, if no match was found, update glosZichtbaar to 1
        # if last_time == 1262304000:
        #     print("last time is 1262304000")
        #     if not match_found and signbank:
        #         try:
        #             cursor.execute("""
        #                 UPDATE form_data 
        #                 SET glosZichtbaar = 1, signbank = NULL
        #                 WHERE glos = %s
        #             """, (fd_glos,))
        #             connection.commit()
        #             logging.info(f"No matching gloss found for '{fd_glos}'. Set glosZichtbaar=1.")
        #         except Exception as e:
        #             logging.error(f"An error occurred while setting glosZichtbaar=1 for '{fd_glos}': {e}")



    # Close the database connection
    cursor.close()
    connection.close()


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
        
def glosSyntaxCheckerStart():
    glosses = {}

    # Load JSON data
    glosses_data = gloss_module.load_json_data()
    # print(glosses_data)
    # Get glosses from JSON data
    glosses = gloss_module.get_glosses(glosses_data)

    # Fetch glosses from the database
    glosses = gloss_module.fetch_form_data(glosses)

    # Check the gloss syntax and get errors
    errors = gloss_module.check_gloss_syntax(glosses)

    # Output errors to a JSON file
    gloss_module.save_errors(errors)

    print("Syntax check completed. Errors have been output to gloss_syntax_errors.json.")


def download_videos(last_time):
    #we have to download the videos again
    if last_time == 1262304000:
        
        #first we open the json file
        with open("/web/glosses_transformed.json", "r") as file:
            data = json.load(file)
            
        #then we forloop the json file and get Video from it
        for item in data:
            for gloss_id, gloss_info in item.items():
                video = gloss_info.get("Video")
                gloss_name = gloss_info.get("Annotation ID Gloss: Dutch")
                if video:
                    #we download the video
                    r = requests.get(video, cookies=cookies, timeout=3600)
                    with open(f"/web/uploads/{gloss_name}.mp4", "wb") as file:
                        print(f"Downloading {gloss_name}")
                        file.write(r.content)
    
    
    
    
#create lock file to prevent multiple instances of the script
        
# def removeLockFile():
#     os.remove("/web/helpScripts/signBankCSVDownloader.lock")

# # Check if the lock file exists and its age
# lock_file_path = "/web/helpScripts/signBankCSVDownloader.lock"
# if os.path.exists(lock_file_path):
#     lock_file_age = time.time() - os.path.getmtime(lock_file_path)
#     if lock_file_age < 3600:  # 3600 seconds = 1 hour
#         print("The lock file exists and is less than one hour old. Exiting the script.")
#         sys.exit()
#     else:
#         print("The lock file is older than one hour. Removing the lock file and continuing.")
        
#         #create new lock file and put the time in it
#         with open(lock_file_path, "w") as file:
#             file.write(time.strftime("%Y-%m-%d %H:%M:%S"))    
# else:
#     with open(lock_file_path, "w") as file:
#             file.write(time.strftime("%Y-%m-%d %H:%M:%S"))   

last_time = 0
# last_time = 1262304000
last_time = download_signbank_json()
convert_signbank_json(last_time)
if last_time != 1262304000:
    update_signbank_json()

# callAutoUpdate(last_time)
# download_videos(last_time)

countSignbank("/web/glosses_transformed.json", "/web/helpScripts/signbank_field_counts.json")
#when the script is done, we we remove the lock file
# removeLockFile()
