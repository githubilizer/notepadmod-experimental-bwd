import re


def convert_coords_to_links(text):
    """Convert GPS coordinates in the text to hyperlinks pointing to deepstatemap.live."""
    coord_pattern = re.compile(r'(\d+\.\d+),\s*(\d+\.\d+)')
    
    def replace_with_link(match):
        lat, lon = match.groups()
        url = f"https://deepstatemap.live/en#7/{lat}/{lon}"
        return f'<a href="{url}">{lat}, {lon}</a>'
    
    return coord_pattern.sub(replace_with_link, text) 