#!/usr/bin/env python3

# /modules/shrtn.py

# How to use: python3 cleanerAI_v1.py inputfile.vhd
# This script updates the input file in place after creating a backup.

# This is basically the AI CORE Script, but inside of '111's instead

import sys
import argparse
import re
import os
import shutil
import time  # For timestamp
from openai import OpenAI  # Keep original import
import logging

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
ELECTRIC_BLUE = "\033[38;2;44;117;255m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
RESET = "\033[0m"  # Added RESET to reset text color

# Set your OpenAI API key securely using an environment variable
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    print(f"{RED}[ERROR] OPENAI_API_KEY environment variable not set.{RESET}")
    sys.exit(1)

client = OpenAI(api_key=api_key)  # Keep original API KEY syntax

def setup_logging():
    """Configure logging settings."""
    logging.basicConfig(
        filename='/home/j/Desktop/code/notepadMOD/logs/cleanerAI_shrtn.log',
        filemode='w',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def parse_segments_with_positions(content):
    """
    Extract segments that are between "111\n" and "\n111", along with their positions.
    """
    pattern = r'(111\s*\n(.*?)\n\s*111)'
    matches = list(re.finditer(pattern, content, re.DOTALL))
    segments = []
    for match in matches:
        full_match = match.group(1)
        segment_content = match.group(2)
        start = match.start()
        end = match.end()
        segments.append({'full_match': full_match, 'content': segment_content, 'start': start, 'end': end})
    logging.info(f"Parsed {len(segments)} segments.")
    print(f"[INFO] Parsed {len(segments)} segments.")
    return segments

def clean_segment(segment):
    """
    Shorten the text segment using OpenAI's LLM with the specified instruction.

    Returns:
    - processed_text (str): The shortened text.
    """
    try:
        # Prepare the instruction prompt
        instruction = """
Please shorten the following text while preserving its original meaning and key information.

Original Text:
{segment}

Shortened Text:
""".strip()

        prompt = instruction.format(segment=segment)

        print("[INFO] Connecting to OpenAI API to process the segment...")
        logging.info("[INFO] Connecting to OpenAI API to process the segment...")

        # Make the API call
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Keep original model name
            messages=[
                {"role": "user", "content": prompt},
            ],
            max_tokens=300,  # Adjust as needed
            n=1,
            stop=None,
            temperature=0  # As per your working structure
        )

        # Extract the assistant's reply
        assistant_reply = response.choices[0].message.content.strip()

        # Log and print the raw API response
        print(f"[INFO] OpenAI API response: {assistant_reply}")
        logging.info(f"OpenAI API response: {assistant_reply}")

        return assistant_reply

    except Exception as e:
        error_message = f"Error processing segment: {e}"
        print(f"[ERROR] {error_message}")
        logging.error(error_message)
        # On error, return the original segment
        return segment

def main():
    setup_logging()
    logging.info("Script started.")
    print("[INFO] Script started.")

    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Process and update segments in the input file.")
    parser.add_argument('input_file', help='Path to the input text file.')
    args = parser.parse_args()

    input_file = args.input_file

    # Read the input file
    try:
        print(f"[INFO] Reading input file '{input_file}'...")
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        logging.info(f"Read input file '{input_file}' successfully.")
        print(f"[INFO] Read input file '{input_file}' successfully.")
    except FileNotFoundError:
        logging.error(f"Input file '{input_file}' not found.")
        print(f"{RED}[ERROR] Input file '{input_file}' not found.{RESET}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error reading input file: {e}")
        print(f"{RED}[ERROR] Error reading input file: {e}{RESET}")
        sys.exit(1)

    # Create a backup of the input file in the specified directory with timestamp
    try:
        # Get the base filename without the path
        base_filename = os.path.basename(input_file)
        # Remove the extension from the filename
        filename_without_ext = os.path.splitext(base_filename)[0]
        # Get the current timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        # Construct the backup filename
        backup_filename = f"{filename_without_ext}_{timestamp}.vhd"
        # Specify the backup directory
        backup_directory = "/home/j/Desktop/Finals/"
        # Ensure the backup directory exists
        if not os.path.exists(backup_directory):
            os.makedirs(backup_directory)
        # Full backup path
        backup_file = os.path.join(backup_directory, backup_filename)
        # Copy the input file to the backup location
        shutil.copyfile(input_file, backup_file)
        logging.info(f"Created backup file '{backup_file}'.")
        print(f"[INFO] Created backup file '{backup_file}'.")
    except Exception as e:
        logging.error(f"Error creating backup file: {e}")
        print(f"{RED}[ERROR] Error creating backup file: {e}{RESET}")
        sys.exit(1)

    # Parse the segments with positions
    segments = parse_segments_with_positions(content)

    if not segments:
        print(f"{YELLOW}[WARNING] No segments found between '111' markers. Please check the input file.{RESET}")
        logging.warning("No segments found between '111' markers.")
        sys.exit(1)

    # Initialize new content parts
    new_content_parts = []
    last_end = 0

    print("[INFO] Starting to process and update segments...")
    for idx, segment in enumerate(segments, 1):
        print(f"[INFO] Processing segment {idx}...")

        # Append content before the current segment
        new_content_parts.append(content[last_end:segment['start']])

        # Update last_end to the end of the segment (after the second '111')
        last_end = segment['end']

        # Process the segment with the new instruction
        updated_content = clean_segment(segment['content'])

        # Insert only the updated content with proper spacing
        inserted_content = '\n\n' + updated_content + '\n\n'

        # Append the inserted content
        new_content_parts.append(inserted_content)

    # Append any remaining content after the last segment
    new_content_parts.append(content[last_end:])

    # Reconstruct the new content
    new_content = ''.join(new_content_parts)

    # Write back to the input file
    try:
        print(f"[INFO] Writing back to the input file '{input_file}'...")
        with open(input_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        logging.info(f"Updated '{input_file}' successfully.")
        print(f"{GREEN}[INFO] Updated {ELECTRIC_BLUE}'{input_file}' {GREEN}successfully.{RESET}")
    except Exception as e:
        logging.error(f"Error writing to input file: {e}")
        print(f"{RED}[ERROR] Error writing to input file: {e}{RESET}")
        sys.exit(1)

    print(f"{GREEN}[INFO] Script completed successfully.{RESET}")

if __name__ == "__main__":
    main()

