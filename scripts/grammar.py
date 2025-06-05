#!/usr/bin/env python3

import sys
import os
import re
import logging
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def fix_grammar(text):
    """Fix grammar and spelling errors in the provided text."""
    try:        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "system",
                "content": "You are a skilled editor who exclusively fixes spelling errors, grammar issues, and improves sentence structure without changing the meaning of the text. Maintain the same tone and style. Only provide the corrected text with no explanations."
            },
            {
                "role": "user",
                "content": f"Fix the grammar and spelling in this text without changing its meaning: {text}"
            }],
            max_tokens=1000,
            temperature=0.3
        )
        
        corrected_text = response.choices[0].message.content.strip()
        print(f"OpenAI API response: {corrected_text}")
        return corrected_text
        
    except Exception as e:
        print(f"Error: {e}")
        return text

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python grammar.py <text_file>")
        sys.exit(1)
    
    try:
        with open(sys.argv[1], 'r') as f:
            text = f.read().strip()
        
        result = fix_grammar(text)
        print(result)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) 
