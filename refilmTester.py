import cv2
import numpy as np
import subprocess
import os
import json
# from deepface import DeepFace
import shutil
import mysql.connector

# MySQL configuration (replace with your actual config)
db_config = {
    'host': 'signlab-db',
    'user': 'user',
    'password': os.environ.get('DB_PASS', ''),
    'database': 'admin_gebarenoverleg'
}

# Establish database connection
def get_db_connection():
    return mysql.connector.connect(**db_config)

def is_clean_background_stddev(image_path, threshold=30):
    # Read the image
    image = cv2.imread(image_path)
    # Calculate standard deviation of pixel values
    stddev = np.std(image)
    # print(f"Standard deviation for {image_path}: {stddev}")
    return stddev

def is_clean_background_edges(image_path, edge_threshold=100):
    # Read the image
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    # Use Canny edge detection
    edges = cv2.Canny(image, 50, 150)
    # Count the number of edges
    num_edges = np.sum(edges > 0)
    # print(f"Number of edges for {image_path}: {num_edges}")
    return num_edges

def is_clean_background_dominant_color(image_path, dominance_threshold=0.9):
    # Read the image
    image = cv2.imread(image_path)
    # Convert to HSV color space
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # Calculate histogram for the hue channel
    hist = cv2.calcHist([hsv_image], [0], None, [180], [0, 180])
    # Find the dominant color percentage
    dominant_percentage = np.max(hist) / np.sum(hist)
    # print(f"Dominant color percentage for {image_path}: {dominant_percentage}")
    return dominant_percentage

# List all .jpg files in the specified directory
def list_jpg_files(directory):
    return [f for f in os.listdir(directory) if f.lower().endswith('.jpg')]

def recognize_face(image_path):
    dfs = DeepFace.find(img_path=image_path, db_path="/web/faceDb")
    return dfs
gloss_aff = {}
gloss_video = {}

# Function to get glosses from glosses data
def get_glosses(glosses_data):
    glosses = {}
    count = 0
    for gloss in glosses_data:
        for gloss_id, gloss_info in gloss.items():
            gloss_dutch = gloss_info.get("Annotation ID Gloss: Dutch")
            glosses[gloss_dutch] = gloss_id
            gloss_aff[gloss_dutch] = gloss_info.get("Affiliation")
            gloss_video[gloss_dutch] = gloss_info.get("Video")

            
    return glosses
# Path to the directories
directory_path = '/web/uploads'
# directory_path2 = '/web/gebarenoverleg_media/studioFilesMini/post/'

def signcollect_db(glosId):
    jsonArray = []
    #first get id from form_data table and then return signbank id
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    sql = "SELECT * FROM form_data WHERE signbank = %s"
    cursor.execute(sql, (glosId,))
    result = cursor.fetchall()
    if len(result) > 0:
        # print(len(result))
        #forloop the result
        for item in result:
            lala = item['id']
            print(lala)
            sql = "SELECT * FROM matched_transcriptions WHERE m_transcription = %s AND zOg NOT LIKE 'Zin'"
            cursor.execute(sql, (lala,))
            result = cursor.fetchall()
            if len(result) > 0:
                # print(result)
                jsonArray.append(item['id'])

            
    return jsonArray

def lookup_zelfopname(glosId):
    jsonArray = []
    #first get id from form_data table and then return signbank id
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    sql = "SELECT * FROM form_data WHERE signbank = %s"
    cursor.execute(sql, (glosId,))
    result = cursor.fetchall()
    # print(glosId)
    if len(result) > 0:
        lala = result[0]['zelfopname']
        #convert from json to list
        try:
            if lala is not None:
                jsonArray = json.loads(lala)
            if len(jsonArray) > 0:
                return jsonArray[0]
            return False
        except json.JSONDecodeError as e:
            return False

def lookup_signbank_glos(glosId):
    jsonArray = []
    #first get id from form_data table and then return signbank id
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    sql = "SELECT * FROM form_data WHERE signbank = %s"
    cursor.execute(sql, (glosId,))
    result = cursor.fetchall()
    if len(result) > 0:
        return result[0]['signbank']
    return False
            
    
def add_form_data(glosId, glos):
    
    wieArray = [1]
    wieArray = json.dumps(wieArray)
    #first check if the gloss is already in the form_data table
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    sql = "SELECT * FROM form_data WHERE signbank = %s"
    cursor.execute(sql, (glosId,))
    result = cursor.fetchall()
    if len(result) > 0:
        return False
    else:
        # We insert the record
        sql = """INSERT INTO form_data
                (signbank, thema, glos, wie) 
                VALUES (%s, %s, %s, %s)"""
        cursor.execute(sql, (
            glosId, "REFILM", glos, wieArray
        ))
        conn.commit()
        return True
    
    
    
# Get the list of .jpg files
jpg_files = list_jpg_files(directory_path)
# jpg_files.extend(list_jpg_files(directory_path2))

refilm_files = {}

# Load JSON data
with open('/web/glosses_transformed.json', 'r') as file:
    glosses_data = json.load(file)
    
count = 0
glosses = get_glosses(glosses_data)
# print(glosses)
for glos in glosses:
    if len(gloss_aff[glos]) > 0:
        
        if gloss_aff[glos][0] == "UvA":
        #i want to check glos individually
        # if glos == "LEEGHOOFD-C":
            # print(glos)
            #we are going to check if the file with .jpg exist in the directory /web/uploads
            if os.path.exists(os.path.join(directory_path, glos + '.jpg')):
                #then we perform background check
                jpg_path = os.path.join(directory_path, glos + '.jpg')
                dominant_color_result = is_clean_background_dominant_color(jpg_path)
                if dominant_color_result > 0.50:
                    is_clean = "True"
                else:
                    is_clean = "False"
                
                if len(jpg_path.split('.')[0]) > 30:
                    source = 'signCollect'
                else:
                    source = 'Signbank'
                file = glos + '.jpg'
            else:
                source = "None"
                dominant_color_result = "None"
                is_clean = "None"
                file = "None"
                
            #we want to check if the gloss has video, if not then we check if we have zelfopname
            # print(gloss_video[glos])
            if not gloss_video[glos]:
                if lookup_zelfopname(glosses[glos]):
                    #we get still image from the zelfopname
                    videoUrl = lookup_zelfopname(glosses[glos])
                    #replace the .webm with .jpg
                    file = videoUrl.replace('.webm', '.jpg')
                    
            else:
                videoUrl = gloss_video[glos]
                
            
            #now we want to know if the gloss is already in the signcollect database
            if not lookup_signbank_glos(glosses[glos]):
            #check with signCollect database if there are already takes of the gloss with glosid
                if not signcollect_db(glosses[glos]):
                        refilm_files[glos] = {
                        'dominant_color': str(dominant_color_result),
                        'clean_background': str(is_clean),
                        'source': gloss_aff[glos],
                        'file': file,
                        'video_url': videoUrl
                    }
                        print(glosses[glos], glos)
                        add_form_data(glosses[glos], glos)

                    
                #i am going to add the refilm_files to form_data database as a new gloss and add under thema REFILM.
        


# Output the list to a JSON file
output_json_path = '/web/helpScripts/refilmChecker.json'
with open(output_json_path, 'w') as json_file:
    json.dump(refilm_files, json_file, indent=4)

#print the result
#count results with average dominant color, count of clean_background true and false and source signbank
#do the same for source signcollect



print(f"List of .jpg files saved to {output_json_path}")
