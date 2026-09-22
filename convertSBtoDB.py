import os
import json
import mysql.connector
from mysql.connector import Error

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'user',
    'password': os.environ.get('DB_PASS', ''),
    'database': 'admin_gebarenoverleg'
}

def create_table(cursor):
    # SQL query to create the table with proper indexes
    create_table_query = """
    CREATE TABLE IF NOT EXISTS sb_records (
        id INT PRIMARY KEY,
        lemma_id_gloss_dutch VARCHAR(255),
        lemma_id_gloss_english VARCHAR(255),
        annotation_id_gloss_dutch VARCHAR(255),
        annotation_id_gloss_english VARCHAR(255),
        senses_dutch JSON,
        senses_english JSON,
        handedness VARCHAR(50),
        strong_hand VARCHAR(50),
        location VARCHAR(255),
        in_web_dictionary BOOLEAN,
        is_proposed_new_sign BOOLEAN,
        exclude_from_ecv BOOLEAN,
        relative_orientation_movement VARCHAR(255),
        relative_orientation_location VARCHAR(255),
        repeated_movement BOOLEAN,
        alternating_movement BOOLEAN,
        movement_direction VARCHAR(255),
        link VARCHAR(512),
        video VARCHAR(512),
        affiliation JSON,
        perspective_videos JSON,
        nme_videos JSON,
        
        INDEX idx_lemma_dutch (lemma_id_gloss_dutch),
        INDEX idx_lemma_english (lemma_id_gloss_english),
        INDEX idx_annotation_dutch (annotation_id_gloss_dutch),
        INDEX idx_annotation_english (annotation_id_gloss_english),
        INDEX idx_location (location),
        INDEX idx_strong_hand (strong_hand),
        FULLTEXT idx_fulltext (lemma_id_gloss_dutch, lemma_id_gloss_english, annotation_id_gloss_dutch, annotation_id_gloss_english)
    )
    """
    cursor.execute(create_table_query)

def convert_sb_to_db():
    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        if conn.is_connected():
            cursor = conn.cursor()
            
            # Create table if it doesn't exist
            create_table(cursor)
            
            # Read the JSON file
            with open('/web/glosses_transformed.json', 'r') as file:
                data = json.load(file)
            
            count = 0
            
            # Process each item in the JSON file
            for item in data:
                # Each item is a dictionary with a single key (the ID)
                for key, value in item.items():
                    if not value:  # Skip empty records
                        continue
                    
                    # Extract the data
                    record_id = int(key)
                    lemma_id_gloss_dutch = value.get('Lemma ID Gloss: Dutch', '')
                    lemma_id_gloss_english = value.get('Lemma ID Gloss: English', '')
                    annotation_id_gloss_dutch = value.get('Annotation ID Gloss: Dutch', '')
                    annotation_id_gloss_english = value.get('Annotation ID Gloss: English', '')
                    senses_dutch = json.dumps(value.get('Senses: Dutch', {}))
                    senses_english = json.dumps(value.get('Senses: English', {}))
                    handedness = value.get('Handedness', '')
                    strong_hand = value.get('Strong Hand', '')
                    location = value.get('Location', '')
                    in_web_dictionary = 1 if value.get('In The Web Dictionary', 'False') == 'True' else 0
                    is_proposed_new_sign = 1 if value.get('Is This A Proposed New Sign?', 'False') == 'True' else 0
                    exclude_from_ecv = 1 if value.get('Exclude From Ecv', 'False') == 'True' else 0
                    relative_orientation_movement = value.get('Relative Orientation: Movement', '')
                    relative_orientation_location = value.get('Relative Orientation: Location', '')
                    repeated_movement = 1 if value.get('Repeated Movement', 'False') == 'True' else 0
                    alternating_movement = 1 if value.get('Alternating Movement', 'False') == 'True' else 0
                    movement_direction = value.get('Movement Direction', '')
                    link = value.get('Link', '')
                    video = value.get('Video', '')
                    affiliation = json.dumps(value.get('Affiliation', []))
                    perspective_videos = json.dumps(value.get('Perspective Videos', []))
                    nme_videos = json.dumps(value.get('NME Videos', []))
                    
                    # Insert query
                    query = """
                    INSERT INTO sb_records 
                    (id, lemma_id_gloss_dutch, lemma_id_gloss_english, annotation_id_gloss_dutch, 
                    annotation_id_gloss_english, senses_dutch, senses_english, handedness, 
                    strong_hand, location, in_web_dictionary, is_proposed_new_sign, 
                    exclude_from_ecv, relative_orientation_movement, relative_orientation_location, 
                    repeated_movement, alternating_movement, movement_direction, link, video, 
                    affiliation, perspective_videos, nme_videos) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    lemma_id_gloss_dutch = VALUES(lemma_id_gloss_dutch),
                    lemma_id_gloss_english = VALUES(lemma_id_gloss_english),
                    annotation_id_gloss_dutch = VALUES(annotation_id_gloss_dutch),
                    annotation_id_gloss_english = VALUES(annotation_id_gloss_english),
                    senses_dutch = VALUES(senses_dutch),
                    senses_english = VALUES(senses_english),
                    handedness = VALUES(handedness),
                    strong_hand = VALUES(strong_hand),
                    location = VALUES(location),
                    in_web_dictionary = VALUES(in_web_dictionary),
                    is_proposed_new_sign = VALUES(is_proposed_new_sign),
                    exclude_from_ecv = VALUES(exclude_from_ecv),
                    relative_orientation_movement = VALUES(relative_orientation_movement),
                    relative_orientation_location = VALUES(relative_orientation_location),
                    repeated_movement = VALUES(repeated_movement),
                    alternating_movement = VALUES(alternating_movement),
                    movement_direction = VALUES(movement_direction),
                    link = VALUES(link),
                    video = VALUES(video),
                    affiliation = VALUES(affiliation),
                    perspective_videos = VALUES(perspective_videos),
                    nme_videos = VALUES(nme_videos)
                    """
                    
                    values = (
                        record_id, lemma_id_gloss_dutch, lemma_id_gloss_english, 
                        annotation_id_gloss_dutch, annotation_id_gloss_english, 
                        senses_dutch, senses_english, handedness, strong_hand, location, 
                        in_web_dictionary, is_proposed_new_sign, exclude_from_ecv, 
                        relative_orientation_movement, relative_orientation_location, 
                        repeated_movement, alternating_movement, movement_direction, 
                        link, video, affiliation, perspective_videos, nme_videos
                    )
                    
                    cursor.execute(query, values)
                    count += 1
                    
                    if count % 100 == 0:
                        print(f"Processed {count} records")
            
            # Commit the changes
            conn.commit()
            print(f"Successfully imported {count} records into sb_records table.")
            
    except Error as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("MySQL connection closed")

if __name__ == "__main__":
    convert_sb_to_db()


