#!/usr/bin/env python3
import argparse
import sys
import re
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

def setup_argparse():
    parser = argparse.ArgumentParser(description='Test OpenAI fine-tuned model with a prompt')
    parser.add_argument('prompt', help='Input prompt for the model')
    return parser

def extract_header_and_content(text):
    # Normalize Unicode paragraph separators to newline characters
    text = text.replace('\u2029', '\n')
    lines = text.splitlines()
    if not lines:
        return text, ""
    header = lines[0].strip()
    content = "\n".join(lines[1:]).strip()
    return header, content

def remove_unwanted_quotes(response_text, header):
    response_text = response_text.strip()
    # Remove wrapping quotes if they exactly enclose the header
    pattern = r"^(['\"])(.+?)\1"
    match = re.match(pattern, response_text)
    if match:
        extracted_header = match.group(2)
        if extracted_header == header:
            response_text = header + response_text[len(match.group(0)):]
    return response_text

def main():
    try:
        parser = setup_argparse()
        args = parser.parse_args()
        
        header, content_to_rewrite = extract_header_and_content(args.prompt)
        
        if not content_to_rewrite:
            prefixed_prompt = (
                "Write in 100 words or less as if it's written by a military journalist: "
                "concise, engaging, factual, and down-to-earth. "
                f"Here is the input: {args.prompt}"
            )
        else:
            prefixed_prompt = (
                "Write in 100 words or less as if it's written by a military journalist: "
                "concise, engaging, factual, and down-to-earth. "
                "IMPORTANT: Your final output MUST begin with the following header EXACTLY as provided, without any modifications.\n"
                f"{header}\n\n"
                "Now, rewrite the following content so that it flows naturally from the header above. "
                "Do NOT modify the header – only rewrite the text below:\n"
                f"{content_to_rewrite}"
            )
        
        # (Optional) Debug: print the prompt to verify its structure
        # print("Prefixed Prompt:\n", prefixed_prompt)
        
        # Get API key from file or environment variable
        api_key = get_api_key()
        if not api_key:
            print("Error: OpenAI API key not found. Please create apikeynew_13012025.txt in the project root directory or set OPENAI_API_KEY environment variable.", file=sys.stderr)
            sys.exit(1)
        
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Get response from the model
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{'role': 'user', 'content': prefixed_prompt}],
            temperature=TEMPERATURE,
            top_p=TOP_P
        )
        response_text = response.choices[0].message.content
        
        # Post-process the output: remove any unwanted wrapping quotes from the header
        if content_to_rewrite and header:
            response_text = remove_unwanted_quotes(response_text, header)
            if not response_text.startswith(header):
                response_text = header + "\n" + response_text
        
        print(response_text)
    
    except Exception as e:
        print("An error occurred:", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

