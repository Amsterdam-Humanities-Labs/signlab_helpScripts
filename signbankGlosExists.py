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

logging.basicConfig(level=logging.DEBUG)


def callAutoUpdate():
    
    glosses = {}

    # Load JSON data
    with open("/web/glosses_transformed.json", "r") as file:
        glosses_data = json.load(file)
    # with open("/web/glosses_transformed.json", "r") as file:
    #     glosses_data = json.load(file)

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
                    "Phonology: Other": gloss_info.get("Phonology: Other"),
                    "Mouth Gesture": gloss_info.get("Mouth Gesture"),
                    "Mouthing": gloss_info.get("Mouthing"),
                    "Phonetic Variation": gloss_info.get("Phonetic Variation"),
                    "Sequential Morphology": gloss_info.get("Sequential Morphology")
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
    query = "SELECT * FROM form_data WHERE glosZichtbaar='0'"
    cursor.execute(query)
    form_data = cursor.fetchall()


    # Then we update glosses from form_data to glosses
    for row in form_data:
        signbank = row[1]
        
        if signbank:
            for gloss_id, gloss_info in glosses.items():

                
                if signbank == gloss_id:
                    glos = gloss_info.get("gloss_dutch")
                    print(glos)

                    # if glos != "GEBAK":
                    #     continue
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
                    phonology_other = gloss_info.get("Phonology: Other")
                    mouth_gesture = gloss_info.get("Mouth Gesture")
                    mouthing = gloss_info.get("Mouthing")
                    phonetic_variation = gloss_info.get("Phonetic Variation")
                    sequential_morphology = process_morphology(gloss_info.get("Sequential Morphology"))
                    # sequential_morphology = gloss_info.get("Sequential Morphology")
                    
                    print(glos)
                    
                    if isinstance(senses, dict):
                        senses = [s.strip(' "') for s in senses.values()]
                    else:
                        senses = [s.strip(' "') for s in senses] if senses else []   
                    senses = json.dumps(senses)
                        
                        # Convert sb_senses_engels from dict to list and strip
                    if isinstance(senses_engels, dict):
                        senses_engels = [s.strip(' "') for s in senses_engels.values()]
                    else:
                        senses_engels = [s.strip(' "') for s in senses_engels] if senses_engels else []   
                        
                    #first we check if there is at least one value filled in gloss_info
                    #if there is at least one value, then commit the update, otherwise skip this glos
                    try:
                        if any(value for value in gloss_info.values()):
                            senses_engels = json.dumps(senses_engels)
                            print(glos, signbank)
                            
                            # Update signCollect database with the values from glosses
                            cursor.execute("""
                                UPDATE form_data 
                                SET glos = %s, glos_engels = %s, senses = %s, sensesEngels = %s, Handeness = %s, 
                                    strongHand = %s, weakHand = %s, HandshapeChange = %s, handLocation = %s, 
                                    RelationArticulators = %s, relativeOrienationMovement = %s, relativeOrienationLocation = %s, 
                                    orientationChange = %s, ContactType = %s, MovementShape = %s, MovementDirection = %s, 
                                    RepeatedMovement = %s, AlternatingMovement = %s, virtualObjectt = %s, PhonologyOther = %s, 
                                    MouthGesture = %s, mouthing = %s, phoneticVariation = %s, morfologie = %s 
                                WHERE signbank = %s
                            """, (glos, glos_engels, senses, senses_engels, handeness, strong_hand, weak_hand, handshape_change, 
                                location, relation_articulators, rel_orientation_move, rel_orientation_loc, orientation_change, 
                                contact_type, movement_shape, movement_direction, repeated_movement, alternating_movement, 
                                virtual_object, phonology_other, mouth_gesture, mouthing, phonetic_variation, sequential_morphology, signbank 
                                ))
                            
                            connection.commit()
                            logging.info("Update committed successfully.")

                    except Exception as e:
                        logging.error(f"An error occurred: {e}")
                        connection.rollback()



    # Close the database connection
    cursor.close()
    connection.close()