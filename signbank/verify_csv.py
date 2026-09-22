#!/usr/bin/env python3
"""
Verify the CSV conversion
"""
import csv

def verify_csv(csv_filepath):
    with open(csv_filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        # Get column names
        columns = reader.fieldnames
        print(f"Total columns: {len(columns)}")
        print(f"\nFirst 10 columns: {columns[:10]}")
        print(f"\nSenses columns (sample): {[c for c in columns if 'Senses' in c][:6]}")

        # Check specific records
        print("\n" + "="*60)
        print("Sample record with multiple senses (ID: 2108):")
        print("="*60)
        f.seek(0)
        reader = csv.DictReader(f)
        for row in reader:
            if row['ID'] == '2108':
                print(f"ID: {row['ID']}")
                print(f"Lemma ID Gloss: Dutch: {row['Lemma ID Gloss: Dutch']}")
                for i in range(1, 7):
                    sense_key = f'Senses_Dutch_{i}'
                    if row.get(sense_key):
                        print(f"  {sense_key}: {row[sense_key]}")
                break

        print("\n" + "="*60)
        print("Sample record with tags (ID: 3913):")
        print("="*60)
        f.seek(0)
        reader = csv.DictReader(f)
        for row in reader:
            if row['ID'] == '3913':
                print(f"ID: {row['ID']}")
                print(f"Tags: {row.get('Tags', 'N/A')}")
                print(f"Affiliation: {row.get('Affiliation', 'N/A')}")
                break

        # Count records
        f.seek(0)
        reader = csv.DictReader(f)
        count = sum(1 for row in reader)
        print(f"\n" + "="*60)
        print(f"Total records in CSV: {count}")
        print("="*60)

if __name__ == '__main__':
    verify_csv('glosses.csv')
