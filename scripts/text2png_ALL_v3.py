from PIL import Image, ImageDraw, ImageFont
import sys
import os
import re
from colorama import init, Fore, Style

# converts Title Tag {words} to pngs brilliantly
# args - usually your daily xxxDraft.vhd file, or, ttag_sort_order.vhd sometimes too



#v3 - now includes hyphenating for better readability


# Initialize colorama
init(autoreset=True)

def split_word(word, max_length=7):
    """Split the word into lines of max_length with hyphenation."""
    parts = [word[i:i + max_length] for i in range(0, len(word), max_length)]
    hyphenated_lines = [f"{part}-" if i < len(parts) - 1 else part for i, part in enumerate(parts)]
    return "\n".join(hyphenated_lines)

def create_image(word, output_dir):
    print(f"Creating image for word: {word}")  # Debug output
    hyphenated_text = split_word(word)
    
    # Create a black square image
    image_size = (500, 500)
    image = Image.new("RGB", image_size, "black")
    
    # Initialize ImageDraw
    draw = ImageDraw.Draw(image)
    
    # Define the font (Ensure the font file is available or adjust the path)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 80)
    except IOError:
        font = ImageFont.load_default()
    
    # Calculate text size and position
    bbox = draw.textbbox((0, 0), hyphenated_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center the text
    text_x = (image_size[0] - text_width) // 2
    text_y = (image_size[1] - text_height) // 2
    
    # Draw text
    draw.text((text_x, text_y), hyphenated_text, font=font, fill="yellow")
    
    # Save image
    output_file = os.path.join(output_dir, f"{word}.png")
    print(f"Saving image to: {output_file}")  # Debug output
    image.save(output_file)
    
    return f"{Fore.GREEN}Image created: {output_file}{Style.RESET_ALL}"

def main():
    # Check if a file path is provided
    if len(sys.argv) != 2:
        print(f"{Fore.RED}Usage: python3 {os.path.basename(sys.argv[0])} <input_file>{Style.RESET_ALL}")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # Check if the input file exists
    if not os.path.isfile(input_file):
        print(f"{Fore.RED}Error: The file '{input_file}' does not exist.{Style.RESET_ALL}")
        sys.exit(1)
    
    # Directory for images
    output_dir = "/home/j/Desktop/YTs/aa UNTV Today/bsqs/"
    os.makedirs(output_dir, exist_ok=True)
    
    title_pattern = re.compile(r'"Title:([^"]+)"')
    words_to_process = set()
    
    # Read file
    with open(input_file, 'r', encoding='utf-8') as file:
        for line_number, line in enumerate(file, start=1):
            matches = title_pattern.findall(line)
            if matches:
                for word in matches:
                    words_to_process.add(word)
            else:
                continue
    
    if not words_to_process:
        print(f"{Fore.YELLOW}No matching 'Title:{{word}}' patterns found in the input file.{Style.RESET_ALL}")
        sys.exit(0)
    
    # Process words
    for word in sorted(words_to_process):
        image_path = os.path.join(output_dir, f"{word}.png")
        if os.path.isfile(image_path):
            print(f"{Fore.BLUE}Image already exists for '{word}': {image_path} (Skipping){Style.RESET_ALL}")
        else:
            try:
                message = create_image(word, output_dir)
                print(message)
            except Exception as e:
                print(f"{Fore.RED}Error creating image for '{word}': {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()

