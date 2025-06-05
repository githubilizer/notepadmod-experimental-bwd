#!/usr/bin/env python3

# /modules/ts3334.py

import sys
import argparse
import re
import os
import shutil
import time  # For timestamp
import threading
import itertools
from openai import OpenAI
import logging

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
ELECTRIC_BLUE = "\033[38;2;44;117;255m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"

# Set your OpenAI API key securely using an environment variable
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Global flag for the spinner
spinner_running = False

def spinning_cursor():
    """Generator for spinning cursor animation frames."""
    while True:
        for cursor in '⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏':
            yield cursor

def update_status_with_spinner(window):
    """Updates the status bar with a spinning cursor."""
    spinner = spinning_cursor()
    global spinner_running
    start_time = time.time()
    
    while spinner_running:
        elapsed = int(time.time() - start_time)
        window.statusBar().showMessage(f"Processing with AI {next(spinner)} (Elapsed: {elapsed}s)")
        time.sleep(0.1)

def setup_logging():
    """Configure logging settings."""
    logging.basicConfig(
        filename='/home/j/Desktop/code/notepadMOD/logs/cleanerAI_ts3334.log',
        filemode='w',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def parse_segments_with_positions(content):
    """
    Extract segments that are between "444\n\n444\n" and "\n555", along with their positions.
    """
    pattern = r'(444\s*\n\n444\s*\n(.*?)\n\s*555)'
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

def clean_segment(segment, window=None):
    """
    Process the text segment using OpenAI's LLM with the specified instruction.

    Returns:
    - processed_text (str): The text generated according to the new instruction.
    """
    try:
        # Prepare the instruction prompt
        instructions = (
            """
Create a concise and cohesive update from multiple seemingly unrelated tweets that are actually about the same single event. Carefully connect the details while ensuring clarity, avoiding repetition, and providing proper context. Ensure towns and regions are accurately distinguished to prevent location confusion.


1) Avoid redundancy: Don't repeat the same information across different updates. If a governor reports the same number of UAVs being shot down in multiple posts, combine the info in a single sentence, and don't restate it unless there's new context.
2) Tone: Keep the tone casual but sharp, with some dry humor or light sarcasm where appropriate, but stick to the facts. This is not the place for sensationalism—focus on real-time updates without over-dramatizing.
3) Precision over generalities: Avoid vague phrases and abstract phases like the following: "tensions rise", "the situation unfolds",  "The situation has drawn significant attention".
ii) If there's a tangible update, such as reports of explosions, focus on that, and don't fall back on generalizations.
4) Concise updates: Each part of the update should be no more than 3-4 sentences long. Break the event into key points, covering the air defense response, actions by local authorities, and resident reports, with a focus on what is confirmed and what is happening right now.
5) Key details: When citing facts, ensure clarity in distinguishing between the town and region/Oblast, especially when talking about separate events in different parts of the same location.

Please action all the above numbered requests on my follow prompt dump of different tweets that are talking about the same story from different angles.

Text:
{segment}

Updated Text:
"""
        )
        prompt = instructions.format(segment=segment)

        print("[INFO] Connecting to OpenAI API to process the segment...")
        logging.info("[INFO] Connecting to OpenAI API to process the segment...")

        if window:
            window.statusBar().showMessage("Sending request to OpenAI API...")

        # Make the API call
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt},
            ],
            max_tokens=300,
            n=1,
            stop=None,
            temperature=0.7
        )

        # Extract the assistant's reply
        assistant_reply = response.choices[0].message.content.strip()

        # Log and print the raw API response
        print(f"[INFO] OpenAI API response: {assistant_reply}")
        logging.info(f"OpenAI API response: {assistant_reply}")

        if window:
            spinner_running = False
            if spinner_thread:
                spinner_thread.join()
            window.statusBar().showMessage("AI processing completed successfully!", 5000)

        return assistant_reply

    except Exception as e:
        error_message = f"Error processing segment: {e}"
        print(f"[ERROR] {error_message}")
        logging.error(error_message)
        
        if window:
            spinner_running = False
            if spinner_thread:
                spinner_thread.join()
            window.statusBar().showMessage(f"Error during AI processing: {str(e)}", 5000)
        
        # On error, return the original segment
        return segment

def create_backup(input_file):
    """
    Create a backup of the input file in /home/j/Desktop/Finals/ with the filename format:
    {filename}_4445_{HHMM}{am/pm}.vhd
    """
    try:
        base_filename = os.path.basename(input_file)
        filename_without_ext = os.path.splitext(base_filename)[0]
        time_str = time.strftime("%I%M%p").lower()
        backup_filename = f"{filename_without_ext}_4445_{time_str}.vhd"

        backup_directory = "/home/j/Desktop/Finals/"
        os.makedirs(backup_directory, exist_ok=True)

        backup_file = os.path.join(backup_directory, backup_filename)
        shutil.copyfile(input_file, backup_file)

        logging.info(f"Created backup file '{backup_file}'.")
        print(f"[INFO] Created backup file '{backup_file}'.")
        return backup_file

    except Exception as e:
        logging.error(f"Error creating backup file: {e}")
        print(f"{RED}[ERROR] Error creating backup file: {e}{RESET}")
        sys.exit(1)

def main():
    setup_logging()
    logging.info("Script started.")
    print("[INFO] Script started.")

    if not os.getenv('OPENAI_API_KEY'):
        error_message = "OpenAI API key is not set. Please set the 'OPENAI_API_KEY' environment variable."
        print(f"{RED}[ERROR] {error_message}{RESET}")
        logging.error(error_message)
        sys.exit(1)

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

    # Create a backup
    create_backup(input_file)

    # Parse segments
    segments = parse_segments_with_positions(content)

    if not segments:
        warning_message = ("No segments found where '444' and '555' lines appear alone. "
                           "Please check the input file.")
        print(f"{YELLOW}[WARNING] {warning_message}{RESET}")
        logging.warning(warning_message)
        sys.exit(1)

    new_content_parts = []
    last_end = 0

    print("[INFO] Starting to process and update segments...")
    for idx, segment in enumerate(segments, 1):
        print(f"[INFO] Processing segment {idx}...")

        # Append everything up to the segment
        new_content_parts.append(content[last_end:segment['start']])

        # Clean the segment's content
        updated_content = clean_segment(segment['context_444'], segment['content_555'])

        # Now we remove the 444/444/555 tags entirely, but place 3 extra newline breaks 
        # (to replace the 'second 444' line) before the updated text:
        #
        #   context_444
        #   <--- 3 extra blank lines here --->
        #   updated_content
        #
        segment_replacement = (
            f"{segment['context_444']}"
            f"\n\n\n\n"  # 1 normal + 3 additional blank lines = 4 newlines total
            f"{updated_content}\n"
        )
        new_content_parts.append(segment_replacement)

        last_end = segment['end']

    # Append any remaining content after the last segment
    new_content_parts.append(content[last_end:])

    new_content = ''.join(new_content_parts)

    # Write the modified content back to the input file
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

