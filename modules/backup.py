# /modules/backup.py

import os
import shutil
import datetime
import logging

from PyQt5.QtWidgets import QMessageBox

class Backup:
    def __init__(self, parent_window):
        self.parent = parent_window

    def backupCurrentFile(self):
        editor = self.parent.currentEditor()
        if not editor:
            self.parent.statusBar().showMessage("No open editor to backup.", 5000)
            logging.warning("Attempted to backup with no open editor.")
            return

        filepath = editor.property("filepath")
        if not filepath:
            self.parent.statusBar().showMessage("Cannot backup an unsaved (Untitled) file.", 5000)
            logging.warning("Attempted to backup an unsaved (Untitled) file.")
            return

        if not os.path.exists(filepath):
            self.parent.statusBar().showMessage(f"File does not exist: {filepath}", 5000)
            logging.error(f"File does not exist for backup: {filepath}")
            return

        # Define backup directory
        backup_dir = os.path.join(os.path.dirname(filepath), 'backups')
        os.makedirs(backup_dir, exist_ok=True)

        # Define backup file name with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        basename = os.path.basename(filepath)
        backup_filename = f"{basename}.{timestamp}.bak"
        backup_path = os.path.join(backup_dir, backup_filename)

        try:
            shutil.copy2(filepath, backup_path)
            self.parent.statusBar().showMessage(f"Backup created: {backup_path}", 5000)
            logging.info(f"Backup created for {filepath} at {backup_path}")
        except Exception as e:
            QMessageBox.warning(self.parent, "Backup Failed", f"Failed to create backup:\n{e}")
            logging.error(f"Failed to create backup for {filepath}: {e}")

