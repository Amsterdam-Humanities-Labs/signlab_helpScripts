#!/usr/bin/env python3
"""
Analyze glosses.json to identify all fields and their types
"""
import json
from collections import defaultdict

def analyze_json_structure(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Collect all field names and their types
    all_fields = set()
    field_types = defaultdict(set)
    nested_fields = defaultdict(set)
    max_senses = 0

    for gloss_id, gloss_data in data.items():
        for key, value in gloss_data.items():
            all_fields.add(key)

            # Track type
            if isinstance(value, dict):
                field_types[key].add('dict')
                # Track nested keys
                for nested_key in value.keys():
                    nested_fields[key].add(nested_key)
                # Track max senses
                if key == "Senses: Dutch":
                    max_senses = max(max_senses, len(value))
            elif isinstance(value, list):
                field_types[key].add('list')
            elif isinstance(value, bool):
                field_types[key].add('bool')
            elif isinstance(value, (int, float)):
                field_types[key].add('number')
            elif isinstance(value, str):
                field_types[key].add('string')
            else:
                field_types[key].add('null' if value is None else type(value).__name__)

    print(f"Total glosses: {len(data)}")
    print(f"\nAll fields ({len(all_fields)}):")
    for field in sorted(all_fields):
        types = ', '.join(sorted(field_types[field]))
        print(f"  - {field}: {types}")
        if field in nested_fields:
            print(f"    Nested keys: {sorted(nested_fields[field])}")

    print(f"\nMax number of senses: {max_senses}")

if __name__ == '__main__':
    analyze_json_structure('glosses.json')
