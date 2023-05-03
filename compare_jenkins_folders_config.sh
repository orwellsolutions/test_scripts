#!/bin/bash

# Ensure that two arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <folder1> <folder2>"
    exit 1
fi

# Check if both arguments are directories
if [ ! -d "$1" ] || [ ! -d "$2" ]; then
    echo "Both arguments should be directories"
    exit 1
fi

# Assign the folder paths to variables
folder1="$1"
folder2="$2"

# Find subdirectories up to 2 folder depth in both directories
find "$folder1" "$folder2" -maxdepth 2 -mindepth 2 -type d | sort | uniq > all_folders.txt

# Loop through each folder and compare config.xml files
while read -r folder_path; do
    # Remove the base folder path to get the relative path
    relative_path=${folder_path#*$folder1}
    relative_path=${relative_path#*$folder2}
    config_file1="$folder1$relative_path/config.xml"
    config_file2="$folder2$relative_path/config.xml"

    if [ -f "$config_file1" ] && [ -f "$config_file2" ]; then
        # Both config.xml files exist, compare them
        diff_output=$(diff -q "$config_file1" "$config_file2")
        if [ -n "$diff_output" ]; then
            echo "Difference found in $relative_path:"
            echo "$diff_output"
        fi
    elif [ ! -f "$config_file1" ] && [ ! -f "$config_file2" ]; then
        # Ignore cases where config.xml is missing from both folders
        continue
    else
        # One of the config.xml files is missing, copy the existing one to the other folder
        echo "config.xml missing in $relative_path:"
        if [ -f "$config_file1" ]; then
            echo "  Copying $config_file1 to $config_file2"
            cp "$config_file1" "$config_file2"
        else
            echo "  Copying $config_file2 to $config_file1"
            cp "$config_file2" "$config_file1"
        fi
    fi
done < all_folders.txt

# Clean up temporary file
rm all_folders.txt
