#!/usr/bin/env python3
import argparse
import sys
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

    # Prefix the prompt
    prefixed_prompt = f"Write this as if it's for a military journalist: as one long sentence - make it: concise, engaging, factual, but also make it down-to-earth just like my writing style in your data set, use short, punchy wording, and keep it professional but conversational and firstly talk about the details of what happened upfront in your response (thus consider everything within the input first). Make it as written in my style, and round it off the ending a bit more down to earth regarding the impact of the event written in my editorial news style, specifically in my writing style from your fine tuned model, drawing the types of conclusions I would in a down to earth manner. Make the output short. Don't put any fluff in the middle. Here is the raw inputs of various twitter data dumps: {args.prompt}"

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

    # Get and print response
    response = get_model_response(client, prefixed_prompt)
    print(response)  # Just print the response without decorations

if __name__ == '__main__':
    main()

