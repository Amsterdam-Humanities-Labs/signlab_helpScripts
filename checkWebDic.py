import os
import json
import requests
import sys


headers = {
        "Authorization": 'Bearer ' + os.environ.get('SIGNBANK_API_KEY', ''),
    }


cookies = {
        'cookie_notification': 'functional',
        'cookies_consent': '-1',
        'sessionid': os.environ.get('SIGNBANK_SESSIONID', ''),
        'csrftoken': os.environ.get('SIGNBANK_CSRFTOKEN', ''),
    }


def openWebDic(gloss_id):
    data = {}
    #send POST request to https://signbank.cls.ru.nl/dictionary/api_update_gloss/5/{glossid}/
    url = "https://signbank.cls.ru.nl/dictionary/api_update_gloss/5/{glossid}/".format(glossid=gloss_id)
    
    
    data["In The Web Dictionary"] = "True"
        
    json_data = json.dumps(data)

    r = requests.post(url, headers=headers, data=json_data, verify=False)  # `verify=False` to ignore SSL certificate verification
    print(r.text)

    
    
    
    

def printWebDic():
    
    glosses = {}
    countGlosses = 0

    # Load JSON data
    # with open("/web/helpScripts/signbank/glosses_converted.json", "r") as file:
    #     glosses_data = json.load(file)
    with open("/web/glosses_transformed.json", "r") as file:
        glosses_data = json.load(file)

    # Function to get glosses from glosses data
    for gloss in glosses_data:
        for gloss_id, gloss_info in gloss.items():
            if gloss_id:
                if gloss_info.get("In The Web Dictionary") == "False":
                    countGlosses+=1
                    glosses[gloss_id] = {
                        "gloss_dutch": gloss_info.get("Annotation ID Gloss: Dutch"),
                        "In The Web Dictionary": gloss_info.get("In The Web Dictionary"),
                        # we also want to get video link
                        "Video": gloss_info.get("Video"),
                        "Affiliation": gloss_info.get("Affiliation"),
                    }
                    
                    if gloss_info.get("Affiliation")[0] == "UvA":
                        #when web dic is false, then execute openWebDic(gloss_id) function
                        print(gloss_id, gloss_info.get("Annotation ID Gloss: Dutch"), gloss_info.get("In The Web Dictionary"), gloss_info.get("Video"), gloss_info.get("Affiliation"))
                        openWebDic(gloss_id)
                        # sys.exit()
                #if In the web dictionary is false then output the int

                
    return glosses, countGlosses

lala, countGlosses = printWebDic()

for k, v in lala.items():
    print(k, v)
    
    
#print count of items in glosses
print(countGlosses)

#we are going to write to JSON file
with open("/web/glosses_not_in_webdic.json", "w") as file:
    json.dump(lala, file, indent=4)