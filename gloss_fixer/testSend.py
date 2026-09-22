import requests
import json
import time

with open('results.json', 'r') as f:
    json_data = json.load(f)

# Limit to 5 items of json_data
# json_data = {k: json_data[k] for k in list(json_data)[:5]}

fields = [
    'glossid', 'Lemma ID Gloss (Dutch)', 'Lemma ID Gloss (English)',
    'Annotation ID Gloss (Dutch)', 'Annotation ID Gloss (English)',
    'Senses: Dutch', 'Senses: English', 'Handedness', 'Strong Hand',
    'Weak Hand', 'Handshape Change', 'Relation Between Articulators',
    'Location', 'Relative Orientation: Movement', 'Relative Orientation: Location',
    'Orientation Change', 'Contact Type', 'Movement Shape', 'Movement Direction',
    'Virtual Object', 'Phonology Other', 'Mouth Gesture', 'Mouthing',
    'Phonetic Variation', 'Repeated Movement', 'Alternating Movement',
    'Semantic Field', 'webDic'
]

for glossid, changes in json_data.items():
    
    if glossid not in ["47053", "46240", "48374", "45740", "45914", "48001", "46894", "46957", "49975", "49977", "49978", "47260", "47096"]:
        continue
    data = {"glossid": glossid}
    for change in changes:
        if change["new_value"] == "-":
            data[change["key_value"]] = change["old_value"]
    payload = { field: data.get(field) or None for field in fields }
    print(payload)
    
    response = requests.post(
        "https://leffe.science.uva.nl:8043/signBankAPI/update_gloss",
        json=payload,
        verify=False
    )
    print(response.status_code, response.text)
    
    try:
        response_json = response.json()
    except json.JSONDecodeError:
        response_json = {"error": "response not in json format"}
    
    # Open the output file, load existing responses as a list, append new response, then save
    try:
        with open('results_output.json', 'r+') as f:
            try:
                existing_data = json.load(f)
                # Ensure existing_data is a list
                if not isinstance(existing_data, list):
                    existing_data = [existing_data]
            except json.JSONDecodeError:
                existing_data = []
            
            existing_data.append(response_json)
            f.seek(0)
            json.dump(existing_data, f, indent=4)
            f.truncate()
    except FileNotFoundError:
        # If file doesn't exist, create it with the first response as list
        with open('results_output.json', 'w') as f:
            json.dump([response_json], f, indent=4)
    
    time.sleep(5)
