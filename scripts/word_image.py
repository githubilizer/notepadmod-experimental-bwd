#!/usr/bin/env python3

from PIL import Image, ImageDraw, ImageFont
import os
import logging
import tempfile

def split_word(word, max_length=7):
    """Split the word into lines of max_length with hyphenation for better readability."""
    parts = [word[i:i + max_length] for i in range(0, len(word), max_length)]
    hyphenated_lines = [f"{part}-" if i < len(parts) - 1 else part for i, part in enumerate(parts)]
    return "\n".join(hyphenated_lines)

def create_word_image(word, output_dir=None):
    """
    Create an image with the word displayed in yellow text on black background.
    
    Args:
        word (str): The word or text to display in the image
        output_dir (str, optional): Directory to save the image. If None, uses a temp directory
        
    Returns:
        str: Path to the created image file
    """
    logging.debug(f"Creating word image for: {word}")
    
    # Use system temp directory if no output directory specified
    if not output_dir:
        output_dir = tempfile.gettempdir()
    
    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Format the text with hyphenation for better readability
    hyphenated_text = split_word(word)
    
    # Create a black square image
    image_size = (500, 500)
    image = Image.new("RGB", image_size, "black")
    
    # Initialize ImageDraw
    draw = ImageDraw.Draw(image)
    
    # Define the font (try DejaVuSans-Bold or fallback to default)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 80)
    except IOError:
        try:
            # Try system font paths
            system_font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
                "/System/Library/Fonts/Helvetica.ttc",  # macOS
                "C:\\Windows\\Fonts\\arial.ttf"  # Windows
            ]
            
            for font_path in system_font_paths:
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, 80)
                    break
            else:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
    
    # Calculate text size and position
    bbox = draw.textbbox((0, 0), hyphenated_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center the text
    text_x = (image_size[0] - text_width) // 2
    text_y = (image_size[1] - text_height) // 2
    
    # Draw text
    draw.text((text_x, text_y), hyphenated_text, font=font, fill="#90EE90")
    
    # Save image with a sanitized filename
    sanitized_word = "".join(c if c.isalnum() else "_" for c in word)
    output_file = os.path.join(output_dir, f"word_image_{sanitized_word}.png")
    image.save(output_file)
    
    logging.debug(f"Word image created at: {output_file}")
    return output_file

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python word_image.py <word>")
        sys.exit(1)
    
    word = sys.argv[1]
    output_dir = os.path.join(tempfile.gettempdir(), "word_images")
    image_path = create_word_image(word, output_dir)
    print(f"Image created: {image_path}") 