#!/usr/bin/env python3

import sys
import os
import re
import logging
import tempfile
from openai import OpenAI

# Import the API key utility
from api_utils import get_api_key

# Set up debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='/tmp/reflow_debug.log',
    filemode='w'
)

def debug_print(message):
    """Print debug messages to both stderr and log file"""
    print(f"DEBUG: {message}", file=sys.stderr)
    logging.debug(message)

def extract_text_parts(highlighted_text):
    """Extract the first line and the rest of the text from the highlighted text."""
    debug_print(f"Highlighted text: {highlighted_text}")
    
    # Handle different types of newlines
    if '\n' in highlighted_text:
        lines = highlighted_text.split('\n', 1)
    elif '\r\n' in highlighted_text:
        lines = highlighted_text.split('\r\n', 1)
    elif '\r' in highlighted_text:
        lines = highlighted_text.split('\r', 1)
    else:
        # Try to find a sentence break if no newlines
        sentences = re.split(r'(?<=[.!?])\s+', highlighted_text)
        if len(sentences) > 1:
            lines = [sentences[0], ' '.join(sentences[1:])]
        else:
            lines = [highlighted_text]
    
    debug_print(f"Split into {len(lines)} parts")
    
    if len(lines) > 1:
        first_line = lines[0].strip()
        rest_of_text = lines[1].strip()
        debug_print(f"First line: {first_line}")
        debug_print(f"Rest of text: {rest_of_text[:100]}...")
        return first_line, rest_of_text
    else:
        # If there's only one line, we can't proceed
        debug_print(f"Only one line found: {lines[0]}")
        return highlighted_text, ""

def reflow_text(first_line, rest_of_text):
    """Keep the first line as is, reword the rest to flow contextually from the first line."""
    try:
        if not rest_of_text:
            debug_print("No rest of text to reflow")
            return first_line  # Nothing to reflow

        # Get API key from file or environment variable
        api_key = get_api_key()
        if not api_key:
            debug_print("OpenAI API key not found. Please create apikeynew_13012025.txt in the project root directory or set OPENAI_API_KEY environment variable.")
            return "Error: OpenAI API key not found"
        
        # Initialize OpenAI client with API key
        client = OpenAI(api_key=api_key)

        debug_print(f"Calling OpenAI API with model gpt-4o-mini")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "system",
                "content": "You are an expert editor who resolves contradictions in text while preserving the intended meaning of the first statement."
            },
            {
                "role": "user",
                "content": f"""I have two paragraphs that contradict each other. The first paragraph states one thing, but the second paragraph contradicts it.

FIRST PARAGRAPH (KEEP EXACTLY AS IS):
{first_line}

SECOND PARAGRAPH (REWRITE TO ALIGN WITH FIRST PARAGRAPH):
{rest_of_text}

Please rewrite ONLY the second paragraph to make it consistent with the first paragraph's facts and claims. The first paragraph is the source of truth. The second paragraph should flow naturally from the first, incorporating similar style and tone.

Return the complete text (both paragraphs) with appropriate paragraph breaks maintained. The first paragraph should remain UNCHANGED.

Return ONLY the rewritten text without explanations."""
            }],
            max_tokens=500,
            temperature=0.7
        )
        
        result = response.choices[0].message.content.strip()
        debug_print(f"API response: {result[:100]}...")
        return result
        
    except Exception as e:
        error_msg = f"Error in reflow_text: {str(e)}"
        debug_print(error_msg)
        return f"Error: {str(e)}"

if __name__ == "__main__":
    debug_print("ReFlow script started")
    if len(sys.argv) != 2:
        debug_print("Usage error: Incorrect number of arguments")
        print("Usage: python ReFlow.py <text_file>")
        sys.exit(1)
    
    try:
        with open(sys.argv[1], 'r') as f:
            text = f.read().strip()
            debug_print(f"Read input file of length {len(text)}")
            
        # The first line should be the highlighted text
        lines = text.split('\n', 1)
        if len(lines) != 2:
            debug_print(f"Input format error: Found {len(lines)} lines instead of 2")
            print("Error: Input should contain highlighted text on first line and full text on second line")
            sys.exit(1)
            
        highlighted_text = lines[0].strip()
        full_text = lines[1].strip()
        
        debug_print(f"Highlighted text length: {len(highlighted_text)}")
        debug_print(f"Full text length: {len(full_text)}")
        
        # Extract first line and rest of text from highlighted text
        first_line, rest_of_text = extract_text_parts(highlighted_text)
        
        if first_line:
            # Reflow the text, keeping the first line as is
            debug_print("Processing text for reflow")
            result = reflow_text(first_line, rest_of_text)
            
            # Replace the original highlighted text with the reflowed text in the full document
            debug_print("Replacing text in document")
            if highlighted_text in full_text:
                modified_text = full_text.replace(highlighted_text, result)
                debug_print("Text replaced successfully")
            else:
                debug_print("Warning: Couldn't find exact highlighted text in document")
                # Try a more flexible approach - find the start and approximate end of the text
                first_line_pos = full_text.find(first_line)
                if first_line_pos >= 0:
                    pre_text = full_text[:first_line_pos]
                    post_text = full_text[first_line_pos + len(first_line) + len(rest_of_text):]
                    modified_text = pre_text + result + post_text
                    debug_print("Used position-based replacement")
                else:
                    debug_print("Failed to find a reliable way to replace text")
                    modified_text = full_text
            
            debug_print(f"Final text length: {len(modified_text)}")
            print(modified_text)
        else:
            debug_print("Error: Could not parse the highlighted text")
            print("Error: Could not parse the highlighted text")
            sys.exit(1)
            
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        debug_print(error_msg)
        print(f"Error: {e}")
        sys.exit(1) 
