#!/usr/bin/env python3
"""Merge skills_expansion.json into skills_seed.json.

Run from backend/: python scripts/merge_skills_expansion.py

Deduplicates by normalized_name. Backup created at skills_seed.json.bak.
"""
from __future__ import annotations

import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
SEED_PATH = BASE / "app" / "data" / "taxonomy" / "skills_seed.json"
EXPANSION_PATH = BASE / "app" / "data" / "taxonomy" / "skills_expansion.json"


def main() -> None:
    with SEED_PATH.open("r", encoding="utf-8") as f:
        seed = json.load(f)

    with EXPANSION_PATH.open("r", encoding="utf-8") as f:
        expansion = json.load(f)

    existing_norm = {s.get("normalized_name", "").lower() for s in seed.get("skills", [])}
    new_skills = [
        s
        for s in expansion.get("skills", [])
        if s.get("normalized_name", "").lower() not in existing_norm
    ]

    if not new_skills:
        print("No new skills to add (all already in seed).")
        return

    # Backup
    backup = SEED_PATH.with_suffix(".json.bak")
    with backup.open("w", encoding="utf-8") as f:
        json.dump(seed, f, indent=2, ensure_ascii=False)
    print(f"Backup: {backup}")

    # Merge
    seed["skills"] = seed.get("skills", []) + new_skills
    with SEED_PATH.open("w", encoding="utf-8") as f:
        json.dump(seed, f, indent=2, ensure_ascii=False)

    print(f"Added {len(new_skills)} skills. Total: {len(seed['skills'])}")


if __name__ == "__main__":
    main()
