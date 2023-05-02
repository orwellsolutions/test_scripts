#!/bin/bash

# Ensure that two arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <jenkins_folder1> <jenkins_folder2>"
    exit 1
fi

# Check if both arguments are directories
if [ ! -d "$1" ] || [ ! -d "$2" ]; then
    echo "Both arguments should be directories"
    exit 1
fi

# Assign the folder paths to variables
jenkins_folder1="$1"
jenkins_folder2="$2"

# Find all subfolders containing config.xml in both directories
find "$jenkins_folder1" "$jenkins_folder2" -type f -name 'config.xml' | sed "s#\(.*\)/config.xml#\1#g" | sort > folders_with_config.txt

# Loop through each folder and compare config.xml files
while read -r folder_path; do
    folder_name=$(basename "$folder_path")
    config_file1="$jenkins_folder1/$folder_name/config.xml"
    config_file2="$jenkins_folder2/$folder_name/config.xml"

    if [ -f "$config_file1" ] && [ -f "$config_file2" ]; then
        # Both config.xml files exist, compare them
        diff_output=$(diff -q "$config_file1" "$config_file2")
        if [ -n "$diff_output" ]; then
            echo "Difference found in $folder_name:"
            echo "$diff_output"
        fi
    else
        # One of the config.xml files is missing
        echo "config.xml missing in $folder_name:"
        [ ! -f "$config_file1" ] && echo "  $config_file1"
        [ ! -f "$config_file2" ] && echo "  $config_file2"
    fi
done < folders_with_config.txt

# Clean up temporary file
rm folders_with_config.txt
