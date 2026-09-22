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

# Query to fetch data from matched_transcriptions table where signbank_upload is '1'
query = "SELECT * FROM matched_transcriptions WHERE signbank_upload='1'"
cursor.execute(query)
form_data = cursor.fetchall()
columns = cursor.column_names

# Get index of the column containing the transcription
transcription_idx = columns.index('m_transcription')

# Loop through form_data and get corresponding signbank from form_data table
for row in form_data:
    m_transcription = row[transcription_idx]
    
    # Query to get signbank value using the id from form_data
    querya = "SELECT signbank FROM form_data WHERE id = %s"
    cursor.execute(querya, (m_transcription,))  # Use the transcription as the ID
    form_dataa = cursor.fetchall()
    
    if form_dataa:
        signbank = form_dataa[0][0]  # Get the signbank ID from the fetched data

        # Prepare payload for the POST request
        payload = {
            'glossid': signbank,
            "webDic": "Yes",
        }

        print("Payload to be sent:", json.dumps(payload, indent=2))

        # Send POST request with SSL verification disabled (update to proper SSL if possible)
        response = requests.post(
            "https://leffe.science.uva.nl:8043/signBankAPI/update_gloss",
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'},
            verify=False  # It's recommended to provide the correct SSL certificate
        )
        
        print(response.text[:5000])  # Limit the output to the first 5000 characters
        # time.sleep(1)  # Delay to avoid overwhelming the server

# Close the cursor and the connection
cursor.close()
connection.close()
