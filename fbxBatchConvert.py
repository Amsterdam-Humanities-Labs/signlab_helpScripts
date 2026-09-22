import os
import requests

# Path to the directory containing the FBX files
fbx_directory = '/web/helpScripts/fbx'

# URL to upload the files
upload_url = 'https://leffe.science.uva.nl:8043/fbx2glb/upload'

# Iterate over each file in the directory
for filename in os.listdir(fbx_directory):
    if filename.endswith('.fbx'):
        file_path = os.path.join(fbx_directory, filename)
        
        # Open the file and prepare it for upload
        with open(file_path, 'rb') as f:
            files = {'file': f}
            
            # Send a POST request to the upload URL with SSL certificate verification disabled
            response = requests.post(upload_url, files=files, verify=False)
            
            # Check the response status code
            if response.status_code == 200:
                print(f'Successfully uploaded {filename}')
            else:
                print(f'Failed to upload {filename}')
                print(response.text)
