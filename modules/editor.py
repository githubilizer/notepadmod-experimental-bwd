# /modules/editor.py

import re
import os
import logging
import time
import webbrowser
import requests
import urllib.parse
import subprocess
import tempfile
from PyQt5.QtCore import Qt, QFileInfo, QTimer, QRegExp
from PyQt5.QtGui import (
    QFont, QFontDatabase, QColor, QTextCursor, QTextDocument, QTextCharFormat
)
from PyQt5.QtWidgets import (
    QPlainTextEdit, QMessageBox, QAction, QMenu, QTextEdit, QInputDialog, QLineEdit, QApplication
)
from .syntax_highlighter import VHDLSyntaxHighlighter

class Editor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        self.setTabStopWidth(40)
        
        # Set font
        font_db = QFontDatabase()
        if "Ubuntu Sans Semi-Bold" in font_db.families():
            self.main_font_size = 16
            self.main_font = QFont("Ubuntu Sans Semi-Bold", self.main_font_size)
            self.main_font.setWeight(65)
        else:
            self.main_font_size = 16
            self.main_font = QFont("Ubuntu Sans Semi Bold", self.main_font_size)
            self.main_font.setWeight(65)
        self.setFont(self.main_font)

        # Set plain text color (handled by syntax highlighter)
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #888888;  /* Darker gray color for regular text */
                selection-background-color: #404040;  /* Changed to grey from blue */
                selection-color: #ffffff;
            }
            QScrollBar:vertical {
                width: 50px;
                background: #2d2d2d;  /* Slightly lighter than editor background */
                border: none;
            }
            QScrollBar::handle:vertical {
                min-width: 30px;
                min-height: 200px;
                background: #4d4d4d;  /* Medium grey for scroll handle */
                border-radius: 4px;
                margin: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
                border: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
                border: none;
            }
        """)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        
        # Initialize syntax highlighter
        self.highlighter = VHDLSyntaxHighlighter(self.document())

        # Enable document block visibility
        self.document().documentLayout().setProperty("BlockLayout", True)

        self.zoomFactor = 1.0

        # Variables for Find functionality
        self.last_search = ""
        self.last_search_position = 0
        self.matches = []
        self.current_match_index = -1

        # Define the highlight format for search matches only
        self.search_format = QTextCharFormat()
        self.search_format.setBackground(QColor("#a8d08d"))

        # Connect cursor position change to parent's image sync
        self.cursorPositionChanged.connect(self.handleCursorMove)
        
        # Connect scroll bar changes to image sync
        self.verticalScrollBar().valueChanged.connect(self.handleScroll)
        
        # Add debounce timer for scroll events
        self._scroll_timer = QTimer()
        self._scroll_timer.setSingleShot(True)
        self._scroll_timer.setInterval(100)  # 100ms debounce
        self._scroll_timer.timeout.connect(self.handleScrollTimeout)

        # Store the last clicked URL
        self.last_clicked_url = None

        # Add requests for web searching
        self.requests = requests

        self.verticalScrollBar().setStyleSheet(
            "QScrollBar:vertical { width: 50px; background: #2d2d2d; }"
            "QScrollBar::handle:vertical { min-width: 30px; min-height: 200px; background: #4d4d4d; border-radius: 4px; margin: 4px; }"
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }"
            "QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }"
        )

    def handleCursorMove(self):
        if hasattr(self.window(), 'syncImageScroll'):
            self.window().syncImageScroll()

    def createMimeDataFromSelection(self):
        mime_data = super().createMimeDataFromSelection()
        if mime_data.hasText():
            # Just use plain text, no HTML conversion needed
            return mime_data
        return mime_data

    def insertFromMimeData(self, source):
        if source.hasText():
            # Just insert plain text directly
            cursor = self.textCursor()
            cursor.insertText(source.text())
        else:
            super().insertFromMimeData(source)

    def keyPressEvent(self, event):
        # Add keyboard shortcut for toggling special lines
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_H:
            self.toggleSpecialLines()
            return
        super().keyPressEvent(event)
        # Emit textChanged signal to trigger title segments update
        self.textChanged.emit()

    def wheelEvent(self, event):
        """Enable Ctrl + Scroll to zoom in and out."""
        if event.modifiers() & Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self.main_font_size *= 1.1
                self.zoomFactor += 0.1
            elif event.angleDelta().y() < 0:
                self.main_font_size = max(self.main_font_size * 0.9, 1)
                self.zoomFactor = max(self.zoomFactor - 0.1, 0.1)

            # Update font
            self.main_font.setPointSizeF(self.main_font_size)
            self.setFont(self.main_font)
            
            event.accept()
        else:
            super(Editor, self).wheelEvent(event)

    def showContextMenu(self, point):
        menu = QMenu(self)
        cursor = self.textCursor()
        selected_text = cursor.selectedText()

        # Add Title segment sending functionality at the top if applicable
        if self._is_title_line(cursor):
            file_targets = self._find_vhd_files()
            if file_targets:
                # Add each matching file option directly to the menu
                for target_file in file_targets:
                    action = menu.addAction(f"Send to {os.path.basename(target_file)}")
                    action.triggered.connect(lambda _, f=target_file: self._send_to_vhd(f))
                menu.addSeparator()
            
            # Add Send to TODAY_ONLY.txt option
            sendTodayAct = QAction("Send to TODAY_ONLY.txt", self)
            sendTodayAct.triggered.connect(lambda: self._send_to_vhd("/home/j/Desktop/IMPORTANT_NOTEPADS/TODAY_ONLY.txt"))
            menu.addAction(sendTodayAct)

            # Add Send to owp123 option
            sendOwpAct = QAction("Send to owp123.vhd", self)
            sendOwpAct.triggered.connect(lambda: self._send_to_vhd("/home/j/Desktop/IMPORTANT_NOTEPADS/owp123.vhd"))
            menu.addAction(sendOwpAct)
            menu.addSeparator()

            # Add new option to move the segment down (nest it under the next segment)
            moveDownAct = QAction("Move segment down", self)
            moveDownAct.triggered.connect(self._move_segment_down)
            menu.addAction(moveDownAct)
            menu.addSeparator()

        # Add cut/copy/paste actions below the 'Send to...' option
        cutAct = menu.addAction("Cut")
        cutAct.triggered.connect(self.cut)
        copyAct = menu.addAction("Copy")
        copyAct.triggered.connect(self.copy)
        pasteAct = menu.addAction("Paste")
        pasteAct.triggered.connect(self.paste)
        menu.addSeparator()
        
        # Add toggle special lines action
        toggleAction = QAction("Toggle URLs/Timestamps", self)
        toggleAction.setShortcut("Ctrl+H")
        toggleAction.triggered.connect(self.toggleSpecialLines)
        menu.addAction(toggleAction)
        menu.addSeparator()
        
        # Add web search action if text is selected
        if selected_text:
            searchWebAct = QAction("Search Web && Insert Results", self)
            searchWebAct.triggered.connect(lambda: self.searchWebAndInsert(selected_text))
            menu.addAction(searchWebAct)
            menu.addSeparator()

        # Get the word under cursor for synonyms
        cursor.select(QTextCursor.WordUnderCursor)
        selected_word = cursor.selectedText()

        # Restore original selection
        cursor.setPosition(self.textCursor().position())
        if selected_text:
            cursor.setPosition(self.textCursor().anchor(), QTextCursor.KeepAnchor)
        self.setTextCursor(cursor)

        # Add a separator before the script actions
        menu.addSeparator()

        # Add Run script actions delegated to ScriptRunner
        try:
            run_timeSaverAct = QAction("Run timeSaver4445", self)
            run_timeSaverAct.triggered.connect(self.window().script_runner.run_timeSaverScript)
            menu.addAction(run_timeSaverAct)

            runTs1Act = QAction("Run ts1", self)
            runTs1Act.triggered.connect(self.window().script_runner.runTs1Script)
            menu.addAction(runTs1Act)

            runTs2Act = QAction("Run ts2", self)
            runTs2Act.triggered.connect(self.window().script_runner.runTs2Script)
            menu.addAction(runTs2Act)

            runTs3Act = QAction("Run ts3", self)
            runTs3Act.triggered.connect(self.window().script_runner.runTs3Script)
            menu.addAction(runTs3Act)

            runTs4Act = QAction("Run ts4", self)
            runTs4Act.triggered.connect(self.window().script_runner.runTs4Script)
            menu.addAction(runTs4Act)

            runIntroAct = QAction("Run intro", self)
            runIntroAct.triggered.connect(self.window().script_runner.runIntroScript)
            menu.addAction(runIntroAct)

        except AttributeError as e:
            logging.error(f"Failed to connect script runner actions: {e}")
        
        if self._is_title_line(cursor):
            menu.addSeparator()
            sendKnyAct = QAction("Send to kny.txt", self)
            sendKnyAct.triggered.connect(self._send_to_kny)
            menu.addAction(sendKnyAct)

        menu.exec_(self.mapToGlobal(point))

    def toggleSpecialLines(self):
        """Toggle visibility of lines starting with https or Timestamp"""
        self.highlighter.toggleSpecialLines()
        # Force layout update
        self.document().documentLayout().documentSizeChanged.emit(self.document().size())
        # Update viewport to reflect changes
        self.viewport().update()

    def searchWebAndInsert(self, query):
        """Create a direct Twitter search link with advanced search operators."""
        try:
            # Clean up the query
            query = query.strip()
            
            # Common words and abbreviations to filter out
            stop_words = {'in', 'at', 'the', 'of', 'and', 'or', 'to', 'for', 'a', 'an', 'st.', 'st', 'dr.', 'dr', 'mr.', 'mr', 'mrs.', 'mrs'}
            
            # Clean and split words
            words = []
            for word in query.split():
                # Remove punctuation and convert to lowercase for checking
                clean_word = word.strip('.,!?()[]{}":;').lower()
                # Skip if it's a stop word
                if clean_word in stop_words:
                    continue
                # Handle hyphenated words - split and add separately
                if '-' in word:
                    parts = [p for p in word.split('-') if p.strip()]
                    words.extend(parts)
                else:
                    words.append(word)
            
            # Initialize priority scoring for terms
            term_scores = {}
            
            # Score proper nouns (highest priority)
            proper_nouns = [word for word in words if word[0].isupper() and len(word) > 1]
            for noun in proper_nouns:
                # Higher score for location names
                if any(loc in noun for loc in ['burg', 'grad', 'ville', 'city', 'region', 'oblast']):
                    term_scores[noun] = 5
                else:
                    term_scores[noun] = 4
            
            # Score important two-word phrases
            for i in range(len(words)-1):
                phrase = " ".join(words[i:i+2])
                if any(term in phrase.lower() for term in ['cyber', 'attack', 'hack', 'breach', 'infrastructure', 'military', 'forces']):
                    # Only add if neither word is a stop word
                    if not any(w.lower() in stop_words for w in phrase.split()):
                        term_scores[f'"{phrase}"'] = 3
            
            # Score technical terms and action words
            important_terms = ['cyber', 'hack', 'attack', 'breach', 'infrastructure', 'military', 'forces', 'looted', 'wiped', 'exfiltrated']
            for word in words:
                if word.lower() in important_terms:
                    term_scores[word] = 2
            
            # Get the top 5 terms by score
            sorted_terms = sorted(term_scores.items(), key=lambda x: (-x[1], len(x[0])))  # Sort by score (desc) and then by length
            top_terms = [term for term, score in sorted_terms[:5]]  # Take top 5
            
            # Create the search query
            search_query = " ".join(top_terms)
            
            # Create Twitter search URL
            encoded_query = requests.utils.quote(search_query)
            twitter_search_url = f"https://twitter.com/search?q={encoded_query}&f=live"
            
            # Format the output text
            formatted_text = f"\n\n[Twitter/X Search Results]\nClick to view live results in Firefox for advanced search:\n{search_query}\nURL: {twitter_search_url}\n"
            
            # Get the cursor and insert the text
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.EndOfLine)
            cursor.insertText(formatted_text)
            
        except Exception as e:
            QMessageBox.warning(self, "Search Error", 
                f"Failed to create Twitter search link: {str(e)}\nTry selecting a smaller portion of text.")

    def replaceWordAtCursor(self, new_word):
        cursor = self.textCursor()
        cursor.beginEditBlock()
        cursor.removeSelectedText()
        cursor.insertText(new_word)
        cursor.endEditBlock()

    def find_title_line_above(self, current_line):
        """
        Searches upwards from the current line to find a line that starts with 'Title:'.
        Supports lines that may start with quotes, e.g., '"Title:YourTitle"'.
        """
        for line in range(current_line - 1, 0, -1):
            block = self.document().findBlockByNumber(line - 1)
            text = block.text().strip()
            if re.match(r'^\s*[\'"]?Title:', text, re.IGNORECASE):
                return text
        return None

    # Find and Highlight Methods
    def highlightAllMatches(self, text, case_sensitive=False, whole_words=False):
        self.clearHighlights()
        self.matches = []
        self.current_match_index = -1
        
        if not text:
            return 0
        
        flags = QTextDocument.FindFlags()
        if whole_words:
            flags |= QTextDocument.FindWholeWords
        if case_sensitive:
            flags |= QTextDocument.FindCaseSensitively
        
        cursor = QTextCursor(self.document())
        while True:
            cursor = self.document().find(text, cursor, flags)
            if cursor.isNull():
                break
            self.matches.append(QTextCursor(cursor))
        
        # Create extra selections for all matches
        extra_selections = []
        for match_cursor in self.matches:
            # Correctly use QTextEdit.ExtraSelection
            selection = QTextEdit.ExtraSelection()
            selection.cursor = match_cursor
            selection.format = self.search_format
            extra_selections.append(selection)
        
        self.setExtraSelections(extra_selections)
        
        return len(self.matches)
    
    def clearHighlights(self):
        self.setExtraSelections([])  # Remove all extra selections
        self.matches = []
        self.current_match_index = -1
    
    def findNextMatch(self):
        if not self.matches:
            return False
        self.current_match_index += 1
        wrapped = False
        if self.current_match_index >= len(self.matches):
            self.current_match_index = 0  # Wrap around
            wrapped = True
        found = self.gotoMatch(self.current_match_index)
        return wrapped
    
    def findPreviousMatch(self):
        if not self.matches:
            return False
        self.current_match_index -= 1
        wrapped = False
        if self.current_match_index < 0:
            self.current_match_index = len(self.matches) - 1  # Wrap around
            wrapped = True
        found = self.gotoMatch(self.current_match_index)
        return wrapped
    
    def gotoMatch(self, index):
        if 0 <= index < len(self.matches):
            cursor = self.matches[index]
            self.setTextCursor(cursor)
            return True
        return False
    
    def countMatches(self):
        return len(self.matches)

    def handleScroll(self):
        """Handle scroll events with debounce."""
        # Only start the timer if this wasn't triggered by our own sync
        if not hasattr(self, '_in_sync'):
            self._scroll_timer.start()

    def handleScrollTimeout(self):
        """Debounced scroll handler."""
        if hasattr(self.window(), 'updateImageDisplay'):
            self._in_sync = True
            self.window().updateImageDisplay()
            delattr(self, '_in_sync')

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            cursor = self.cursorForPosition(event.pos())
            # Get the line of text under the cursor
            line = cursor.block().text()
            # Get the position within the line
            pos_in_line = cursor.positionInBlock()
            
            # Find any URLs in the line
            url_pattern = re.compile(r'\bhttps?://[^\s]+\b')
            for match in url_pattern.finditer(line):
                start, end = match.span()
                # Check if click was within URL boundaries
                if start <= pos_in_line < end:
                    url = line[start:end]
                    reply = QMessageBox.question(
                        self,
                        'Open URL',
                        f'Do you want to open this URL in Firefox?\n\n{url}',
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )
                    
                    if reply == QMessageBox.Yes:
                        try:
                            import subprocess
                            
                            # Set environment variables to force Firefox
                            os.environ['BROWSER'] = '/usr/bin/firefox'
                            os.environ['DESKTOP_SESSION'] = 'gnome'
                            
                            logging.info(f"Attempting to open URL: {url}")
                            
                            # Try different methods in sequence
                            try:
                                logging.info("Trying direct Firefox call...")
                                subprocess.run(['firefox', '-new-tab', url], check=True)
                                logging.info("Success with direct Firefox call")
                                return
                            except Exception as e1:
                                logging.error(f"Direct Firefox call failed: {str(e1)}")
                                
                                try:
                                    logging.info("Trying full path Firefox call...")
                                    subprocess.run(['/usr/bin/firefox', '-new-tab', url], check=True)
                                    logging.info("Success with full path Firefox call")
                                    return
                                except Exception as e2:
                                    logging.error(f"Full path Firefox call failed: {str(e2)}")
                                    
                                    try:
                                        logging.info("Trying xdg-open...")
                                        subprocess.run(['xdg-open', url], check=True)
                                        logging.info("Success with xdg-open")
                                        return
                                    except Exception as e3:
                                        logging.error(f"xdg-open failed: {str(e3)}")
                                        
                                        logging.info("Trying Python webbrowser...")
                                        webbrowser.get('firefox').open_new_tab(url)
                                        logging.info("Success with Python webbrowser")
                                        return
                            
                        except Exception as e:
                            error_msg = f"Failed to open Firefox. Error: {str(e)}"
                            logging.error(error_msg)
                            QMessageBox.warning(self, "Error", error_msg)
                    return
        
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.last_clicked_url = None

    def _is_title_line(self, cursor):
        """Check if the current block's text starts with Title: (with optional quotes)"""
        line_text = cursor.block().text().strip()
        return bool(re.match(r'^[\'"]?Title:', line_text))

    def _find_vhd_files(self):
        """Find 4-digit .vhd or .txt files on the desktop"""
        vhd_files = []
        
        # Search the user's Desktop directory for files matching 4-digit .vhd or .txt
        desktop_path = os.path.expanduser("~/Desktop")
        if os.path.exists(desktop_path):
            for fname in os.listdir(desktop_path):
                # Match files with 4 digits extension .vhd or .txt
                if re.match(r'^\d{4}\.(vhd|txt)$', fname, re.IGNORECASE):
                    vhd_files.append(os.path.join(desktop_path, fname))
        
        return sorted(vhd_files)

    def _send_to_vhd(self, target_file):
        """Send selected title segment to target file (.vhd or .txt) and remove original"""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.StartOfLine)
        start_pos = cursor.position()
        end_pos = self.document().end().position()
        
        # Search forward for next title line
        while True:
            cursor.movePosition(QTextCursor.Down)
            if cursor.atEnd():
                break
            original_pos = cursor.position()
            cursor.select(QTextCursor.LineUnderCursor)
            line_text = cursor.selectedText().strip()
            cursor.setPosition(original_pos)  # Restore position after check
            if re.match(r'^[\'"]?Title:', line_text, re.IGNORECASE):
                end_pos = original_pos
                break
        
        # Get the content to move
        cursor.setPosition(start_pos)
        cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
        content = cursor.selectedText()

        # Create backup copy before sending
        if re.match(r'^TODAY_ONLY\.(vhd|txt)$', os.path.basename(target_file), re.IGNORECASE):
            import datetime
            backup_dir = "/home/j/Desktop/Finals/NotepadApp_backups/TODAY_ONLY"
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            ext = os.path.splitext(os.path.basename(target_file))[1]
            backup_file = os.path.join(backup_dir, f"TODAY_ONLY_{timestamp}{ext}")
            if os.path.exists(target_file):
                with open(target_file, 'r', encoding='utf-8', errors='replace') as backup_source:
                    backup_content = backup_source.read()
            else:
                backup_content = ""
            with open(backup_file, 'w', encoding='utf-8') as backup_dest:
                backup_dest.write(backup_content)
        elif re.match(r'^\d{4}\.(vhd|txt)$', os.path.basename(target_file), re.IGNORECASE):
            import datetime
            backup_dir = "/home/j/Desktop/Finals/NotepadApp_backups/tomorrows"
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = os.path.basename(target_file)
            ext = os.path.splitext(base_name)[1]
            backup_file = os.path.join(backup_dir, f"{base_name[:-len(ext)]}_{timestamp}{ext}")
            if os.path.exists(target_file):
                with open(target_file, 'r', encoding='utf-8', errors='replace') as backup_source:
                    backup_content = backup_source.read()
            else:
                backup_content = ""
            with open(backup_file, 'w', encoding='utf-8') as backup_dest:
                backup_dest.write(backup_content)

        try:
            # Write to target file
            if os.path.exists(target_file):
                with open(target_file, 'r', encoding='utf-8', errors='replace') as f:
                    existing = f.read()
            else:
                existing = ""
                
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(content + '\n\n' + existing)
            
            # Remove original content if write succeeded
            cursor = self.textCursor()
            cursor.beginEditBlock()  # Start undoable operation
            cursor.setPosition(start_pos)
            cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            cursor.endEditBlock()
            self.setTextCursor(cursor)
            
            self.window().statusBar().showMessage(f"Content moved to {os.path.basename(target_file)}", 5000)
            
        except Exception as e:
            self.window().statusBar().showMessage(f"Failed to move content: {str(e)}", 5000)

    def _move_segment_down(self):
        """Move the current segment (starting with a Title: line) below the next 3 segments by repositioning it, while preserving the editor's position."""
        cursor = self.textCursor()
        if not self._is_title_line(cursor):
            self.window().statusBar().showMessage("Not on a Title segment.", 5000)
            return

        # Save current editor state
        old_cursor_pos = cursor.position()
        old_scroll = self.verticalScrollBar().value()
        
        full_text = self.document().toPlainText()
        pattern = r'^\s*[\'"]?Title:.*$'
        matches = list(re.finditer(pattern, full_text, flags=re.MULTILINE))
        if not matches:
            self.window().statusBar().showMessage("No title segments found.", 5000)
            return

        current_pos = cursor.block().position()
        seg_index = None
        for i, m in enumerate(matches):
            start = m.start()
            end = matches[i+1].start() if i+1 < len(matches) else len(full_text)
            if start <= current_pos < end:
                seg_index = i
                break
        if seg_index is None:
            self.window().statusBar().showMessage("Current segment not found.", 5000)
            return

        # Check if there are at least 3 segments below this one
        if seg_index + 3 >= len(matches):
            self.window().statusBar().showMessage(f"Not enough segments below. Need 3 but found {len(matches) - seg_index - 1}.", 5000)
            return

        # Define boundaries for current segment (S) and the next 3 segments (B, C, D)
        S_start = matches[seg_index].start()
        S_end = matches[seg_index+1].start()
        S_text = full_text[S_start:S_end]

        # The segment to move below (3 segments down)
        target_start = matches[seg_index+3].start()
        target_end = matches[seg_index+4].start() if seg_index + 4 < len(matches) else len(full_text)

        # Text before current segment
        A = full_text[:S_start]
        
        # Text between current segment and target position (the 3 segments to jump over)
        B = full_text[S_end:target_end]
        
        # Text after target position
        C = full_text[target_end:]

        # New text: A + B (3 segments) + S (current segment) + C
        new_text = A + B + S_text + C

        # Update document
        self.setPlainText(new_text)
        
        # Use QTimer to restore positions after content is rendered
        def restore_positions():
            # Restore scroll position first
            self.verticalScrollBar().setValue(old_scroll)
            
            # Move cursor to the NEXT segment's title (segment that's now at the previous position)
            new_cursor = self.textCursor()
            
            # Find the Title: line at the position where the current segment used to be
            # (which now contains the next segment that was directly below the moved segment)
            next_title_pos = S_start
            
            # Get the block at that position
            block = self.document().findBlock(next_title_pos)
            if block.isValid():
                # Make sure we're putting the cursor at a Title: line
                text = block.text()
                if not re.match(r'^\s*[\'"]?Title:', text):
                    # Find the first Title: line in or after this block
                    while block.isValid() and not re.match(r'^\s*[\'"]?Title:', block.text()):
                        block = block.next()
                
                if block.isValid():
                    new_cursor.setPosition(block.position())
                    self.setTextCursor(new_cursor)
                    self.ensureCursorVisible()
                else:
                    # If no Title: line found, use old cursor position as fallback
                    new_cursor.setPosition(min(old_cursor_pos, self.document().characterCount() - 1))
                    self.setTextCursor(new_cursor)
            else:
                # Fallback to old cursor position if block can't be found
                new_cursor.setPosition(min(old_cursor_pos, self.document().characterCount() - 1))
                self.setTextCursor(new_cursor)
            
            self.window().statusBar().showMessage("Segment moved down below the 3rd segment.", 5000)
        
        # Schedule the position restoration after a short delay
        QTimer.singleShot(100, restore_positions)

    def _send_to_kny(self):
        """Send selected title segment to kny.txt and remove original after backup"""
        target_file = "/home/j/Desktop/IMPORTANT_NOTEPADS/kny.txt"
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.StartOfLine)
        start_pos = cursor.position()
        end_pos = self.document().end().position()
        
        # Search forward for next title line
        while True:
            cursor.movePosition(QTextCursor.Down)
            if cursor.atEnd():
                break
            original_pos = cursor.position()
            cursor.select(QTextCursor.LineUnderCursor)
            line_text = cursor.selectedText().strip()
            cursor.setPosition(original_pos)  # Restore position after check
            if re.match(r'^[\'\"]?Title:', line_text, re.IGNORECASE):
                end_pos = original_pos
                break
        
        # Get the content to move
        cursor.setPosition(start_pos)
        cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
        content = cursor.selectedText()
        
        # Create backup copy before sending
        backup_dir = "/home/j/Desktop/Finals/NotepadApp_backups/misc_backups"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"kny_{timestamp}.txt")
        if os.path.exists(target_file):
            with open(target_file, 'r', encoding='utf-8', errors='replace') as backup_source:
                backup_content = backup_source.read()
        else:
            backup_content = ""
        with open(backup_file, 'w', encoding='utf-8') as backup_dest:
            backup_dest.write(backup_content)
        
        try:
            # Write to target file by prepending the segment content
            if os.path.exists(target_file):
                with open(target_file, 'r', encoding='utf-8', errors='replace') as f:
                    existing = f.read()
            else:
                existing = ""
                
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(content + '\n\n' + existing)
            
            # Remove original content if write succeeded
            cursor = self.textCursor()
            cursor.beginEditBlock()
            cursor.setPosition(start_pos)
            cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            cursor.endEditBlock()
            self.setTextCursor(cursor)
            self.window().statusBar().showMessage("Content moved to kny.txt", 5000)
        except Exception as e:
            self.window().statusBar().showMessage(f"Failed to move content: {str(e)}", 5000)

    def contextMenuEvent(self, event):
        """
        Handle right-click events to position the cursor at the clicked position
        before showing the context menu.
        """
        # Store the event position for later use
        self._context_menu_pos = event.pos()
        
        # Get the cursor position at the clicked location
        cursor = self.cursorForPosition(event.pos())
        
        # Set the cursor position and ensure it's visible
        self.setTextCursor(cursor)
        self.ensureCursorVisible()
        
        # Use a timer to delay showing the menu (allows cursor to be positioned first)
        QTimer.singleShot(10, self._showDelayedContextMenu)
        
        # Prevent the default context menu from appearing
        event.accept()
        
    def _showDelayedContextMenu(self):
        """Show the context menu after ensuring cursor position is set"""
        # Create a custom menu
        menu = QMenu(self)
        cursor = self.textCursor()  # Get the current cursor after it was positioned
        selected_text = cursor.selectedText()

        # Add Title segment sending functionality at the top if applicable
        if self._is_title_line(cursor):
            file_targets = self._find_vhd_files()
            if file_targets:
                # Add each matching file option directly to the menu
                for target_file in file_targets:
                    action = menu.addAction(f"Send to {os.path.basename(target_file)}")
                    action.triggered.connect(lambda _, f=target_file: self._send_to_vhd(f))
                menu.addSeparator()
            
            # Add Send to TODAY_ONLY.txt option
            sendTodayAct = QAction("Send to TODAY_ONLY.txt", self)
            sendTodayAct.triggered.connect(lambda: self._send_to_vhd("/home/j/Desktop/IMPORTANT_NOTEPADS/TODAY_ONLY.txt"))
            menu.addAction(sendTodayAct)

            # Add Send to owp123 option
            sendOwpAct = QAction("Send to owp123.vhd", self)
            sendOwpAct.triggered.connect(lambda: self._send_to_vhd("/home/j/Desktop/IMPORTANT_NOTEPADS/owp123.vhd"))
            menu.addAction(sendOwpAct)
            menu.addSeparator()

            # Add new option to move the segment down (nest it under the next segment)
            moveDownAct = QAction("Move segment down", self)
            moveDownAct.triggered.connect(self._move_segment_down)
            menu.addAction(moveDownAct)
            menu.addSeparator()

        # Add cut/copy/paste actions below the 'Send to...' option
        cutAct = menu.addAction("Cut")
        cutAct.triggered.connect(self.cut)
        copyAct = menu.addAction("Copy")
        copyAct.triggered.connect(self.copy)
        pasteAct = menu.addAction("Paste")
        pasteAct.triggered.connect(self.paste)
        menu.addSeparator()
        
        # Add toggle special lines action
        toggleAction = QAction("Toggle URLs/Timestamps", self)
        toggleAction.setShortcut("Ctrl+H")
        toggleAction.triggered.connect(self.toggleSpecialLines)
        menu.addAction(toggleAction)
        menu.addSeparator()
        
        # Add web search action if text is selected
        if selected_text:
            searchWebAct = QAction("Search Web && Insert Results", self)
            searchWebAct.triggered.connect(lambda: self.searchWebAndInsert(selected_text))
            menu.addAction(searchWebAct)
            menu.addSeparator()

        # Add a separator before the script actions
        menu.addSeparator()

        # Add Run script actions delegated to ScriptRunner
        try:
            run_timeSaverAct = QAction("Run timeSaver4445", self)
            run_timeSaverAct.triggered.connect(self.window().script_runner.run_timeSaverScript)
            menu.addAction(run_timeSaverAct)

            runTs1Act = QAction("Run ts1", self)
            runTs1Act.triggered.connect(self.window().script_runner.runTs1Script)
            menu.addAction(runTs1Act)

            runTs2Act = QAction("Run ts2", self)
            runTs2Act.triggered.connect(self.window().script_runner.runTs2Script)
            menu.addAction(runTs2Act)

            runTs3Act = QAction("Run ts3", self)
            runTs3Act.triggered.connect(self.window().script_runner.runTs3Script)
            menu.addAction(runTs3Act)

            runTs4Act = QAction("Run ts4", self)
            runTs4Act.triggered.connect(self.window().script_runner.runTs4Script)
            menu.addAction(runTs4Act)

            runIntroAct = QAction("Run intro", self)
            runIntroAct.triggered.connect(self.window().script_runner.runIntroScript)
            menu.addAction(runIntroAct)

        except AttributeError as e:
            logging.error(f"Failed to connect script runner actions: {e}")
        
        if self._is_title_line(cursor):
            menu.addSeparator()
            sendKnyAct = QAction("Send to kny.txt", self)
            sendKnyAct.triggered.connect(self._send_to_kny)
            menu.addAction(sendKnyAct)

        # Show the menu at the stored event position
        menu.exec_(self.mapToGlobal(self._context_menu_pos))
