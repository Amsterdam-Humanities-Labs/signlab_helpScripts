import json
import sys

# Load the translation data from the selects_data_combined.json file
with open('selects_data_combined.json') as file:
    translation_data = json.load(file)

# Load the results from the result.json file
with open('../result.json') as result_file:
    results = json.load(result_file)

# Create translation dictionaries
translation_dicts = {}
for key, translations in translation_data.items():
    translation_dicts[key] = {entry['NL']: entry['EN'] for entry in translations}


# Fields that require translation
fields_to_translate = [
    "Handeness",
    "strongHand",
    "weakHand",
    "handLocation",
    "Virtual Object",
    "RelationArticulators",
    "relativeOrienationMovement",
    "relativeOrienationLocation",
    "orientationChange",
    "HandshapeChange",
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


# Store errors
translation_errors = {}

# Translate the fields in the results
for glossid, payload in results.items():
    print(glossid)
    for field in fields_to_translate:
        if field in payload:
            value = payload[field]
            if value is None or value == '' or value == 'null':
                payload[field] = ""
            else:
                translated_value = translation_dicts.get(field, {}).get(value, value)
                payload[field] = translated_value
                print(payload[field], translated_value)


# Save the translated results to translated_result.json
with open('translated_result.json', 'w') as translated_result_file:
    json.dump(results, translated_result_file, indent=4)

# Save the translation errors to translation_errors.json
with open('translation_errors.json', 'w') as error_file:
    json.dump(translation_errors, error_file, indent=4)

print("Translation complete. Translated results saved in 'translated_result.json'. Errors saved in 'translation_errors.json'.")
