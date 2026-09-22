import os
import mysql.connector
from pathlib import Path
import sys

# MySQL configuration
db_config = {
    'host': 'signlab-db',
    'user': 'user',
    'password': os.environ.get('DB_PASS', ''),
    'database': 'admin_gebarenoverleg'
}


def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            print("Successfully connected to the database.")
            return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
    return None




def lookup_records():
   
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to the database. Exiting.")
        return
    cursor = conn.cursor(dictionary=True)
    sql = "SELECT * FROM studio_data WHERE ready IN ('1', '2') ORDER BY date DESC LIMIT 1"
    cursor.execute(sql)
    records = cursor.fetchall()
    cursor.close()
    conn.close()
    for record in records:
        #we get records from matched_transcriptions matching date
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        sql = f"SELECT * FROM matched_transcriptions WHERE date = '{record['date']}'"
        cursor.execute(sql)
        matched_transcriptions = cursor.fetchall()
        cursor.close()
        conn.close()
        m_array = []
        
        for mt in matched_transcriptions:
            #we get records from transcriptions matching date
            l_file = mt['l_file']
            r_file = mt['r_file']
            m_file = mt['m_file']
            a_file = mt['a_file']
            b_file = mt['b_file']
            m_array.append(m_file)
            
            #if all is not empty then we continue to check the transcriptions
            if l_file and r_file and m_file and a_file and b_file:
                print("All files are present")
            else: 
                print("Not all files are present")
                continue
            
        #show the count of records 
        print(f"Date: {record['date']}")
        print(f"Number of records: {len(matched_transcriptions)}")
        #we also get the number of files from studio_data
        print(record['l_count'], record['r_count'], record['m_count'], record['a_count'], record['b_count'])
        
        print(m_array)
        
        #we are going to look in directory /web/gebarenoverleg_media/studioFiles/2024-11-11/raw and get files starting M2024 and then compare with m_file from mt
        raw_dir = Path(f"/web/gebarenoverleg_media/studioFiles/{record['date']}/raw")
        for file in raw_dir.iterdir():
         if file.is_file() and file.suffix.lower() == '.mp4':
            if file.name.startswith('M2024'):
                #translate .MP4 to .wav
                file_name = file.name.replace('.MP4', '.wav')
                if file_name not in m_array:
                    print(f"File {file.name} is missing in matched_transcriptions")
        
        
        
lookup_records()
