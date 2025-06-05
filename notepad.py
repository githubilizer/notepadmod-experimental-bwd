#!/usr/bin/env python3

import sys
import os
import re
import webbrowser
import logging

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

logging.basicConfig(
    filename=os.path.join(project_root, "notepadmod.log"),
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    force=True
)

from modules.notepad_window import NotepadWindow
from PyQt5.QtWidgets import QApplication
from modules.link_converter import convert_coords_to_links

def main():
    app = QApplication(sys.argv)
    window = NotepadWindow()
    window.show()
    sys.exit(app.exec_())

def log_uncaught_exceptions(exctype, value, tb):
    logging.critical("Uncaught exception", exc_info=(exctype, value, tb))

sys.excepthook = log_uncaught_exceptions

if __name__ == '__main__':
    main()

