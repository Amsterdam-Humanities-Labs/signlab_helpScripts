import json
import requests
import time

# URL of the SignBank API
url = "https://leffe.science.uva.nl:8043/signBankAPI/update_gloss"
headers = {'Content-Type': 'application/json'}

# Load the results from the JSON file
with open('/web/translated_result.json') as result_file:
    results = json.load(result_file)

# Fields to check if all are empty
fields_to_check_empty = [
    "Handeness",
    "strongHand",
    "weakHand",
    "handLocation",
    "Virtual Object",
    "RelationArticulators",
    "relativeOrienationMovement",
    "relativeOrienationLocation",
    "Orientation Change",
    "handshapeChange",
    "repeatedMovement",
    "alternatingMovement",
    "MovementShape",
    "MovementDirection",
    "ContactType",
    "Phonology Other",
    "Mouthing",
    "Mouth Gesture",
    "Phonetic Variation"
]

# Store the errors
errors = {}

# Function to check if all relevant fields in payload are empty
def all_fields_empty(payload, fields):
    for field in fields:
        if payload.get(field, '') != '':
            return False
    return True

# Iterate through the results and send the payload to the SignBank API
for glossid, data in results.items():
    # Check if all relevant fields in payload are empty
    if all_fields_empty(data, fields_to_check_empty):
        print(f"Skipping entry due to all relevant fields being empty for glossid: {glossid}")
        continue
    
    # Construct the payload
    payload = {
        'glossid': data.get('glossid') or None,
        'Lemma ID Gloss (Dutch)': data.get('Lemma ID Gloss (Dutch)') or None,
        'Lemma ID Gloss (English)': data.get('Lemma ID Gloss (English)') or None,
        'Annotation ID Gloss (Dutch)': data.get('Annotation ID Gloss (Dutch)') or None,
        'Annotation ID Gloss (English)': data.get('Annotation ID Gloss (English)') or None,
        'Senses: Dutch': data.get('Senses: Dutch') or None,
        'Senses: English': data.get('Senses: English') or None,
        'Handedness': data.get('Handeness') or None,
        'Strong Hand': data.get('strongHand') or None,
        'Weak Hand': data.get('weakHand') or None,
        'Handshape Change': data.get('handshapeChange') or None,
        'Relation Between Articulators': data.get('RelationArticulators') or None,
        'Location': data.get('handLocation') or None,
        'Relative Orientation: Movement': data.get('relativeOrienationMovement') or None,
        'Relative Orientation: Location': data.get('relativeOrienationLocation') or None,
        'Orientation Change': data.get('orientationChange') or None,
        'Contact Type': data.get('ContactType') or None,
        'Movement Shape': data.get('MovementShape') or None,
        'Movement Direction': data.get('MovementDirection') or None,
        'Virtual Object': data.get('Virtual Object') or None,
        'Phonology Other': data.get('Phonology Other') or None,
        'Mouth Gesture': data.get('Mouth Gesture') or None,
        'Mouthing': data.get('Mouthing') or None,
        'Phonetic Variation': data.get('Phonetic Variation') or None,
        'Repeated Movement': data.get('repeatedMovement') or None,
        'Alternating Movement': data.get('alternatingMovement') or None,
        'Semantic Field': data.get('Semantic Field') or None,
        'WebDic': data.get('webDic') or None
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), verify=False)
        response_data = json.loads(response.text)  # Load the nested JSON from response text
        if response.status_code == 200 and response_data.get('updatestatus') == 'Success':
            print(f"Successfully sent data for glossid {glossid}")
        else:
            print(f"Failed to send data for glossid {glossid}: {response.status_code} - {response.text}")
            errors[glossid] = response_data.get('errors', {})
        
        # Sleep for 1 second between requests
        time.sleep(1)
    except Exception as e:
        print(f"Exception occurred for glossid {glossid}: {e}")
        errors[glossid] = str(e)

# Save the errors to a JSON file
with open('send_errors.json', 'w') as error_file:
    json.dump(errors, error_file, indent=4)

print("Data sending complete. Errors saved in 'send_errors.json'.")
