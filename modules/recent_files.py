# /modules/recent_files.py

from PyQt5.QtWidgets import QAction, QMenu, QLineEdit, QWidgetAction, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
import os
import logging

class RecentFiles:
    def __init__(self, parent, menu, max_files=20, recent_files_path="/home/j/Desktop/notepadmod/recentfiles.txt"):
        self.parent = parent
        self.menu = menu
        self.max_files = max_files
        self.recent_files_path = recent_files_path
        self.recent_files = self.load_recent_files()
        self.file_actions = []

        # Set menu style to increase text size
        self.menu.setStyleSheet("""
            QMenu {
                font-size: 16px;
            }
            QMenu::item {
                padding: 8px 20px;
                min-height: 36px;
            }
            QMenu::item:selected {
                background-color: #2d2d2d;
            }
            QMenu::item[yellowText="true"] {
                color: yellow;
            }
        """)

        self.create_search_box()
        self.menu.aboutToShow.connect(self.update_menu)

    def load_recent_files(self):
        if os.path.exists(self.recent_files_path):
            with open(self.recent_files_path, 'r', encoding='utf-8', errors='replace') as file:
                files = file.read().splitlines()
                return files[:self.max_files]
        return []

    def save_recent_files(self):
        try:
            os.makedirs(os.path.dirname(self.recent_files_path), exist_ok=True)
            with open(self.recent_files_path, 'w', encoding='utf-8') as file:
                for file_path in self.recent_files:
                    file.write(f"{file_path}\n")
        except Exception as e:
            print(f"Error saving recent files: {e}")

    def create_search_box(self):
        """Creates a search box at the top of the Recent menu."""
        search_action = QWidgetAction(self.parent)
        search_box = QLineEdit(self.parent)
        search_box.setPlaceholderText("Search recent files...")
        search_box.setStyleSheet("""
            QLineEdit {
                font-size: 16px;
                padding: 8px;
                min-height: 36px;
            }
        """)
        search_box.textChanged.connect(self.filter_recent_files)
        search_action.setDefaultWidget(search_box)
        self.menu.addAction(search_action)
        self.menu.addSeparator()

    def update_menu(self):
        """Updates the Recent Files menu with the latest files and applies filtering."""
        self.recent_files = self.load_recent_files()
        # Remove all existing file actions except the search box and separator
        for action in self.file_actions:
            self.menu.removeAction(action)
        self.file_actions.clear()

        # Create a list of tuples (display_name, file_path) for sorting
        file_entries = []
        
        # Add recent files
        for file_path in self.recent_files:
            if os.path.exists(file_path):
                display_name = os.path.basename(file_path)
                file_entries.append((display_name, file_path, False))  # False indicates not a desktop number file

        # Add files from desktop that start with 4 numbers
        desktop_path = os.path.expanduser("~/Desktop")
        if os.path.exists(desktop_path):
            for filename in os.listdir(desktop_path):
                if len(filename) >= 4 and filename[:4].isdigit():
                    file_path = os.path.join(desktop_path, filename)
                    if os.path.isfile(file_path):
                        file_entries.append((filename, file_path, True))  # True indicates a desktop number file

        # Sort by display name (case-insensitive)
        file_entries.sort(key=lambda x: x[0].lower())

        # Add file actions based on sorted entries
        for display_name, file_path, is_desktop_number in file_entries:
            # Skip duplicates (prefer desktop number files)
            if any(a.data() == file_path for a in self.file_actions):
                continue
                
            action = QAction(display_name, self.parent)
            action.setData(file_path)
            
            # Set yellow text for special files and desktop number files
            if display_name in ['TODAY_ONLY.vhd', 'ttag_sort_order.vhd'] or is_desktop_number:
                action.setProperty("yellowText", True)
                
            action.triggered.connect(self.open_recent_file)
            self.menu.addAction(action)
            self.file_actions.append(action)

    def filter_recent_files(self, text):
        """Filters the visible recent files based on the search text."""
        for action in self.file_actions:
            file_name = action.text()
            if text.lower() in file_name.lower():
                action.setVisible(True)
            else:
                action.setVisible(False)

    def open_recent_file(self):
        """Opens the selected recent file."""
        action = self.parent.sender()
        if action:
            file_path = action.data()
            if os.path.exists(file_path):
                self.parent.openFile(file_path)
                self.add_file(file_path)  # Move to top of recent files
            else:
                if file_path in self.recent_files:
                    self.recent_files.remove(file_path)
                    self.save_recent_files()

    def add_file(self, file_path):
        """Adds a file to the recent files list."""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        if len(self.recent_files) > self.max_files:
            self.recent_files = self.recent_files[:self.max_files]
        self.save_recent_files()
        self.update_menu()

