import os
import mysql.connector
from mysql.connector import Error
import pandas as pd
import json
import sys

def connect_to_db(db_config):
    """
    Establishes a connection to the MySQL database using the provided configuration.
    """
    try:
        connection = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database']
        )
        if connection.is_connected():
            print("Successfully connected to the database.")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        sys.exit(1)

def fetch_data(connection):
    """
    Fetches data from matched_transcription and form_data tables by performing a JOIN on m_transcription and id.
    Extracts the fields l, m, a, b, r_file, m_transcription, and signbank.
    """
    try:
        query = """
            SELECT 
            mt.l_file, 
            mt.m_file, 
            mt.a_file, 
            mt.b_file, 
            mt.r_file, 
            mt.m_transcription, 
            fd.signbank
            FROM 
            matched_transcriptions mt
            LEFT JOIN 
            form_data fd 
            ON 
            mt.m_transcription = fd.id
            WHERE 
            mt.zOg = 'glos'
        """
        df = pd.read_sql(query, connection)
        print("Data fetched successfully from the database.")
        return df
    except Error as e:
        print(f"Error fetching data: {e}")
        sys.exit(1)

def process_r_file(r_file):
    """
    Processes the r_file field. If it's a JSON array, it parses and joins the files with a separator.
    If it's a single file or NULL, it returns it as is.
    """
    if pd.isna(r_file):
        return ''
    try:
        # Attempt to parse as JSON
        files = json.loads(r_file)
        if isinstance(files, list):
            return ', '.join(files)
        else:
            return str(files)
    except json.JSONDecodeError:
        # If not JSON, return the string as is
        return str(r_file)

def export_to_csv(df, output_csv):
    """
    Exports the processed DataFrame to a CSV file with columns 'all_files' and 'signbank'.
    """
    try:
        # Process the r_file column
        df['all_files'] = df.apply(lambda row: ', '.join(filter(None, [
            process_r_file(row['l_file']),
            process_r_file(row['m_file']),
            process_r_file(row['a_file']),
            process_r_file(row['b_file']),
            process_r_file(row['r_file'])
        ])), axis=1)
        
        # Select the required columns
        export_df = df[['all_files', 'signbank']]
        
        # Handle NULL signbank values
        export_df['signbank'] = export_df['signbank'].fillna('')
        
        # Export to CSV
        export_df.to_csv(output_csv, index=False, encoding='utf-8')
        print(f"Extraction complete. Data saved to {output_csv}")
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        sys.exit(1)

def main():
    # MySQL configuration
    db_config = {
        'host': 'signlab-db',
        'user': 'user',
        'password': os.environ.get('DB_PASS', ''),
        'database': 'admin_gebarenoverleg'
    }
    
    # Output CSV file path
    output_csv = 'exported_matched_transcription.csv'
    
    # Step 1: Connect to the database
    connection = connect_to_db(db_config)
    
    # Step 2: Fetch data with JOIN
    df = fetch_data(connection)
    
    # Step 3: Close the database connection
    if connection.is_connected():
        connection.close()
        print("Database connection closed.")
    
    # Step 4: Export to CSV
    export_to_csv(df, output_csv)

if __name__ == "__main__":
    main()
