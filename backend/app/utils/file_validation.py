from __future__ import annotations

from typing import Optional


MAGIC_HEADERS = {
    "pdf": [b"%PDF"],
    "docx": [b"PK\x03\x04"],
    "doc": [b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1"],
    "rtf": [b"{\\rtf"],
    "txt": [],
}


def detect_file_type(data: bytes) -> Optional[str]:
    for file_type, signatures in MAGIC_HEADERS.items():
        for sig in signatures:
            if data.startswith(sig):
                return file_type
    return None


def validate_magic(data: bytes, extension: str) -> bool:
    if extension == "txt":
        return True
    detected = detect_file_type(data)
    if extension == "docx" and detected == "docx":
        return True
    if extension == "doc" and detected == "doc":
        return True
    if extension == "pdf" and detected == "pdf":
        return True
    if extension == "rtf" and data.startswith(b"{\\rtf"):
        return True
    return False
