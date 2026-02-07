from __future__ import annotations

import hashlib


def hash_value(value: str) -> str:
    return hashlib.sha256(value.lower().encode("utf-8")).hexdigest()
