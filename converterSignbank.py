import json

# Loading the original JSON 
# data into a dictionary
with open("glosses.json", "r") as file:
    data = json.load(file)

# Transforming the data
transformed_data = [{key: value} for key, value in data.items()]

# Converting the transformed data back to JSON
transformed_json = json.dumps(transformed_data, indent=4)


# Writing the transformed data to a new file
with open("../glosses_transformed.json", "w") as file:
    file.write(transformed_json)
    