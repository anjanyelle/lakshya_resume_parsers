"""
Resume text preprocessor that normalizes raw extracted text.
Runs BEFORE any parsing to ensure consistent, clean input for all parsers.
"""

import re
from typing import Dict, Any


class ResumePreprocessor:
    """
    Preprocessor that cleans and normalizes raw resume text.
    Ensures consistent input for all parsing components.
    """
    
    def __init__(self):
        """Initialize the preprocessor."""
        self.encoding_fixes = {
            'â€™': "'", 'â€œ': '"', 'â€': '"',
            'Ã©': 'é', 'Ã¨': 'è', 'Ã ': 'à',
            '\u2019': "'", '\u201c': '"', '\u201d': '"',
            '\u2013': '-', '\u2014': '-',
        }
    
    def preprocess(self, raw_text: str) -> str:
        """
        Main preprocessing pipeline that applies all normalization steps.
        
        Args:
            raw_text: Raw extracted text from PDF/DOCX files
            
        Returns:
            Cleaned and normalized text ready for parsing
        """
        if not raw_text:
            return ""
        
        text = self._normalize_bullets(raw_text)
        text = self._fix_broken_lines(text)
        text = self._normalize_section_headers(text)
        text = self._fix_encoding_artifacts(text)
        text = self._normalize_whitespace(text)
        
        return text.strip()
    
    def _normalize_bullets(self, text: str) -> str:
        """
        Normalize all bullet variants to a plain dash.
        
        Handles various bullet characters that might appear in different formats:
        • ● ◦ ▪ ▸ ◆ ■ ◉ ➤ → - – —
        
        Args:
            text: Text with potentially inconsistent bullet characters
            
        Returns:
            Text with normalized bullet characters
        """
        # Normalize all bullet variants to a plain dash
        return re.sub(r'[•●◦▪▸◆■◉➤→\-–—]+\s*', '- ', text)
    
    def _fix_broken_lines(self, text: str) -> str:
        """
        Fix broken lines that commonly occur in PDF extraction.
        
        Handles two common issues:
        1. Words split mid-line with hyphen at line end
        2. Lines that are clearly continuations (no punctuation at end)
        
        Args:
            text: Text with potentially broken lines
            
        Returns:
            Text with fixed line breaks
        """
        # Fix hyphenated words split across lines (case insensitive)
        text = re.sub(r'([a-zA-Z])-\n([a-zA-Z])', r'\1\2', text)
        
        # Join lines that are clearly continuations (no punctuation at end)
        # This handles cases where a line ends without punctuation and next line starts with lowercase
        text = re.sub(r'([^.\n:,;!?])\n([a-z])', r'\1 \2', text)
        
        return text
    
    def _normalize_section_headers(self, text: str) -> str:
        """
        Normalize section headers to Title Case format.
        
        Converts ALL CAPS lines that look like section headers to Title Case.
        Only affects lines that are 4+ characters long and all uppercase.
        
        Args:
            text: Text with potentially inconsistent section header formatting
            
        Returns:
            Text with normalized section headers
        """
        def title_if_header(match):
            line = match.group(0).strip()
            # Only convert if it's all uppercase and longer than 3 characters
            # and contains only letters and spaces (no numbers or special chars)
            if len(line) > 3 and line.isupper() and re.match(r'^[A-Z ]+$', line):
                return line.title()
            return line
        
        return re.sub(r'^[A-Z ]{4,}$', title_if_header, text, flags=re.MULTILINE)
    
    def _fix_encoding_artifacts(self, text: str) -> str:
        """
        Fix common encoding artifacts from PDF extraction.
        
        Handles various encoding issues that can occur when extracting text
        from PDFs, especially those with special characters or international content.
        
        Args:
            text: Text with potential encoding artifacts
            
        Returns:
            Text with fixed encoding
        """
        for bad, good in self.encoding_fixes.items():
            text = text.replace(bad, good)
        
        return text
    
    def _normalize_whitespace(self, text: str) -> str:
        """
        Normalize whitespace throughout the document.
        
        Handles excessive blank lines and trailing spaces.
        
        Args:
            text: Text with inconsistent whitespace
            
        Returns:
            Text with normalized whitespace
        """
        # Remove trailing spaces on each line first
        text = '\n'.join(line.rstrip() for line in text.splitlines())
        
        # Collapse 3+ blank lines to 2
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text
    
    def get_preprocessing_stats(self, original_text: str, processed_text: str) -> Dict[str, Any]:
        """
        Get statistics about the preprocessing changes.
        
        Args:
            original_text: Text before preprocessing
            processed_text: Text after preprocessing
            
        Returns:
            Dictionary with preprocessing statistics
        """
        return {
            'original_length': len(original_text),
            'processed_length': len(processed_text),
            'lines_before': len(original_text.splitlines()),
            'lines_after': len(processed_text.splitlines()),
            'encoding_fixes_applied': sum(1 for bad in self.encoding_fixes.keys() if bad in original_text),
            'size_reduction': len(original_text) - len(processed_text)
        }
