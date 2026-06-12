from __future__ import annotations


def assert_non_empty(value, field_name: str) -> None:
    assert value, f"{field_name} should not be empty"


def assert_contains_any(haystack: list[str], needles: list[str], field_name: str) -> None:
    normalized = {item.lower() for item in haystack}
    assert any(item.lower() in normalized for item in needles), (
        f"{field_name} missing expected values: {needles}"
    )
