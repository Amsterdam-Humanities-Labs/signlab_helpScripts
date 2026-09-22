import os
import requests
import mysql.connector
from mysql.connector import Error

# Database Configuration
db_config = {
    'host': 'signlab-db',
    'user': 'user',
    'password': os.environ.get('DB_PASS', ''),
    'database': 'admin_gebarenoverleg'
}

# SignBank Server Configuration
# signbank_api_base = "https://signbank.cls.ru.nl/dictionary/api_delete_gloss_nmevideo"
API_KEY = os.environ.get('SIGNBANK_API_KEY', '')  # Replace with actual API key

def delete_gloss_video(gloss_id):
    """
    Sends a DELETE request to the SignBank server to delete a gloss video.
    """
    #we are going to delete all videos from the gloss_id by forloop from index 0 till 3

    #first we are going to request   'https://signbank.cls.ru.nl/dictionary/get_gloss_data/5/49515' to get     "NME Videos", then get ID from that and forloop to delete the videos
    
    url = f"https://signbank.cls.ru.nl/dictionary/get_gloss_data/5/{gloss_id}"
    headers = {
            'Authorization': f'Bearer {API_KEY}'
        }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # print(data[gloss_id]['NME Videos'])
            try:
                nme_videos = data[gloss_id]['NME Videos']
                if nme_videos:
                    for video in nme_videos:
                        video_id = video['ID']
                        print(video_id)
                        delete_url = f"{signbank_api_base}/5/{gloss_id}/{video_id}/"
                        delete_response = requests.delete(delete_url, headers=headers)
                        if delete_response.status_code in [200, 204]:
                            print(f"Successfully deleted video {video_id} for gloss {gloss_id}.")
                        else:
                            print(f"Failed to delete video {video_id}. Status Code: {delete_response.status_code}")
                            print("Response:", delete_response.text)
                else:
                    print(f"No NME Videos found for gloss {gloss_id}.")
            except KeyError:
                print(f"KeyError: 'NME Videos' not found for gloss {gloss_id}. Continuing to next row.")

            else:
                print(f"No NME Videos found for gloss {gloss_id}.")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request: {e}")
    

def find_and_process_duplicates():
    """
    Finds duplicate m_transcription entries and deletes them from SignBank and local database.
    """
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            print("Connected to the database.")
            cursor = connection.cursor(dictionary=True)
            
            # Step 1: Find duplicates in m_transcription
            find_duplicates_query = """
                SELECT m_transcription
                FROM matched_transcriptions
                WHERE zOg='nmm' AND post_processed='1'
                
            """
            cursor.execute(find_duplicates_query)
            m_rows = cursor.fetchall()
            
            if not m_rows:
                print("No duplicates found.")
                return
            
            
            #remove duplicates based on m_transcription in m_rows
            unique_transcriptions = {}
            for row in m_rows:
                m_transcription = row['m_transcription']
                if m_transcription not in unique_transcriptions:
                    unique_transcriptions[m_transcription] = row
            m_rows = list(unique_transcriptions.values())
           
            print(m_rows)

            
            
            # Step 2: Process each duplicate
            for duplicate in m_rows:
                m_transcription_id = duplicate['m_transcription']
                #get signbank_id from nmm_data
                sql = "SELECT signbank_id FROM nmm_data WHERE id = %s"
                cursor.execute(sql, (m_transcription_id,))
                result = cursor.fetchall()
                if result:
                    signbank_id = result[0]['signbank_id']
                    
                    #then we get signbank from form_data based on signbank_id
                    sql = "SELECT signbank FROM form_data WHERE id = %s"
                    cursor.execute(sql, (signbank_id,))
                    result = cursor.fetchall()
                    if result:
                        signbank = result[0]['signbank']
                        # Delete the gloss video from SignBank server
                        print(signbank, duplicate)
                        delete_gloss_video(signbank)
                        #then we are going to set signbank_upload to 0 at m_transcription in matched_transcription
                        # sql = "UPDATE matched_transcriptions SET signbank_upload = 0 WHERE m_transcription = %s"
                        # cursor.execute(sql, (m_transcription_id,))
                        # connection.commit()
                        # break
                    
                    
                    
    except Error as e:
        print(f"Database error: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed.")

if __name__ == "__main__":
    find_and_process_duplicates()
