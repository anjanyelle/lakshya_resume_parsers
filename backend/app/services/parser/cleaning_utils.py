"""
Utilities for cleaning and normalizing resume text.
"""
import re
import unicodedata
import logging

logger = logging.getLogger(__name__)

_NLP_CACHE = {}


def clean_resume_text(text: str) -> str:
    """
    Apply a series of cleaning operations to raw resume text.
    Targeting PDF artifacts, broken unicode, and common noise.
    """
    if not text:
        return ""

    # 1. Unicode normalization
    text = unicodedata.normalize("NFKC", text)

    # 2. Fix page numbers (e.g. "Page 1 of 3")
    # This often breaks sentences or sections.
    text = re.sub(r"\n\s*Page\s+\d+\s+of\s+\d+\s*\n", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"\n\s*Page\s+\d+\s*\n", "\n", text, flags=re.IGNORECASE)

    # 3. Fix broken words (e.g. "Manag  er" -> "Manager")
    # We look for letters separated by 2-3 spaces, but be careful not to merge distinct words.
    # A safe heuristic is looking for a pattern like "S o f t w a r e" (spaced out chars)
    # or "Manag  er" (single split in a common word).
    # For now, we'll try a conservative whitespace collapse.

    # Collapse multiple spaces/tabs into single space, but preserve newlines
    lines = []
    for line in text.splitlines():
        # Replace tabs and multiple spaces
        cleaned_line = re.sub(r"[ \t]+", " ", line).strip()
        
        # Remove "replacement character" artifacts
        cleaned_line = cleaned_line.replace("\ufffd", "")
        
        # Remove zero-width spaces
        cleaned_line = re.sub(r"[\u200b\u200c\u200d\u2060\ufeff]", "", cleaned_line)
        
        if cleaned_line:
            lines.append(cleaned_line)

    text = "\n".join(lines)

    # 4. Fix common PDF extraction artifact: "Ti tle" -> "Title"
    text = fix_spaced_words(text)

    # 5. Fix common broken words via regex
    text = re.sub(r"\n\s*([A-Z]\s){3,}[A-Z]\s*\n", lambda m: "\n" + m.group(0).replace(" ", "") + "\n", text)
    
    return text


def fix_spaced_words(text: str) -> str:
    """
    Fixes words that have been split by spaces due to PDF extraction issues.
    Example: "M a n a g e r" -> "Manager"
    Strategy: Look for sequences of single letters separated by spaces.
    """
    # Regex for single letters separated by space, at least 3 letters.
    # e.g. S o f t w a r e
    # We use a lookahead to ensure we don't merge "I a m" -> "Iam" blindly, 
    # but for now, we assume >2 letters is a broken word.
    
    def replacer(match: re.Match) -> str:
        # Join the characters and remove spaces
        # If there are double spaces, they might be word separators in the spaced text
        # e.g. "S o f t w a r e   E n g i n e e r"
        content = match.group(0)
        # If we see double spaces, we treat them as a word boundary
        if "  " in content:
            parts = re.split(r"\s{2,}", content)
            return " ".join(p.replace(" ", "") for p in parts)
        return content.replace(" ", "")

    # Pattern: a single letter, followed by (space + single letter) repeated 2+ times.
    # \b ensures we start at a word boundary.
    # [A-Za-z] matches letters.
    # We handle basic latin letters.
    # We allow single spaces between letters, and optionally double spaces between words if the pattern continues
    # But a simple regex is specific to "letter space letter space".
    pattern = r"\b[A-Za-z](?:\s+[A-Za-z]){2,}\b"
    
    # We operate line by line to avoid merging across newlines (though regex is per line usually)
    lines = []
    for line in text.splitlines():
        # Only apply if the line looks like it has these artifacts
        # We don't want to corrupt valid text like "I a m a".
        # Heuristic: if the match is long enough.
        new_line = re.sub(pattern, replacer, line)
        lines.append(new_line)
        
    return "\n".join(lines)


def clean_job_title(title: str | None) -> str | None:
    if not title:
        return None
    cleaned = title.strip()
    # Remove trailing punctuation often captured
    cleaned = re.sub(r"[,|\-–—]+$", "", cleaned).strip()
    return cleaned if len(cleaned) > 2 else None


def clean_company_name(company: str | None) -> str | None:
    if not company:
        return None
    cleaned = company.strip()
    # Remove legal entity noise if it's the *only* thing (unlikely, but good safety)
    if cleaned.lower() in {"inc", "llc", "ltd", "corp"}:
        return None
    return cleaned if len(cleaned) > 2 else None


def get_spacy_model(model_name: str):
    """
    Load a SpaCy model and cache it to avoid repeated loading.
    """
    if model_name not in _NLP_CACHE:
        try:
            import spacy
            logger.info(f"Loading SpaCy model: {model_name}")
            _NLP_CACHE[model_name] = spacy.load(model_name)
        except Exception as e:
            logger.warning(f"Could not load SpaCy model {model_name}: {e}")
            return None
    return _NLP_CACHE[model_name]
