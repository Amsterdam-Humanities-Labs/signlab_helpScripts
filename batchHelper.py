import os
import mysql.connector
import json
import requests
import time

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
query = "SELECT * FROM form_data WHERE glosZichtbaar='0'"
cursor.execute(query)
form_data = cursor.fetchall()

# Count the number of records
total_records = len(form_data)
signbankCounter = 0

# Load JSON data
with open('/web/glosses_transformed.json', 'r') as file:
    glosses_data = json.load(file)

# Function to get senses from glosses data
def get_gloss_senses(glosses_data):
    gloss_senses = {}
    for gloss in glosses_data:
        for gloss_id, gloss_info in gloss.items():
            senses_dutch = list(gloss_info.get("Senses: Dutch", {}).values())
            senses_english = list(gloss_info.get("Senses: English", {}).values())
            annotation_dutch = gloss_info.get("Annotation ID Gloss: Dutch")
            gloss_senses[gloss_id] = {
                "senses_dutch": senses_dutch,
                "senses_english": senses_english,
                "annotation_dutch": annotation_dutch
            }
    return gloss_senses

gloss_senses = get_gloss_senses(glosses_data)

# Get column names from the cursor
columns = cursor.column_names

# Extract necessary column indices
signbank_idx = columns.index('signbank')
senses_idx = columns.index('senses')
senses_engels_idx = columns.index('sensesEngels')
overwriteCounter = 0

# Compare the data and display information
for row in form_data:
    signbank = row[signbank_idx]
    senses = row[senses_idx]
    senses_engels = row[senses_engels_idx]

    if signbank:
        signbankCounter += 1

        gloss_info = gloss_senses.get(str(signbank), {})
        gloss_senses_dutch = gloss_info.get("senses_dutch", [])
        gloss_senses_english = gloss_info.get("senses_english", [])
        gloss = gloss_info.get("annotation_dutch", "")

        if senses:
            # Convert string senses and gloss_senses_dutch into arrays
            senses_list = json.loads(senses)
            
            if senses_engels:
                senses_engels_list = json.loads(senses_engels)
            else:
                senses_engels_list = []

            # Calculate lengths
            senses_length = len(senses_list)
            senses_engels_length = len(senses_engels_list)
            gloss_senses_dutch_length = len(gloss_senses_dutch)
            gloss_senses_english_length = len(gloss_senses_english)

            # Determine if signCollect overwrites Signbank or do nothing
            overwriteSignbank = False
            # if gloss_senses_dutch_length == 0:
            #     if senses_length > gloss_senses_dutch_length:
            #         overwriteSignbank = True
            
            #senses and senses english must have same lengths
            # if senses_length == senses_engels_length:
            #     if gloss_senses_dutch_length != senses_length:
            #         overwriteSignbank = True
            
            if senses_engels_length == 0 and gloss_senses_english_length == 0:

                if senses_length == 0 and gloss_senses_dutch_length == 0:
                    
                    if senses_length == gloss_senses_dutch_length:
                        overwriteSignbank = False
                    else:
                        overwriteSignbank = True
            
                
            if overwriteSignbank:
                print(f"Signbank ID: {signbank}")
                print(f"Signbank Gloss: {gloss}")
                print(f"signCollect Senses: {senses_list}")
                print(f"signCollect Senses Length: {senses_length}")
                print(f"signCollect Senses Engels: {senses_engels_list}")
                print(f"signCollect Senses Engels Length: {senses_engels_length}")
                print(f"Signbank Dutch: {gloss_senses_dutch}")
                print(f"Signbank Dutch Length: {gloss_senses_dutch_length}")
                print(f"Signbank English: {gloss_senses_english}")
                print(f"Signbank English Length: {gloss_senses_english_length}")
                print("------------")
                
                
                # senses = [[item] for item in senses_list]
                # senses_engels = [[item] for item in senses_engels_list]
                # payload = {
                #     'glossid': signbank,
                #     "Senses: Dutch": senses,
                #     "Senses: English": senses_engels
                # }

                # print("Payload to be sent:", json.dumps(payload, indent=2))

                # # Send POST request with SSL verification disabled
                # response = requests.post(
                #     "https://leffe.science.uva.nl:8043/signBankAPI/update_gloss",
                #     data=json.dumps(payload),
                #     headers={'Content-Type': 'application/json'},
                #     verify=False
                # )
                # print(response.text[:5000])  # Limit the output to the first 5000 characters
                
                # #sleep for one sec 
                # time.sleep(1)
                
                
                

                # Ask user if they want to overwrite signbank with signcollect or vice versa
                choice = input("Press 'c' to overwrite Signbank with Signcollect values, 's' for the opposite, or any other key to skip: ").strip().lower()
                if choice == 's':
                    
                    gloss_senses_dutch = [[item] for item in gloss_senses_dutch]
                    gloss_senses_english = [[item] for item in gloss_senses_english]

                    print(gloss_senses_dutch, gloss_senses_english)
                    # Overwrite signbank with signcollect values
                    cursor.execute(
                        "UPDATE form_data SET senses = %s, sensesEngels = %s WHERE signbank = %s",
                        (json.dumps(gloss_senses_dutch), json.dumps(gloss_senses_english), signbank)
                    )
                    print(connection.commit())

                    print(f"Signbank ID {signbank} updated with Signcollect values.")
                elif choice == 'c':
                      # Prepare payload
                    senses = [[item] for item in senses_list]
                    senses_engels = [[item] for item in senses_engels_list]
                    payload = {
                        'glossid': signbank,
                        "Senses: Dutch": senses,
                        "Senses: English": senses_engels
                    }

                    print("Payload to be sent:", json.dumps(payload, indent=2))

                    # Send POST request with SSL verification disabled
                    response = requests.post(
                        "https://leffe.science.uva.nl:8043/signBankAPI/update_gloss",
                        data=json.dumps(payload),
                        headers={'Content-Type': 'application/json'},
                        verify=False
                    )
                    print(response.text[:5000])  # Limit the output to the first 5000 characters
                else:
                    print(f"No changes made for Signbank ID {signbank}.")

                overwriteCounter += 1

# Print counts
print(f"Total records in form_data: {total_records}")
print(f"Records with signbank ID: {signbankCounter}")
print(f"Records to check: {overwriteCounter}")

# Close the cursor and connection
cursor.close()
connection.close()
