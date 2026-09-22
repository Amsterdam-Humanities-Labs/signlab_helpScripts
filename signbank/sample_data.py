#!/usr/bin/env python3
"""
Sample data from glosses.json to see actual values
"""
import json

def sample_data(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Get a few samples
    count = 0
    for gloss_id, gloss_data in data.items():
        if count >= 3:
            break

        print(f"\n{'='*60}")
        print(f"Gloss ID: {gloss_id}")
        print(f"{'='*60}")

        # Show Senses
        if "Senses: Dutch" in gloss_data:
            print(f"\nSenses: Dutch:")
            for sense_num, sense_text in gloss_data["Senses: Dutch"].items():
                print(f"  {sense_num}: {sense_text[:100]}...")

        if "Senses: English" in gloss_data:
            print(f"\nSenses: English:")
            for sense_num, sense_text in gloss_data["Senses: English"].items():
                print(f"  {sense_num}: {sense_text[:100]}...")

        # Show arrays
        if "Affiliation" in gloss_data:
            print(f"\nAffiliation: {gloss_data['Affiliation']}")

        if "Tags" in gloss_data:
            print(f"Tags: {gloss_data['Tags']}")

        if "Notes" in gloss_data:
            print(f"Notes (first 200 chars): {str(gloss_data['Notes'])[:200]}...")

        count += 1

if __name__ == '__main__':
    sample_data('glosses.json')
