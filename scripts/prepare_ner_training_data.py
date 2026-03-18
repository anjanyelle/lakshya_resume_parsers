"""Prepare unified resume NER training data into spaCy DocBin (and optional JSONL).

This script is designed to merge multiple token-level resume NER datasets (e.g., ResumeNER
and others) into a single spaCy training set with a consistent label schema.

Usage:
    python scripts/prepare_ner_training_data.py \
      --sources data/ResumeNER/Entity\ Recognition\ in\ Resumes.json \
      --output-dir data/ner \
      --train-ratio 0.9

Output:
- data/ner/train.spacy
- data/ner/valid.spacy
- (optional) data/ner/train.jsonl
- (optional) data/ner/valid.jsonl

The default label schema is: ORG, TITLE, DATE.
"""

from __future__ import annotations

import argparse
import json
import random
import zipfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import spacy
from spacy.tokens import DocBin


# ------------------
# Label normalization
# ------------------
# Map labels from datasets to the canonical labels used for training.
LABEL_MAP: Dict[str, str] = {
    # ResumeNER (common labels)
    "Companies worked at": "ORG",
    "Company": "ORG",
    "CompanyName": "ORG",
    "Company Name": "ORG",
    "Company name": "ORG",
    "Employer": "ORG",
    "Organisation": "ORG",
    "Organization": "ORG",
    "Organisation Name": "ORG",
    "Employer Name": "ORG",

    "Designation": "TITLE",
    "Job Title": "TITLE",
    "Title": "TITLE",
    "JobTitle": "TITLE",
    "Position": "TITLE",

    "Graduation Year": "DATE",
    "Year": "DATE",
    "Date": "DATE",
    "Period": "DATE",
    "Start Date": "DATE",
    "End Date": "DATE",
    "Employment Date": "DATE",
}


def _normalize_label(label: str) -> Optional[str]:
    if not label:
        return None
    label = label.strip()
    if label in LABEL_MAP:
        return LABEL_MAP[label]
    # Some datasets use lower-case/upper-case variations
    normalized = LABEL_MAP.get(label.title()) or LABEL_MAP.get(label.lower())
    if normalized:
        return normalized
    # If it's already in our desired schema, keep it.
    if label in {"ORG", "TITLE", "DATE"}:
        return label
    return None


