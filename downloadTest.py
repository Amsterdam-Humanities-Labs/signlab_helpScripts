import os
import json
import time
import datetime
import requests
import zipfile

cookies = {
        'cookie_notification': 'functional',
        'cookies_consent': '-1',
        'sessionid': os.environ.get('SIGNBANK_SESSIONID', ''),
        'csrftoken': os.environ.get('SIGNBANK_CSRFTOKEN', ''),
    }

def download_signbank_json():
    
    #we want to remove old flies from signbank folder first
    signbankFolder = "/web/helpScripts/signbank"
    for filename in os.listdir(signbankFolder):
        os.remove(f"{signbankFolder}/{filename}")
    
    #we want to get last time when the function was called
    #so we get json file signBankCSVDownloader.json
    with open("/web/helpScripts/signBankCSVDownloader.json", "r") as file:
        data = json.load(file)
        
    #if the file doesnt have json, then we create new one
    if not data:
        data = []
        #we add service, date and first_today to the file
        data.append({"service": "signBankCSVDownloader", "date": 0, "first_today": time.strftime("")})
        
    
    #then we get the last time when the function was called, if its empty then we set it to 0
    last_time = 0
    print(data)
    for item in data:
        if item["service"] == "signBankCSVDownloader":
            last_time = item["date"]
            first_today = item["first_today"]
            break

    #if first_today has date of today, then we dont set last_time to 0
    #if first_today has date of yesterday, then we set last_time to 0
    if first_today != time.strftime("%Y-%m-%d"):
        last_time = 1704067200 #1 january 2024
    else:
        last_time = datetime.datetime.strptime(str(last_time), '%Y-%m-%d %H:%M:%S %Z')   # last_time_dt -= datetime.timedelta(seconds=30)
        last_time = int(last_time.timestamp())

    
    print(last_time)
    url = "https://signbank.cls.ru.nl/dictionary/package/?extended_fields=true&since_timestamp=" + str(last_time)
    print(url)
    r = requests.get(url, cookies=cookies)
    with open("signbank.zip", "wb") as file:
        file.write(r.content)
    
    try:
        with zipfile.ZipFile("/web/signbank.zip", 'r') as zip_ref:
            zip_ref.extractall(signbankFolder)
    except zipfile.BadZipFile:
        print("Error: Bad zip file. Operation stopped.")
        return  # Stop the operation

    
        
        
download_signbank_json()