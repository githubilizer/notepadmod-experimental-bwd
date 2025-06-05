#!/usr/bin/env python3
import argparse
import sys
import os
from openai import OpenAI

# Import the API key utility
from api_utils import get_api_key

# Configuration
MODEL_NAME = 'ft:gpt-4o-mini-2024-07-18:personal::Alh2FOfj'

# Baked-in temperature/top_p
TEMPERATURE = 0.2
TOP_P = 0.9

def setup_argparse():
    parser = argparse.ArgumentParser(description='Test OpenAI fine-tuned model with a prompt')
    parser.add_argument('prompt', help='Input prompt for the model')
    return parser

def get_model_response(client, prompt):
    try:
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
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = setup_argparse()
    args = parser.parse_args()
    original_text = args.prompt
    
    # Check for direction in brackets at the end
    direction = ""
    if original_text.rstrip().endswith(')'):
        start_bracket = original_text.rfind('(')
        if start_bracket != -1:
            direction = original_text[start_bracket + 1:-1].strip()
            original_text = original_text[:start_bracket].rstrip()

    # Construct prompt based on whether direction is provided
    if direction:
        prefixed_prompt = f"You are a helpful assistant that completes sentences and paragraphs in a natural way. When given text, you will continue and complete it in a way that provides a satisfying conclusion based on the context, heading in the direction of '{direction}'. The output is to be upto 30 words. Here is the text: {original_text}"
    else:
        prefixed_prompt = f"You are a helpful assistant that completes sentences and paragraphs in a natural way. When given text, you will continue and complete it in a way that provides a satisfying conclusion based on the context; the output it to be no more than 30 words. Here is the text: {original_text}"

    # Get API key from file or environment variable
    api_key = get_api_key()
    if not api_key:
        print("Error: OpenAI API key not found. Please create apikeynew_13012025.txt in the project root directory or set OPENAI_API_KEY environment variable.", file=sys.stderr)
        sys.exit(1)

    # Initialize OpenAI client
    try:
        client = OpenAI(api_key=api_key)
    except Exception as e:
        print(f"Error initializing OpenAI client: {str(e)}", file=sys.stderr)
        sys.exit(1)

    # Get response and combine with original text
    response = get_model_response(client, prefixed_prompt)
    print(f"{original_text} {response}")

if __name__ == '__main__':
    main()

