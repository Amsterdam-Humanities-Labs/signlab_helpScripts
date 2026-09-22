import os
import json
import mysql.connector
# Load JSON data
with open('/web/glosses_transformed.json', 'r') as file:
    glosses_data = json.load(file)

gloss_fono = {}
check_list = {}

# Function to get senses from glosses data
def get_gloss_fono(glosses_data):
    for gloss in glosses_data:
        for gloss_id, gloss_info in gloss.items():
            glossId = gloss_id
            handedness = gloss_info.get("Handedness")
            strong_hand = gloss_info.get("Strong Hand")
            weak_hand = gloss_info.get("Weak Hand")
            handshape_change = gloss_info.get("Handshape Change")
            hand_location = gloss_info.get("Location")
            relation_articulators = gloss_info.get("Relation Between Articulators")
            rel_orientation_move = gloss_info.get("Relative Orientation: Movement")
            rel_orientation_loc = gloss_info.get("Relative Orientation: Location")
            orientation_change = gloss_info.get("Orientation Change")
            contact_type = gloss_info.get("Contact Type")
            movement_shape = gloss_info.get("Movement Shape")
            movement_direction = gloss_info.get("Movement Direction")
            repeated_movement = gloss_info.get("Repeated Movement")
            alternating_movement = gloss_info.get("Alternating Movement")
            annotation_dutch = gloss_info.get("Annotation ID Gloss: Dutch")
            simultaneous_morphology = gloss_info.get("Simultaneous Morphology")
            blend_morphology = gloss_info.get("Blend Morphology")
            sequental_morphology = gloss_info.get("Sequential Morphology")
            affilation = gloss_info.get("Affiliation")

            #get first item of affilation list, but first check if it is a list
            #also check if affilation is not empty
            if affilation:
                if isinstance(affilation, list):
                    affilation = affilation[0]
                else:
                    affilation = affilation
                                            
            gloss_fono[gloss_id] = {
                "glossId": glossId,
                "annotation_dutch": annotation_dutch,
                "Handedness": handedness,
                "Strong Hand": strong_hand,
                "Weak Hand": weak_hand,
                "Handshape Change": handshape_change,
                "Location": hand_location,
                "Relation Between Articulators": relation_articulators,
                "Relative Orientation: Movement": rel_orientation_move,
                "Relative Orientation: location": rel_orientation_loc,
                "orientation Change": orientation_change,
                "Contact Type": contact_type,
                "Movement Shape": movement_shape,
                "Movement Direction": movement_direction,
                "Repeated Movement": repeated_movement,
                "Alternating Movement": alternating_movement,
                "Simultaneous Morphology": simultaneous_morphology,
                "Blend Morphology": blend_morphology,
                "Sequential Morphology": sequental_morphology,
                "Affiliation": affilation
                
            }
    return gloss_fono

get_gloss_fono(glosses_data)

for gloss_id, gloss_info in gloss_fono.items():
    glossId = gloss_info.get("glossId")
    annotation_dutch = gloss_info.get("annotation_dutch")
    handeness = gloss_info.get("Handedness")
    strong_hand = gloss_info.get("Strong Hand")
    weak_hand = gloss_info.get("Weak Hand")
    handshape_change = gloss_info.get("Handshape Change")
    hand_location = gloss_info.get("Location")
    relation_articulators = gloss_info.get("Relation Between Articulators")
    rel_orientation_move = gloss_info.get("Relative Orientation: Movement")
    rel_orientation_loc = gloss_info.get("Relative Orientation: Location")
    orientation_change = gloss_info.get("Orientation Change")
    contact_type = gloss_info.get("Contact Type")
    movement_shape = gloss_info.get("Movement Shape")
    movement_direction = gloss_info.get("Movement Direction")
    repeated_movement = gloss_info.get("Repeated Movement")
    alternating_movement = gloss_info.get("Alternating Movement")
    simultaneous_morphology = gloss_info.get("Simultaneous Morphology")
    blend_morphology = gloss_info.get("Blend Morphology")
    sequental_morphology = gloss_info.get("Sequential Morphology")
    affilation = gloss_info.get("Affiliation")
            
        
   #we want to check if at least one value is filled in, otherwise add to check_list
    if not handeness:
        if not simultaneous_morphology and not blend_morphology and not sequental_morphology:
            check_list[gloss_id] = {
                "glossId": glossId,
                "annotation_dutch": annotation_dutch,
                "Handeness": handeness,
                "Strong Hand": strong_hand,
                "Weak Hand": weak_hand,
                "Handshape Change": handshape_change,
                "Location": hand_location,
                "Relation Between Articulators": relation_articulators,
                "Relative Orientation: Movement": rel_orientation_move,
                "Relative Orientation: location": rel_orientation_loc,
                "orientation Change": orientation_change,
                "Contact Type": contact_type,
                "Movement Shape": movement_shape,
                "Movement Direction": movement_direction,
                "Repeated Movement": repeated_movement,
                "Alternating Movement": alternating_movement,
                "Simultaneous Morphology": simultaneous_morphology,
                "Blend Morphology": blend_morphology,
                "Sequential Morphology": sequental_morphology,
                "reason": "Handeness not filled in",
                "Affiliation": affilation
            }
        
    
        
# #now we want to lookup signcollect database if there are values in senses and sensesenglish
# # Database connection details
# db_config = {
#     'host': 'signlab-db',
#     'user': 'user',
#     'password': os.environ.get('DB_PASS', ''),
#     'database': 'admin_gebarenoverleg'
# }

# # Connect to the MySQL database
# connection = mysql.connector.connect(**db_config)
# cursor = connection.cursor()

# # Query to fetch data from form_data table where glosZichtbaar is '0'
# query = "SELECT * FROM form_data WHERE glosZichtbaar='0'"
# cursor.execute(query)
# form_data = cursor.fetchall()


# # Get column names from the cursor
# columns = cursor.column_names

# # Extract necessary column indices
# signbank_idx = columns.index('signbank')
# senses_idx = columns.index('senses')
# senses_engels_idx = columns.index('sensesEngels')

# for gloss_id, gloss_info in check_list.gloss_infos():
#     for row in form_data:
#         signbank = row[signbank_idx]
#         senses = row[senses_idx]
#         senses_engels = row[senses_engels_idx]
        
#         if gloss_id == signbank:
#             check_list[gloss_id] = {
#                 "senses_dutch": gloss_info.get("senses_dutch"),
#                 "senses_english": gloss_info.get("senses_english"),
#                 "annotation_dutch": gloss_info.get("annotation_dutch"),
#                 "reason": "No English and Dutch senses",
#                 "sc_senses": senses,
#                 "sc_senses_engels": senses_engels,
#                 "action": "overwrite_signbank_senses"
            # }

# Write to JSON file
with open('/web/fono_check.json', 'w') as file:
    json.dump(check_list, file, indent=4)
