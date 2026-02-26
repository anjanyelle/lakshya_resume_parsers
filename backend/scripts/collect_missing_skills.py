#!/usr/bin/env python3
"""Collect missing skills from resume text for failure analysis.

Extracts skill-like tokens from text that are NOT in the taxonomy.
Output: JSON list of candidates to add to skills_expansion.json.

Usage:
  python scripts/collect_missing_skills.py path/to/resumes.txt
  python scripts/collect_missing_skills.py --from-dir path/to/resumes/
  python scripts/collect_missing_skills.py --from-json path/to/parsed_jobs.json

Output: missing_skills_candidates.json (sorted by frequency)
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
TAXONOMY_PATH = BASE / "app" / "data" / "taxonomy" / "skills_seed.json"
EXPANSION_PATH = BASE / "app" / "data" / "taxonomy" / "skills_expansion.json"

# Common non-skill tokens to filter
STOP_TOKENS = {
    "the", "and", "for", "with", "from", "using", "via", "etc", "e.g", "i.e",
    "years", "experience", "team", "project", "work", "role", "responsibilities",
    "developed", "implemented", "designed", "built", "created", "managed",
    "company", "organization", "client", "department", "division",
}


def load_taxonomy_normalized() -> set[str]:
    """Return set of normalized skill names from seed + expansion."""
    norm: set[str] = set()
    for path in [TAXONOMY_PATH, EXPANSION_PATH]:
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        for s in data.get("skills", []):
            n = (s.get("normalized_name") or "").strip().lower()
            if n:
                norm.add(n)
            for syn in s.get("synonyms", []):
                if syn:
                    norm.add(str(syn).strip().lower())
            name = (s.get("name") or "").strip().lower()
            if name:
                norm.add(name)
    return norm


def extract_skill_candidates(text: str) -> list[str]:
    """Extract potential skill tokens (2-4 word phrases, tech-looking)."""
    text = re.sub(r"[^\w\s\-\.\/\+#]", " ", text)
    words = text.split()
    candidates: list[str] = []

    # Single tokens: CamelCase, ALL_CAPS, or known patterns (e.g. "Python", "AWS")
    for w in words:
        w_clean = w.strip(".-,")
        if not w_clean or len(w_clean) < 2:
            continue
        if w_clean.lower() in STOP_TOKENS:
            continue
        if re.match(r"^[A-Z][a-z]+$", w_clean) or re.match(r"^[A-Z]{2,}$", w_clean):
            candidates.append(w_clean)
        if re.match(r"^[A-Za-z]+\.[A-Za-z]+$", w_clean):  # e.g. Node.js
            candidates.append(w_clean)
        if re.match(r"^[A-Za-z]+#[A-Za-z]*$", w_clean):  # C#
            candidates.append(w_clean)

    # Bigrams
    for i in range(len(words) - 1):
        b = f"{words[i]} {words[i+1]}".strip(".-,")
        if b and b.lower() not in STOP_TOKENS and 3 <= len(b) <= 40:
            candidates.append(b)

    # Trigrams (e.g. "Machine Learning", "Spring Boot")
    for i in range(len(words) - 2):
        t = f"{words[i]} {words[i+1]} {words[i+2]}".strip(".-,")
        if t and 5 <= len(t) <= 50:
            candidates.append(t)

    return candidates


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect missing skills from resume text")
    parser.add_argument("input", nargs="?", help="Path to text file or directory")
    parser.add_argument("--from-dir", help="Directory of .txt resume files")
    parser.add_argument("--from-json", help="JSON file with parsed jobs (skills, descriptions)")
    parser.add_argument("-o", "--output", default="missing_skills_candidates.json")
    parser.add_argument("--min-count", type=int, default=2, help="Min occurrences to include")
    args = parser.parse_args()

    known = load_taxonomy_normalized()
    counter: Counter[str] = Counter()

    def process_text(t: str) -> None:
        for c in extract_skill_candidates(t or ""):
            c_lower = c.lower().strip()
            if c_lower in known or c_lower in STOP_TOKENS:
                continue
            if len(c_lower) < 2 or len(c_lower) > 60:
                continue
            counter[c_lower] += 1

    if args.from_json:
        with open(args.from_json, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    process_text(item.get("description") or "")
                    for s in item.get("skills") or []:
                        process_text(str(s) if isinstance(s, str) else s.get("name", ""))
        elif isinstance(data, dict):
            for job in data.get("work_experience", data.get("experience", [])) or []:
                process_text(job.get("description") or "")
            for s in data.get("skills", []) or []:
                process_text(str(s) if isinstance(s, str) else s.get("name", ""))
    elif args.from_dir:
        for p in Path(args.from_dir).rglob("*.txt"):
            process_text(p.read_text(encoding="utf-8", errors="ignore"))
    elif args.input:
        process_text(Path(args.input).read_text(encoding="utf-8", errors="ignore"))
    else:
        parser.print_help()
        return

    # Build output: candidates with count >= min_count, sorted by count desc
    results = [
        {"name": k, "count": v}
        for k, v in counter.most_common()
        if v >= args.min_count
    ]

    out_path = Path(args.output)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(
            {"candidates": results, "total_unique": len(results)},
            f,
            indent=2,
            ensure_ascii=False,
        )
    print(f"Wrote {len(results)} candidates to {out_path}")


if __name__ == "__main__":
    main()
