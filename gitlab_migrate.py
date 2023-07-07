import requests
import time
import subprocess
import base64

source_gitlab_instance = input("Please enter the source GitLab instance URL (default: PUT GITLAB SOURCE URL HERE): ") or "PUT GITLAB SOURCE URL HERE"
destination_gitlab_instance = input("Please enter the destination GitLab instance URL: ")
source_project_path = input("Please enter the source project path: ")
destination_project_path = input("Please enter the destination project path: ")

source_private_token = input("Please enter the source private token: ")
destination_private_token = input("Please enter the destination private token: ")

bash_command = f"your_bash_command {source_project_path}"

# Run bash command and get output
output = subprocess.check_output(['bash','-c', bash_command]).decode().split('\n')

# Check the output
if any("No secrets found" in line for line in output):
    print("'No secrets found' found in the repository. Continuing operation.")
else:
    print("Secrets found in the repository. Aborting operation.")
    exit()

# Check if .gitlab-ci.yml exists in the repository
response = requests.get(f"{source_gitlab_instance}/{source_project_path}/-/blob/master/.gitlab-ci.yml", headers={"PRIVATE-TOKEN": source_private_token}, verify=False)

if response.status_code == 200:
    print("The repository contains a .gitlab-ci.yml file. Aborting operation.")
    exit()

headers = {"PRIVATE-TOKEN": source_private_token}

# Request the export
response = requests.post(f"{source_gitlab_instance}/api/v4/projects/{source_project_path}/export", headers=headers, verify=False)

if response.status_code == 202:
    print("Export started successfully.")
else:
    print(f"Failed to start export: {response.json()}")  # print the API response
    exit()

# Get the export download link
while True:
    response = requests.get(f"{source_gitlab_instance}/api/v4/projects/{source_project_path}/export", headers=headers, verify=False)
    print(response.json())  # print the API response
    if response.json()["export_status"] == "finished":
        download_url = response.json()["download_url"]
        break
    time.sleep(1)

# Download the exported project
response = requests.get(download_url, headers=headers, verify=False)

with open("project_export.tar.gz", "wb") as f:
    f.write(response.content)

headers = {"PRIVATE-TOKEN": destination_private_token}

# Import the project into the new GitLab instance
with open("project_export.tar.gz", "rb") as f:
    data = {
        "file": f,
        "path": destination_project_path,
        "name": destination_project_path,
        "namespace": destination_project_path.split('/')[0]
    }
    response = requests.post(f"{destination_gitlab_instance}/api/v4/projects/import", headers=headers, data=data, verify=False)

if response.status_code == 201:
    print("Project imported successfully.")
else:
    print(f"Failed to import project: {response.json()}")  # print the API response
    exit()

# Wait for the import to finish
time.sleep(10)  # Adjust this sleep time as necessary

# Update README.md file in the new repository
new_content = f"This project has been moved to {destination_gitlab_instance}/{destination_project_path}"
b64_content = base64.b64encode(new_content.encode()).decode()  # README content must be base64 encoded

data = {
    "branch": "master",
    "commit_message": "Updated README with new project location",
    "actions": [
        {
            "action": "update",
            "file_path": "README.md",
            "content": b64_content
        }
    ]
}

response = requests.post(f"{destination_gitlab_instance}/api/v4/projects/{destination_project_path}/repository/commits", headers=headers, json=data, verify=False)

if response.status_code == 201:
    print("README.md updated successfully.")
else:
    print(f"Failed to update README.md: {response.json()}")  # print the API response