def _load_json_lines(path: Path) -> Iterable[Dict[str, Any]]:
    """Load JSON objects from either a JSONL file or a JSON list file."""

    text = path.read_text(encoding="utf-8", errors="ignore")
    text = text.strip()
    if not text:
        return []

    # JSONL (one object per line)
    if text.startswith("{") or text.startswith("["):
        try:
            data = json.loads(text)
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                # for single-object files, wrap in list
                return [data]
        except json.JSONDecodeError:
            pass

    # fallback: line-by-line parse
    results: List[Dict[str, Any]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                results.append(obj)
        except json.JSONDecodeError:
            continue
    return results


def _extract_entities(record: Dict[str, Any]) -> List[Tuple[int, int, str]]:
    """Extract (start, end, label) tuples from a record."""

    entities: List[Tuple[int, int, str]] = []

    # Common field names for resume NER datasets
    annotations = record.get("annotation") or record.get("annotations") or record.get("entities")
    labels_list = record.get("labels")

    if annotations:
        for ann in annotations:
            # label may be a list like ['Designation'] or string
            label = ann.get("label")
            if isinstance(label, list) and label:
                label = label[0]
            if not isinstance(label, str):
                continue

            canonical = _normalize_label(label)
            if not canonical:
                continue

            points = ann.get("points") or []
            if not isinstance(points, list):
                continue

            for point in points:
                if not isinstance(point, dict):
                    continue
                start = point.get("start")
                end = point.get("end")
                if start is None or end is None:
                    continue
                # Many datasets use inclusive end indices; spaCy uses exclusive
                try:
                    start_i = int(start)
                    end_i = int(end) + 1
                except Exception:
                    continue
                if start_i >= end_i:
                    continue
                entities.append((start_i, end_i, canonical))

    if labels_list and isinstance(labels_list, list):
        for lbl_entry in labels_list:
            if isinstance(lbl_entry, list) and len(lbl_entry) >= 3:
                start, end, label = lbl_entry[:3]
                canonical = _normalize_label(label)
                if canonical:
                    # Assume inclusive end if it looks like typical Kaggle NER JSON
                    entities.append((int(start), int(end) + 1, canonical))

    return entities


def _make_docbin_from_records(
    records: List[Dict[str, Any]],
    nlp: spacy.Language,
    dedupe: bool = True,
) -> DocBin:
    db = DocBin()
    total_spans = 0
    discarded_spans = 0
    for record in records:
        text = record.get("content") or record.get("text") or record.get("raw_text")
        if not isinstance(text, str) or not text.strip():
            continue

        entities = _extract_entities(record)
        if not entities:
            continue

        doc = nlp.make_doc(text)
        spans = []
        occupied = set()
        for start, end, label in sorted(entities, key=lambda x: x[0]):
            total_spans += 1
            span = doc.char_span(start, end, label=label, alignment_mode="contract")
            if span is None:
                discarded_spans += 1
                continue
            if dedupe:
                overlap = any(i in occupied for i in range(span.start, span.end))
                if overlap:
                    continue
                for i in range(span.start, span.end):
                    occupied.add(i)
            spans.append(span)

        if spans:
            doc.ents = spans
            db.add(doc)
    
    print(f"DocBin summary: docs={len(db)}, total_spans={total_spans}, discarded={discarded_spans}")
    return db


def main():
    parser = argparse.ArgumentParser(description="Prepare unified spaCy NER training data")
    parser.add_argument(
        "--sources",
        nargs="+",
        required=True,
        help="Paths to JSON/JSONL NER datasets (can be inside zip archives).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/ner"),
        help="Output directory for train/valid DocBin and optional jsonl",
    )
    parser.add_argument(
        "--train-ratio",
        type=float,
        default=0.90,
        help="Fraction of examples to use for training (rest for validation).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for train/valid split.",
    )
    parser.add_argument(
        "--jsonl",
        action="store_true",
        help="Also emit train/valid JSONL in addition to spaCy DocBin.",
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    records: List[Dict[str, Any]] = []
    for src in args.sources:
        src_path = Path(src)
        if not src_path.exists():
            raise FileNotFoundError(src_path)

        if src_path.suffix.lower() == ".zip":
            with zipfile.ZipFile(src_path, "r") as z:
                for name in z.namelist():
                    if name.endswith(".json") or name.endswith(".jsonl"):
                        with z.open(name) as f:
                            try:
                                raw = f.read().decode("utf-8", errors="ignore")
                            except Exception:
                                continue
                            # write to temp file for parsing
                            tmp = Path(args.output_dir) / f"_tmp_{Path(name).name}"
                            tmp.write_text(raw, encoding="utf-8")
                            records.extend(list(_load_json_lines(tmp)))
                            tmp.unlink(missing_ok=True)
        else:
            records.extend(list(_load_json_lines(src_path)))

    random.Random(args.seed).shuffle(records)

    # Split
    split_at = int(len(records) * args.train_ratio)
    train_records = records[:split_at]
    valid_records = records[split_at:]

    nlp = spacy.blank("en")

    train_db = _make_docbin_from_records(train_records, nlp)
    valid_db = _make_docbin_from_records(valid_records, nlp)

    train_path = args.output_dir / "train.spacy"
    valid_path = args.output_dir / "valid.spacy"

    train_db.to_disk(train_path)
    valid_db.to_disk(valid_path)

    print(f"Saved {len(train_db)} training docs to {train_path}")
    print(f"Saved {len(valid_db)} validation docs to {valid_path}")

    if args.jsonl:
        def write_jsonl(path: Path, records_list: List[Dict[str, Any]]):
            with open(path, "w", encoding="utf-8") as f:
                for r in records_list:
                    json.dump(r, f, ensure_ascii=False)
                    f.write("\n")

        write_jsonl(args.output_dir / "train.jsonl", train_records)
        write_jsonl(args.output_dir / "valid.jsonl", valid_records)


if __name__ == "__main__":
    main()
