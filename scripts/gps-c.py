#!/usr/bin/env python3

# /scripts/gps-c.py - Context-aware GPS coordinate extraction from tweets/text

import sys
import argparse
import re
import os
import logging
from openai import OpenAI

# Import the API key utility
from api_utils import get_api_key

def get_openai_client():
    """Get OpenAI client using API key from file or environment."""
    api_key = get_api_key()
    if not api_key:
        logging.error("OpenAI API key not found. Please create apikeynew_13012025.txt in the project root directory or set OPENAI_API_KEY environment variable.")
        print("Error: OpenAI API key not found. Please create apikeynew_13012025.txt in the project root directory or set OPENAI_API_KEY environment variable.", file=sys.stderr)
        sys.exit(1)
    return OpenAI(api_key=api_key)

def setup_logging():
    """Configure logging settings."""
    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Set up file handler
    file_handler = logging.FileHandler('/home/j/Desktop/code/notepadMOD/logs/gps-c.log', mode='w')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Set up console handler but send to stderr instead of stdout
    console_handler = logging.StreamHandler(sys.stderr)
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

    logging.info("Logging initialized - outputs will appear in log file and stderr")

def format_coordinates_to_deepstate_link(coordinates):
    """
    Format coordinates as a Deep State Map link.
    
    Args:
        coordinates (str): Coordinates in "lat, lon" format
    
    Returns:
        str: Formatted Deep State Map link
    """
    # Check if we have valid coordinates
    if not coordinates or ',' not in coordinates:
        return "Unable to generate Deep State Map link (invalid coordinates)"
    
    try:
        # Parse the coordinates
        parts = coordinates.split(',')
        if len(parts) != 2:
            return "Unable to generate Deep State Map link (invalid format)"
            
        lat = float(parts[0].strip())
        lon = float(parts[1].strip())
        
        # Format to 7 decimal places
        formatted_lat = f"{lat:.7f}"
        formatted_lon = f"{lon:.7f}"
        
        # Create the Deep State Map link with English language support
        deep_state_link = f"https://deepstatemap.live/en/#9/{formatted_lat}/{formatted_lon}"
        
        return deep_state_link
    except Exception as e:
        logging.error(f"Error formatting Deep State Map link: {e}")
        return "Unable to generate Deep State Map link (error)"

def format_coordinates(coordinates):
    """
    Format coordinates to 7 decimal places.
    
    Args:
        coordinates (str): Coordinates in "lat, lon" format
    
    Returns:
        str: Formatted coordinates to 7 decimal places
    """
    # Check if we have valid coordinates
    if not coordinates or ',' not in coordinates:
        return coordinates
    
    try:
        # Parse the coordinates
        parts = coordinates.split(',')
        if len(parts) != 2:
            return coordinates
            
        lat = float(parts[0].strip())
        lon = float(parts[1].strip())
        
        # Format to 7 decimal places
        formatted_coords = f"{lat:.7f}, {lon:.7f}"
        
        return formatted_coords
    except Exception as e:
        logging.error(f"Error formatting coordinates: {e}")
        return coordinates

def extract_coordinates_from_tweets(text, client=None):
    """
    Extract decimal GPS coordinates from tweets or longer text using context analysis.
    
    Args:
        text (str): The tweet text to analyze
        client: OpenAI client instance
        
    Returns:
        str: Formatted output with coordinates, link and original text
    """
    try:
        if client is None:
            client = get_openai_client()

        logging.info(f"Processing tweet text: {text[:100]}...")  # Log first 100 chars
        logging.info("Connecting to OpenAI API...")

        # Prepare the instruction prompt to extract GPS coordinates from tweet context
        instruction = """
You are a geolocation expert. Analyze the following text which likely contains tweets or social media posts about locations in Ukraine or Russia.
Your task is to extract any GPS coordinates mentioned directly or indirectly, or determine the location based on context clues.

For direct coordinates: Convert them to decimal format (latitude, longitude).
For indirect references: Use contextual clues (e.g., "near X", "10km west of Y") to determine the coordinates.
For place names: Convert to coordinates of that location.

If multiple possible coordinates are found, return only the one with highest confidence.
Only return the final coordinates in decimal format (latitude, longitude), nothing else.

Text:
{text}

Coordinates:
"""
        prompt = instruction.format(text=text)

        # Make the API call with GPT-4
        response = client.chat.completions.create(
            model="gpt-4o",  # Using the more capable model for context understanding
            messages=[
                {"role": "user", "content": prompt},
            ],
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0
        )

        # Extract the assistant's reply
        coordinates = response.choices[0].message.content.strip()

        # Format coordinates to 7 decimal places
        formatted_coordinates = format_coordinates(coordinates)
        
        # Generate Deep State Map link
        deep_state_link = format_coordinates_to_deepstate_link(coordinates)

        # Log the results
        logging.info(f"OpenAI API response: {coordinates}")
        logging.info(f"Formatted coordinates: {formatted_coordinates}")
        logging.info(f"Deep State Map link: {deep_state_link}")

        # Create the formatted output with coordinates, link, and original text
        result = f"{formatted_coordinates}\n{deep_state_link}\n\n{text}"
        
        return result

    except Exception as e:
        error_message = f"Error processing tweet text: {e}"
        logging.error(error_message)
        # Print error to stderr, not stdout
        print(f"Error: {error_message}", file=sys.stderr)
        return f"Error extracting coordinates: {e}\n\n---Original Text---\n{text}"

def main():
    setup_logging()
    logging.info("GPS-C Script started.")
    
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Extract GPS coordinates from tweet content.")
    parser.add_argument('input_file', help='Path to the input text file.')
    args = parser.parse_args()

    input_file = args.input_file

    # Initialize OpenAI client
    client = get_openai_client()

    # Read the input file
    try:
        logging.info(f"Reading input file '{input_file}'...")
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        logging.info(f"Read input file '{input_file}' successfully.")
    except FileNotFoundError:
        logging.error(f"Input file '{input_file}' not found.")
        print(f"Error: Input file '{input_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error reading input file: {e}")
        print(f"Error: Reading input file: {e}", file=sys.stderr)
        sys.exit(1)

    # Process the entire content directly without looking for 111 markers
    logging.info("Processing content for GPS coordinates...")
    processed_content = extract_coordinates_from_tweets(content, client)

    # Write the processed content back to the file
    try:
        logging.info(f"Writing results back to '{input_file}'...")
        with open(input_file, 'w', encoding='utf-8') as f:
            f.write(processed_content)
        logging.info(f"Updated '{input_file}' successfully.")
    except Exception as e:
        logging.error(f"Error writing to input file: {e}")
        print(f"Error: Writing to input file: {e}", file=sys.stderr)
        sys.exit(1)

    logging.info("GPS-C Script completed successfully.")
    
    # Print result to stdout (this is what will be captured by the parent process)
    print(processed_content)

if __name__ == "__main__":
    main() 