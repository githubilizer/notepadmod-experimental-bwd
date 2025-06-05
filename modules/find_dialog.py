# /modules/find_dialog.py

import logging
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCharFormat, QColor
from PyQt5.QtWidgets import QTextEdit

class FindDialog(QDialog):
    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.setWindowTitle("Find")
        self.setModal(False)
        self.setupUI()
        self.setupConnections()
        logging.debug("FindDialog initialized.")

    def setupUI(self):
        layout = QVBoxLayout()

        # Search input
        self.searchInput = QLineEdit()
        self.searchInput.setPlaceholderText("Enter text to find")
        layout.addWidget(QLabel("Find:"))
        layout.addWidget(self.searchInput)

        # Options
        optionsLayout = QHBoxLayout()
        self.caseCheckbox = QCheckBox("Case Sensitive")
        self.wholeCheckbox = QCheckBox("Whole Words")
        optionsLayout.addWidget(self.caseCheckbox)
        optionsLayout.addWidget(self.wholeCheckbox)
        layout.addLayout(optionsLayout)

        # Buttons
        buttonsLayout = QHBoxLayout()
        self.findNextBtn = QPushButton("Find Next")
        self.findPrevBtn = QPushButton("Find Previous")
        self.closeBtn = QPushButton("Close")
        buttonsLayout.addWidget(self.findNextBtn)
        buttonsLayout.addWidget(self.findPrevBtn)
        buttonsLayout.addStretch()
        buttonsLayout.addWidget(self.closeBtn)
        layout.addLayout(buttonsLayout)

        # Counter Label
        self.counterLabel = QLabel("0 matches found.")
        layout.addWidget(self.counterLabel)

        self.setLayout(layout)
        logging.debug("FindDialog UI setup complete.")

    def setupConnections(self):
        self.findNextBtn.clicked.connect(self.findNext)
        self.findPrevBtn.clicked.connect(self.findPrevious)
        self.closeBtn.clicked.connect(self.close)
        self.searchInput.textChanged.connect(self.updateSearch)
        logging.debug("FindDialog connections established.")

    def updateSearch(self):
        text = self.searchInput.text()
        case_sensitive = self.caseCheckbox.isChecked()
        whole_words = self.wholeCheckbox.isChecked()

        # Perform search and highlight
        count = self.editor.highlightAllMatches(text, case_sensitive, whole_words)
        logging.debug(f"Search updated. Text: '{text}', Matches found: {count}")

        if count > 0 and text:
            self.editor.currentMatchIndex = 0  # Initialize current match index
            # Get the cursor and move it to the first match; adjust to select the found text
            cursor = self.editor.textCursor()
            start_pos = self.editor.matches[0].position() - len(text)
            cursor.setPosition(max(start_pos, 0))
            self.editor.setTextCursor(cursor)
            self.editor.ensureCursorVisible()
            cursor.movePosition(cursor.Right, cursor.KeepAnchor, len(text))

        self.updateCounterLabel()

    def findNext(self):
        if not self.editor.matches:
            QMessageBox.information(self, "Find", "No matches found.")
            logging.info("Find Next: No matches found.")
            return

        total = len(self.editor.matches)
        if not hasattr(self.editor, 'currentMatchIndex'):
            self.editor.currentMatchIndex = 0
        else:
            self.editor.currentMatchIndex = (self.editor.currentMatchIndex + 1) % total
            if self.editor.currentMatchIndex == 0:
                self.parent().statusBar().showMessage("Reached end of document. Wrapped to beginning.", 5000)
                logging.info("Find Next: Wrapped to beginning of document.")

        match_cursor = self.editor.matches[self.editor.currentMatchIndex]
        cursor = self.editor.textCursor()
        start_pos = match_cursor.position() - len(self.searchInput.text())
        cursor.setPosition(max(start_pos, 0))
        # Expand selection by moving right by the length of the search text
        cursor.movePosition(cursor.Right, cursor.KeepAnchor, len(self.searchInput.text()))
        self.editor.setTextCursor(cursor)
        self.editor.ensureCursorVisible()
        self.searchInput.selectAll()
        self.updateCounterLabel()

        # Apply extra selection with a purple background
        extra_sel = QTextEdit.ExtraSelection()
        fmt = QTextCharFormat()
        fmt.setBackground(QColor("purple"))
        extra_sel.format = fmt
        extra_sel.cursor = self.editor.textCursor()
        self.editor.setExtraSelections([extra_sel])

    def findPrevious(self):
        if not self.editor.matches:
            QMessageBox.information(self, "Find", "No matches found.")
            logging.info("Find Previous: No matches found.")
            return

        total = len(self.editor.matches)
        if not hasattr(self.editor, 'currentMatchIndex'):
            self.editor.currentMatchIndex = 0
        else:
            self.editor.currentMatchIndex = (self.editor.currentMatchIndex - 1) % total
            if self.editor.currentMatchIndex == total - 1:
                self.parent().statusBar().showMessage("Reached beginning of document. Wrapped to end.", 5000)
                logging.info("Find Previous: Wrapped to end of document.")

        match_cursor = self.editor.matches[self.editor.currentMatchIndex]
        cursor = self.editor.textCursor()
        start_pos = match_cursor.position() - len(self.searchInput.text())
        cursor.setPosition(max(start_pos, 0))
        # Expand selection by moving right by the length of the search text
        cursor.movePosition(cursor.Right, cursor.KeepAnchor, len(self.searchInput.text()))
        self.editor.setTextCursor(cursor)
        self.editor.ensureCursorVisible()
        self.searchInput.selectAll()
        self.updateCounterLabel()

        # Apply extra selection with a purple background
        extra_sel = QTextEdit.ExtraSelection()
        fmt = QTextCharFormat()
        fmt.setBackground(QColor("purple"))
        extra_sel.format = fmt
        extra_sel.cursor = self.editor.textCursor()
        self.editor.setExtraSelections([extra_sel])

    def closeEvent(self, event):
        # Optionally clear highlights when the dialog is closed
        self.editor.clearHighlights()
        logging.debug("FindDialog closed and highlights cleared.")
        event.accept()

    def updateCounterLabel(self):
        if hasattr(self.editor, 'matches') and self.editor.matches:
            # Use currentMatchIndex if available, default to 0
            idx = self.editor.currentMatchIndex if hasattr(self.editor, 'currentMatchIndex') else 0
            total = len(self.editor.matches)
            self.counterLabel.setText(f"Match {idx + 1} of {total}")
        else:
            self.counterLabel.setText("0 matches found.")

