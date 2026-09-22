import time
import json

file_path = "/web/servicesRecords.json"
    
# Load the JSON data from the file
with open(file_path, "r") as file:
    data = json.load(file)

# Define the service name
service_name = "signBankCSVDownloader"

# Search for an existing entry with the same service name
found = False
for entry in data:
    if entry['service'] == service_name:
        # Update the date for the existing entry
        entry['date'] = time.strftime("%Y-%m-%d %H:%M:%S")
        found = True
        break

# If no existing entry found, append a new one
if not found:
    data.append({"service": service_name, "date": time.strftime("%Y-%m-%d %H:%M:%S")})

    print(data)
print(entry)