#!/usr/bin/env python3

# /modules/cpyimagesv4.py


###################################################
#depricated, dont use#
###################################################

import os
import sys
import shutil
import urllib.parse

# Variables
input_file = sys.argv[1] if len(sys.argv) > 1 else None
search_dirs = [
    "/home/j/Desktop",
    "/home/j/Videos/untv/Ukraine",
    "/home/j/Downloads",
    "/home/j/Pictures/Screenshots",
]
destination_dir = "/home/j/Desktop/ScriptKing/temp_pics"
yesterday_dir = os.path.join(destination_dir, "yesterday")
greeting = "Hello, your file has been successfully copied!"
error_messages = []
generic_image = "/home/j/Desktop/YTs/aa UNTV Today/bsqs/bsq.png"
specific_bsqs_dir = "/home/j/Desktop/YTs/aa UNTV Today/bsqs"

# ANSI color codes
RED = '\033[0;31m'
GREEN = '\033[0;32m'
ORANGE = '\033[0;33m'
NC = '\033[0m'  # No Color

# Ensure the 'yesterday' directory exists
os.makedirs(yesterday_dir, exist_ok=True)

# Move any files from 'temp_pics' to 'yesterday', replacing any existing files
for item in os.listdir(destination_dir):
    s = os.path.join(destination_dir, item)
    d = os.path.join(yesterday_dir, item)
    if os.path.isfile(s):
        shutil.move(s, d)

# Check if the input file exists
if not input_file or not os.path.isfile(input_file):
    error_messages.append(f"{RED}Failure: Input file does not exist.{NC}")
    print('\n'.join(error_messages))
    sys.exit(1)

# Create the destination directory if it doesn't exist
os.makedirs(destination_dir, exist_ok=True)

# Initialize counters
count_success = 0
count_failure = 0
file_number = 1  # File numbering counter
last_copied_bsq = False  # Flag to track if the last copied file was bsq.png

# Build a file index to speed up searches
file_index = {}
for dir_path in search_dirs:
    for root, _, files in os.walk(dir_path):
        for name in files:
            file_index[name] = os.path.join(root, name)

# Read the input file line by line
with open(input_file, 'r') as f:
    lines = f.readlines()

for line in lines:
    line = line.strip()
    # Check if the line starts with '"Title:'
    if line.startswith('"Title:'):
        # Extract the title from the line
        title = line.strip('"').split(':', 1)[-1]

        if not title:
            error_messages.append(f"{RED}Failure: Could not extract title from line: {line}{NC}")
            count_failure += 1
            continue

        # Define the specific image path
        specific_image = os.path.join(specific_bsqs_dir, f"{title}.png")

        # Decide which image to copy
        if os.path.isfile(specific_image):
            image_to_copy = specific_image
            is_specific = True
        else:
            image_to_copy = generic_image
            is_specific = False

        # Decide whether to copy based on last_copied_bsq flag
        if is_specific or not last_copied_bsq:
            if os.path.isfile(image_to_copy):
                # Format the file number with leading zeros
                formatted_number = f"{file_number:03d}"

                # Extract basename of the image
                image_filename = os.path.basename(image_to_copy)

                # Construct new filename with number prefix
                new_image_filename = f"{formatted_number}_{image_filename}"

                # Copy the image with the new name
                shutil.copy(image_to_copy, os.path.join(destination_dir, new_image_filename))

                if is_specific:
                    print(f"{GREEN}Success: {greeting} Specific Image: {specific_image} was copied as {new_image_filename} to {destination_dir}{NC}")
                    last_copied_bsq = False
                else:
                    print(f"{GREEN}Success: {greeting} Generic Image: {generic_image} was copied as {new_image_filename} to {destination_dir}{NC}")
                    last_copied_bsq = True

                count_success += 1
                file_number += 1
            else:
                error_messages.append(f"{RED}Failure: Image {ORANGE}{image_to_copy}{RED} does not exist.{NC}")
                count_failure += 1
        else:
            print(f"{GREEN}Notice: Consecutive 'Title:' line detected. Skipping duplicate image copy.{NC}")
        continue  # Skip to the next line to prevent processing as media reference

    # Check if the line contains a media file reference
    if line.startswith('--'):
        # Skip lines that start with '--http'
        if line.startswith('--http'):
            print(f"{GREEN}Notice: Line starts with '--http'. Skipping copy and failure reporting.{NC}")
            continue

        # Extract the path or filename (remove all leading dashes)
        path_or_filename = line.lstrip('-')

        # Decode URL-encoded characters like '%20' to ' '
        path_or_filename = urllib.parse.unquote(path_or_filename)

        # Handle paths starting with 'file://'
        if path_or_filename.startswith('file://'):
            path_or_filename = path_or_filename[7:]  # Remove 'file://' prefix

        # Check if the path is absolute
        if os.path.isabs(path_or_filename):
            # Absolute path, copy directly
            if os.path.isfile(path_or_filename):
                # Format the file number with leading zeros
                formatted_number = f"{file_number:03d}"

                # Extract basename of the file
                filename = os.path.basename(path_or_filename)

                # Construct new filename with number prefix
                new_filename = f"{formatted_number}_{filename}"

                # Copy the file with the new name
                shutil.copy(path_or_filename, os.path.join(destination_dir, new_filename))

                print(f"{GREEN}Success: {greeting} File: {path_or_filename} was copied as {new_filename} to {destination_dir}{NC}")
                count_success += 1
                file_number += 1
                last_copied_bsq = False
            else:
                error_messages.append(f"{RED}Failure: File {ORANGE}{path_or_filename}{RED} not found.{NC}")
                count_failure += 1
        else:
            # Relative filename, search in the file index
            file_found = False
            if path_or_filename in file_index:
                find_result = file_index[path_or_filename]

                # Format the file number with leading zeros
                formatted_number = f"{file_number:03d}"

                # Extract basename of the file
                filename = os.path.basename(find_result)

                # Construct new filename with number prefix
                new_filename = f"{formatted_number}_{filename}"

                # Copy the file with the new name
                shutil.copy(find_result, os.path.join(destination_dir, new_filename))

                print(f"{GREEN}Success: {greeting} File: {find_result} was copied as {new_filename} to {destination_dir}{NC}")
                count_success += 1
                file_number += 1
                last_copied_bsq = False
                file_found = True
            else:
                error_messages.append(f"{RED}Failure: File {ORANGE}{path_or_filename}{RED} not found in the specified directories.{NC}")
                count_failure += 1

# Summary
print(f"{GREEN}Operation completed. {count_success} files copied successfully, {RED}{count_failure} files failed to copy.{NC}")

# Display all accumulated error messages at the bottom
print('\n'.join(error_messages))

