import os
import requests
import base64
import json
import mysql.connector
from mysql.connector import Error
import sys
import time


# Database Configuration
db_config = {
    'host': 'signlab-db',
    'user': 'user',
    'password': os.environ.get('DB_PASS', ''),
    'database': 'admin_gebarenoverleg'
}

# Directory Configuration
post_dir = "/web/gebarenoverleg_media/studioFilesMini/post"
intermediary_url = "https://leffe.science.uva.nl:8043/signBankAPI/create_nme_video_gloss"  # Endpoint of intermediary server

def create_nme_video_gloss(gloss_id, index, desc_nl, desc_en, video_file_path):
    """
    Sends a POST request to the intermediary server with gloss details and file path.
    """
    headers = {
        'Content-Type': 'application/json',
    }
    
    # Prepare the JSON payload
    payload = {
        'gloss_id': gloss_id,
        'index': index,
        'desc_nl': desc_nl,
        'desc_en': desc_en,
        'video_file_path': video_file_path
    }
    # print("Payload:", payload)
    try:
        response = requests.post(intermediary_url, headers=headers, json=payload, verify=False)
        
        # Check if the request was successful
        if response.status_code in [200, 201]:
            print("Request to intermediary server was successful.")
            # print("Response:", response.json())
            return True
        else:
            print(f"Failed to create NME Video gloss. Status Code: {response.status_code}")
            # print("Response:", response.text)
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request: {e}")
        return False

def get_mp4_path(wav_path):
    """
    Changes the file extension from .wav to .mp4.

    Args:
        wav_path (str): The original path to the .wav file.

    Returns:
        str: The new path with the .mp4 extension, or None if not found.
    """
    mp4_path = os.path.splitext(wav_path)[0] + '.mp4'
    if not os.path.isfile(mp4_path):
        print(f"MP4 file does not exist: {mp4_path}")
        return None

    print(f"MP4 path obtained: {mp4_path}")
    return mp4_path

def fetch_gloss_id(cursor, m_transcription_id):
    """
    Fetches the gloss_id from the database based on m_transcription_id, and extracts senses as descriptions.
    """
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True, buffered=True)


    try:
        # Fetch signbank_id from nmm_data
        cursor.execute("SELECT signbank_id, type, glos FROM nmm_data WHERE id = %s", (m_transcription_id,))
        result = cursor.fetchone()
        if not result:
            print(f"No signbank_id found for m_transcription_id: {m_transcription_id}")
            return None, 'No description', 'No description', None

        signbank_id = result['signbank_id']
        type = result['type']
        glos = result['glos']
        
        
        # Fetch gloss_id, senses, and sensesEngels from form_data
        cursor.execute("SELECT signbank, senses, sensesEngels FROM form_data WHERE signbank = %s", (signbank_id,) AND extern IS NULL)
        result = cursor.fetchone()
        if not result:
            print(f"No gloss_id found for signbank_id: {signbank_id}")
            return None, 'No description', 'No description', None
        
        gloss_id = result['signbank']
        
        # Decode senses and sensesEngels JSON arrays, get the first item if it exists
        senses = json.loads(result['senses']) if result['senses'] else []
        sensesEngels = json.loads(result['sensesEngels']) if result['sensesEngels'] else []
        
        description_dutch = senses[0] if senses else 'No description'
        description_english = sensesEngels[0] if sensesEngels else 'No description'
        
        return gloss_id, description_dutch, description_english, type
    except Error as e:
        print(f"Database error: {e}")
        return None, 'No description', 'No description', None

