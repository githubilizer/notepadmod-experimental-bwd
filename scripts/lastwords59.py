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
TEMPERATURE = 0.3
TOP_P = 0.9

def debug_print(message):
    """Print debug message to stderr"""
    print(f"DEBUG: {message}", file=sys.stderr)

def setup_argparse():
    parser = argparse.ArgumentParser(description='Complete the last sentence with 5-9 appropriate words')
    parser.add_argument('text', help='Input text with an incomplete last sentence')
    return parser

def find_last_sentence(text):
    """Extract the last sentence or sentence fragment from the text"""
    # Clean text
    text = text.strip()
    if not text:
        return ""
    
    # Split text into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Get the last sentence (which might be incomplete)
    last_sentence = sentences[-1].strip()
    
    # If the last sentence is very short, also include the previous sentence for context
    if len(sentences) > 1 and len(last_sentence.split()) < 3:
        return sentences[-2] + " " + last_sentence
    
    return last_sentence

def get_model_response(client, text):
    try:
        # Extract the last sentence for completion
        last_sentence = find_last_sentence(text)
        debug_print(f"Last sentence to complete: {last_sentence}")
        
        # Create prompt for sentence completion
        prompt = f"""
You are tasked with completing a sentence by adding 5-9 NEW, DIFFERENT words.

RULES:
1. ONLY provide 5-9 NEW words that complete the sentence naturally
2. NEVER repeat any words that are already in the input sentence
3. Your response should ONLY contain the new words, nothing else
4. Do not add periods or punctuation unless absolutely necessary
5. Make sure the completion feels natural and flows from the existing text

Text for context: {text}

Last sentence to complete: {last_sentence}

Your completion (ONLY 5-9 NEW words):"""
        
        debug_print(f"Sending prompt to OpenAI")
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {'role': 'user', 'content': prompt}
            ],
            temperature=TEMPERATURE,
            top_p=TOP_P,
            max_tokens=40  # Increased token limit for longer completions
        )
        
        completion = response.choices[0].message.content.strip()
        debug_print(f"Completion received: {completion}")
        
        # Ensure we only return 5-9 words
        words = completion.split()
        if len(words) > 9:
            debug_print(f"Trimming completion to 9 words")
            completion = " ".join(words[:9])
        elif len(words) < 5:
            debug_print(f"Completion too short, requesting another one")
            # Simple retry mechanism for too-short completions
            return get_model_response(client, text)
        
        return completion
    except Exception as e:
        debug_print(f"Error in get_model_response: {str(e)}")
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

def parse_segments_with_positions(content):
    """
    Simple wrapper function to maintain compatibility with the script_runner's generic script handler
    """
    # For lastwords.py, we treat the entire content as a single segment
    return [{
        'content': content.strip(),
        'start': 0,
        'end': len(content)
    }]

def clean_segment(content, window=None):
    """
    Complete the last sentence of the provided text with 5-9 appropriate words.
    This function follows the convention expected by script_runner.
    """
    try:
        debug_print(f"Processing text: {content[:100]}...")
        
        # Get API key and initialize client
        api_key = get_api_key()
        if not api_key:
            debug_print("OpenAI API key not found. Please create apikeynew_13012025.txt in the project root directory or set OPENAI_API_KEY environment variable.")
            return content + " [API KEY MISSING]"
            
        client = OpenAI(api_key=api_key)
        
        # Get completion
        completion = get_model_response(client, content)
        
        # Append completion to the original text with a space
        # but ensure we don't add extra spaces
        if content.endswith(' '):
            result = f"{content}{completion}"
        else:
            result = f"{content} {completion}"
        
        debug_print(f"Final result: {result[:100]}...")
        return result
    except Exception as e:
        debug_print(f"Error in clean_segment: {str(e)}")
        traceback.print_exc(file=sys.stderr)
        return content  # Return original text if there's an error

def main():
    debug_print("LastWords script started")
    parser = setup_argparse()
    
    try:
        args = parser.parse_args()
    except Exception as e:
        debug_print(f"Argument parsing error: {str(e)}")
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    
    text = args.text
    debug_print(f"Text received: {text[:200]}...")

    # Get API key and initialize client
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

    # Get completion and format output
    try:
        completion = get_model_response(client, text)
        debug_print(f"Completion words: {completion}")
        
        # Append completion to the original text
        if text.endswith(' '):
            result = f"{text}{completion}"
        else:
            result = f"{text} {completion}"
        
        print(result)
    except Exception as e:
        debug_print(f"Error getting model response: {str(e)}")
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main() 
