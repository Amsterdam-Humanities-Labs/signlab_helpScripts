import re
import json
from typing import List, Dict, Optional


def increment_filename(filename: str, increment: int = 2) -> Optional[str]:
    """
    Increments the numerical part of the filename by the specified increment.
    
    Example:
        'left_1001.MP4' with increment=2 becomes 'left_1003.MP4'
    
    Args:
        filename (str): The original filename.
        increment (int): The value to add to the numerical part. Defaults to 2.
    
    Returns:
        Optional[str]: The incremented filename, or None if no numerical part is found.
    """
    if not filename:
        return None
    # Search for an underscore followed by digits
    match = re.search(r'_(\d+)', filename)
    if match:
        number = int(match.group(1))
        new_number = number + increment
        # Replace the old number with the new incremented number, preserving leading zeros
        new_filename = re.sub(r'_(\d+)', f'_{new_number}', filename)
        return new_filename
    return None


def fill_missing_values(records: List[Dict]) -> List[Dict]:
    """
    Fills in missing values by adding 2 to the numerical part of the previous glosid's filenames.
    
    Args:
        records (List[Dict]): The list of records to process.
    
    Returns:
        List[Dict]: The list of records with missing values filled.
    """
    # Sort records based on glosid numerically
    sorted_records = sorted(
        records, 
        key=lambda x: int(x['glosid']) if x['glosid'] and x['glosid'].isdigit() else 0
    )
    previous_record = None
    for record in sorted_records:
        if previous_record:
            for field in ['l', 'm', 'r', 'a', 'b']:
                if not record.get(field):
                    prev_field_value = previous_record.get(field)
                    if prev_field_value:
                        new_value = increment_filename(prev_field_value, 2)
                        record[field] = new_value
        previous_record = record
    return sorted_records


def main():
    """
    Main function to process video data from a JSON file, fill missing values, and write to an output JSON file.
    """
    # Define input and output file paths
    input_file = 'raw_video_data.txt'  # Replace with your input JSON file path
    output_file = 'video_data.json'     # Replace with your desired output JSON file path
    
    # Read raw data from the JSON input file
    try:
        with open(input_file, 'r') as file:
            records = json.load(file)
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return
    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON from '{input_file}'. Details: {e}")
        return

    # Validate that the JSON data is a list of dictionaries
    if not isinstance(records, list):
        print("Error: Invalid JSON format. Expected a list of records.")
        return
    for idx, record in enumerate(records):
        if not isinstance(record, dict):
            print(f"Error: Record at index {idx} is not a JSON object.")
            return
        if 'glosid' not in record:
            print(f"Error: Record at index {idx} is missing the 'glosid' field.")
            return

    # Fill missing values in the records
    filled_records = fill_missing_values(records)

    # Convert the processed records to a JSON string with indentation for readability
    try:
        json_output = json.dumps(filled_records, indent=2)
    except (TypeError, ValueError) as e:
        print(f"Error: Failed to serialize records to JSON. Details: {e}")
        return

    # Write the JSON output to the specified output file
    try:
        with open(output_file, 'w') as json_file:
            json_file.write(json_output)
        print(f"Success: Processed data has been written to '{output_file}'.")
    except IOError as e:
        print(f"Error: Failed to write to output file '{output_file}'. Details: {e}")


if __name__ == "__main__":
    main()
