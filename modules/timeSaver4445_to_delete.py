#!/usr/bin/env python3

# /modules/timeSaver4445_to_delete.py

import sys
import argparse
import re
import os
import shutil
import time  # For timestamp
from openai import OpenAI
import logging

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
ELECTRIC_BLUE = "\033[38;2;44;117;255m"
RESET = "\033[0m"

# Set your OpenAI API key securely using an environment variable
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def setup_logging():
    """Configure logging settings."""
    logging.basicConfig(
        filename='cleanerAI_v1.log',
        filemode='w',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def parse_segments_with_positions(content):
    """
    Extract segments where lines containing '444' and '555' appear alone.
    Pattern (multiline-aware):
        444
        (some context)
        444
        (some text to reword)
        555
    """
    # The ^ and $ anchors, combined with re.MULTILINE, ensure the markers 
    # appear alone on their lines (ignoring lines like "the cost is $444").
    # The pattern uses DOTALL (?s) to match across newlines and 
    # MULTILINE (?m) so ^ and $ match the start/end of lines within the file content.
    pattern = r'(?s)(?m)^[ \t]*444[ \t]*\r?\n(.*?)\r?\n[ \t]*444[ \t]*\r?\n(.*?)\r?\n[ \t]*555[ \t]*\r?\n?'
    matches = list(re.finditer(pattern, content))

    segments = []
    for match in matches:
        full_match = match.group(0)
        context_444 = match.group(1).strip()
        content_555 = match.group(2).strip()
        start = match.start()
        end = match.end()
        segments.append({
            'full_match': full_match,
            'context_444': context_444,
            'content_555': content_555,
            'start': start,
            'end': end
        })
    logging.info(f"Parsed {len(segments)} segments.")
    print(f"[INFO] Parsed {len(segments)} segments.")
    return segments

def clean_segment(context_444, content_555):
    """
    Process the text segment using OpenAI's LLM:
    - Keep the context from '444' as reference without changes.
    - Reword the content in '555' with a more journalistic/military tone, ideally a single sentence.
    """
    try:
        instruction = """
You are to use the context provided from the '444' tags as reference but do not alter it. 
Focus on rewording the text found between the '555' tags into something more journalistic tone, 
ideally one sentence or less and around the same length as the original content.

Context from '444':
{context_444}

Text in '555' to reword:
{content_555}

Updated Text for '555':
"""
        prompt = instruction.format(context_444=context_444, content_555=content_555)

        print("[INFO] Connecting to OpenAI API to process the segment...")
        logging.info("[INFO] Connecting to OpenAI API to process the segment...")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt},
            ],
            max_tokens=300,
            n=1,
            stop=None,
            temperature=0
        )

        assistant_reply = response.choices[0].message.content.strip()
        print(f"[INFO] OpenAI API response: {assistant_reply}")
        logging.info(f"OpenAI API response: {assistant_reply}")

        return assistant_reply

    except Exception as e:
        error_message = f"Error processing segment: {e}"
        print(f"[ERROR] {error_message}")
        logging.error(error_message)
        # If there's an error, return the original content for '555'
        return content_555

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

        # Clean the segment’s content
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

