# Resume fixture cases

Each case folder under this directory contains:

- `original.<ext>`: The original resume file used as input (for example: `.pdf`, `.docx`, `.rtf`, `.txt`).
- `truth.json`: The expected structured JSON output.

`truth.json` must follow the agreed schema used by the LLM structured resume parser (the same shape returned by `LLMParsingService.extract_structured_resume`).
