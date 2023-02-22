import os
import requests

# Set up the variables for the Nexus 3 repository
nexus_url = "https://your-nexus-repository-url.com"
repository = "your-repository-name"
auth = ("your-nexus-username", "your-nexus-password")

# Set up the variables for the local directory where artifacts will be downloaded
local_dir = "your-local-directory-path"

# Set up the variables for the Nexus 3 API
url = f"{nexus_url}/service/rest/v1/search/assets"
params = {"repository": repository}

# Iterate through all the artifacts in the repository and download them
while url:
    response = requests.get(url, auth=auth, params=params)
    data = response.json()
    items = data["items"]
    
    for item in items:
        download_url = item["downloadUrl"]
        artifact_path = item["path"].lstrip("/")
        artifact_filename = os.path.basename(artifact_path)
        artifact_dirname = os.path.dirname(artifact_path)
        local_path = os.path.join(local_dir, artifact_path)
        
        # Create the directory hierarchy in the local directory
        local_dirname = os.path.join(local_dir, artifact_dirname)
        if not os.path.exists(local_dirname):
            os.makedirs(local_dirname)
        
        print(f"Downloading {artifact_path} to {local_path}")
        response = requests.get(download_url, auth=auth)
        
        with open(local_path, "wb") as f:
            f.write(response.content)
    
    if "continuationToken" in data:
        url = f"{nexus_url}/service/rest/v1/search/assets?continuationToken={data['continuationToken']}"
    else:
        break

