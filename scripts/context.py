#!/usr/bin/env python3

import sys
import os
import re
import logging
from openai import OpenAI

# Use environment variable for API key
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def get_last_n_sentences(text, n=3):
    sentences = re.split(r'[.!?]+\s*', text.strip())
    return [s.strip() for s in sentences if s.strip()][-n:]

def process_text(text):
    try:
        sentences = get_last_n_sentences(text)
        context = '. '.join(sentences) + '.'
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "system",
                "content": "You are a helpful assistant that explains things in simple, practical terms. When explaining what something is, start with 'this means' or 'this is' and use everyday language."
            },
            {
                "role": "user",
                "content": f"Explain in a bracketed single line what this is (like how a journalist would quickly explain something): {context}"
            }],
            max_tokens=150,
            temperature=0.7
        )
        
        explanation = response.choices[0].message.content.strip()
        result = f"{text} ({explanation})"
        print(f"OpenAI API response: {result}")
        return result
        
    except Exception as e:
        print(f"Error: {e}")
        return text

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python context.py <text_file>")
        sys.exit(1)
    
    try:
        with open(sys.argv[1], 'r') as f:
            text = f.read().strip()
        process_text(text)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) 
