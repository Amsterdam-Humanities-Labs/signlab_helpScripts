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

# Load JSON data
with open('/web/glosses_transformed.json', 'r') as file:
    glosses_data = json.load(file)

# Function to get senses from glosses data
def get_origin(glosses_data):
    gloss_senses = {}
    for gloss in glosses_data:
        for gloss_id, gloss_info in gloss.items():
            Affiliation = gloss_info.get("Affiliation")
            gloss_senses[gloss_id] = {
                "Affiliation": Affiliation,
            }
    return gloss_senses


gloss_senses = get_origin(glosses_data)


params = []

for item, data in gloss_senses.items():
    affiliation = data.get("Affiliation", "")
    if not affiliation:
        continue

    print(item)
    print(data)
    print("\n")
    params.append((affiliation[0], item))

if params:
    query = "UPDATE form_data SET `origin` = %s WHERE `signbank` = %s"
    cursor.executemany(query, params)
    connection.commit()
    print(len(params), "record(s) affected")
    print("\n")