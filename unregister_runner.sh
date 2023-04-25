To have your GitLab runners unregister themselves when they receive a shutdown signal, you can create a script that runs on shutdown and sends an unregister command to the GitLab instance. You can achieve this by using the GitLab Runner API and the instance metadata to identify the runner you want to unregister.

Follow these steps to create a shutdown script:

First, create a script file, e.g., unregister_runner.sh, with the following content:
bash
Copy code
#!/bin/bash

# Replace with your GitLab instance URL and access token
GITLAB_INSTANCE_URL="https://gitlab.com"
GITLAB_ACCESS_TOKEN="your_access_token"

# Get the runner's token from the GitLab Runner configuration
RUNNER_TOKEN=$(cat /etc/gitlab-runner/config.toml | grep "token" | awk -F '"' '{print $2}')

# Unregister the runner using the API
curl --request DELETE "${GITLAB_INSTANCE_URL}/api/v4/runners" \
     --header "PRIVATE-TOKEN: ${GITLAB_ACCESS_TOKEN}" \
     --form "token=${RUNNER_TOKEN}"
Replace your_access_token with your GitLab access token. You can create an access token by following the instructions in the GitLab documentation.

Make the script executable:

bash
Copy code
chmod +x unregister_runner.sh
Move the script to the /etc/init.d directory, so it's executed on shutdown:
bash
Copy code
sudo mv unregister_runner.sh /etc/init.d/
Create a symbolic link to the script in the appropriate runlevel directory. For example, for runlevel 0 (shutdown) and 6 (reboot), run:
bash
Copy code
sudo ln -s /etc/init.d/unregister_runner.sh /etc/rc0.d/K20unregister_runner
sudo ln -s /etc/init.d/unregister_runner.sh /etc/rc6.d/K20unregister_runner
Now, when your GitLab Runner instances receive a shutdown signal, they will execute the unregister_runner.sh script and unregister themselves from your GitLab instance.
