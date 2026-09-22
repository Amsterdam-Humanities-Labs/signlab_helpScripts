import os
import requests
import json

cookies = {
        'cookie_notification': 'functional',
        'cookies_consent': '-1',
        'sessionid': os.environ.get('SIGNBANK_SESSIONID', ''),
        'csrftoken': os.environ.get('SIGNBANK_CSRFTOKEN', ''),
    }
def download_videos(last_time):
    #we have to download the videos again
    if last_time == 1704067200:
        
        #first we open the json file
        with open("/web/glosses_transformed.json", "r") as file:
            data = json.load(file)
            
        #then we forloop the json file and get Video from it
        for item in data:
            for gloss_id, gloss_info in item.items():
                video = gloss_info.get("Video")
                gloss_name = gloss_info.get("Annotation ID Gloss: Dutch")
                if video:
                    #we download the video
                    r = requests.get(video, cookies=cookies)
                    with open(f"/web/uploads/{gloss_name}.mp4", "wb") as file:
                        print(f"Downloading {gloss_name}")
                        file.write(r.content)
                        

download_videos(1704067200)