import re

MONTH_TOKEN = r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
DATE_TOKEN = (
    r"(?:"
    r"\d{4}-\d{2}-\d{2}"  # YYYY-MM-DD
    r"|\d{4}[/-]\d{1,2}"  # YYYY-MM or YYYY/MM
    r"|\d{1,2}[/-]\d{2,4}"  # MM/YY or MM/YYYY
    r"|\d{4}[/-]\d{2,4}"  # YYYY-YY or YYYY-YYYY range fragment
    r"|'\s*\d{2}"            # '20, '22
    r"|\b(?:19|20)\d{2}\b" # YYYY (restrictive for bare years)
    r"|Q[1-4]\s+\d{4}"    # Q1 2020, Q4 2019
    r"|(?:Spring|Fall|Summer|Winter|Autumn|Spring|Fall)\s+\d{4}"  # Seasonal
    r"|" + MONTH_TOKEN + r"\s*[\'\u2019]\d{2,4}"  # Jan '20, Feb '19
    r"|\d{4}\.\d{2}|\d{2,4}\.\d{2,4}"  # 2020.01, 01.2020
    r"|" + MONTH_TOKEN + r"[.,]?\s+\d{2,4}"  # MMM YYYY or MMM YY
    r"|" + MONTH_TOKEN + r"\s*[\u2019']\s*\d{2,4}"  # MMM 'YY
    r"|(?:\b[A-Za-z]{3,9}\s+\d{4}\b)" # September 2020
    r"|\b\d{2}/\d{4}\b" # 06/2024
    r")"
)

DATE_RANGE_RE = re.compile(
    rf"(?P<start>{DATE_TOKEN})\s*(?:\s*(?:[-–—→/]|->|to|until|thru|through|till)\s*)\s*(?P<end>present|current|till\s+date|now|ongoing|until\s+now|up\s+to\s+now|{DATE_TOKEN})",
    re.IGNORECASE,
)

samples = [
    "Jan 2020 - Dec 2021",
    "Feb 2022 - Present"
]

for s in samples:
    print(f"Testing: '{s}'")
    m = DATE_RANGE_RE.search(s)
    if m:
        print(f" FOUND: {m.group(0)}")
    else:
        print(" NOT FOUND")
        # Test individual tokens
        tokens = re.findall(DATE_TOKEN, s, re.IGNORECASE)
        print(f" Tokens found: {tokens}")
