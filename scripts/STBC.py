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
    parser = argparse.ArgumentParser(description='Test OpenAI fine-tuned model with a prompt and surrounding context')
    parser.add_argument('prompt', help='Input prompt for the model')
    return parser

def get_surrounding_context(text, max_sentences=3):
    """Extract surrounding context from the text"""
    sentences = re.split(r'[.!?]+\s*', text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # If there are fewer sentences than max_sentences, use all available
    if len(sentences) <= max_sentences:
        return ' '.join(sentences)
    
    # Otherwise, get the last few sentences as context
    return ' '.join(sentences[-max_sentences:])

def get_model_response(client, prompt, context):
    try:
        debug_print(f"Sending prompt to OpenAI with context: {context[:100]}...")
        
        # Construct enhanced prompt with context
        enhanced_prompt = f"Here is some surrounding context to understand the text better: {context}\n\nNow, rewrite the following to say it clearer and better and in the style from your finetuned dataset, and in a journalistic style: {prompt}"
        
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
    debug_print("STBC script started")
    parser = setup_argparse()
    
    try:
        args = parser.parse_args()
    except Exception as e:
        debug_print(f"Argument parsing error: {str(e)}")
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    
    original_text = args.prompt
    debug_print(f"Original text received: {original_text[:200]}...")
    
    # Extract surrounding context
    context = get_surrounding_context(original_text)
    debug_print(f"Extracted context: {context[:200]}...")

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

    # Get response and format output
    try:
        response = get_model_response(client, original_text, context)
        debug_print(f"Response received: {response[:200]}...")
        print(f"{response}\n\n\n{original_text}")
    except Exception as e:
        debug_print(f"Error getting model response: {str(e)}")
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main() 