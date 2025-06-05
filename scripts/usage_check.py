#!/usr/bin/env python3

import sys
import os
import re
import logging
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def get_sentence_context(text, highlighted_word):
    """Get the sentence containing the highlighted word and split it into before/after parts."""
    # Split text into sentences
    sentences = re.split(r'[.!?]+\s*', text.strip())
    
    # Find the sentence containing the highlighted word
    target_sentence = None
    for sentence in sentences:
        if highlighted_word in sentence:
            target_sentence = sentence.strip()
            break
    
    if not target_sentence:
        return None, None, None
        
    # Split the sentence into before and after parts
    parts = target_sentence.split(highlighted_word)
    before_context = parts[0].strip() if parts else ""
    after_context = parts[1].strip() if len(parts) > 1 else ""
    
    return target_sentence, before_context, after_context

def analyze_word_usage(sentence, word, before_context, after_context):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "system",
                "content": "You are a helpful assistant that analyzes whether words make sense in their context. Respond with either 'MAKES_SENSE: [explanation]' or 'DOES_NOT_MAKE_SENSE: [explanation] | Suggestions: [alternative words]'"
            },
            {
                "role": "user",
                "content": f"Analyze if the word '{word}' makes sense in this sentence: '{sentence}'\nContext before word: '{before_context}'\nContext after word: '{after_context}'"
            }],
            max_tokens=150,
            temperature=0.7
        )
        
        result = response.choices[0].message.content.strip()
        print(f"OpenAI API response: {result}")
        return result
        
    except Exception as e:
        print(f"Error: {e}")
        return f"Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python usage_check.py <text_file>")
        sys.exit(1)
    
    try:
        with open(sys.argv[1], 'r') as f:
            text = f.read().strip()
            
        # The first line should be the highlighted word
        lines = text.split('\n', 1)
        if len(lines) != 2:
            print("Error: Input should contain highlighted word on first line and full text on second line")
            sys.exit(1)
            
        highlighted_word = lines[0].strip()
        full_text = lines[1].strip()
        
        sentence, before_ctx, after_ctx = get_sentence_context(full_text, highlighted_word)
        if sentence:
            result = analyze_word_usage(sentence, highlighted_word, before_ctx, after_ctx)
            print(result)
        else:
            print("Error: Could not find the highlighted word in the text")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) 
