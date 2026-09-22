import os
import mysql.connector
import json

# Database connection details
db_config = {
    'host': 'signlab-db',
    'user': 'user',
    'password': os.environ.get('DB_PASS', ''),
    'database': 'admin_gebarenoverleg'
}

try:
    # Connect to the MySQL database
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Query to fetch logboek field where conditions are met
    query = """
    SELECT logboek, glos, Handeness
    FROM form_data
    WHERE fonologie_fase1 = 0
          AND morfologie = '[]' AND signbank IS NOT NULL
    """
    cursor.execute(query)
    logboek_entries = cursor.fetchall()

    latest_json_arrays = []

    # Process each logboek entry
    for logboek_text, glos, Handeness in logboek_entries:
        json_arrays = []
        if logboek_text is None:
            latest_json_arrays.append(None)
            continue

        # Split by lines and try to parse each as JSON from bottom to top
        for line in reversed(logboek_text.strip().splitlines()):
            line = line.strip()
            if not line:
                continue
            try:
                if '"Handeness"' in line:
                    # Extract the JSON part
                    start_index = line.index('{"Handeness":')
                    end_index = line.index('}') + 1
                    json_str = line[start_index:end_index]
                    json_data = json.loads(json_str)

                    # Compare Handeness from JSON with the table's Handeness
                    if json_data.get('Handeness') == Handeness:
                        break  # Stop if there's a match
                    else:
                        json_arrays.append(json_data)
            except (json.JSONDecodeError, ValueError) as e:
                # Ignore lines that are not valid JSON or missing braces
                continue

        # Get the latest JSON array if any
        latest_json = json_arrays[0] if json_arrays else None
        latest_json_arrays.append((latest_json, glos))

except mysql.connector.Error as err:
    print(f"Error: {err}")
finally:
    # Close the database connection
    if cursor:
        cursor.close()
    if connection:
        connection.close()

# Output results only when Handeness is not ''
for entry in latest_json_arrays:
    if entry is not None:
        item, glos = entry
        if item is not None and glos is not None:
            handeness = item.get('Handeness', '')
            # if handeness != '':
            print(glos, item)
            print()
