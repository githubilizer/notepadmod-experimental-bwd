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

    # Prefix the prompt
    prefixed_prompt = f"Write as follows: Take the following news draft and refine it by making small, precise edits to improve spelling, grammar, and punctuation. Keep the structure, tone, and flow as close to the original as possible, while subtly enhancing word choice for greater impact and engagement. Do not alter the core style or rewrite entire sentences—only make minor, thoughtful adjustments that elevate clarity and readability. If part of the input sounds of elementary-school writing level, spruce it up to sound more academic. Here is the raw input: {args.prompt}"

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

    # Get response and format output
    response = get_model_response(client, prefixed_prompt)
    print(f"{response}\n\n\n{original_text}")  # API output, 3 line breaks, then original text

if __name__ == '__main__':
    main() 
