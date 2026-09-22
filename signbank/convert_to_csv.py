#!/usr/bin/env python3
"""
Convert glosses.json to glosses.csv

Strategy:
- Add ID column for the top-level keys
- Flatten Senses: Dutch and Senses: English into separate columns (1-11)
- Join array fields (Affiliation, Tags, etc.) with " | " separator
"""
import json
import csv

def convert_json_to_csv(json_filepath, csv_filepath):
    # Load JSON
    print(f"Loading {json_filepath}...")
    with open(json_filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Loaded {len(data)} glosses")

    # Define all possible columns
    # Start with ID
    columns = ['ID']

    # Regular string fields (in order they appear)
    string_fields = [
        'Lemma ID Gloss: Dutch',
        'Lemma ID Gloss: English',
        'Annotation ID Gloss: Dutch',
        'Annotation ID Gloss: English',
        'Annotation Instructions',
        'Handedness',
        'Strong Hand',
        'Strong Hand Letter',
        'Strong Hand Number',
        'Weak Hand',
        'Weak Hand Letter',
        'Weak Hand Number',
        'Location',
        'Relative Orientation: Location',
        'Relative Orientation: Movement',
        'Orientation Change',
        'Handshape Change',
        'Repeated Movement',
        'Alternating Movement',
        'Movement Shape',
        'Movement Direction',
        'Contact Type',
        'Weak Drop',
        'Weak Prop',
        'Relation Between Articulators',
        'Mouth Gesture',
        'Mouthing',
        'Phonology Other',
        'Phonetic Variation',
        'Iconic Image',
        'Named Entity',
        'Semantic Field',
        'Word Class',
        'Sequential Morphology',
        'Simultaneous Morphology',
        'Blend Morphology',
        'Virtual Object',
        'In The Web Dictionary',
        'Is This A Proposed New Sign?',
        'Exclude From Ecv',
        'Link',
        'Video',
    ]
    columns.extend(string_fields)

    # Add Senses columns (Dutch and English, 1-11)
    for i in range(1, 12):
        columns.append(f'Senses_Dutch_{i}')
    for i in range(1, 12):
        columns.append(f'Senses_English_{i}')

    # Array fields (will be joined with " | ")
    array_fields = [
        'Affiliation',
        'Tags',
        'Notes',
        'NME Videos',
        'Perspective Videos',
    ]
    columns.extend(array_fields)

    # Write CSV
    print(f"Writing to {csv_filepath}...")
    with open(csv_filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore')
        writer.writeheader()

        for gloss_id, gloss_data in data.items():
            row = {'ID': gloss_id}

            # Copy string fields directly
            for field in string_fields:
                if field in gloss_data:
                    row[field] = gloss_data[field]

            # Flatten Senses: Dutch
            if 'Senses: Dutch' in gloss_data:
                for sense_num, sense_text in gloss_data['Senses: Dutch'].items():
                    col_name = f'Senses_Dutch_{sense_num}'
                    if col_name in columns:
                        row[col_name] = sense_text

            # Flatten Senses: English
            if 'Senses: English' in gloss_data:
                for sense_num, sense_text in gloss_data['Senses: English'].items():
                    col_name = f'Senses_English_{sense_num}'
                    if col_name in columns:
                        row[col_name] = sense_text

            # Join array fields
            for field in array_fields:
                if field in gloss_data:
                    value = gloss_data[field]
                    if isinstance(value, list):
                        row[field] = ' | '.join(str(v) for v in value)
                    else:
                        row[field] = str(value)

            writer.writerow(row)

    print(f"Conversion complete! {len(data)} records written to {csv_filepath}")

if __name__ == '__main__':
    convert_json_to_csv('glosses.json', 'glosses.csv')
