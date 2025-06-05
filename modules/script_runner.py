#!/usr/bin/env python3

# notepad_app/modules/script_runner.py

import os
import re
import subprocess
import tempfile
import logging
import sys
import requests
import importlib.util
from PyQt5.QtCore import QObject, QTimer, QUrl
from PyQt5.QtWidgets import QMessageBox, QApplication
from PyQt5.QtGui import QTextCursor

from PyQt5.QtWidgets import QMessageBox

# Get the base directory path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, base_dir)  # Add the base directory to Python path

from scripts.c6sortv2 import read_file, parse_input, get_sort_order, sort_blocks

class ScriptRunner:
    def __init__(self, parent_window):
        """Initialize ScriptRunner with a reference to the parent window"""
        self.parent_window = parent_window  # Store reference to parent window
        logging.debug("ScriptRunner initialized with parent window reference")
        self.scripts_dir = os.path.join(base_dir, 'scripts')

        # Cache for imported modules
        self._module_cache = {}

        # Existing scripts
        self.TIME_SAVER_SCRIPT_4445 = os.path.join(self.scripts_dir, 'timeSaver4445.py')
        self.INTRO_SCRIPT = os.path.join(self.scripts_dir, 'intro.py')
        self.TS1_SCRIPT = os.path.join(self.scripts_dir, 'ts1.py')
        self.TS2_SCRIPT = os.path.join(self.scripts_dir, 'ts2.py')
        self.TS3_SCRIPT = os.path.join(self.scripts_dir, 'ts3.py')
        self.TS3334_SCRIPT = os.path.join(self.scripts_dir, 'ts3334.py')
        self.TS4_SCRIPT = os.path.join(self.scripts_dir, 'ts4.py')
        self.CPYIMAGES_SCRIPT = os.path.join(self.scripts_dir, 'cpyimagesv4.py')
        self.C6SORTV2_SCRIPT = os.path.join(self.scripts_dir, 'c6sortv2.py')
        self.QQ_SCRIPT = os.path.join(self.scripts_dir, 'qq.py')
        self.SHRTN_SCRIPT = os.path.join(self.scripts_dir, 'shrtn.py')
        self.SYN_SCRIPT = os.path.join(self.scripts_dir, 'syn.py')
        self.GPS_SCRIPT = os.path.join(self.scripts_dir, 'gps.py')
        self.CONTEXT_SCRIPT = os.path.join(self.scripts_dir, 'context.py')
        self.CMNT_SNTMNT_SCRIPT = os.path.join(self.scripts_dir, 'CmntSntmnt.py')
        self.STB_SCRIPT = os.path.join(self.scripts_dir, 'STB.py')
        self.STBC_SCRIPT = os.path.join(self.scripts_dir, 'STBC.py')
        self.LASTWORDS_SCRIPT = os.path.join(self.scripts_dir, 'lastwords.py')
        self.STBC_MIDDLE_SCRIPT = os.path.join(self.scripts_dir, 'STBC-Middle.py')
        self.LASTWORDS59_SCRIPT = os.path.join(self.scripts_dir, 'lastwords59.py')
        self.DTMS_SCRIPT = os.path.join(self.scripts_dir, 'DTMS.py')
        self.SKEPTICAL_OUTRO_SCRIPT = os.path.join(self.scripts_dir, 'SkepticalOutro.py')

        self.python_executable = sys.executable

        # Pre-import commonly used modules
        self._preload_modules()

    def _preload_modules(self):
        """Pre-import commonly used script modules."""
        common_scripts = [
            self.TIME_SAVER_SCRIPT_4445,
            self.INTRO_SCRIPT,
            self.TS1_SCRIPT,
            self.TS2_SCRIPT,
            self.TS3_SCRIPT,
            self.TS3334_SCRIPT,
            self.TS4_SCRIPT
        ]
        for script in common_scripts:
            self._import_module(script)

    def _import_module(self, script_path):
        """Import a module and cache it."""
        if script_path not in self._module_cache:
            try:
                script_name = os.path.basename(script_path)
                module_name = os.path.splitext(script_name)[0]
                spec = importlib.util.spec_from_file_location(module_name, script_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self._module_cache[script_path] = module
            except Exception as e:
                logging.error(f"Failed to import module {script_path}: {e}")
                return None
        return self._module_cache[script_path]

    def run_timeSaverScript(self):
        editor = self.parent_window.currentEditor()
        if not editor:
            self.parent_window.statusBar().showMessage("No open editor to run timeSaver4445.", 5000)
            logging.warning("Attempted to run timeSaver4445 with no open editor.")
            return
        selected_text = editor.textCursor().selectedText()
        if not selected_text.strip():
            self.parent_window.statusBar().showMessage("No text selected for timeSaver4445.", 5000)
            logging.warning("No text selected for timeSaver4445.")
            return
        self.run_generic_script(
            script=self.TIME_SAVER_SCRIPT_4445,
            markers=("444\n\n444\n", "\n555"),
            pattern=r'^444\s*\n\n444\s*\n([\s\S]*?)\n555$',
            selected_text=selected_text
        )

    def runIntroScript(self):
        """Run the intro script on the selected text, preserving the first line as the header and rewriting the rest to flow naturally from it."""
        editor = self.parent_window.currentEditor()
        if not editor:
            self.parent_window.statusBar().showMessage("No open editor for intro.", 5000)
            logging.warning("Attempted to run intro with no open editor.")
            return
            
        selected_text = editor.textCursor().selectedText()
        if not selected_text.strip():
            self.parent_window.statusBar().showMessage("No text selected for intro.", 5000)
            logging.warning("No text selected for intro.")
            return

        # Split the selected text into header (first line) and content to reword
        lines = selected_text.splitlines()
        if len(lines) < 2:
            self.parent_window.statusBar().showMessage("Please select at least two lines for intro.", 5000)
            logging.warning("Not enough text selected for intro to separate header and content.")
            return

        header = lines[0]
        content_to_reword = "\n".join(lines[1:]).strip()
        if not content_to_reword:
            self.parent_window.statusBar().showMessage("No rewording content found after the header.", 5000)
            logging.warning("No rewording content found in intro selection.")
            return

        try:
            # Get the path to intro.py
            script_path = os.path.join(self.scripts_dir, 'intro.py')
            if not os.path.exists(script_path):
                error_msg = f"intro.py script not found at {script_path}"
                self.parent_window.statusBar().showMessage(error_msg, 5000)
                logging.error(error_msg)
                return
            
            # Construct a prompt that instructs the script to use the provided header as-is and then rewrite the rest to flow naturally
            new_prompt = (f"Use the following header exactly as given:\n{header}\n\n"
                          f"Then rewrite the following content so that it seamlessly flows from the header while maintaining the style and tone:\n{content_to_reword}")

            # Run the script with the new prompt
            logging.debug(f"Running intro script with prompt: {new_prompt[:100]}...")
            result = subprocess.run(
                ['python3', script_path, new_prompt],
                capture_output=True,
                text=True,
                check=False
            )

            # Log both stdout and stderr for debugging
            logging.debug(f"intro script stdout: {result.stdout}")
            if result.stderr:
                logging.debug(f"intro script stderr: {result.stderr}")

            if result.returncode == 0:
                output_text = result.stdout.strip()
                
                # Double-check that the output starts with the header
                if not output_text.startswith(header):
                    logging.warning(f"Model didn't preserve header. Header: '{header}', Output starts with: '{output_text[:len(header)]}'")
                    
                    # Try to fix the output by ensuring the header is preserved
                    if header.lower() in output_text.lower()[:len(header) + 20]:
                        # The header is present but with different casing or spacing
                        output_text = header + output_text[output_text.lower().find(header.lower()) + len(header):].lstrip()
                    else:
                        # Header not found, just prepend it
                        output_text = f"{header} {output_text}"
                
                cursor = editor.textCursor()
                cursor.beginEditBlock()
                cursor.removeSelectedText()
                cursor.insertText(output_text)
                cursor.endEditBlock()
                self.parent_window.statusBar().showMessage("intro script completed successfully.", 5000)
            else:
                error_msg = f"intro script failed: {result.stderr}"
                self.parent_window.statusBar().showMessage(error_msg, 5000)
                logging.error(error_msg)
        except Exception as e:
            error_msg = f"Error running intro script: {str(e)}"
            self.parent_window.statusBar().showMessage(error_msg, 5000)
            logging.error(error_msg, exc_info=True)

    def runOutroScript(self):
        """Run the outro script on the selected text."""
        editor = self.parent_window.currentEditor()
        if not editor:
            self.parent_window.statusBar().showMessage("No open editor for outro.", 5000)
            logging.warning("Attempted to run outro with no open editor.")
            return
            
        cursor = editor.textCursor()
        selected_text = cursor.selectedText()
        auto_select_range = None
        if not selected_text.strip():
            full_text = editor.toPlainText()
            lines = full_text.splitlines()
            current_line = cursor.blockNumber()  # 0-indexed current line
            header_line = None
            import re
            for i in range(current_line, -1, -1):
                if re.match(r'^[\'"]?Title:\s*.+', lines[i]):
                    header_line = i
                    break
            if header_line is not None:
                computed_start_line = header_line + 1
            else:
                computed_start_line = 0
            doc = editor.document()
            auto_select_range = (doc.findBlockByNumber(computed_start_line).position(), cursor.position())
            selected_text = "\n".join(lines[computed_start_line: current_line+1])
            if not selected_text.strip():
                self.parent_window.statusBar().showMessage("No text found for outro segment.", 5000)
                logging.warning("No text found for outro segment after header search.")
                return

        try:
            # Get the path to outro.py
            script_path = os.path.join(self.scripts_dir, 'outro.py')
            
            # Run the script with the selected text
            result = subprocess.run(
                ['python3', script_path, selected_text],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                if auto_select_range:
                    new_cursor = editor.textCursor()
                    new_cursor.setPosition(auto_select_range[0])
                    new_cursor.setPosition(auto_select_range[1], new_cursor.KeepAnchor)
                    new_cursor.beginEditBlock()
                    new_cursor.removeSelectedText()
                    new_cursor.insertText(result.stdout)
                    new_cursor.endEditBlock()
                else:
                    cursor.beginEditBlock()
                    cursor.removeSelectedText()
                    cursor.insertText(result.stdout)
                    cursor.endEditBlock()
                self.parent_window.statusBar().showMessage("outro script completed successfully.", 5000)
            else:
                error_msg = f"outro script failed: {result.stderr}"
                self.parent_window.statusBar().showMessage(error_msg, 5000)
                logging.error(error_msg)
                
        except Exception as e:
            error_msg = f"Error running outro script: {str(e)}"
            self.parent_window.statusBar().showMessage(error_msg, 5000)
            logging.error(error_msg)

    def runTs1Script(self):
        editor = self.parent_window.currentEditor()
        if not editor:
            self.parent_window.statusBar().showMessage("No open editor for ts1.", 5000)
            logging.warning("Attempted to run ts1 with no open editor.")
            return
        selected_text = editor.textCursor().selectedText()
        if not selected_text.strip():
            self.parent_window.statusBar().showMessage("No text selected for ts1.", 5000)
            logging.warning("No text selected for ts1.")
            return
        self.run_generic_script(
            script=self.TS1_SCRIPT,
            markers=("111\n", "\n111"),
            pattern=r'^111\s*\n([\s\S]*?)\n111$',
            selected_text=selected_text
        )

    def runTs2Script(self):
        editor = self.parent_window.currentEditor()
        if not editor:
            self.parent_window.statusBar().showMessage("No open editor for ts2.", 5000)
            logging.warning("Attempted to run ts2 with no open editor.")
            return
        selected_text = editor.textCursor().selectedText()
        if not selected_text.strip():
            self.parent_window.statusBar().showMessage("No text selected for ts2.", 5000)
            logging.warning("No text selected for ts2.")
            return
        self.run_generic_script(
            script=self.TS2_SCRIPT,
            markers=("222\n", "\n222"),
            pattern=r'^222\s*\n([\s\S]*?)\n222$',
            selected_text=selected_text
        )

    def runTs3Script(self):
        editor = self.parent_window.currentEditor()
        if not editor:
            self.parent_window.statusBar().showMessage("No open editor for ts3.", 5000)
            logging.warning("Attempted to run ts3 with no open editor.")
            return
        selected_text = editor.textCursor().selectedText()
        if not selected_text.strip():
            self.parent_window.statusBar().showMessage("No text selected for ts3.", 5000)
            logging.warning("No text selected for ts3.")
            return
        self.run_generic_script(
            script=self.TS3_SCRIPT,
            markers=("111\n", "\n111"),
            pattern=r'^111\s*\n([\s\S]*?)\n111$',
            selected_text=selected_text
        )

    def runTs3334Script(self):
        editor = self.parent_window.currentEditor()
        if not editor:
            self.parent_window.statusBar().showMessage("No open editor for ts3334.", 5000)
            logging.warning("Attempted to run ts3334 with no open editor.")
            return
        selected_text = editor.textCursor().selectedText()
        if not selected_text.strip():
            self.parent_window.statusBar().showMessage("No text selected for ts3334.", 5000)
            logging.warning("No text selected for ts3334.")
            return
        self.run_generic_script(
            script=self.TS3334_SCRIPT,
            markers=("444\n\n444\n", "\n555"),
            pattern=r'^444\s*\n\n444\s*\n([\s\S]*?)\n555$',
            selected_text=selected_text
        )

    def runQqScript(self):
        """
        Runs the qq script on either:
        1. The current line where the cursor is located (if no text is selected)
        2. The selected text (if text is selected)
        Replaces the line/selection with the API response.
        """
        editor = self.parent_window.currentEditor()
        if not editor:
            QMessageBox.warning(self.parent_window, "No Editor", "No active editor found.")
            logging.warning("QQ script triggered with no open editor.")
            return

        # Get the cursor and check for selection
        cursor = editor.textCursor()
        selected_text = cursor.selectedText()

        if selected_text:
            # Use selected text
            text_to_process = selected_text
            logging.debug(f"Processing selected text: {text_to_process}")
        else:
            # Use current line
            current_line_number = cursor.blockNumber()
            document = editor.document()
            block = document.findBlockByNumber(current_line_number)
            text_to_process = block.text()
            logging.debug(f"Processing current line: {text_to_process}")

        if not text_to_process.strip():
            QMessageBox.warning(self.parent_window, "Empty Text", "Cannot process empty text.")
            logging.warning("QQ script triggered on empty text.")
            return

        try:
            # Get the correct path to qq.py in the scripts folder
            script_path = os.path.join(self.scripts_dir, 'qq.py')
            
            logging.debug(f"Processing text: {text_to_process}")
            logging.debug(f"Using script at: {script_path}")
            
            # Create a temporary file with the text wrapped in 111 markers
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                processed_text = f"111\n{text_to_process}\n111\n"
                temp_file.write(processed_text)
                temp_file_path = temp_file.name
                logging.debug(f"Created temp file at: {temp_file_path} with content: {processed_text}")

            # Run the qq.py script with the temporary file
            result = subprocess.run(
                ['python3', script_path, temp_file_path],
                capture_output=True, 
                text=True,
                check=False
            )

            # Clean up the temporary file
            os.unlink(temp_file_path)

            # Log the complete output for debugging
            logging.debug(f"Script stdout: {result.stdout}")
            logging.debug(f"Script stderr: {result.stderr}")
            logging.debug(f"Return code: {result.returncode}")

            if result.returncode == 0:
                # Get the API response from the output
                output_lines = result.stdout.split('\n')
                api_response = None
                for line in output_lines:
                    if "OpenAI API response:" in line:
                        api_response = line.split("OpenAI API response:", 1)[1].strip()
                        break
                
                if api_response:
                    cursor.beginEditBlock()
                    if selected_text:
                        # Replace selected text
                        cursor.removeSelectedText()
                        cursor.insertText(api_response)
                    else:
                        # Replace current line
                        cursor.movePosition(cursor.StartOfBlock)
                        cursor.movePosition(cursor.EndOfBlock, cursor.KeepAnchor)
                        
                        # If this is not the last line, include the newline character
                        if cursor.blockNumber() < editor.document().blockCount() - 1:
                            cursor.movePosition(cursor.Right, cursor.KeepAnchor)
                        
                        cursor.insertText(api_response)
                    cursor.endEditBlock()
                    
                    logging.info(f"QQ Script successful for text: {text_to_process}")
                else:
                    raise Exception("No API response found in output")
            else:
                error_msg = f"Script failed:\nExit code: {result.returncode}\nError: {result.stderr}\nOutput: {result.stdout}"
                raise Exception(error_msg)

        except Exception as e:
            error_details = str(e)
            QMessageBox.critical(self.parent_window, "Error", f"Failed to process text:\n{error_details}")
            logging.error(f"QQ Script error: {error_details}")
            print(f"Exception details: {error_details}")

    def runShrtnScript(self):
        editor = self.parent_window.currentEditor()
        if not editor:
            self.parent_window.statusBar().showMessage("No open editor for shrtn.", 5000)
            logging.warning("Attempted to run shrtn.py with no open editor.")
            return
        selected_text = editor.textCursor().selectedText()
        if not selected_text.strip():
            self.parent_window.statusBar().showMessage("No text selected for shrtn script.", 5000)
            logging.warning("No text selected for shrtn.py.")
            return
        self.run_generic_script(
            script=self.SHRTN_SCRIPT,
            markers=("111\n", "\n111"),
            pattern=r'^111\s*\n([\s\S]*?)\n111$',
            selected_text=selected_text
        )

    # NEW: runSynScript
    def runSynScript(self):
        """
        Runs the synonym script on the selected word to suggest alternatives based on context.
        """
        editor = self.parent_window.currentEditor()
        if not editor:
            QMessageBox.warning(self.parent_window, "No Editor", "No active editor found.")
            return

        # Get the cursor and check for selection
        cursor = editor.textCursor()
        highlighted_word = cursor.selectedText()

        if not highlighted_word.strip():
            QMessageBox.warning(self.parent_window, "No Selection", "Please highlight a word to get synonym suggestions.")
            return

        # Get the full text of the editor
        full_text = editor.toPlainText()

        try:
            # Create a temporary file with the highlighted word on first line and full text on second line
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp:
                temp.write(f"{highlighted_word}\n{full_text}")
                temp_path = temp.name

            # Run synonym.py with the temporary file
            script_path = os.path.join(self.scripts_dir, 'synonym.py')
            
            if not os.path.exists(script_path):
                self.parent_window.statusBar().showMessage(f"Synonym script not found: {script_path}", 10000)
                return
                
            # Run the script and capture its output
            result = subprocess.run(
                ["python3", script_path, temp_path],
                capture_output=True,
                text=True,
                check=False
            )

            # Clean up the temporary file
            os.unlink(temp_path)

            if result.returncode == 0:
                # Get the API response from the output
                output_lines = result.stdout.split('\n')
                api_response = None
                for line in output_lines:
                    if "OpenAI API response:" in line:
                        api_response = line.split("OpenAI API response:", 1)[1].strip()
                        break
                
                if api_response:
                    # Parse the response to extract synonyms
                    synonyms = []
                    if api_response.startswith("SYNONYMS:"):
                        # Extract the part after "SYNONYMS:"
                        synonyms_text = api_response[len("SYNONYMS:"):].strip()
                        # Split by comma and clean up
                        synonyms = [syn.strip() for syn in synonyms_text.split(',')]
                        # Remove brackets if present
                        synonyms = [syn.strip('[]') for syn in synonyms]
                    else:
                        # Try to extract any comma-separated words from the response
                        synonyms = [syn.strip() for syn in api_response.split(',')]
                    
                    # Limit to 3 synonyms if more are provided
                    synonyms = synonyms[:3]
                    
                    # Create a popup with the synonyms
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setWindowTitle("Synonym Suggestions")
                    
                    # Format the message text
                    synonym_list = "\n".join(f"• {syn}" for syn in synonyms)
                    msg.setText(f"Synonyms for '{highlighted_word}':\n\n{synonym_list}")
                    
                    msg.setMinimumSize(500, 300)
                    msg.setStyleSheet("""
                        QLabel { 
                            font-size: 24pt; 
                            color: #d4d4d4; 
                            font-weight: bold;
                        } 
                        QMessageBox { 
                            background-color: #2d2d2d; 
                        }
                    """)
                    msg.exec_()
                    
                    self.parent_window.statusBar().showMessage("Synonym suggestions displayed", 5000)
                else:
                    raise Exception("No API response found in output")
            else:
                error_msg = f"Synonym script failed:\nExit code: {result.returncode}\nError: {result.stderr}\nOutput: {result.stdout}"
                raise Exception(error_msg)
                
        except Exception as e:
            error_msg = f"Error in Synonym script: {str(e)}"
            self.parent_window.statusBar().showMessage(error_msg, 10000)
            logging.error(error_msg, exc_info=True)
            QMessageBox.warning(self.parent_window, "Synonym Error", error_msg)

    def runTranslateScript(self):
        """
        Translates the selected text or current line using the translate.py script.
        Works like QQ script - processes selected text or current line through a local script.
        """
        editor = self.parent_window.currentEditor()
        if not editor:
            QMessageBox.warning(self.parent_window, "No Editor", "No active editor found.")
            logging.warning("Translate script triggered with no open editor.")
            return

        # Get the cursor and check for selection
        cursor = editor.textCursor()
        selected_text = cursor.selectedText()

        if selected_text:
            # Use selected text
            text_to_translate = selected_text
            logging.debug(f"Translating selected text: {text_to_translate}")
        else:
            # Use current line
            current_line_number = cursor.blockNumber()
            document = editor.document()
            block = document.findBlockByNumber(current_line_number)
            text_to_translate = block.text()
            logging.debug(f"Translating current line: {text_to_translate}")

        if not text_to_translate.strip():
            QMessageBox.warning(self.parent_window, "Empty Text", "Cannot translate empty text.")
            logging.warning("Translate script triggered on empty text.")
            return

        try:
            # Get the correct path to translate.py in the scripts folder
            script_path = os.path.join(self.scripts_dir, 'translate.py')
            
            logging.debug(f"Processing text: {text_to_translate}")
            logging.debug(f"Using script at: {script_path}")
            
            # Create a temporary file with the text wrapped in 111 markers
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                processed_text = f"111\n{text_to_translate}\n111\n"
                temp_file.write(processed_text)
                temp_file_path = temp_file.name
                logging.debug(f"Created temp file at: {temp_file_path} with content: {processed_text}")

            # Run the translate.py script with the temporary file
            result = subprocess.run(
                ['python3', script_path, temp_file_path],
                capture_output=True, 
                text=True,
                check=False
            )

            # Log the complete stdout for debugging
            logging.debug(f"Translate script stdout: {result.stdout}")

            # Clean up the temporary file
            os.unlink(temp_file_path)

            if result.returncode == 0:
                # Get the API response from the output
                output_lines = result.stdout.split('\n')
                api_response = None
                
                # Try to find the explicit "OpenAI API response:" marker
                for line in output_lines:
                    if "OpenAI API response:" in line:
                        api_response = line.split("OpenAI API response:", 1)[1].strip()
                        break
                
                # If we couldn't find the explicit marker, try to extract any meaningful output
                if not api_response:
                    # Filter out log messages and other non-content lines
                    content_lines = []
                    capture_content = False
                    for line in output_lines:
                        line = line.strip()
                        if "[INFO] Script started" in line:
                            capture_content = True
                            continue
                        if capture_content and line and not line.startswith("[") and not line.startswith("ERROR:"):
                            content_lines.append(line)
                    
                    if content_lines:
                        api_response = "\n".join(content_lines)
                
                if api_response:
                    cursor.beginEditBlock()
                    if selected_text:
                        # Replace selected text
                        cursor.removeSelectedText()
                        cursor.insertText(api_response)
                    else:
                        # Replace current line
                        cursor.movePosition(cursor.StartOfBlock)
                        cursor.movePosition(cursor.EndOfBlock, cursor.KeepAnchor)
                        
                        # If this is not the last line, include the newline character
                        if cursor.blockNumber() < editor.document().blockCount() - 1:
                            cursor.movePosition(cursor.Right, cursor.KeepAnchor)
                        
                        cursor.insertText(api_response)
                    cursor.endEditBlock()
                    
                    logging.info(f"Translation successful for text: {text_to_translate}")
                else:
                    raise Exception("No API response found in output")
            else:
                error_msg = f"Script failed:\nExit code: {result.returncode}\nError: {result.stderr}\nOutput: {result.stdout}"
                raise Exception(error_msg)

        except Exception as e:
            error_details = str(e)
            QMessageBox.critical(self.parent_window, "Error", f"Failed to translate text:\n{error_details}")
            logging.error(f"Translation error: {error_details}")
            print(f"Exception details: {error_details}")

    def run_cpyimagesv4_on_tab(self):
        """
        Alias for runCpyImagesScript to maintain consistency
        """
        self.runCpyImagesScript()

    def run_c6sortv2_script_on_tab(self):
        editor = self.parent_window.currentEditor()
        if editor is None:
            logging.error("No editor is currently open.")
            return

        # Get the content of the current tab
        input_content = editor.toPlainText()

        # Define the sort order file path
        sort_order_file = "/home/j/Desktop/ttag_sort_order.vhd"
        if not os.path.exists(sort_order_file):
            logging.error(f"Sort order file not found: {sort_order_file}")
            return

        # Read the sort order
        try:
            sort_order_content = read_file(sort_order_file)
        except Exception as e:
            logging.error(f"Error reading sort order file: {str(e)}")
            return

        try:
            # Parse and sort the blocks
            blocks = parse_input(input_content)
            if not blocks:
                logging.warning("No valid blocks found in the input content.")
                return

            sort_order = get_sort_order(sort_order_content)
            if not sort_order:
                logging.warning("Sort order file is empty or invalid.")
                return

            sorted_blocks = sort_blocks(blocks, sort_order)
            sorted_content = ''.join(sorted_blocks)

            # Save cursor and scroll positions
            cursor = editor.textCursor()
            scrollbar = editor.verticalScrollBar()
            scroll_pos = scrollbar.value()
            cursor_pos = cursor.position()

            # Update the editor content
            editor.setPlainText(sorted_content)
            
            # Use QTimer to restore positions after content is rendered
            def restore_positions():
                # Restore scroll position
                scrollbar.setValue(scroll_pos)
                
                # Restore cursor position if it's within the new content length
                if cursor_pos <= len(sorted_content):
                    cursor.setPosition(cursor_pos)
                    editor.setTextCursor(cursor)
                
                # Update file modification time if needed
                filepath = editor.property("filepath")
                if filepath and os.path.exists(filepath):
                    new_mtime = os.path.getmtime(filepath)
                    editor.setProperty("last_modified_time", new_mtime)

                # Clear any external change warning
                self.parent_window.statusBar().setStyleSheet("")
                self.parent_window.statusBar().showMessage("Sorting completed successfully", 5000)

            # Schedule the position restoration after a short delay
            QTimer.singleShot(100, restore_positions)

        except Exception as e:
            logging.error(f"Error during sorting: {str(e)}")
            self.parent_window.statusBar().showMessage("Sort operation failed", 5000)

    def run_generic_script(self, script, markers, pattern, selected_text):
        """Generic script runner that handles the common pattern of processing selected text."""
        try:
            # Get or import the module
            module = self._import_module(script)
            if not module:
                self.parent_window.statusBar().showMessage("Failed to load script module.", 5000)
                return

            # Process the text in memory instead of using a temporary file
            marked_text = f"{markers[0]}{selected_text}{markers[1]}"
            
            # Parse segments and process them
            segments = module.parse_segments_with_positions(marked_text)
            if not segments:
                self.parent_window.statusBar().showMessage("No valid segments found to process.", 5000)
                return

            # Process each segment
            editor = self.parent_window.currentEditor()
            cursor = editor.textCursor()
            cursor.beginEditBlock()

            # Cache the module's clean_segment signature to avoid repeated checks
            module_name = module.__name__
            if module_name not in self._module_cache:
                self._module_cache[module_name] = {}
            
            if 'accepts_window' not in self._module_cache[module_name]:
                import inspect
                sig = inspect.signature(module.clean_segment)
                self._module_cache[module_name]['accepts_window'] = 'window' in sig.parameters

            accepts_window = self._module_cache[module_name]['accepts_window']

            # Process all segments first
            processed_texts = []
            for segment in segments:
                # Handle timeSaver4445.py's different segment structure
                if module_name == 'timeSaver4445':
                    processed_text = module.clean_segment(segment['context_444'], segment['content_555'], window=self.parent_window)
                else:
                    # Use cached information about window parameter support
                    if accepts_window:
                        processed_text = module.clean_segment(segment['content'], window=self.parent_window)
                    else:
                        processed_text = module.clean_segment(segment['content'])
                
                if processed_text:
                    processed_texts.append(processed_text)

            # Replace the entire selection with the processed text
            if processed_texts:
                # Join all processed texts with double newlines
                final_text = '\n\n'.join(processed_texts)
                # Replace the selection
                cursor.removeSelectedText()
                cursor.insertText(final_text)

            cursor.endEditBlock()
            self.parent_window.statusBar().showMessage("Text processing completed successfully.", 5000)

        except Exception as e:
            error_message = f"Error running script: {str(e)}"
            self.parent_window.statusBar().showMessage(error_message, 5000)
            logging.error(error_message)
            print(f"[ERROR] {error_message}")

    def runCpyImagesScript(self):
        """
        Runs the cpyimagesv4.py script on the current editor content.
        Creates a temporary file with the current content and processes it.
        """
        print("DEBUG: CpyImages button clicked!")  # Simple debug print
        self.parent_window.statusBar().showMessage("DEBUG: CpyImages button clicked!")
        
        editor = self.parent_window.currentEditor()
        if not editor:
            self.parent_window.statusBar().showMessage("Error: No active editor found")
            logging.warning("CpyImages script triggered with no open editor.")
            return

        try:
            self.parent_window.statusBar().showMessage("Starting CpyImages script...")
            
            # Get the current editor content
            content = editor.toPlainText()
            if not content.strip():
                self.parent_window.statusBar().showMessage("Error: Editor is empty")
                return
            
            self.parent_window.statusBar().showMessage("Creating temporary file...")
            # Create a temporary file with the editor content
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.vhd') as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name
                logging.debug(f"Created temp file at: {temp_file_path}")

            # Get the correct path to cpyimagesv4.py
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            script_path = os.path.join(current_dir, 'scripts', 'cpyimagesv4.py')
            
            self.parent_window.statusBar().showMessage(f"Running cpyimagesv4 script on temp file: {temp_file_path}")
            logging.debug(f"Using script at: {script_path}")
            
            # Run the cpyimagesv4.py script with the temporary file
            self.parent_window.statusBar().showMessage("Executing script...")
            result = subprocess.run(
                ['python3', script_path, temp_file_path],
                capture_output=True, 
                text=True,
                check=False
            )

            # Clean up the temporary file
            os.unlink(temp_file_path)

            # Log the complete output for debugging
            logging.debug(f"Script stdout: {result.stdout}")
            logging.debug(f"Script stderr: {result.stderr}")
            logging.debug(f"Return code: {result.returncode}")

            if result.returncode == 0:
                success_msg = "CpyImages completed successfully"
                self.parent_window.statusBar().showMessage(success_msg)
                logging.info(success_msg)
                
                # Show detailed output in console or log
                print("Script Output:")
                print(result.stdout)
            else:
                error_msg = f"Script failed (code {result.returncode})"
                self.parent_window.statusBar().showMessage(error_msg)
                print("Error Output:")
                print(result.stderr)
                print("Standard Output:")
                print(result.stdout)
                raise Exception(error_msg)

        except Exception as e:
            error_details = str(e)
            self.parent_window.statusBar().showMessage(f"Error: {error_details}")
            logging.error(f"CpyImages Script error: {error_details}")
            print(f"Exception details: {error_details}")

    def runTs4Script(self):
        editor = self.parent_window.currentEditor()
        if not editor:
            self.parent_window.statusBar().showMessage("No open editor for ts4.", 5000)
            logging.warning("Attempted to run ts4 with no open editor.")
            return
        selected_text = editor.textCursor().selectedText()
        if not selected_text.strip():
            self.parent_window.statusBar().showMessage("No text selected for ts4.", 5000)
            logging.warning("No text selected for ts4.")
            return
        self.run_generic_script(
            script=self.TS4_SCRIPT,
            markers=("111\n", "\n111"),
            pattern=r'^111\s*\n([\s\S]*?)\n111$',
            selected_text=selected_text
        )

    def runTestModelScript(self):
        """Run the test_model script on the selected text."""
        editor = self.parent_window.currentEditor()
        if not editor:
            self.parent_window.statusBar().showMessage("No open editor for model1.", 5000)
            logging.warning("Attempted to run model1 with no open editor.")
            return
            
        selected_text = editor.textCursor().selectedText()
        if not selected_text.strip():
            self.parent_window.statusBar().showMessage("No text selected for model1.", 5000)
            logging.warning("No text selected for model1.")
            return

        try:
            # Get the path to model1.py
            script_path = os.path.join(self.scripts_dir, 'model1.py')
            
            # Run the script with the selected text
            result = subprocess.run(
                ['python3', script_path, selected_text],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                # Replace selected text with the script output
                cursor = editor.textCursor()
                # Store the current position to navigate back to later
                start_position = cursor.selectionStart()
                
                # Replace the text
                cursor.beginEditBlock()
                cursor.removeSelectedText()
                cursor.insertText(result.stdout)
                cursor.endEditBlock()
                
                # Move cursor to the beginning of the inserted text
                cursor.setPosition(start_position)
                editor.setTextCursor(cursor)
                
                self.parent_window.statusBar().showMessage("test_model script completed successfully.", 5000)
            else:
                error_msg = f"test_model script failed: {result.stderr}"
                self.parent_window.statusBar().showMessage(error_msg, 5000)
                logging.error(error_msg)
                
        except Exception as e:
            error_msg = f"Error running test_model script: {str(e)}"
            self.parent_window.statusBar().showMessage(error_msg, 5000)
            logging.error(error_msg)

    def runTestModelExperimentalScript(self):
        """Run the test_model_experimental script on the selected text."""
        editor = self.parent_window.currentEditor()
        if not editor:
            self.parent_window.statusBar().showMessage("No open editor for model2.", 5000)
            logging.warning("Attempted to run model2 with no open editor.")
            return
            
        selected_text = editor.textCursor().selectedText()
        if not selected_text.strip():
            self.parent_window.statusBar().showMessage("No text selected for model2.", 5000)
            logging.warning("No text selected for model2.")
            return

        try:
            # Get the path to model2.py
            script_path = os.path.join(self.scripts_dir, 'model2.py')
            
            # Run the script with the selected text
            result = subprocess.run(
                ['python3', script_path, selected_text],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                # Replace selected text with the script output
                cursor = editor.textCursor()
                # Store the current position to navigate back to later
                start_position = cursor.selectionStart()
                
                # Replace the text
                cursor.beginEditBlock()
                cursor.removeSelectedText()
                cursor.insertText(result.stdout)
                cursor.endEditBlock()
                
                # Move cursor to the beginning of the inserted text
                cursor.setPosition(start_position)
                editor.setTextCursor(cursor)
                
                self.parent_window.statusBar().showMessage("test_model_experimental script completed successfully.", 5000)
            else:
                error_msg = f"test_model_experimental script failed: {result.stderr}"
                self.parent_window.statusBar().showMessage(error_msg, 5000)
                logging.error(error_msg)
                
        except Exception as e:
            error_msg = f"Error running test_model_experimental script: {str(e)}"
            self.parent_window.statusBar().showMessage(error_msg, 5000)
            logging.error(error_msg)

    def runTestModel3Script(self):
        """Run the test_model_3 script on the selected text."""
        editor = self.parent_window.currentEditor()
        if not editor:
            self.parent_window.statusBar().showMessage("No open editor for model3.", 5000)
            logging.warning("Attempted to run model3 with no open editor.")
            return
            
        selected_text = editor.textCursor().selectedText()
        if not selected_text.strip():
            self.parent_window.statusBar().showMessage("No text selected for model3.", 5000)
            logging.warning("No text selected for model3.")
            return

        try:
            # Get the path to model3.py
            script_path = os.path.join(self.scripts_dir, 'model3.py')
            
            # Run the script with the selected text
            result = subprocess.run(
                ['python3', script_path, selected_text],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                # Replace selected text with the script output
                cursor = editor.textCursor()
                # Store the current position to navigate back to later
                start_position = cursor.selectionStart()
                
                # Replace the text
                cursor.beginEditBlock()
                cursor.removeSelectedText()
                cursor.insertText(result.stdout)
                cursor.endEditBlock()
                
                # Move cursor to the beginning of the inserted text
                cursor.setPosition(start_position)
                editor.setTextCursor(cursor)
                
                self.parent_window.statusBar().showMessage("test_model_3 script completed successfully.", 5000)
            else:
                error_msg = f"test_model_3 script failed: {result.stderr}"
                self.parent_window.statusBar().showMessage(error_msg, 5000)
                logging.error(error_msg)
                
        except Exception as e:
            error_msg = f"Error running test_model_3 script: {str(e)}"
            self.parent_window.statusBar().showMessage(error_msg, 5000)
            logging.error(error_msg)

    def runTestModel4Script(self):
        """Run the test_model_4 script on the selected text."""
        editor = self.parent_window.currentEditor()
        if not editor:
            self.parent_window.statusBar().showMessage("No open editor for model4.", 5000)
            logging.warning("No open editor for model4.")
            return

        selected_text = editor.textCursor().selectedText()
        if not selected_text.strip():
            self.parent_window.statusBar().showMessage("No text selected for model4.", 5000)
            logging.warning("No text selected for model4.")
            return

        script_path = os.path.join(self.scripts_dir, 'model4.py')

        try:
            result = subprocess.run(['python3', script_path, selected_text], capture_output=True, text=True, check=True)

            cursor = editor.textCursor()
            # Store the current position to navigate back to later
            start_position = cursor.selectionStart()
            
            # Replace the text
            cursor.beginEditBlock()
            cursor.removeSelectedText()
            cursor.insertText(result.stdout)
            cursor.endEditBlock()
            
            # Move cursor to the beginning of the inserted text
            cursor.setPosition(start_position)
            editor.setTextCursor(cursor)

            self.parent_window.statusBar().showMessage("model4 script completed successfully.", 5000)
        except Exception as e:
            error_msg = f"model4 script failed: {str(e)}"
            self.parent_window.statusBar().showMessage(error_msg, 5000)
            logging.error(error_msg)

    def runTestModelJScript(self):
        """Run the modelj script on the selected text."""
        editor = self.parent_window.currentEditor()
        if not editor:
            self.parent_window.statusBar().showMessage("No open editor for modelj.", 5000)
            logging.warning("No open editor for modelj.")
            return

        selected_text = editor.textCursor().selectedText()
        logging.debug(f"runTestModelJScript: selected text length = {len(selected_text)}")
        if not selected_text.strip():
            self.parent_window.statusBar().showMessage("No text selected for modelj.", 5000)
            logging.debug("runTestModelJScript: No text selected.")
            return

        script_path = os.path.join(self.scripts_dir, 'modelj.py')

        try:
            result = subprocess.run(['python3', script_path, selected_text], capture_output=True, text=True, check=True)

            cursor = editor.textCursor()
            cursor.beginEditBlock()
            cursor.removeSelectedText()
            cursor.insertText(result.stdout)
            cursor.endEditBlock()

            self.parent_window.statusBar().showMessage("modelj script completed successfully.", 5000)
        except Exception as e:
            error_msg = f"modelj script failed: {str(e)}"
            self.parent_window.statusBar().showMessage(error_msg, 5000)
            logging.error(error_msg)

    def runModel2iScript(self):
        """Run the model2i script on the selected text."""
        editor = self.parent_window.currentEditor()
        if not editor:
            self.parent_window.statusBar().showMessage("No open editor for model2i.", 5000)
            logging.warning("No open editor for model2i.")
            return

        selected_text = editor.textCursor().selectedText()
        logging.debug(f"runModel2iScript: selected text length = {len(selected_text)}")
        if not selected_text.strip():
            self.parent_window.statusBar().showMessage("No text selected for model2i.", 5000)
            logging.debug("runModel2iScript: No text selected.")
            return

        script_path = os.path.join(self.scripts_dir, 'model2i.py')

        try:
            result = subprocess.run(['python3', script_path, selected_text], capture_output=True, text=True, check=True)

            cursor = editor.textCursor()
            cursor.beginEditBlock()
            cursor.removeSelectedText()
            cursor.insertText(result.stdout)
            cursor.endEditBlock()

            self.parent_window.statusBar().showMessage("model2i script completed successfully.", 5000)
        except Exception as e:
            error_msg = f"model2i script failed: {str(e)}"
            self.parent_window.statusBar().showMessage(error_msg, 5000)
            logging.error(error_msg)

    def runGpsScript(self):
        """
        Runs the GPS script on either the selected text or the current line where the cursor is.
        Gets decimal GPS coordinates from the text.
        """
        editor = self.parent_window.currentEditor()
        if not editor:
            self.parent_window.statusBar().showMessage("No open editor for GPS.", 5000)
            logging.warning("GPS script triggered with no open editor.")
            return

        # Get the cursor and check for selection
        cursor = editor.textCursor()
        selected_text = cursor.selectedText()

        # If no text is selected, get the text of the current line
        if not selected_text.strip():
            block = editor.document().findBlock(cursor.position())
            selected_text = block.text().strip()
            logging.debug(f"No selection, using current line: {selected_text}")
            
            # If the current line is also empty, show warning
            if not selected_text:
                QMessageBox.warning(self.parent_window, "No Text", "The current line is empty. Please select text or position cursor on a line with content.")
                logging.warning("GPS script triggered with no text on current line.")
                return

        try:
            # Get the correct path to gps.py in the scripts folder
            script_path = os.path.join(self.scripts_dir, 'gps.py')
            
            logging.debug(f"Processing text: {selected_text}")
            logging.debug(f"Using script at: {script_path}")
            
            # Create a temporary file with the text wrapped in 111 markers
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                processed_text = f"111\n{selected_text}\n111\n"
                temp_file.write(processed_text)
                temp_file_path = temp_file.name
                logging.debug(f"Created temp file at: {temp_file_path} with content: {processed_text}")

            # Run the gps.py script with the temporary file
            result = subprocess.run(
                ['python3', script_path, temp_file_path],
                capture_output=True, 
                text=True,
                check=False
            )

            # Clean up the temporary file
            os.unlink(temp_file_path)

            if result.returncode == 0:
                # Get the API response from the output
                output_lines = result.stdout.split('\n')
                api_response = None
                for line in output_lines:
                    if "OpenAI API response:" in line:
                        api_response = line.split("OpenAI API response:", 1)[1].strip()
                        break
                
                if api_response:
                    # If there was a selection, replace it
                    # Otherwise, replace the entire line
                    cursor.beginEditBlock()
                    if cursor.hasSelection():
                        cursor.removeSelectedText()
                        cursor.insertText(api_response)
                    else:
                        # Select the current line and replace it
                        cursor.movePosition(cursor.StartOfBlock)
                        cursor.movePosition(cursor.EndOfBlock, cursor.KeepAnchor)
                        cursor.removeSelectedText()
                        cursor.insertText(api_response)
                    cursor.endEditBlock()
                    
                    logging.info(f"GPS Script successful for text: {selected_text}")
                else:
                    raise Exception("No API response found in output")
            else:
                error_msg = f"Script failed:\nExit code: {result.returncode}\nError: {result.stderr}\nOutput: {result.stdout}"
                raise Exception(error_msg)

        except Exception as e:
            error_details = str(e)
            QMessageBox.critical(self.parent_window, "Error", f"Failed to process text:\n{error_details}")
            logging.error(f"GPS Script error: {error_details}")

    def runContextScript(self):
        """Run the context script on the selected text."""
        editor = self.parent_window.currentEditor()
        if not editor:
            QMessageBox.warning(self.parent_window, "No Editor", "No active editor found.")
            logging.warning("Context script triggered with no open editor.")
            return

        # Get the cursor and check for selection
        cursor = editor.textCursor()
        selected_text = cursor.selectedText()

        if not selected_text.strip():
            QMessageBox.warning(self.parent_window, "No Selection", "Please select some text to get context.")
            logging.warning("Context script triggered with no text selection.")
            return

        try:
            # Get the correct path to context.py in the scripts folder
            script_path = os.path.join(self.scripts_dir, 'context.py')
            
            logging.debug(f"Processing text: {selected_text}")
            logging.debug(f"Using script at: {script_path}")
            
            # Create a temporary file with just the selected text
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                temp_file.write(selected_text)
                temp_file_path = temp_file.name
                logging.debug(f"Created temp file at: {temp_file_path} with content: {selected_text}")

            # Run the context.py script with the temporary file
            result = subprocess.run(
                ['python3', script_path, temp_file_path],
                capture_output=True, 
                text=True,
                check=False
            )

            # Clean up the temporary file
            os.unlink(temp_file_path)

            if result.returncode == 0:
                # Get the API response from the output
                output_lines = result.stdout.split('\n')
                api_response = None
                for line in output_lines:
                    if "OpenAI API response:" in line:
                        api_response = line.split("OpenAI API response:", 1)[1].strip()
                        break
                
                if api_response:
                    cursor.beginEditBlock()
                    cursor.removeSelectedText()
                    cursor.insertText(api_response)
                    cursor.endEditBlock()
                    
                    logging.info(f"Context Script successful for text: {selected_text}")
                else:
                    raise Exception("No API response found in output")
            else:
                error_msg = f"Script failed:\nExit code: {result.returncode}\nError: {result.stderr}\nOutput: {result.stdout}"
                raise Exception(error_msg)

        except Exception as e:
            error_details = str(e)
            QMessageBox.critical(self.parent_window, "Error", f"Failed to process text:\n{error_details}")
            logging.error(f"Context Script error: {error_details}")
            print(f"Exception details: {error_details}")

    def runCmntSntmntScript(self):
        """Run the CmntSntmnt script on the selected text to analyze sentiment of comments."""
        editor = self.parent_window.currentEditor()
        if not editor:
            self.parent_window.statusBar().showMessage("No open editor for comment sentiment analysis.", 5000)
            logging.warning("Attempted to run CmntSntmnt with no open editor.")
            return
            
        selected_text = editor.textCursor().selectedText()
        if not selected_text.strip():
            self.parent_window.statusBar().showMessage("No text selected for comment sentiment analysis.", 5000)
            logging.warning("No text selected for CmntSntmnt.")
            return

        try:
            # Get the path to CmntSntmnt.py
            script_path = os.path.join(self.scripts_dir, 'CmntSntmnt.py')
            
            # Run the script with the selected text
            result = subprocess.run(
                ['python3', script_path, selected_text],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                # Replace selected text with the script output
                cursor = editor.textCursor()
                cursor.beginEditBlock()
                cursor.removeSelectedText()
                cursor.insertText(result.stdout)
                cursor.endEditBlock()
                self.parent_window.statusBar().showMessage("Comment sentiment analysis completed successfully.", 5000)
            else:
                error_msg = f"Comment sentiment analysis failed: {result.stderr}"
                self.parent_window.statusBar().showMessage(error_msg, 5000)
                logging.error(error_msg)
                
        except Exception as e:
            error_msg = f"Error running comment sentiment analysis: {str(e)}"
            self.parent_window.statusBar().showMessage(error_msg, 5000)
            logging.error(error_msg)

    def runSTBScript(self):
        """Run the STB script on the current editor's text."""
        logging.debug("Starting runSTBScript method")
        
        try:
            editor = self.parent_window.currentEditor()
            if not editor:
                logging.warning("No open editor for STB.")
                self.parent_window.statusBar().showMessage("No open editor for STB.", 5000)
                return
            
            selected_text = editor.textCursor().selectedText()
            if not selected_text.strip():
                # If no text is selected, use the entire document
                selected_text = editor.toPlainText()
            
            if not selected_text.strip():
                logging.warning("No text available for STB.")
                self.parent_window.statusBar().showMessage("No text available for STB.", 5000)
                return

            logging.debug(f"Running STB script with text length: {len(selected_text)}")

            # Run the STB script using subprocess with detailed error capturing
            result = subprocess.run(
                ['python3', self.STB_SCRIPT, selected_text],
                capture_output=True,
                text=True,
                check=False
            )

            # Log both stdout and stderr
            logging.debug(f"STB script stdout: {result.stdout}")
            logging.debug(f"STB script stderr: {result.stderr}")

            if result.returncode == 0:
                cursor = editor.textCursor()
                cursor.beginEditBlock()
                
                # Replace the selected text or entire document with the script output
                if editor.textCursor().hasSelection():
                    cursor.removeSelectedText()
                    cursor.insertText(result.stdout)
                else:
                    cursor.select(QTextCursor.Document)
                    cursor.removeSelectedText()
                    cursor.insertText(result.stdout)
                
                cursor.endEditBlock()
                self.parent_window.statusBar().showMessage("STB script completed successfully.", 5000)
            else:
                error_msg = f"STB script failed (return code {result.returncode}): {result.stderr}"
                self.parent_window.statusBar().showMessage(error_msg, 5000)
                logging.error(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error in runSTBScript: {str(e)}"
            self.parent_window.statusBar().showMessage(error_msg, 5000)
            logging.error(error_msg, exc_info=True)  # Log full traceback

    def runSTBCScript(self):
        """Run the STBC script on the current editor's text, using surrounding context for better understanding."""
        logging.debug("Starting runSTBCScript method")
        
        try:
            editor = self.parent_window.currentEditor()
            if not editor:
                logging.warning("No open editor for STBC.")
                self.parent_window.statusBar().showMessage("No open editor for STBC.", 5000)
                return
            
            selected_text = editor.textCursor().selectedText()
            if not selected_text.strip():
                # If no text is selected, use the entire document
                selected_text = editor.toPlainText()
            
            if not selected_text.strip():
                logging.warning("No text available for STBC.")
                self.parent_window.statusBar().showMessage("No text available for STBC.", 5000)
                return

            logging.debug(f"Running STBC script with text length: {len(selected_text)}")

            # Run the STBC script using subprocess with detailed error capturing
            result = subprocess.run(
                ['python3', self.STBC_SCRIPT, selected_text],
                capture_output=True,
                text=True,
                check=False
            )

            # Log both stdout and stderr
            logging.debug(f"STBC script stdout: {result.stdout}")
            logging.debug(f"STBC script stderr: {result.stderr}")

            if result.returncode == 0:
                cursor = editor.textCursor()
                cursor.beginEditBlock()
                
                # Replace the selected text or entire document with the script output
                if editor.textCursor().hasSelection():
                    cursor.removeSelectedText()
                    cursor.insertText(result.stdout)
                else:
                    cursor.select(cursor.Document)
                    cursor.removeSelectedText()
                    cursor.insertText(result.stdout)
                
                cursor.endEditBlock()
                self.parent_window.statusBar().showMessage("STBC script completed successfully.", 5000)
            else:
                error_msg = f"STBC script failed: {result.stderr}"
                self.parent_window.statusBar().showMessage(error_msg, 5000)
                logging.error(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error in runSTBCScript: {str(e)}"
            self.parent_window.statusBar().showMessage(error_msg, 5000)
            logging.error(error_msg, exc_info=True)

    def runSTBCMiddleScript(self):
        """Run the STBC-Middle script on the current editor's text, using surrounding context for a balanced middle perspective."""
        logging.debug("Starting runSTBCMiddleScript method")
        
        try:
            editor = self.parent_window.currentEditor()
            if not editor:
                logging.warning("No open editor for STBC-Middle.")
                self.parent_window.statusBar().showMessage("No open editor for STBC-Middle.", 5000)
                return
            
            # Get the current cursor and document
            cursor = editor.textCursor()
            document = editor.document()
            
            # Store selection information
            has_selection = cursor.hasSelection()
            selected_text = cursor.selectedText()
            
            if not selected_text.strip():
                # If no text is selected, use the entire document
                selected_text = editor.toPlainText()
                
                if not selected_text.strip():
                    logging.warning("No text available for STBC-Middle.")
                    self.parent_window.statusBar().showMessage("No text available for STBC-Middle.", 5000)
                    return
                    
                # Use the entire document
                text_to_process = selected_text
            else:
                # Store the selection range
                selection_start = cursor.selectionStart()
                selection_end = cursor.selectionEnd()
                
                # Get full text for context
                full_text = editor.toPlainText()
                
                # Replace line breaks in selected text for proper processing
                # QTextCursor.selectedText() uses Unicode U+2029 for line breaks
                # We need to normalize this for proper processing
                selected_text_normalized = selected_text.replace(u'\u2029', '\n')
                logging.debug(f"Normalized selected text (with proper newlines): '{selected_text_normalized}'")
                
                # Find paragraph boundaries
                # First, find a reasonable paragraph start by looking for 2+ consecutive newlines before selection
                paragraph_start = selection_start
                consecutive_newlines = 0
                for i in range(selection_start - 1, max(0, selection_start - 500), -1):
                    if full_text[i] == '\n':
                        consecutive_newlines += 1
                    else:
                        consecutive_newlines = 0
                    
                    if consecutive_newlines >= 2:
                        paragraph_start = i + 1  # Position after the double newline
                        break
                
                # If we didn't find a paragraph start with double newlines, 
                # look for at least one newline or just start from the beginning
                if paragraph_start == selection_start and selection_start > 0:
                    for i in range(selection_start - 1, max(0, selection_start - 500), -1):
                        if full_text[i] == '\n':
                            paragraph_start = i + 1
                            break
                
                # Then, find a reasonable paragraph end by looking for 2+ consecutive newlines after selection
                paragraph_end = selection_end
                consecutive_newlines = 0
                for i in range(selection_end, min(len(full_text), selection_end + 500)):
                    if full_text[i] == '\n':
                        consecutive_newlines += 1
                    else:
                        consecutive_newlines = 0
                    
                    if consecutive_newlines >= 2:
                        paragraph_end = i - 1  # Position before the double newline
                        break
                
                # If we didn't find a paragraph end with double newlines,
                # look for at least one newline or just go to the end
                if paragraph_end == selection_end and selection_end < len(full_text):
                    for i in range(selection_end, min(len(full_text), selection_end + 500)):
                        if full_text[i] == '\n':
                            paragraph_end = i
                            break
                
                # Extract the full paragraph that contains the selection, preserving internal newlines
                paragraph_text = full_text[paragraph_start:paragraph_end]
                
                # Combine multi-line text into a continuous paragraph for better processing
                # Replace multiple consecutive newlines with spaces, but preserve single newlines
                processed_paragraph = paragraph_text
                
                # Calculate the selection's position within the processed paragraph
                relative_selection_start = selection_start - paragraph_start
                relative_selection_end = selection_end - paragraph_start
                
                logging.debug(f"Original paragraph_text: '{paragraph_text}'")
                logging.debug(f"Processed paragraph: '{processed_paragraph}'")
                logging.debug(f"Selection positions: start={relative_selection_start}, end={relative_selection_end}")
                
                # Create a temporary file with two lines:
                # Line 1: The full paragraph text (for context)
                # Line 2: The start and end positions of the selected text within the paragraph
                with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                    temp_file.write(f"{processed_paragraph}\n{relative_selection_start},{relative_selection_end}")
                    temp_file_path = temp_file.name
                    logging.debug(f"Created temp file at: {temp_file_path}")
                
                # This is now the path to the temporary file instead of the text itself
                text_to_process = temp_file_path
                
                logging.debug(f"Selected text: '{selected_text_normalized}'")
                logging.debug(f"Paragraph context: '{processed_paragraph}'")
                logging.debug(f"Selection positions within paragraph: {relative_selection_start},{relative_selection_end}")
            
            logging.debug(f"Running STBC-Middle script")

            # Run the STBC-Middle script with the temp file path that contains both context and selection info
            result = subprocess.run(
                ['python3', self.STBC_MIDDLE_SCRIPT, text_to_process],
                capture_output=True,
                text=True,
                check=False
            )
            
            # Clean up the temporary file if it exists
            if has_selection and os.path.exists(text_to_process):
                os.unlink(text_to_process)

            # Log both stdout and stderr
            logging.debug(f"STBC-Middle script stdout: {result.stdout}")
            logging.debug(f"STBC-Middle script stderr: {result.stderr}")

            if result.returncode == 0:
                # The STBC-Middle script returns just the improved text for the selected portion
                modified_text = result.stdout.strip()
                logging.debug(f"Modified text received: '{modified_text}'")
                
                # Begin editing
                cursor.beginEditBlock()
                
                if has_selection:
                    # Set cursor to start of selection
                    cursor.setPosition(selection_start)
                    # Set anchor to end of selection
                    cursor.setPosition(selection_end, QTextCursor.KeepAnchor)
                    # Remove the selected text
                    cursor.removeSelectedText()
                    # Insert only the modified text
                    cursor.insertText(modified_text)
                else:
                    # If no selection, replace entire document
                    cursor.select(QTextCursor.Document)
                    cursor.removeSelectedText()
                    cursor.insertText(modified_text)
                
                cursor.endEditBlock()
                self.parent_window.statusBar().showMessage("STBC-Middle script completed successfully.", 5000)
            else:
                error_msg = f"STBC-Middle script failed: {result.stderr}"
                self.parent_window.statusBar().showMessage(error_msg, 5000)
                logging.error(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error in runSTBCMiddleScript: {str(e)}"
            self.parent_window.statusBar().showMessage(error_msg, 5000)
            logging.error(error_msg, exc_info=True)

    def runGrammarScript(self):
        """Run the grammar script on the selected text to fix spelling and grammar issues."""
        editor = self.parent_window.currentEditor()
        if not editor:
            QMessageBox.warning(self.parent_window, "No Editor", "No active editor found.")
            logging.warning("Grammar script triggered with no open editor.")
            return

        # Get the cursor and check for selection
        cursor = editor.textCursor()
        selected_text = cursor.selectedText()

        if not selected_text.strip():
            QMessageBox.warning(self.parent_window, "No Selection", "Please select text to fix grammar and spelling.")
            logging.warning("Grammar script triggered with no text selection.")
            return

        try:
            # Get the correct path to grammar.py in the scripts folder
            script_path = os.path.join(self.scripts_dir, 'grammar.py')
            
            logging.debug(f"Processing text for grammar: {selected_text}")
            logging.debug(f"Using script at: {script_path}")
            
            # Create a temporary file with just the selected text
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                temp_file.write(selected_text)
                temp_file_path = temp_file.name
                logging.debug(f"Created temp file at: {temp_file_path} with content: {selected_text}")

            # Run the grammar.py script with the temporary file
            result = subprocess.run(
                ['python3', script_path, temp_file_path],
                capture_output=True, 
                text=True,
                check=False
            )

            # Clean up the temporary file
            os.unlink(temp_file_path)

            if result.returncode == 0:
                # Get the API response from the output
                output_lines = result.stdout.split('\n')
                api_response = None
                for line in output_lines:
                    if "OpenAI API response:" in line:
                        api_response = line.split("OpenAI API response:", 1)[1].strip()
                        break
                
                if api_response:
                    cursor.beginEditBlock()
                    cursor.removeSelectedText()
                    cursor.insertText(api_response)
                    cursor.endEditBlock()
                    
                    self.parent_window.statusBar().showMessage("Grammar and spelling corrected", 5000)
                    logging.info(f"Grammar Script successful for text: {selected_text}")
                else:
                    raise Exception("No API response found in output")
            else:
                error_msg = f"Grammar script failed:\nExit code: {result.returncode}\nError: {result.stderr}\nOutput: {result.stdout}"
                raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Error in Grammar script: {str(e)}"
            self.parent_window.statusBar().showMessage(error_msg, 10000)
            logging.error(error_msg, exc_info=True)
            QMessageBox.warning(self.parent_window, "Grammar Error", error_msg)

    def runPronounceScript(self):
        """Run the pronounce script on the selected word to get its pronunciation."""
        editor = self.parent_window.currentEditor()
        if not editor:
            QMessageBox.warning(self.parent_window, "No Editor", "No active editor found.")
            logging.warning("Pronounce script triggered with no open editor.")
            return

        # Get the cursor and check for selection
        cursor = editor.textCursor()
        selected_text = cursor.selectedText()

        if not selected_text.strip():
            QMessageBox.warning(self.parent_window, "No Selection", "Please select a word to get its pronunciation.")
            logging.warning("Pronounce script triggered with no text selection.")
            return

        try:
            # Get the correct path to pronounce.py in the scripts folder
            script_path = os.path.join(self.scripts_dir, 'pronounce.py')
            
            logging.debug(f"Processing word for pronunciation: {selected_text}")
            logging.debug(f"Using script at: {script_path}")
            
            # Create a temporary file with just the selected word
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                temp_file.write(selected_text)
                temp_file_path = temp_file.name
                logging.debug(f"Created temp file at: {temp_file_path} with content: {selected_text}")

            # Run the pronounce.py script with the temporary file
            result = subprocess.run(
                ['python3', script_path, temp_file_path],
                capture_output=True, 
                text=True,
                check=False
            )

            # Clean up the temporary file
            os.unlink(temp_file_path)

            if result.returncode == 0:
                # Get the API response from the output
                output_lines = result.stdout.split('\n')
                api_response = None
                for line in output_lines:
                    if "OpenAI API response:" in line:
                        api_response = line.split("OpenAI API response:", 1)[1].strip()
                        break
                
                if api_response:
                    # Insert the pronunciation right after the selected word
                    cursor.beginEditBlock()
                    cursor.setPosition(cursor.selectionEnd())  # Move to the end of selection
                    cursor.insertText(api_response)  # Insert pronunciation
                    cursor.endEditBlock()
                    
                    self.parent_window.statusBar().showMessage("Pronunciation added", 5000)
                    logging.info(f"Pronunciation Script successful for word: {selected_text}")
                else:
                    raise Exception("No API response found in output")
            else:
                error_msg = f"Pronounce script failed:\nExit code: {result.returncode}\nError: {result.stderr}\nOutput: {result.stdout}"
                raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Error in Pronounce script: {str(e)}"
            self.parent_window.statusBar().showMessage(error_msg, 10000)
            logging.error(error_msg, exc_info=True)
            QMessageBox.warning(self.parent_window, "Pronunciation Error", error_msg)

    def runLastWordsScript(self):
        """Run the LastWords script to complete the last sentence with 1-4 appropriate words."""
        logging.critical("Starting runLastWordsScript method in ScriptRunner!")
        print("DEBUG: Starting runLastWordsScript method in ScriptRunner!")
        
        try:
            editor = self.parent_window.currentEditor()
            if not editor:
                logging.critical("No open editor for LastWords.")
                self.parent_window.statusBar().showMessage("No open editor for LastWords.", 5000)
                return
            
            selected_text = editor.textCursor().selectedText()
            logging.critical(f"Selected text length: {len(selected_text)}")
            print(f"DEBUG: Selected text length: {len(selected_text)}")
            
            if not selected_text.strip():
                # If no text is selected, use the current paragraph or line
                cursor = editor.textCursor()
                cursor.select(cursor.BlockUnderCursor)
                selected_text = cursor.selectedText()
                logging.critical(f"Block text length: {len(selected_text)}")
                print(f"DEBUG: Block text length: {len(selected_text)}")
                
                # If still empty, try to get surrounding context
                if not selected_text.strip():
                    # Move to the start of the current paragraph
                    cursor = editor.textCursor()
                    cursor.movePosition(cursor.StartOfBlock)
                    # Select to the current cursor position
                    start_pos = cursor.position()
                    cursor.movePosition(cursor.EndOfBlock, cursor.KeepAnchor)
                    selected_text = cursor.selectedText()
                    logging.critical(f"Paragraph text length: {len(selected_text)}")
                    print(f"DEBUG: Paragraph text length: {len(selected_text)}")
            
            if not selected_text.strip():
                logging.critical("No text available for LastWords to process.")
                self.parent_window.statusBar().showMessage("No text available for LastWords to process.", 5000)
                return

            logging.critical(f"Running LastWords script with text: {selected_text[:50]}...")
            print(f"DEBUG: Running LastWords script with text: {selected_text[:50]}...")

            # Run the LastWords script using subprocess
            logging.critical(f"LASTWORDS_SCRIPT path: {self.LASTWORDS_SCRIPT}")
            print(f"DEBUG: LASTWORDS_SCRIPT path: {self.LASTWORDS_SCRIPT}")
            
            # Check if the script exists
            import os
            if not os.path.exists(self.LASTWORDS_SCRIPT):
                logging.critical(f"LastWords script does not exist at: {self.LASTWORDS_SCRIPT}")
                self.parent_window.statusBar().showMessage(f"LastWords script not found at: {self.LASTWORDS_SCRIPT}", 5000)
                return
                
            logging.critical("Script exists, running subprocess...")
            print("DEBUG: Script exists, running subprocess...")
            
            result = subprocess.run(
                ['python3', self.LASTWORDS_SCRIPT, selected_text],
                capture_output=True,
                text=True,
                check=False
            )

            # Log outputs for debugging
            logging.critical(f"LastWords script returncode: {result.returncode}")
            logging.critical(f"LastWords script stdout: {result.stdout[:100]}")
            logging.critical(f"LastWords script stderr: {result.stderr[:100]}")
            print(f"DEBUG: LastWords script returncode: {result.returncode}")
            print(f"DEBUG: LastWords script stdout: {result.stdout[:100]}")
            print(f"DEBUG: LastWords script stderr: {result.stderr[:100]}")

            if result.returncode == 0:
                cursor = editor.textCursor()
                cursor.beginEditBlock()
                
                # Replace the selected text with the completed text
                if editor.textCursor().hasSelection():
                    cursor.removeSelectedText()
                    cursor.insertText(result.stdout)
                else:
                    # If no selection, replace the current paragraph/line
                    cursor.movePosition(cursor.StartOfBlock)
                    cursor.movePosition(cursor.EndOfBlock, cursor.KeepAnchor)
                    cursor.removeSelectedText()
                    cursor.insertText(result.stdout)
                
                cursor.endEditBlock()
                self.parent_window.statusBar().showMessage("LastWords script completed successfully.", 5000)
            else:
                error_msg = f"LastWords script failed: {result.stderr}"
                self.parent_window.statusBar().showMessage(error_msg, 5000)
                logging.error(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error in runLastWordsScript: {str(e)}"
            self.parent_window.statusBar().showMessage(error_msg, 5000)
            logging.error(error_msg, exc_info=True)

    def runLastWords59Script(self):
        """Run the LastWords59 script to complete the last sentence with 5-9 appropriate words."""
        logging.critical("Starting runLastWords59Script method in ScriptRunner!")
        print("DEBUG: Starting runLastWords59Script method in ScriptRunner!")
        
        try:
            editor = self.parent_window.currentEditor()
            if not editor:
                logging.critical("No open editor for LastWords59.")
                self.parent_window.statusBar().showMessage("No open editor for LastWords59.", 5000)
                return
            
            selected_text = editor.textCursor().selectedText()
            logging.critical(f"Selected text length: {len(selected_text)}")
            print(f"DEBUG: Selected text length: {len(selected_text)}")
            
            if not selected_text.strip():
                # If no text is selected, use the current paragraph or line
                cursor = editor.textCursor()
                cursor.select(cursor.BlockUnderCursor)
                selected_text = cursor.selectedText()
                logging.critical(f"Block text length: {len(selected_text)}")
                print(f"DEBUG: Block text length: {len(selected_text)}")
                
                # If still empty, try to get surrounding context
                if not selected_text.strip():
                    # Move to the start of the current paragraph
                    cursor = editor.textCursor()
                    cursor.movePosition(cursor.StartOfBlock)
                    # Select to the current cursor position
                    start_pos = cursor.position()
                    cursor.movePosition(cursor.EndOfBlock, cursor.KeepAnchor)
                    selected_text = cursor.selectedText()
                    logging.critical(f"Paragraph text length: {len(selected_text)}")
                    print(f"DEBUG: Paragraph text length: {len(selected_text)}")
            
            if not selected_text.strip():
                logging.critical("No text available for LastWords59 to process.")
                self.parent_window.statusBar().showMessage("No text available for LastWords59 to process.", 5000)
                return

            logging.critical(f"Running LastWords59 script with text: {selected_text[:50]}...")
            print(f"DEBUG: Running LastWords59 script with text: {selected_text[:50]}...")

            # Run the LastWords59 script using subprocess
            logging.critical(f"LASTWORDS59_SCRIPT path: {self.LASTWORDS59_SCRIPT}")
            print(f"DEBUG: LASTWORDS59_SCRIPT path: {self.LASTWORDS59_SCRIPT}")
            
            # Check if the script exists
            import os
            if not os.path.exists(self.LASTWORDS59_SCRIPT):
                logging.critical(f"LastWords59 script does not exist at: {self.LASTWORDS59_SCRIPT}")
                self.parent_window.statusBar().showMessage(f"LastWords59 script not found at: {self.LASTWORDS59_SCRIPT}", 5000)
                return
                
            logging.critical("Script exists, running subprocess...")
            print("DEBUG: Script exists, running subprocess...")
            
            result = subprocess.run(
                ['python3', self.LASTWORDS59_SCRIPT, selected_text],
                capture_output=True,
                text=True,
                check=False
            )

            # Log outputs for debugging
            logging.critical(f"LastWords59 script returncode: {result.returncode}")
            logging.critical(f"LastWords59 script stdout: {result.stdout[:100]}")
            logging.critical(f"LastWords59 script stderr: {result.stderr[:100]}")
            print(f"DEBUG: LastWords59 script returncode: {result.returncode}")
            print(f"DEBUG: LastWords59 script stdout: {result.stdout[:100]}")
            print(f"DEBUG: LastWords59 script stderr: {result.stderr[:100]}")

            if result.returncode == 0:
                cursor = editor.textCursor()
                cursor.beginEditBlock()
                
                # Replace the selected text with the completed text
                if editor.textCursor().hasSelection():
                    cursor.removeSelectedText()
                    cursor.insertText(result.stdout)
                else:
                    # If no selection, replace the current paragraph/line
                    cursor.movePosition(cursor.StartOfBlock)
                    cursor.movePosition(cursor.EndOfBlock, cursor.KeepAnchor)
                    cursor.removeSelectedText()
                    cursor.insertText(result.stdout)
                
                cursor.endEditBlock()
                self.parent_window.statusBar().showMessage("LastWords59 script completed successfully.", 5000)
            else:
                error_msg = f"LastWords59 script failed: {result.stderr}"
                self.parent_window.statusBar().showMessage(error_msg, 5000)
                logging.error(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error in runLastWords59Script: {str(e)}"
            self.parent_window.statusBar().showMessage(error_msg, 5000)
            logging.error(error_msg, exc_info=True)

    def runDTMSScript(self):
        """Run the DTMS script to analyze if a selected word makes sense in its context."""
        logging.debug("Starting runDTMSScript method in ScriptRunner")
        
        editor = self.parent_window.currentEditor()
        if not editor:
            QMessageBox.warning(self.parent_window, "No Editor", "No active editor found.")
            logging.warning("DTMS script triggered with no open editor.")
            return

        # Get the cursor and check for selection
        cursor = editor.textCursor()
        highlighted_word = cursor.selectedText()

        if not highlighted_word.strip():
            QMessageBox.warning(self.parent_window, "No Selection", "Please highlight a word to analyze its usage in context.")
            logging.warning("DTMS script triggered with no text selection.")
            return

        # Get the full text of the editor
        full_text = editor.toPlainText()

        try:
            # Create a temporary file with the highlighted word on first line and full text on second line
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp:
                temp.write(f"{highlighted_word}\n{full_text}")
                temp_path = temp.name

            # Run DTMS.py with the temporary file
            script_path = self.DTMS_SCRIPT
            
            if not os.path.exists(script_path):
                self.parent_window.statusBar().showMessage(f"DTMS script not found: {script_path}", 10000)
                logging.error(f"DTMS script not found at: {script_path}")
                return
                
            # Run the script and capture its output
            result = subprocess.run(
                ["python3", script_path, temp_path],
                capture_output=True,
                text=True,
                check=False
            )

            # Clean up the temporary file
            os.unlink(temp_path)

            if result.returncode == 0:
                # Get the API response from the output
                output_lines = result.stdout.split('\n')
                api_response = None
                for line in output_lines:
                    if "OpenAI API response:" in line:
                        api_response = line.split("OpenAI API response:", 1)[1].strip()
                        break
                
                if api_response:
                    # Create a popup with the analysis
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setWindowTitle("Word Usage Analysis")
                    
                    # Format the message text
                    msg.setText(f"Analysis for '{highlighted_word}':\n\n{api_response}")
                    
                    msg.setMinimumSize(500, 300)
                    msg.setStyleSheet("""
                        QLabel { 
                            font-size: 18pt; 
                            color: #d4d4d4; 
                        } 
                        QMessageBox { 
                            background-color: #2d2d2d; 
                        }
                    """)
                    msg.exec_()
                    
                    self.parent_window.statusBar().showMessage("Word usage analysis displayed", 5000)
                else:
                    raise Exception("No API response found in output")
            else:
                error_msg = f"DTMS script failed:\nExit code: {result.returncode}\nError: {result.stderr}\nOutput: {result.stdout}"
                raise Exception(error_msg)
                
        except Exception as e:
            error_msg = f"Error in DTMS script: {str(e)}"
            self.parent_window.statusBar().showMessage(error_msg, 10000)
            logging.error(error_msg, exc_info=True)
            QMessageBox.warning(self.parent_window, "DTMS Error", error_msg)

    def runSkepticalOutroScript(self):
        """Run the SkepticalOutro script to create a skeptical perspective of the selected text."""
        logging.debug("Starting runSkepticalOutroScript method in ScriptRunner")
        
        try:
            editor = self.parent_window.currentEditor()
            if not editor:
                logging.critical("No open editor for SkepticalOutro.")
                self.parent_window.statusBar().showMessage("No open editor for SkepticalOutro.", 5000)
                return
            
            selected_text = editor.textCursor().selectedText()
            logging.debug(f"Selected text length: {len(selected_text)}")
            
            if not selected_text.strip():
                # If no text is selected, use the current paragraph or line
                cursor = editor.textCursor()
                cursor.select(cursor.BlockUnderCursor)
                selected_text = cursor.selectedText()
                logging.debug(f"Block text length: {len(selected_text)}")
                
                # If still empty, try to get surrounding context
                if not selected_text.strip():
                    # Move to the start of the current paragraph
                    cursor = editor.textCursor()
                    cursor.movePosition(cursor.StartOfBlock)
                    # Select to the current cursor position
                    cursor.movePosition(cursor.EndOfBlock, cursor.KeepAnchor)
                    selected_text = cursor.selectedText()
                    logging.debug(f"Paragraph text length: {len(selected_text)}")
            
            if not selected_text.strip():
                logging.critical("No text available for SkepticalOutro to process.")
                self.parent_window.statusBar().showMessage("No text available for SkepticalOutro to process.", 5000)
                return

            logging.debug(f"Running SkepticalOutro script with text: {selected_text[:50]}...")

            # Check if the script exists
            if not os.path.exists(self.SKEPTICAL_OUTRO_SCRIPT):
                logging.critical(f"SkepticalOutro script does not exist at: {self.SKEPTICAL_OUTRO_SCRIPT}")
                self.parent_window.statusBar().showMessage(f"SkepticalOutro script not found at: {self.SKEPTICAL_OUTRO_SCRIPT}", 5000)
                return
                
            # Run the SkepticalOutro script using subprocess
            result = subprocess.run(
                ['python3', self.SKEPTICAL_OUTRO_SCRIPT, selected_text],
                capture_output=True,
                text=True,
                check=False
            )

            # Log outputs for debugging
            logging.debug(f"SkepticalOutro script returncode: {result.returncode}")
            logging.debug(f"SkepticalOutro script stdout: {result.stdout[:100]}")
            logging.debug(f"SkepticalOutro script stderr: {result.stderr[:100]}")

            if result.returncode == 0:
                cursor = editor.textCursor()
                cursor.beginEditBlock()
                
                # Get the skeptical perspective directly without special formatting
                skeptical_outro = result.stdout.strip()
                
                # If text is selected, we move to the end and add a new line
                if editor.textCursor().hasSelection():
                    # Move to the end of the selection
                    cursor.setPosition(cursor.selectionEnd())
                    # Insert a newline and the skeptical perspective
                    cursor.insertText(f"\n\n{skeptical_outro}")
                else:
                    # If no selection, add after the current paragraph
                    cursor.movePosition(cursor.EndOfBlock)
                    cursor.insertText(f"\n\n{skeptical_outro}")
                
                cursor.endEditBlock()
                self.parent_window.statusBar().showMessage("Skeptical perspective added.", 5000)
            else:
                error_msg = f"SkepticalOutro script failed: {result.stderr}"
                self.parent_window.statusBar().showMessage(error_msg, 5000)
                logging.error(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error in runSkepticalOutroScript: {str(e)}"
            self.parent_window.statusBar().showMessage(error_msg, 5000)
            logging.error(error_msg, exc_info=True)

    def runGpsCScript(self):
        """
        Runs the GPS-C script on the selected text to extract GPS coordinates from tweet content.
        This method analyzes context in tweets or longer text to identify locations.
        """
        editor = self.parent_window.currentEditor()
        if not editor:
            self.parent_window.statusBar().showMessage("No open editor for GPS-C.", 5000)
            logging.warning("GPS-C script triggered with no open editor.")
            return

        # Get the cursor and check for selection
        cursor = editor.textCursor()
        selected_text = cursor.selectedText()

        # GPS-C requires selected text (unlike regular GPS which can work with a single line)
        if not selected_text.strip():
            QMessageBox.warning(self.parent_window, "No Text Selected", 
                                "Please select some text (tweets/content) to analyze for GPS coordinates.")
            logging.warning("GPS-C script triggered with no text selection.")
            return

        try:
            # Get the correct path to gps-c.py in the scripts folder
            script_path = os.path.join(self.scripts_dir, 'gps-c.py')
            
            logging.debug(f"Processing tweet content: {selected_text[:100]}...")  # First 100 chars
            logging.debug(f"Using script at: {script_path}")
            
            # Create a temporary file with just the selected text (no 111 markers)
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                temp_file.write(selected_text)
                temp_file_path = temp_file.name
                logging.debug(f"Created temp file at: {temp_file_path}")

            # Run the gps-c.py script with the temporary file
            result = subprocess.run(
                ['python3', script_path, temp_file_path],
                capture_output=True, 
                text=True,
                check=False
            )

            # Clean up the temporary file
            os.unlink(temp_file_path)

            if result.returncode == 0:
                # The script now returns the full formatted output directly
                output = result.stdout.strip()
                
                if output:
                    # Replace the selected text with the processed output
                    cursor.beginEditBlock()
                    cursor.removeSelectedText()
                    cursor.insertText(output)
                    cursor.endEditBlock()
                    
                    self.parent_window.statusBar().showMessage("GPS coordinates extracted from tweet content.", 5000)
                    logging.info(f"GPS-C Script successful.")
                else:
                    raise Exception("No output returned from the script")
            else:
                error_msg = f"Script failed:\nExit code: {result.returncode}\nError: {result.stderr}\nOutput: {result.stdout}"
                raise Exception(error_msg)

        except Exception as e:
            error_details = str(e)
            QMessageBox.critical(self.parent_window, "Error", f"Failed to extract GPS coordinates:\n{error_details}")
            logging.error(f"GPS-C Script error: {error_details}")