def obtain_gloss_info(gloss_id):
    url = f"https://signbank.cls.ru.nl/dictionary/get_gloss_data/5/{gloss_id}"
    
    headers = {
        "Authorization": "Bearer UlerhGrfFpU03RD3",
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code in [200, 201]:
            print("Request to Signbank was successful.")
        else:
            print(f"Failed to obtain gloss information. Status Code: {response.status_code}")
            # print("Response:", response.text)
        
        # Then we get the gloss information from the response 
        response_data = response.json()
        # print(response_data )
        gloss_info = response_data.get(str(gloss_id), {})
        nme_videos = gloss_info.get("NME Videos", [])
        # Then we create a temp array with Index from NME Videos as key and ID as value
        nme_videos_dict = {}
        nme_videos_link = {}
        nme_videos_description_dutch = {}
        nme_videos_description_english = {}
        nme_videos_checksum = {}
        for item in nme_videos:
            if item['Index'] not in nme_videos_dict:
                nme_videos_dict[item['Index']] = []
                nme_videos_link[item['Index']] = []
                nme_videos_description_dutch[item['Index']] = []
                nme_videos_description_english[item['Index']] = []
                nme_videos_checksum[item['Index']] = []

            nme_videos_dict[item['Index']].append(item['ID'])
            nme_videos_link[item['Index']].append(item['Link'])
            nme_videos_description_dutch[item['Index']].append(item['Description: Dutch'])
            nme_videos_description_english[item['Index']].append(item['Description: English'])
            nme_videos_checksum[item['Index']].append(item['Checksum'])
            
        return nme_videos_dict, nme_videos_link, nme_videos_description_dutch, nme_videos_description_english, nme_videos_checksum
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request: {e}")
        return {}
    

def obtain_nme_video_array(gloss_id):
    url = f"https://signbank.cls.ru.nl/dictionary/get_gloss_data/5/{gloss_id}"
    
    headers = {
        "Authorization": "Bearer UlerhGrfFpU03RD3",
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code in [200, 201]:
            print("Request to Signbank was successful.")
        else:
            print(f"Failed to obtain gloss information. Status Code: {response.status_code}")
            # print("Response:", response.text)
        
        # Then we get the gloss information from the response 
        response_data = response.json()
        # print(response_data )
        gloss_info = response_data.get(str(gloss_id), {})
        nme_videos = gloss_info.get("NME Videos", [])
        return nme_videos
    except:
        return []
def obtain_mt_id(lemma, type='nmm'):
    """
    Connects to the database to determine the m_file from matched_transcriptions based on nmm_data.
    Assumes gloss contains "Lemma ID Gloss: Dutch" used to query the nmm_data table.
    """
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True, buffered=True)
            # Use the lemma from gloss to query nmm_data.
            if not lemma:
                print("Lemma ID Gloss: Dutch missing in gloss.")
                return None
            
            type_mt = ""
            if type == "nmm":
                type_mt = "ready"
            if type == "nmm_oc":
                type_mt = "oc"

            query1 = "SELECT id FROM nmm_data WHERE glos = %s AND type = %s LIMIT 1"
            cursor.execute(query1, (lemma,type_mt,))
            row = cursor.fetchone()
            if not row:
                print(f"No record found in nmm_data for glos: {lemma} and type {type_mt}")
                return None
            m_transcription_id = row['id']


            # Use the obtained m_transcription_id to get m_file from matched_transcriptions.
            query2 = "SELECT m_file FROM matched_transcriptions WHERE m_transcription = %s AND zOg=%s ORDER BY id DESC LIMIT 1"
            cursor.execute(query2, (m_transcription_id,type,))
            row2 = cursor.fetchone()
            if not row2:
                print(f"No record found in matched_transcriptions for m_transcription: {m_transcription_id}")
                return None
            m_file = row2['m_file']
            return m_file

    except Error as e:
        print(f"Database error in obtain_mt_id: {e}")
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

def remove_gloss_video(gloss_id, videoid):
    url = f"https://signbank.cls.ru.nl/dictionary/api_delete_gloss_nmevideo/5/{gloss_id}/{videoid}/"
    
    headers = {
        "Authorization": "Bearer UlerhGrfFpU03RD3",
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code in [200, 201]:
            print("Request to Signbank to DELETE was successful.")
            print("Response:", response.json())
            return True
        else:
            print(f"Failed to remove gloss information. Status Code: {response.status_code}")
            # print("Response:", response.text)
            return False
        
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request: {e}")
        return False

def process_transcriptions():
    """
    Main function to process matched_transcriptions and create NME Video glosses.
    """
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            print("Connected to the database.")
            # Change here: use buffered cursor to avoid 'Unread result found'
            cursor = connection.cursor(dictionary=True, buffered=True)
            
            # Step 1: Fetch the latest row for each m_transcription
            query = """
                SELECT mt.m_file, mt.m_transcription, zOg
                FROM matched_transcriptions AS mt
                INNER JOIN (
                    SELECT m_transcription, MAX(id) AS latest_id
                    FROM matched_transcriptions
                    WHERE (zOG = 'nmm' OR zOg = 'nmm_oc') AND post_processed = '1' AND added = '1' AND (signbank_upload != '1' OR signbank_upload IS NULL)
                    GROUP BY m_transcription
                ) AS latest_transcriptions
                ON mt.m_transcription = latest_transcriptions.m_transcription
                AND mt.id = latest_transcriptions.latest_id
                ORDER BY mt.id DESC
            """ 


            # query = """
            # SELECT * FROM matched_transcriptions WHERE m_transcription = 59 AND zOg LIKE '%nmm%' ORDER BY ID DESC LIMIT 1"""

            cursor.execute(query)
            rows = cursor.fetchall()
            
            
            
            
            if not rows:
                print("No matching transcriptions found.")
                return
                        
            for row in rows:
                m_file = row['m_file']
                m_transcription_id = row['m_transcription']
                m_zOg = row['zOg']
                
                # if m_transcription_id == "59":
                if m_transcription_id:
                    print("match")
                    # To be sure, check in matched_transcription if there is at least one row with signbank_upload = 1
                    # If so, we skip this m_file
                    cursor.execute("""
                        SELECT COUNT(*) AS count
                        FROM matched_transcriptions
                        WHERE signbank_upload = 'NULL' AND zOg = %s  AND added='1' AND m_transcription = %s
                    """, (m_zOg, m_transcription_id,))
                    result = cursor.fetchone()
                    if result['count'] > 0:
                        print(f"Skipping {m_file} as it has already been processed.")
                        continue
                    
                    print(m_transcription_id)
                    # sys.exit()
                    # Step 2: Fetch gloss_id and descriptions
                    gloss_id, description_dutch, description_english, type = fetch_gloss_id(cursor, m_transcription_id)
                    if not gloss_id:
                        continue
                    print(f"Creating NME Video gloss for {m_file} at gloss {gloss_id} and m_transcription {m_transcription_id} and type {type}")
                    
                    # Step 3: Get MP4 path by changing the file extension
                    wav_path = os.path.join(post_dir, m_file)
                    mp4_path = get_mp4_path(wav_path)
                    
                    if not mp4_path:
                        continue
                    
                    INDEX = 0
                    # Step 4: Determine INDEX based on type
                    if type == "ready":
                        INDEX = 0
                    elif type == "oc":
                        INDEX = 1
                    elif type == "nmm":
                        INDEX = 2
                    
                    print(f"Creating NME Video gloss for {m_file} at gloss {gloss_id} and m_transcription {m_transcription_id} and type {type}")
                    
                    # First, obtain gloss information from Signbank
                    try:
                        rA, rB, nme_videos_description_dutch, nme_videos_description_english, nme_videos_checksum = obtain_gloss_info(gloss_id=gloss_id)
                    except (Error, ValueError) as e:
                        print(e)
                        continue

                    print(f"rA: {rA}")
                    print(f"rB: {rB}")

                    # Then, check if INDEX is already in the array rA, if so then remove that video
                    if str(INDEX) in rA:
                        # print(f"Index {INDEX} already exists in the gloss {gloss_id}. Removing the existing video(s).")

                        for item in rA[str(INDEX)]:
                            #we want to check first if the video from signbank is same a the video we want to upload
                            #download the video from signbank from rA[item]
                            
                            nme_video = rB[str(INDEX)][0]
                            checksum = nme_videos_checksum[str(INDEX)][0]
                            # print(nme_video)
                            #download the video
                            # r = requests.get(nme_video, allow_redirects=True)
                            #save the video as temp_video.mp4
                            # open('/web/temp_video.mp4', 'wb').write(r.content)
                            #check if the video is the same as the videoCenter
                            try:
                                md5sum = os.popen(f"md5sum {mp4_path}").read().split()[0]
                                #get md5sum of temp_video.mp4
                                
                                if md5sum:
                                    #check if index is higher than 0 with md5sum_temp
                                        if md5sum == checksum:
                                            print("Video is the same, no need to remove it...setting signbak_upload to 1")
                                            update_query = """
                                                UPDATE matched_transcriptions
                                                SET signbank_upload = 1
                                                WHERE m_file = %s
                                            """
                                            print(update_query, m_transcription_id)
                                            # if m_file == "M20250107_3296.wav":
                                            #     sys.exit()
                                            cursor.execute(update_query, (m_file,))
                                            connection.commit()
                                            # sys.exit()

                                        else:
                                            print(f"Removing video ID: {item}")
                                            remove_success = remove_gloss_video(gloss_id, item)
                                            if remove_success:
                                                #after it's removed then recreate the video again but after 5 seconds of sleep 
                                                
                                                time.sleep(5)
                                                
                                                nme_videos_dict, nme_videos_link, description_dutch, description_english, nme_videos_checksum = obtain_gloss_info(gloss_id=gloss_id)
                                                
                                                # Create new NME Video gloss
                                                upload_success = create_nme_video_gloss(
                                                    gloss_id=gloss_id,
                                                    index=INDEX,
                                                    desc_nl=description_dutch,
                                                    desc_en=description_english,
                                                    video_file_path=mp4_path
                                                )
                                                
                                                
                                                if upload_success:
                                                    continue
                                                    
                                                print("Sleeping....")
                                                time.sleep(5)
                                                
                                            else:
                                                print(f"Failed to remove video ID: {item}")
                                else:
                                    remove_success = remove_gloss_video(gloss_id, item)

                            except Error as e:
                                print(e)
                    else:
                        
                        nme_videos_dict, nme_videos_link, description_dutch, description_english, nme_videos_checksum = obtain_gloss_info(gloss_id=gloss_id)
                        # Create new NME Video gloss
                        upload_success = create_nme_video_gloss(
                            gloss_id=gloss_id,
                            index=INDEX,
                            desc_nl=description_dutch,
                            desc_en=description_english,
                            video_file_path=mp4_path
                        )
                        print(gloss_id, INDEX, description_dutch, description_english, mp4_path)

                        if upload_success:
                            # we do nothing, for the next iteration we will check if it's there   
                            continue                             
                            
                
               

                    
    except Error as e:
        print(f"Error while connecting to the database: {e}")

def check_every_sb_records_for_nme_video():
    """
    Opens /web/glosses_transformed.json, cleans extra NME videos (indices other than 0,1,2)
    and for index 0 downloads the video to compare with the local version.
    Expects each element in the JSON array to be an object with a single key (the gloss_id)
    whose value is the gloss data.
    """
    try:
        with open('/web/glosses_transformed.json', 'r') as f:
            records = json.load(f)
    except Exception as e:
        print(f"Failed to open glosses file: {e}")
        return
    connection = mysql.connector.connect(**db_config)
    if connection.is_connected():
        print("Connected to the database.")
        # Change here: use buffered cursor to avoid unread results
        cursor = connection.cursor(dictionary=True, buffered=True)
        # Iterate over each record and then over the gloss inside it.
        for record in records:
            for gloss_id, gloss in record.items():
                lemma = gloss.get('Lemma ID Gloss: Dutch')
                affilation = gloss.get('Affiliation')
                if len(affilation) == 0:
                    continue
                if affilation[0] != "UvA":	
                    continue
                # if lemma != "#CDA":
                #     continue
                # nme_videos = gloss.get('NME Videos', {})
                nme_videos = obtain_nme_video_array(gloss_id)
                print(nme_videos)
                # sys.exit()
                # If nme_videos is a list, convert it into a dict keyed by video's Index.
                if isinstance(nme_videos, list):
                    converted = {}
                    for video in nme_videos:
                        idx = str(video.get('Index'))
                        converted.setdefault(idx, []).append(video)
                    nme_videos = converted
                # Remove any indices not in 0,1
                for idx in list(nme_videos.keys()):
                    if idx not in ['0', '1']:
                        for video in nme_videos[idx]:
                            video_id = video.get('ID')
                            print(f"Removing extra video with index {idx} for gloss {gloss_id}, video ID: {video_id}")
                            remove_gloss_video(gloss_id, video_id)
                            # sys.exit()
                        del nme_videos[idx]
                # If index 0 exists, download and compare video
                if '0' in nme_videos and nme_videos['0']:
                    video_link = nme_videos['0'][0].get('Link')
                    video_id = nme_videos['0'][0].get('ID')
                    md5_sb = nme_videos['0'][0].get('Checksum')

                    if video_link:
                        try:
                            local_video_path = obtain_mt_id(lemma)
                            local_video_path = "/web/gebarenoverleg_media/studioFilesMini/post/" + local_video_path.replace('.wav', '.mp4')
                            print(local_video_path)
                            if not local_video_path or not os.path.exists(local_video_path):
                                print(f"Local video for gloss {gloss_id} not found.")
                                continue
                            md5_local = os.popen(f"md5sum {local_video_path}").read().split()[0]
                            if md5_sb == md5_local:
                                print(f"Gloss {gloss_id}: Video matches. Set signbank_upload to 1.")
                            else:
                                print(f"Gloss {gloss_id}: Video differs. Set signbank_upload to 0.")
                                remove_gloss_video(gloss_id, video_id)

                                #update signbank_upload to 0
                                update_query = """
                                                    UPDATE matched_transcriptions
                                                    SET signbank_upload = NULL
                                                    WHERE m_file = %s AND (zOg = 'nmm' OR zOg = 'nmm_oc')
                                                """
                                cursor.execute(update_query, (local_video_path,))
                                connection.commit()
                                # sys.exit()

                        except Exception as ex:
                            print(f"Error processing video for gloss {gloss_id}: {ex}")
                    else:
                        print(f"No video link found for gloss {gloss_id} at index 0.")
                else:
                    print(f"No NME video at index 0 for gloss {gloss_id}.")
                    
                    
                #do the same for index 1

                for idx in list(nme_videos.keys()):
                    print(idx)
                
                if '1' in nme_videos and nme_videos['1']:
                    video_link = nme_videos['1'][0].get('Link')
                    video_id = nme_videos['1'][0].get('ID')
                    md5_sb = nme_videos['1'][0].get('Checksum')
                    
                    if video_link:
                        try:
                            local_video_path = obtain_mt_id(lemma, "nmm_oc")

                            if not local_video_path or not os.path.exists(local_video_path):
                                print(f"Local video for gloss {gloss_id} not found.")
                                print(local_video_path)
                                remove_gloss_video(gloss_id, video_id)
                                    #update signbank_upload to 0
                                update_query = """
                                                    UPDATE matched_transcriptions
                                                    SET signbank_upload = NULL
                                                    WHERE m_file = %s AND (zOg = 'nmm' OR zOg = 'nmm_oc')
                                                """
                                cursor.execute(update_query, (local_video_path,))
                                connection.commit()
                                continue
                            local_video_path = "/web/gebarenoverleg_media/studioFilesMini/post/" + local_video_path.replace('.wav', '.mp4')
                            print(local_video_path)
                            md5_local = os.popen(f"md5sum {local_video_path}").read().split()[0]
                            if md5_sb == md5_local:
                                print(f"Gloss {gloss_id}: Video matches. Set signbank_upload to 1.")
                            else:
                                print(f"Gloss {gloss_id}: Video differs. Set signbank_upload to 0.")

                                #update signbank_upload to 0
                                update_query = """
                                                    UPDATE matched_transcriptions
                                                    SET signbank_upload = NULL
                                                    WHERE m_file = %s AND (zOg = 'nmm' OR zOg = 'nmm_oc')
                                                """
                                remove_gloss_video(gloss_id, video_id)
                                cursor.execute(update_query, (local_video_path,))
                                connection.commit()

                        except Exception as ex:
                            print(f"Error processing video for gloss {gloss_id}: {ex}")
                    else:
                        print(f"No video link found for gloss {gloss_id} at index 1.")
                else:
                    print(f"No NME video at index 1 for gloss {gloss_id}.")
                
if __name__ == "__main__":
    
    #disable for now
    # sys.exit()
    # Process new transcriptions
    process_transcriptions()
    
    # Check and update existing NME videos
    # check_if_nme_video_should_be_there() 
    # check_every_sb_records_for_nme_video()

    #do this only between 6 and 8 am
    if 6 <= time.localtime().tm_hour <= 8:
        check_every_sb_records_for_nme_video()
