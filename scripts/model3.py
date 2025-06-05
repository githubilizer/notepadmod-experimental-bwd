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
    # NO LIMITATIONS ON SIZE - GOOD FOR BIG DATA SET STORIES - WHERE WANTING BIG STORY OUTPUT
    prefixed_prompt = f"""
Write a concise, engaging, and factual report in 150 words or less, following the military journalist style from your fine-tuned model. 
- Use short, punchy sentences. 
- Get straight to the details first—no journalistic intro. 
- Keep it professional yet down-to-earth. 
- Apply the conclusions and tone from your fine-tuned training. 
- don't say the words: "stark" or "underscores" or "escalation"
- created it as a compelling flowing narrative.

Here is the raw input data dumps to construct it out of: {args.prompt}
"""

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
    print(f"{response}\n\n\nOG\n\n{original_text}")  # API output, 3 line breaks, "OG", 2 line breaks, then original text

if __name__ == '__main__':
    main()

