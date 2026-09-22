import json

# Load data from results_output.json
with open('results_output.json', 'r') as file:
    data = json.load(file)

# Iterate through each item in data
for item in data:
    # Parse the nested JSON string in "response"
    details = json.loads(item["response"])
    # Check if the updatestatus is not "Success"
    if details.get("updatestatus") != "Success":
        print(details["glossid"])
