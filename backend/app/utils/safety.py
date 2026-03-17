def safe_lower(text):
    """Safely convert text to lowercase, handling None and non-string values"""
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)
    return text.lower().strip()