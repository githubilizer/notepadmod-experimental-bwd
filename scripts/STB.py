#!/usr/bin/env python3
import argparse
import sys
import traceback
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
    parser = argparse.ArgumentParser(description='Test OpenAI fine-tuned model with a prompt')
    parser.add_argument('prompt', help='Input prompt for the model')
    return parser

def get_model_response(client, prompt):
    try:
        debug_print(f"Sending prompt to OpenAI: {prompt[:200]}...")
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {'role': 'user', 'content': prompt}
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
    debug_print("STB script started")
    parser = setup_argparse()
    
    try:
        args = parser.parse_args()
    except Exception as e:
        debug_print(f"Argument parsing error: {str(e)}")
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    
    original_text = args.prompt
    debug_print(f"Original text received: {original_text[:200]}...")

    # Prefix the prompt
    prefixed_prompt = f"update the following writing to say it clearer and better and in the style from your finetuned dataset, and in a military journalistic style. But also, keep the structure as same as you can, fixing spelling, grammar etc, and chosing better words to more effectively update the input, because the input it written in a way that is right structurally but it does need a bit of clean up still:  {args.prompt}"

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
        response = get_model_response(client, prefixed_prompt)
        debug_print(f"Response received: {response[:200]}...")
        print(f"{response}\n\n\n{original_text}")
    except Exception as e:
        debug_print(f"Error getting model response: {str(e)}")
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
