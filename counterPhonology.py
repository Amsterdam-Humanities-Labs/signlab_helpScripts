import json
from collections import defaultdict

# Load the JSON data
def load_data(filepath):
    with open(filepath, 'r') as file:
        data = json.load(file)
    return data

# Count occurrences of each unique value for specified fields
def count_values(data, fields):
    counts = defaultdict(lambda: defaultdict(int))
    for item in data:
        gloss_data = next(iter(item.values()))  # Access the dictionary inside the list item
        for field in fields:
            value = gloss_data.get(field)
            if value:
                counts[field][value] += 1
    return counts

# Write the counts to a new JSON file
def write_counts_to_file(counts, output_filepath):
    with open(output_filepath, 'w') as file:
        json.dump(counts, file, indent=4)

# Main function to orchestrate the flow
def main():
    filepath = '../glosses_transformed.json'
    output_filepath = 'output_counts.json'
    fields = [
        'Weak Hand',
        'Handshape Change',
        'Relation Between Articulators',
        'Location',
        'Contact Type',
        'Movement Shape',
        'Movement Direction',
        'Relative Orientation: Movement',
        'Relative Orientation: Location',
        'Orientation Change',
        'Repeated Movement',
        'Alternating Movement',
        'Virtual Object',
        'Phonology Other',
        'Mouth Gesture',
        'Mouthing',
        'Phonetic Variation',
    ]
    
    data = load_data(filepath)
    counts = count_values(data, fields)
    write_counts_to_file(counts, output_filepath)

if __name__ == "__main__":
    main()
