filePath="../servicesRecords.json"
service_name="convert"
current_date=$(date "+%Y-%m-%d %H:%M:%S")

# Check if the service entry exists
found=$(jq --arg service_name "$service_name" '.[] | select(.service == $service_name)' "$filePath")

if [[ -z $found ]]; then
    # Append new record if not found
    jq --arg service_name "$service_name" --arg date "$current_date" \
       '. += [{"service": $service_name, "date": $date}]' "$filePath" > tmp.json
else
    # Update existing record if found
    jq --arg service_name "$service_name" --arg date "$current_date" \
       'map(if .service == $service_name then .date = $date else . end)' "$filePath" > tmp.json
fi

# Safely move the temporary file back to the original file
mv tmp.json "$filePath"
