import os
import mysql.connector
import json

db_config = {
    'host': 'signlab-db',
    'user': 'user',
    'password': os.environ.get('DB_PASS', ''),
    'database': 'admin_gebarenoverleg'
}

# Establish database connection
def get_db_connection():
    return mysql.connector.connect(**db_config)

def signcollect_db():
    
    #first get id from form_data table and then return signbank id
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    sql = "SELECT * FROM form_data WHERE videoCenter IS NOT NULL"
    cursor.execute(sql)
    result = cursor.fetchall()
    
    for res in result:
        
        if res['videoCenter'] is None or res['videoLeft'] is None or res['videoRight'] is None or res['videoTop'] is None:
            continue
        
        #convert the videoleft, center, right from json to list
        try:
            videoCenter = json.loads(res['videoCenter'])
            videoLeft = json.loads(res['videoLeft'])
            videoRight = json.loads(res['videoRight'])
            videoTop = json.loads(res['videoTop'])
            glosId = res['id']
        except json.JSONDecodeError as e:
            continue
        
        
        # [{"userid":"2","file":"\/web\/gebarenoverleg_media\/studioFiles\/2024-05-21\/raw\/M20240521_0012.MP4"}]
        
        # check if any video has length greater than 0
        if len(videoCenter) > 0 and len(videoLeft) > 0 and len(videoRight) > 0 and len(videoTop) > 0:
            
            videoLeft = videoLeft[0]['file'].split('/')[-1].replace('.MP4', '.wav').replace('.mp4', '.wav')
            videoRight = videoRight[0]['file'].split('/')[-1].replace('.MP4', '.wav').replace('.mp4', '.wav')
            videoTop = videoTop[0]['videoTop']
            videoCenter = videoCenter[0]['file'].split('/')[-1].replace('.MP4', '.wav').replace('.mp4', '.wav')
            

            #then look for id in matched_transcriptions table if it already exist:
            sql = "SELECT * FROM matched_transcriptions WHERE m_transcription = %s AND zOg NOT LIKE 'Zin'"
            cursor.execute(sql, (res['id'],))
            result = cursor.fetchall()
            if len(result) > 0:
                print("Gloss with id: " + str(res['id']) + " already exists")
            else:
                # We insert the record
                    sql = """INSERT INTO matched_transcriptions
                            (m_file, m_transcription, l_file, r_file, 
                            l_transcription, r_transcription, added, definitive_outcome, zOg, videoTop) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                    cursor.execute(sql, (
                        videoCenter, glosId, videoLeft, videoRight, glosId, glosId, "1", glosId, "glos", videoTop
                    ))
                    conn.commit()
    
        
signcollect_db()