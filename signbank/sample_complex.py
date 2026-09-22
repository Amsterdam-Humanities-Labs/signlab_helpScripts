#!/usr/bin/env python3
"""
Find records with multiple senses and array values
"""
import json

def find_complex_records(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Find records with multiple senses
    multi_sense_records = []
    array_field_records = []

    for gloss_id, gloss_data in data.items():
        if "Senses: Dutch" in gloss_data and len(gloss_data["Senses: Dutch"]) > 3:
            multi_sense_records.append((gloss_id, gloss_data))

        if "Tags" in gloss_data and len(gloss_data["Tags"]) > 1:
            array_field_records.append((gloss_id, gloss_data))

        if len(multi_sense_records) >= 2 and len(array_field_records) >= 2:
            break

    print("Records with multiple senses:")
    for gloss_id, gloss_data in multi_sense_records[:2]:
        print(f"\nGloss ID: {gloss_id}")
        print(f"Senses: Dutch:")
        for sense_num, sense_text in sorted(gloss_data["Senses: Dutch"].items(), key=lambda x: int(x[0])):
            print(f"  {sense_num}: {sense_text}")

    print("\n" + "="*60)
    print("Records with multiple tags/arrays:")
    for gloss_id, gloss_data in array_field_records[:2]:
        print(f"\nGloss ID: {gloss_id}")
        if "Tags" in gloss_data:
            print(f"Tags: {gloss_data['Tags']}")
        if "Affiliation" in gloss_data:
            print(f"Affiliation: {gloss_data['Affiliation']}")
        if "Notes" in gloss_data:
            print(f"Notes: {gloss_data['Notes'][:3] if isinstance(gloss_data['Notes'], list) else gloss_data['Notes']}")

if __name__ == '__main__':
    find_complex_records('glosses.json')
