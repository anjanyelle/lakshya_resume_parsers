Resume Parser Fine-Tuning Project

This repository includes a resume parsing system and a small synthetic dataset
generator for fine-tuning or evaluation.

Quick Start
- Generate dataset files:
  - python scripts/prepare_dataset.py

Outputs
- data/train.jsonl
- data/val.jsonl

Each JSONL line has:
{
  "input": "<raw resume text>",
  "output": "<stringified JSON with structured fields>"
}

Notes
- The dataset generator includes 5 diverse examples.
- Intended for local experimentation and prompt/finetune iteration.



