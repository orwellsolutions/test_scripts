import requests
import time
import os
import subprocess

# Prompt user for input
source_gitlab_instance = input("Enter the URL of the original GitLab instance: ")
target_gitlab_instance = input("Enter the URL of the new GitLab instance: ")

source_token = input("Enter the access token for the original GitLab instance: ")
target_token = input("Enter the access token for the new GitLab instance: ")

source_username = input("Enter the username for the original GitLab instance: ")
source_project_name = input("Enter the project name for the original GitLab instance: ")

target_username = input("Enter the username for the new GitLab instance: ")
target_project_name = input("Enter the project name for the new GitLab instance: ")

# Check if the .gitlab-ci.yml file exists in the root of the repository
headers = {"PRIVATE-TOKEN": source_token}
file_check_url = f"{source_gitlab_instance}/api/v4/projects/{source_username}%2F{source_project_name}/repository/files/.gitlab-ci.yml"

response = requests.get(file_check_url, headers=headers)

if response.status_code == 200:
    print("The .gitlab-ci.yml file exists in the root of the repository. Aborting operation.")
    exit()

# Run a bash command against the original repo
bash_command = "bash_command"  # Replace this with your command
process = subprocess.run(bash_command, shell=True, check=True, text=True, capture_output=True)

if "No secrets found" not in process.stdout:
    print("Secrets found in the repository. Aborting operation.")
    exit()

# Step 1: Export the project from the source GitLab instance
export_url = f"{source_gitlab_instance}/api/v4/projects/{source_username}%2F{source_project_name}/export"
response = requests.post(export_url, headers=headers)

if response.status_code == 202:
    print("Export started successfully.")
else:
    print("Failed to start export.")

# Step 2: Download the export file
while True:
    response = requests.get(export_url, headers=headers)
    if response.json()["export_status"] == "finished":
        download_url = response.json()["download_url"]
        break
    time.sleep(1)

response = requests.get(f"{source_gitlab_instance}{download_url}", headers=headers, stream=True)

with open("project_export.tar.gz", "wb") as f:
    for chunk in response.iter_content(chunk_size=8192):
        f.write(chunk)

# Step 3: Create a new project on the target GitLab instance
headers = {"PRIVATE-TOKEN": target_token}
create_project_url = f"{target_gitlab_instance}/api/v4/projects"

data = {"name": target_project_name, "namespace_id": target_username}
response = requests.post(create_project_url, headers=headers, json=data)

if response.status_code == 201:
    print("Project created successfully.")
else:
    print("Failed to create project.")

# Step 4: Import the project to the target GitLab instance
target_project_id = response.json()["id"]

headers = {"PRIVATE-TOKEN": target_token}
import_url = f"{target_gitlab_instance}/api/v4/projects/{target_project_id}/import"

with open("project_export.tar.gz", "rb") as f:
    data = {"namespace": target_username, "file": f}
    response = requests.post(import_url, headers=headers, files=data)

if response.status_code == 201:
    print("Import started successfully.")
else:
    print("Failed to start import.")

# Remove the downloaded file
os.remove("project_export.tar.gz")
