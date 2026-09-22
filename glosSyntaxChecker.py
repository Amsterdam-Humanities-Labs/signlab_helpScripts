import os
import json
import re
import mysql.connector

glosses = {}

# Load JSON data
with open('/web/glosses_transformed.json', 'r') as file:
    glosses_data = json.load(file)

# Function to get glosses from glosses data
def get_glosses(glosses_data):
    for gloss in glosses_data:
        for gloss_id, gloss_info in gloss.items():
            gloss_dutch = gloss_info.get("Annotation ID Gloss: Dutch")
            Affiliation = gloss_info.get("Affiliation") #     "Affiliation": [ "Radboud"]
            print(Affiliation)
            #check if Affiliation first value is UvA
            #also check first if there is more than 1 items in Affiliation
            # if len(Affiliation) > 0:
            #     if Affiliation[0] == "UvA":
            if gloss_dutch:
                glosses[gloss_dutch] = gloss_id
    return glosses


#we also want to add glosses from mysql database form_data

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

#then we add glosses from form_data to glosses
for row in form_data:
    gloss_dutch = row[6]
    glosses[gloss_dutch] = row[1]


glosses = get_glosses(glosses_data)

for glos in glosses:
    print(glos)

# Function to check the syntax of glosses
def check_gloss_syntax(glosses):
    errors = []
    base_glosses = {}

    # Regex to identify glosses with a hyphen followed by a single letter at the end
    pattern = re.compile(r'-[A-Z]$')

    for gloss in glosses:
        if pattern.search(gloss):
            base, suffix = gloss.rsplit('-', 1)
            if base not in base_glosses:
                base_glosses[base] = []
            base_glosses[base].append(suffix)
        else:
            if gloss not in base_glosses:
                base_glosses[gloss] = []

    for base, suffixes in base_glosses.items():
        if suffixes:
            sorted_suffixes = sorted(suffixes)
            expected_suffixes = [chr(i) for i in range(ord('A'), ord('A') + len(suffixes))]
            if sorted_suffixes != expected_suffixes:
                error = {
                    "base_gloss": base,
                    "found_suffixes": sorted_suffixes,
                    "expected_suffixes": expected_suffixes,
                    "reason": f"Expected sequential suffixes {expected_suffixes} but found {sorted_suffixes}"
                }
                errors.append(error)

            # Check for incorrect suffixes without corresponding base or base-A
            for suffix in ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']:
                suffixed_gloss = f"{base}-{suffix}"
                if suffixed_gloss in glosses:
                    if f"{base}" not in glosses and f"{base}-A" not in glosses:
                        error = {
                            "incorrect_gloss": suffixed_gloss,
                            "suggested_gloss": base,
                            "reason": f"Gloss '{suffixed_gloss}' does not have a corresponding '{base}' or '{base}-A'. Suggest changing to '{base}'."
                        }
                        errors.append(error)
    
    return errors

# Check the gloss syntax and get errors
errors = check_gloss_syntax(glosses)

# Output errors to a JSON file
with open('/web/gloss_syntax_errors.json', 'w') as error_file:
    json.dump(errors, error_file, indent=4)

print("Syntax check completed. Errors have been output to gloss_syntax_errors.json.")
