#!/bin/bash

# Source Nexus 3 Repository Configuration
SOURCE_REPO_URL="http://localhost:8081/repository/source-repo/"
SOURCE_REPO_USER="admin"
SOURCE_REPO_PASS="admin123"

# Target Nexus 3 Repository Configuration
TARGET_REPO_URL="http://localhost:8081/repository/target-repo/"
TARGET_REPO_USER="admin"
TARGET_REPO_PASS="admin123"

# Export items from source repository
ITEMS=$(curl -s -u ${SOURCE_REPO_USER}:${SOURCE_REPO_PASS} "${SOURCE_REPO_URL}?describe=items" | jq -r '.items[].downloadUrl')

# Import items into target repository with their respective MIME types
for ITEM in ${ITEMS}; do
    MIME_TYPE=$(curl -sI -u ${SOURCE_REPO_USER}:${SOURCE_REPO_PASS} "${ITEM}" | grep "Content-Type" | awk '{print $2}')
    FILENAME=$(echo ${ITEM} | rev | cut -d'/' -f1 | rev)
    curl -u ${TARGET_REPO_USER}:${TARGET_REPO_PASS} --upload-file ${FILENAME} -H "Content-Type: ${MIME_TYPE}" "${TARGET_REPO_URL}${FILENAME}"
done
