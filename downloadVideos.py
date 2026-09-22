import json
import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

cookies = {
        'cookie_notification': 'functional',
        'cookies_consent': '-1',
        'sessionid': os.environ.get('SIGNBANK_SESSIONID', ''),
        'csrftoken': os.environ.get('SIGNBANK_CSRFTOKEN', ''),
    }

def download_video(url, filename):
    video_path = f"/web/uploads/{filename}.mp4"
    try:
        r = requests.get(url, cookies=cookies)
        if r.status_code == 200:
            with open(video_path, "wb") as file:
                file.write(r.content)
            print(f"Downloaded {filename}.mp4")
        else:
            print(f"Failed to download {filename}.mp4. Status code: {r.status_code}")
    except requests.RequestException as e:
        print(f"Error downloading {filename}.mp4: {e}")

def download_videos():
    with open("/web/glosses_transformed.json", "r") as file:
        data = json.load(file)

    tasks = []
    with ThreadPoolExecutor(max_workers=1) as executor:
        for item in data:
            for key, value in item.items():
                if "Video" in value:
                    filename = value["Annotation ID Gloss: Dutch"]
                    url = value["Video"]
                    tasks.append(executor.submit(download_video, url, filename))
        
        for future in as_completed(tasks):
            try:
                future.result()
            except Exception as e:
                print(f"Error during download: {e}")

def generate_thumbnail_for_video(filename):
    video_path = f"/web/uploads/{filename}.mp4"
    thumbnail_path = f"/web/uploads/{filename}.jpg"
    try:
        # Use ffmpeg to generate thumbnail
        command = f"nice -19 ffmpeg -y -i {video_path} -ss 00:00:01.000 -vframes 1 {thumbnail_path} -loglevel quiet"
        os.system(command)
        print(f"Generated thumbnail for {filename}.mp4")
    except Exception as e:
        print(f"Error generating thumbnail for {filename}.mp4: {e}")

def generate_thumbnails():
    with open("/web/glosses_transformed.json", "r") as file:
        data = json.load(file)

    tasks = []
    with ThreadPoolExecutor(max_workers=1) as executor:
        for item in data:
            for key, value in item.items():
                if "Video" in value:
                    filename = value["Annotation ID Gloss: Dutch"]
                    tasks.append(executor.submit(generate_thumbnail_for_video, filename))
        
        for future in as_completed(tasks):
            try:
                future.result()
            except Exception as e:
                print(f"Error during thumbnail generation: {e}")

if __name__ == "__main__":
    download_videos()  # Uncomment if you want to download videos first
    generate_thumbnails()
