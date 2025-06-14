#!/usr/bin/env python3

# /scripts/CmntSntmnt.py

# This script analyzes comments for sentiment using AI.
# It follows the same pattern as qq.py but focuses on sentiment analysis.

import sys
import argparse
import re
import os
import shutil
import time  # For timestamp
from openai import OpenAI  # Updated import syntax
import logging
from collections import Counter

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
ELECTRIC_BLUE = "\033[38;2;44;117;255m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"

def get_openai_client():
    """Get OpenAI client with API key validation."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        error_msg = """
ERROR: OpenAI API key not found!

Please set your OpenAI API key as an environment variable:

    export OPENAI_API_KEY='your-api-key-here'

You can add this line to your ~/.bashrc file to make it permanent.
"""
        print(error_msg)
        logging.error("OpenAI API key not found in environment variables")
        sys.exit(1)
    return OpenAI(api_key=api_key)

def setup_logging():
    """Configure logging settings."""
    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Set up file handler
    file_handler = logging.FileHandler('/home/j/Desktop/code/notepadMOD/logs/CmntSntmnt.log', mode='w')
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

    logging.info("Logging initialized - outputs will appear in both console and CmntSntmnt.log")

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

def analyze_sentiment(segment, client=None):
    """
    Analyze the sentiment of the text segment using OpenAI's LLM.

    Returns:
    - sentiment_analysis (str): The sentiment analysis generated by the model.
    """
    try:
        if client is None:
            client = get_openai_client()

        # Prepare the instruction prompt to analyze sentiment
        instruction = """
Please analyze the sentiment of the following comment or text. 
Identify whether it's positive, negative, or neutral, and explain why.
Provide specific emotion indicators and the overall tone.

Comment:
{segment}

Sentiment Analysis:
"""
        prompt = instruction.format(segment=segment)

        logging.info(f"Processing segment: {segment}")
        logging.info("Connecting to OpenAI API...")

        # Make the API call
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Using a valid model name
            messages=[
                {"role": "user", "content": prompt},
            ],
            max_tokens=300,  # Adjust as needed
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

def analyze_multiple_comments(content, client=None):
    """
    Analyze multiple comments and extract the main sentiments expressed.
    
    Args:
        content (str): The text content containing multiple comments
        client: OpenAI client instance
        
    Returns:
        str: A summary of the main sentiments found in the comments
    """
    try:
        if client is None:
            client = get_openai_client()
            
        # Split the content into separate comments (assuming each line or paragraph is a comment)
        comments = re.split(r'\n+', content)
        comments = [comment.strip() for comment in comments if comment.strip()]
        
        if not comments:
            return "No comments found to analyze."
            
        logging.info(f"Analyzing {len(comments)} comments for sentiment")
        
        # For large sets of comments, we'll use a batch approach
        if len(comments) > 20:
            # Sample a subset of comments if there are too many
            import random
            sampled_comments = random.sample(comments, min(20, len(comments)))
            logging.info(f"Sampled {len(sampled_comments)} comments for detailed analysis")
        else:
            sampled_comments = comments
            
        # Create a prompt to analyze multiple comments at once
        comments_text = "\n\n".join([f"Comment {i+1}: {comment}" for i, comment in enumerate(sampled_comments)])
        
        instruction = """
Please analyze the sentiment of the following set of comments.
Identify the top sentiments expressed across all comments (up to 7 main sentiments).
For each sentiment, put the information on a single line, and provide:
- The sentiment name/type
- A very brief explanation of how it manifests in the comments
- An approximate percentage of comments expressing this sentiment

Comments:
{comments}

Sentiment Analysis Summary:
"""
        prompt = instruction.format(comments=comments_text)
        
        # Make the API call
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt},
            ],
            max_tokens=800,  # Increased token limit for comprehensive analysis
            n=1,
            stop=None,
            temperature=0
        )
        
        # Extract the assistant's reply
        sentiment_summary = response.choices[0].message.content.strip()
        
        # Format the output
        result = f"# Sentiment Analysis of {len(comments)} Comments\n\n"
        result += sentiment_summary
        
        return result
        
    except Exception as e:
        error_message = f"Error analyzing multiple comments: {e}"
        logging.error(error_message)
        print(f"Error: {error_message}")
        return f"Error analyzing comments: {str(e)}"

def clean_segment(segment, window=None):
    """Process a segment and return the cleaned/processed text."""
    client = get_openai_client()
    return analyze_multiple_comments(segment, client)

def main():
    setup_logging()
    logging.info("Script started.")
    print("[INFO] Script started.")

    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Process and update segments in the input file.")
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
        # If no segments are found, treat the entire content as a single segment
        print(f"[INFO] No segments found between '111' markers. Processing entire content.")
        result = analyze_multiple_comments(content, client)
        print(result)
        sys.exit(0)

    # Initialize new content parts
    new_content_parts = []
    last_end = 0

    print("[INFO] Starting to process and update segments...")
    for idx, segment in enumerate(segments, 1):
        print(f"[INFO] Processing segment {idx}...")

        # Append content up to the start of the segment
        new_content_parts.append(content[last_end:segment['start']])

        # Update last_end to the end of the segment
        last_end = segment['end']

        # Process the segment by analyzing sentiment
        updated_content = analyze_multiple_comments(segment['content'], client)

        # Append the updated content
        new_content_parts.append(updated_content)

    # Append any remaining content after the last segment
    if last_end < len(content):
        new_content_parts.append(content[last_end:])

    # Join all parts to form the new content
    new_content = ''.join(new_content_parts)

    # Print the result to stdout (for the GUI to capture)
    print(new_content)

if __name__ == "__main__":
    # Check if an argument was provided
    if len(sys.argv) == 2:
        # If the argument doesn't look like a file path, treat it as direct text input
        if not os.path.exists(sys.argv[1]) and '/' not in sys.argv[1]:
            setup_logging()
            client = get_openai_client()
            result = analyze_multiple_comments(sys.argv[1], client)
            print(result)
            sys.exit(0)
    
    main()
