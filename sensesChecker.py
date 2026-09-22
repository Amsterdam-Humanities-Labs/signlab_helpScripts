import os
import json
import mysql.connector
# Load JSON data
with open('/web/glosses_transformed.json', 'r') as file:
    glosses_data = json.load(file)

gloss_senses = {}
check_list = {}

# Function to get senses from glosses data
def get_gloss_senses(glosses_data):
    for gloss in glosses_data:
        for gloss_id, gloss_info in gloss.items():
            senses_dutch = list(gloss_info.get("Senses: Dutch", {}).values())
            senses_english = list(gloss_info.get("Senses: English", {}).values())
            annotation_dutch = gloss_info.get("Annotation ID Gloss: Dutch")
            
            
            gloss_senses[gloss_id] = {
                "senses_dutch": senses_dutch,
                "senses_english": senses_english,
                "annotation_dutch": annotation_dutch,
                "Affiliation": gloss_info.get("Affiliation") 
            }
    return gloss_senses

get_gloss_senses(glosses_data)

for gloss_id, gloss_info in gloss_senses.items():
    senses_dutch = gloss_info.get("senses_dutch")
    senses_english = gloss_info.get("senses_english")
    annotation_dutch = gloss_info.get("annotation_dutch")
    affiliation = gloss_info.get("Affiliation")
    
    # We want to check if senses_english or senses_dutch are not empty, otherwise add to check_list
    if not senses_dutch and not senses_english:
        check_list[gloss_id] = {
            "senses_dutch": senses_dutch,
            "senses_english": senses_english,
            "annotation_dutch": annotation_dutch,
            "reason": "No English and Dutch senses",
            "Affiliation": affiliation
        }
    elif not senses_dutch:
        check_list[gloss_id] = {
            "senses_dutch": senses_dutch,
            "senses_english": senses_english,
            "annotation_dutch": annotation_dutch,
            "reason": "No Dutch senses",
            "Affiliation": affiliation
        }
    elif not senses_english:
        check_list[gloss_id] = {
            "senses_dutch": senses_dutch,
            "senses_english": senses_english,
            "annotation_dutch": annotation_dutch,
            "reason": "No English senses",
            "Affiliation": affiliation
        }
        
#now we want to lookup signcollect database if there are values in senses and sensesenglish
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


# Get column names from the cursor
columns = cursor.column_names

# Extract necessary column indices
signbank_idx = columns.index('signbank')
senses_idx = columns.index('senses')
senses_engels_idx = columns.index('sensesEngels')

for gloss_id, gloss_info in check_list.items():
    for row in form_data:
        signbank = row[signbank_idx]
        senses = row[senses_idx]
        senses_engels = row[senses_engels_idx]
        
        if gloss_id == signbank:
            check_list[gloss_id] = {
                "senses_dutch": gloss_info.get("senses_dutch"),
                "senses_english": gloss_info.get("senses_english"),
                "annotation_dutch": gloss_info.get("annotation_dutch"),
                "reason": "No English and Dutch senses",
                "sc_senses": senses,
                "sc_senses_engels": senses_engels,
                "action": "overwrite_signbank_senses"
            }

# Write to JSON file
with open('/web/senses_check.json', 'w') as file:
    json.dump(check_list, file, indent=4)
