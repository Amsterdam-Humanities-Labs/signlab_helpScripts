import os
import requests
import json
import mysql.connector


DB_CONFIG = {
        'host': 'localhost',
        'user': 'user',
        'password': os.environ.get('DB_PASS', ''),
        'database': 'admin_gebarenoverleg'
    }


API_KEY = os.environ.get('OPENROUTER_API_KEY', '')
API_URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "HTTP-Referer": "https://your-site-url.com",  # Optional. Replace with your site URL.
    "X-Title": "YourSiteName",                    # Optional. Replace with your site name.
    "Content-Type": "application/json"
}

# Connect to the database
conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

# Get all unique lemmas from hh_words
cursor.execute("SELECT DISTINCT lemma FROM hh_words")
all_lemmas = [row[0] for row in cursor.fetchall()]

# Get existing lemmas in hh_synonyms to avoid duplicates
cursor.execute("SELECT DISTINCT lemma FROM hh_synonyms")
existing_lemmas = [row[0] for row in cursor.fetchall()]

# Filter out lemmas that already have synonyms
lemmas_to_process = [lemma for lemma in all_lemmas if lemma not in existing_lemmas]

print(f"Found {len(all_lemmas)} unique lemmas.")
print(f"Processing {len(lemmas_to_process)} lemmas that don't have synonyms yet.")

for lemma in lemmas_to_process:
    payload = {
        "model": "google/gemini-2.0-flash-lite-001",
        "messages": [
            {
                "role": "user",
                "content": f"Provide dutch synonyms for the word '{lemma}' in JSON format with an array called 'synonyms'. Only include the JSON output, nothing else."
            }
        ]
    }
    
    print(f"Requesting synonyms for: {lemma}")
    response = requests.post(API_URL, headers=HEADERS, data=json.dumps(payload))
    
    if response.ok:
        try:
            # Extract the content from the response
            content = response.json()["choices"][0]["message"]["content"].strip()
            
            # Try to parse the JSON from the content
            # The model might not always return perfect JSON, so we handle potential errors
            try:
                # Look for JSON-like structure in the response
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = content[json_start:json_end]
                    synonyms_data = json.loads(json_str)
                    
                    if 'synonyms' in synonyms_data and isinstance(synonyms_data['synonyms'], list):
                        synonyms = synonyms_data['synonyms']
                        
                        # Insert each synonym into the database
                        for synonym in synonyms:
                            if isinstance(synonym, str) and synonym.strip() and synonym.strip() != lemma:
                                # Check if this specific lemma-synonym pair already exists
                                cursor.execute(
                                    "SELECT COUNT(*) FROM hh_synonyms WHERE lemma = %s AND synonym = %s",
                                    (lemma, synonym.strip())
                                )
                                if cursor.fetchone()[0] == 0:
                                    cursor.execute(
                                        "INSERT INTO hh_synonyms (lemma, synonym) VALUES (%s, %s)",
                                        (lemma, synonym.strip())
                                    )
                                    print(f"  Added synonym: {synonym.strip()}")
                        
                        conn.commit()
                    else:
                        print(f"  No valid synonyms array found for {lemma}")
                else:
                    print(f"  No valid JSON found in response for {lemma}")
            except json.JSONDecodeError:
                print(f"  Could not parse JSON from response for {lemma}")
        except (KeyError, IndexError) as e:
            print(f"  Error processing response for {lemma}: {e}")
    else:
        print(f"  API error for {lemma}: {response.status_code}")

# Close database connection
cursor.close()
conn.close()

print("Processing complete.")
