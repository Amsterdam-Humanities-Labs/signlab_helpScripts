import json
import requests

def add_form_data(glos):
    # Define the URL
    url = "https://leffe.science.uva.nl:8043/createGlos.php"

    # Define the initial data to be sent
    allInputValues = [
        {"id": "user", "value": 1},  # Replace with the actual user ID
        {"id": "wieNaam", "value": 1},  # Replace with the actual logged-in user name
        {"id": "wie", "value": 1},  # Replace with the actual user ID
        {"id": "thema", "value": 'REFILM'},  # Replace with the selected theme
        {"id": "glosZoekInput", "value": glos},  # Add the GLOS value
    ]

    # Convert the data to JSON format
    payload = {'createData': json.dumps(allInputValues)}

    # Send the initial POST request
    try:
        response = requests.post(url, data=payload, verify=False)  # verify=False to ignore SSL warnings
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Check if the response is in JSON format and process it
        try:
            response_data = response.json()
            print("Response data:", response_data)

            # Check the callback type in the response
            if response_data.get('callback') == 'glosAlreadyExist':
                print("GLOS already exists. Skipping next request.")
                return  # Skip the next request
            else:
                # Prepare and send the second request with the confirm value if GLOS does not already exist
                allInputValues.append({"id": "confirm", "value": "glosCreate"})
                payload = {'createData': json.dumps(allInputValues)}

                # Send the POST request again with the confirm value
                confirm_response = requests.post(url, data=payload, verify=False)
                confirm_response.raise_for_status()
                print("Request with confirm was successful:", confirm_response.text)
        except json.JSONDecodeError:
            print("Failed to decode JSON response:", response.text)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

# Call the function with a test value
add_form_data("leeghoofd-c")
