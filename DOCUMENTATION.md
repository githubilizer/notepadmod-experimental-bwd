# NotepadMod Documentation

## Project Structure Overview

### Core Components
- `notepad.py` - Main application entry point
- `modules/notepad_window.py` - Main window GUI implementation
- `modules/editor.py` - Text editor core functionality
- `modules/script_runner.py` - Script execution framework

### Key Scripts (scripts/)
- **Text Processing**:
  - `timeSaver4445.py` - Primary text formatting engine
  - `ts[1-4].py` - Specialized text processors
  - `shrtn.py` - Text compression/shortening
  
- **Media Handling**:
  - `cpyimagesv4.py` - Image management system
  - `text2png_ALL_v3.py` - Text-to-image converter

- **Geospatial**:
  - `gps.py` - Coordinate processing
  - `segmentMoversAllv6.py` - Geospatial segment analysis

### Resources
- Icons: `c6sortv2_icon.png`, `cpyimages_icon.png`
- Requirements: `resources/requirements.txt`

## Getting Started
```bash
# Install dependencies
pip install -r resources/requirements.txt

# Launch application
python notepad.py
```

## Key Shortcuts
- Ctrl+N: New file (now in first toolbar)
- Ctrl+S: Save file
- Ctrl+I: Toggle image pane