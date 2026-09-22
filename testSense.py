import requests
import json
from bs4 import BeautifulSoup

headers = {
    "Authorization": "Bearer UlerhGrfFpU03RD3",
}

url = "https://signbank.cls.ru.nl/dictionary/api_update_gloss/5/45834/"

data = {
    "Senses": {
        "en": [
            ["hire"],
            ["rent, lease"]
        ],
        "nl": [
            ["huren"],
            ["huren"]
        ]
    }
}


print("Data to be sent:")
print(data)

# # Sending the data as raw JSON
# response = requests.post(url, headers=headers, data=data)

# print(f"Response Status Code: {response.status_code}")

# if response.status_code == 200:
#     try:
#         # Parse JSON response
#         json_response = response.json()
#         print("JSON Response:")
#         print(json.dumps(json_response, indent=4))
#     except json.JSONDecodeError:
#         print("Failed to decode JSON response.")
# elif response.status_code == 500:
#     # Save response.text to an HTML file
#     with open("error_response.html", "w") as file:
#         file.write(response.text)
#     print("HTML error response saved to 'error_response.html'.")

#     # Parse the HTML response with BeautifulSoup
#     soup = BeautifulSoup(response.text, 'html.parser')

#     # Find all <li> tags with class "frame user"
#     li_elements = soup.find_all('li', class_='frame user')

#     # Extract and print the content of the <li> elements
#     print("Parsed <li> elements with class 'frame user':")
#     for li in li_elements:
#         text = li.get_text()
#         if text.strip() != "":
#             print(text.strip())
# else:
#     print(f"Unhandled status code: {response.status_code}")
#     print("Response Text:")
#     print(response.text)
