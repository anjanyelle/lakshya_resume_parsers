#!/usr/bin/env python3
"""Test the is_available logic."""

is_loaded = False
structured_parser = object()  # Some object

result = is_loaded or structured_parser is not None
print(f"is_loaded: {is_loaded}")
print(f"structured_parser is not None: {structured_parser is not None}")
print(f"Result: {result}")
