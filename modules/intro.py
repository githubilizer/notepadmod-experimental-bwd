def process_intro(text):
    # Split into first line and remaining content
    lines = text.split('\n')
    if not lines:
        return ""
    
    first_line = lines[0].strip()
    remaining_text = '\n'.join(lines[1:])
    
    # Only process the remaining text
    if remaining_text:
        # Existing API call logic here (simplified example)
        processed_rest = rewrite_content(remaining_text)  # Your existing rewrite function
        return f"{first_line}\n\n{processed_rest}"
    
    return first_line 