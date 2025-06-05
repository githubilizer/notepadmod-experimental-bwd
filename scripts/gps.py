#!/usr/bin/env python3

# /scripts/gps.py

import sys
import argparse
import re
import os
import shutil
import time  # For timestamp
from openai import OpenAI  # Updated import syntax
import logging

# Import the API key utility
from api_utils import get_api_key

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
ELECTRIC_BLUE = "\033[38;2;44;117;255m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"

def get_openai_client():
    """Get OpenAI client using API key from file or environment."""
    api_key = get_api_key()
    if not api_key:
        logging.error("OpenAI API key not found. Please create apikeynew_13012025.txt in the project root directory or set OPENAI_API_KEY environment variable.")
        print(f"{RED}[ERROR] OpenAI API key not found. Please create apikeynew_13012025.txt in the project root directory or set OPENAI_API_KEY environment variable.")
        sys.exit(1)
    return OpenAI(api_key=api_key)

def setup_logging():
    """Configure logging settings."""
    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Set up file handler
    file_handler = logging.FileHandler('/home/j/Desktop/code/notepadMOD/logs/gps.log', mode='w')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Set up console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    logging.info("Logging initialized - outputs will appear in both console and gps.log")

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

def clean_segment(segment, client=None):
    """
    Extract decimal GPS coordinates from the text segment using OpenAI's LLM.

    Returns:
    - coordinates (str): The decimal GPS coordinates.
    """
    try:
        if client is None:
            client = get_openai_client()

        # Prepare the instruction prompt to extract GPS coordinates
        instruction = """
Please extract or convert any GPS coordinates in the following text to decimal format (latitude, longitude).
Nb. This location is likely Russia or Ukraine. 
Only return the coordinates in decimal format, nothing else.

Text:
{segment}

Coordinates:
"""
        prompt = instruction.format(segment=segment)

        logging.info(f"Processing segment: {segment}")
        logging.info("Connecting to OpenAI API...")

        # Make the API call
        response = client.chat.completions.create(
            model="gpt-4.1-mini",  # Using a valid model name
            messages=[
                {"role": "user", "content": prompt},
            ],
            max_tokens=100,  # Reduced since we only need coordinates
            n=1,
            stop=None,
            temperature=0
        )

        # Extract the assistant's reply
        assistant_reply = response.choices[0].message.content.strip()

        # Log the raw API response with the specific format the GUI is looking for
        print(f"OpenAI API response: {assistant_reply}")
        logging.info(f"OpenAI API response: {assistant_reply}")

        return assistant_reply

    except Exception as e:
        error_message = f"Error processing segment: {e}"
        logging.error(error_message)
        print(f"Error: {error_message}")  # Print error to stdout for GUI to catch
        # On error, return the original segment
        return segment

def main():
    setup_logging()
    logging.info("Script started.")
    print("[INFO] Script started.")

    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Extract GPS coordinates from text.")
    parser.add_argument('input_file', help='Path to the input text file.')
    args = parser.parse_args()

    input_file = args.input_file

    # Initialize OpenAI client
    client = get_openai_client()

    # Read the input file
    try:
        print(f"[INFO] Reading input file '{input_file}'...")
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        logging.info(f"Read input file '{input_file}' successfully.")
        print(f"[INFO] Read input file '{input_file}' successfully.")
    except FileNotFoundError:
        logging.error(f"Input file '{input_file}' not found.")
        print(f"[ERROR] Input file '{input_file}' not found.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error reading input file: {e}")
        print(f"[ERROR] Error reading input file: {e}")
        sys.exit(1)

    # Parse the segments with positions
    segments = parse_segments_with_positions(content)

    if not segments:
        print(f"[WARNING] No segments found between '111' markers. Please check the input file.")
        logging.warning("No segments found between '111' markers.")
        sys.exit(1)

    # Initialize new content parts
    new_content_parts = []
    last_end = 0

    print("[INFO] Starting to process and update segments...")
    for idx, segment in enumerate(segments, 1):
        print(f"[INFO] Processing segment {idx}...")

        # **Modify this line to exclude the '111' markers by appending content up to the start of the segment**
        new_content_parts.append(content[last_end:segment['start']])

        # Update last_end to the end of the segment (after the second '111')
        last_end = segment['end']

        # Process the segment by extracting GPS coordinates
        updated_content = clean_segment(segment['content'], client)

        # Insert only the updated content with proper spacing
        inserted_content = updated_content

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
        print(f"{GREEN}[INFO] Updated {ELECTRIC_BLUE}'{input_file}' {GREEN}successfully.")
    except Exception as e:
        logging.error(f"Error writing to input file: {e}")
        print(f"[ERROR] Error writing to input file: {e}")
        sys.exit(1)

    print(f"{GREEN}[INFO] Script completed successfully.")

if __name__ == "__main__":
    main() 
