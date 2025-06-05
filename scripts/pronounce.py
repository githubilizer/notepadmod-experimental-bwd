#!/usr/bin/env python3

import sys
import os
import re
import logging
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def get_pronunciation(word):
    """Get phonetic pronunciation of the provided word."""
    try:        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "system",
                "content": "You are a skilled linguistics assistant who provides simple phonetic pronunciations of words. Your responses should be concise and easy to understand for non-linguists. Only provide the phonetic pronunciation with no explanations."
            },
            {
                "role": "user",
                "content": f"Provide a simple phonetic pronunciation guide for the word: '{word}'. Use common syllable spellings rather than IPA symbols. Your response should ONLY contain the pronunciation without any explanations or additional text."
            }],
            max_tokens=100,
            temperature=0.3
        )
        
        pronunciation = response.choices[0].message.content.strip()
        # Clean up the pronunciation to remove any extra text the model might add
        pronunciation = re.sub(r'^[\'"]*|[\'"]*$', '', pronunciation)  # Remove quotes
        pronunciation = re.sub(r'^.*?pronunciation:?\s*', '', pronunciation, flags=re.IGNORECASE)  # Remove "pronunciation:" prefix
        
        # Format the pronunciation with double brackets
        formatted_pronunciation = f" (({pronunciation}))"
        print(f"OpenAI API response: {formatted_pronunciation}")
        return formatted_pronunciation
        
    except Exception as e:
        print(f"Error: {e}")
        return f" ((Error: Could not get pronunciation))"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python pronounce.py <text_file>")
        sys.exit(1)
    
    try:
        with open(sys.argv[1], 'r') as f:
            text = f.read().strip()
        
        # The word to get pronunciation for is the entire content of the file
        word = text.strip()
        
        if not word:
            print("Error: Empty input")
            sys.exit(1)
            
        result = get_pronunciation(word)
        print(result)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) 