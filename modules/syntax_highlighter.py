import re
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor
import os

class VHDLSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlightingRules = []
        self.hide_special_lines = False  # Toggle state for hiding lines

        # Add rule for URLs
        urlFormat = QTextCharFormat()
        urlFormat.setForeground(QColor("#3498db"))  # Blue color for URLs
        urlFormat.setUnderlineStyle(QTextCharFormat.SingleUnderline)
        self.urlPattern = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*')
        self.highlightingRules.append((self.urlPattern, urlFormat))

        # Add rule for Timestamp lines
        self.timestampPattern = re.compile(r'^Timestamp.*$', re.MULTILINE)

        # Add rule for lines starting with '--'
        commentFormat = QTextCharFormat()
        commentFormat.setForeground(QColor("#0e8420"))  # Green color for comments
        self.highlightingRules.append((re.compile(r'--.*'), commentFormat))

        # Add rule for numbers (integers and decimals)
        numberFormat = QTextCharFormat()
        numberFormat.setForeground(QColor("#7ba3e6"))  # Darker shade of light blue for numbers
        self.highlightingRules.append((re.compile(r'\b\d+\.?\d*\b'), numberFormat))

        # Add rule for lines starting with cc-
        ccLineFormat = QTextCharFormat()
        ccLineFormat.setForeground(QColor("#DB7093"))  # Pale violet red - a more faint pink
        self.highlightingRules.append((re.compile(r'^cc-.*$', re.MULTILINE), ccLineFormat))

        # Add rule for lines starting with mm-
        mmLineFormat = QTextCharFormat()
        mmLineFormat.setForeground(QColor("#800080"))  # Purple color for mm- lines
        self.highlightingRules.append((re.compile(r'^mm-.*$', re.MULTILINE), mmLineFormat))

        # Add rule for specific words to be highlighted in light pink
        keywordFormat = QTextCharFormat()
        keywordFormat.setForeground(QColor("#FFB6C1"))  # Light pink color for specific words
        keywords = ['to', 'the', 'now', 'as', 'if', 'where', 'because', 'so', 'that', 'additional', 'words']
        # Create a regex pattern that matches whole words only
        pattern = r'\b(?:' + '|'.join(re.escape(word) for word in keywords) + r')\b'
        self.highlightingRules.append((re.compile(pattern, re.IGNORECASE), keywordFormat))

        # Add rule for location names from file
        locationFormat = QTextCharFormat()
        locationFormat.setForeground(QColor("#FFB6C1"))  # Same color as title text
        
        # Read locations from file
        locations = []
        try:
            locations_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'highlighted_locations.txt')
            with open(locations_file, 'r', encoding='utf-8', errors='replace') as f:
                locations = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"Warning: Could not read locations file: {e}")
            
        if locations:
            # Create a regex pattern that matches whole words only for locations
            location_pattern = r'(?<!"Title:)\b(?:' + '|'.join(re.escape(loc) for loc in locations) + r')\b'
            self.highlightingRules.append((re.compile(location_pattern), locationFormat))

    def highlightBlock(self, text):
        # Check if line should be hidden
        if self.hide_special_lines:
            if (self.urlPattern.match(text) or 
                self.timestampPattern.match(text)):
                block = self.currentBlock()
                block.setVisible(False)
                return

        # Make sure block is visible when not hidden
        self.currentBlock().setVisible(True)

        # Set default text color
        defaultFormat = QTextCharFormat()
        defaultFormat.setForeground(QColor("#aaaaaa"))  # Slightly lighter gray color for regular text
        self.setFormat(0, len(text), defaultFormat)
        
        # Handle quotes first - this needs to be done before other rules
        stringFormat = QTextCharFormat()
        stringFormat.setForeground(QColor("#e6d4a3"))  # Yellow color for quoted text
        
        # Process both types of quotes
        pos = 0
        while pos < len(text):
            # Look for either type of quote
            quote_match = None
            for quote in ['"', '"']:
                next_quote = text.find(quote, pos)
                if next_quote != -1 and (quote_match is None or next_quote < quote_match[0]):
                    quote_match = (next_quote, quote)
            
            if quote_match is None:
                break
                
            start, quote_char = quote_match
            # Find matching closing quote
            end = text.find(quote_char, start + 1)
            
            if end == -1:
                # No closing quote found - highlight to end of line
                self.setFormat(start, len(text) - start, stringFormat)
                break
            else:
                # Highlight between and including quotes
                self.setFormat(start, end - start + 1, stringFormat)
                pos = end + 1
        
        # Apply other highlighting rules
        for pattern, format in self.highlightingRules:
            # Skip the quote patterns since we handle them separately
            if isinstance(pattern, re.Pattern) and ('\"' in pattern.pattern or '"' in pattern.pattern):
                continue
            for match in re.finditer(pattern, text):
                start, end = match.span()
                self.setFormat(start, end - start, format)
        
        self.setCurrentBlockState(0)

    def toggleSpecialLines(self):
        """Toggle visibility of lines starting with https or Timestamp"""
        self.hide_special_lines = not self.hide_special_lines
        # Need to rehighlight and update document layout
        doc = self.document()
        doc.markContentsDirty(0, doc.characterCount())
        self.rehighlight()
        # Force layout update
        doc.documentLayout().documentSizeChanged.emit(doc.size()) 