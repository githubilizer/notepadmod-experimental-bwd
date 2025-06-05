#!/usr/bin/env python3
import argparse
import sys
import traceback
import re
import os
from openai import OpenAI

# Import the API key utility
from api_utils import get_api_key

# Configuration
MODEL_NAME = 'ft:gpt-4o-mini-2024-07-18:personal::Alh2FOfj'

# Baked-in temperature/top_p
TEMPERATURE = 0.2
TOP_P = 0.9

def debug_print(message):
    """Print debug message to stderr"""
    print(f"DEBUG: {message}", file=sys.stderr)

def setup_argparse():
    """Set up argument parser"""
    parser = argparse.ArgumentParser(description='Test OpenAI fine-tuned model with a prompt and surrounding context')
    parser.add_argument('input', help='Input file containing paragraph and selection positions or direct text input')
    return parser

def read_input_file(filepath):
    """Read input file with full text and selection positions"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # The last line should contain the selection positions (start,end)
        # Everything before that is the context text
        lines = content.splitlines()
        if not lines:
            debug_print(f"Input file is empty")
            return None, None, None
        
        # Last line should be the position information
        last_line = lines[-1]
        # Check if last line is a position specification (contains a comma and two numbers)
        if ',' in last_line and all(part.strip().isdigit() for part in last_line.split(',')):
            position_line = last_line
            # Everything except the last line is the full text
            full_text = '\n'.join(lines[:-1])
        else:
            debug_print(f"Last line doesn't contain position information, using entire file as text")
            return content, 0, len(content)
        
        try:
            start_pos, end_pos = map(int, position_line.split(','))
            debug_print(f"Full text length: {len(full_text)}")
            debug_print(f"Selection positions: {start_pos},{end_pos}")
            return full_text, start_pos, end_pos
        except ValueError:
            debug_print(f"Error parsing position values: {position_line}")
            return None, None, None
    except Exception as e:
        debug_print(f"Error reading input file: {str(e)}")
        return None, None, None

def get_model_response(client, full_text, start_pos, end_pos):
    """Get improved text from OpenAI, using context within the same news segment and excluding tags"""
    try:
        # Find all "Title:{word}\n" positions to identify segment boundaries
        title_matches = list(re.finditer(r'^Title:\w+\n', full_text, re.MULTILINE))
        if not title_matches:
            # If no titles, treat the entire text as one segment
            segment_start = 0
            segment_end = len(full_text)
        else:
            # Find the segment containing the highlighted text
            for i, match in enumerate(title_matches):
                content_start = match.end()  # Position after "Title:{word}\n"
                if i < len(title_matches) - 1:
                    next_title_start = title_matches[i + 1].start()
                else:
                    next_title_start = len(full_text)
                if content_start <= start_pos < next_title_start:
                    segment_start = content_start
                    segment_end = next_title_start
                    break
            else:
                # Handle case where highlighted text is before the first title
                if start_pos < title_matches[0].start():
                    segment_start = 0
                    segment_end = title_matches[0].start()
                else:
                    raise ValueError("Highlighted text not within any segment")

        # Find metadata start after end_pos within the segment to exclude tags
        metadata_pattern = r'(?m)^(Timestamp:|http|--|cc-)'
        metadata_match = re.search(metadata_pattern, full_text[end_pos:segment_end])
        if metadata_match:
            metadata_start = end_pos + metadata_match.start()
        else:
            metadata_start = segment_end

        # Extract context within the segment, excluding metadata
        before_text = full_text[segment_start:start_pos]
        selected_text = full_text[start_pos:end_pos]
        after_text = full_text[end_pos:metadata_start]

        debug_print(f"Segment start: {segment_start}, Metadata start: {metadata_start}")
        debug_print(f"Before text: '{before_text[-20:]}' and after: '{after_text[:20]}'")
        
        # Clean up the text to handle multi-line inputs better
        # Replace consecutive newlines with spaces for cleaner prompt formatting
        def normalize_text(text):
            # Replace runs of 2+ newlines with a single space
            normalized = re.sub(r'\n{2,}', ' ', text)
            # Replace single newlines with spaces to maintain flow
            normalized = normalized.replace('\n', ' ')
            # Remove extra spaces
            normalized = re.sub(r'\s+', ' ', normalized)
            return normalized.strip()
        
        # Normalize texts for better prompt formatting
        before_text_clean = normalize_text(before_text)
        selected_text_clean = normalize_text(selected_text)
        after_text_clean = normalize_text(after_text)
        
        debug_print(f"Normalized selected text: '{selected_text_clean}'")

        # Construct enhanced prompt with context limited to the segment
        enhanced_prompt = (
            f"I need you to improve a highlighted portion of text while ensuring it grammatically fits with the text before and after it.\n\n"
            f"FULL TEXT WITH HIGHLIGHTED PORTION IN [BRACKETS]:\n"
            f"{before_text_clean}[{selected_text_clean}]{after_text_clean}\n\n"
            f"INSTRUCTIONS:\n"
            f"1. Improve ONLY the portion in [brackets] to be more clear, engaging, and journalistic in style, while fully maintaining its original sentiment and meaning\n"
            f"2. Your response must maintain proper grammar with the text that comes before and after\n"
            f"3. The improved text must be a grammatically correct continuation of the sentence structure\n"
            f"4. Keep proper capitalization based on its position in the sentence\n"
            f"5. Maintain the meaning of the original highlighted text while improving its clarity\n"
            f"6. DO NOT include any brackets in your response - return ONLY the improved highlighted portion\n\n"
            f"IMPROVED HIGHLIGHTED PORTION (without brackets):"
        )

        debug_print(f"Enhanced prompt: {enhanced_prompt[:200]}...")

        # Make API call
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {'role': 'user', 'content': enhanced_prompt}
            ],
            temperature=TEMPERATURE,
            top_p=TOP_P
        )
        return response.choices[0].message.content
    except Exception as e:
        debug_print(f"Error in get_model_response: {str(e)}")
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

def main():
    """Main function to process input and get model response"""
    debug_print("STBC-Middle script started")
    parser = setup_argparse()
    
    try:
        args = parser.parse_args()
    except Exception as e:
        debug_print(f"Argument parsing error: {str(e)}")
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    
    input_arg = args.input
    
    # Check if input is a file path
    if os.path.isfile(input_arg):
        debug_print(f"Reading input from file: {input_arg}")
        full_text, start_pos, end_pos = read_input_file(input_arg)
        if not full_text or start_pos is None or end_pos is None:
            debug_print("Failed to read input file properly")
            sys.exit(1)
    else:
        # Handle direct text input (limited functionality)
        debug_print("Using direct text input - note: context limitations may not fully apply")
        full_text = input_arg
        start_pos = 0
        end_pos = len(full_text)
    
    debug_print(f"Selected text to improve: {full_text[start_pos:end_pos][:100]}...")

    # Get API key from file or environment variable
    api_key = get_api_key()
    if not api_key:
        debug_print("OpenAI API key not found. Please create apikeynew_13012025.txt in the project root directory or set OPENAI_API_KEY environment variable.")
        sys.exit(1)

    # Initialize OpenAI client
    try:
        client = OpenAI(api_key=api_key)
    except Exception as e:
        debug_print(f"Error initializing OpenAI client: {str(e)}")
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

    # Get response and output
    try:
        improved_text = get_model_response(client, full_text, start_pos, end_pos)
        debug_print(f"Improved text received: {improved_text[:100]}...")
        print(improved_text)
    except Exception as e:
        debug_print(f"Error getting model response: {str(e)}")
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
