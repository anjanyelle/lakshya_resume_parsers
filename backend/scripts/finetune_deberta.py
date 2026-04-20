"""
Transformer Fine-Tuning for Work History NER
============================================
CPU-compatible training script for models like DeBERTa, RoBERTa, and JobBERTa.
Uses standard PyTorch datasets to avoid MemoryErrors on Windows.

Task:  Token Classification — NER with IOB2 labels
Labels: B-COMPANY, I-COMPANY, B-TITLE, I-TITLE, B-DATE, I-DATE,
        B-LOCATION, I-LOCATION, O
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any
import torch
from torch.utils.data import Dataset

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# ── Label schema ────────────────────────────────────────────────────────────
LABEL_LIST = [
    "O",
    "B-COMPANY", "I-COMPANY",
    "B-TITLE",   "I-TITLE",
    "B-DATE",    "I-DATE",
    "B-LOCATION","I-LOCATION",
]
LABEL2ID = {l: i for i, l in enumerate(LABEL_LIST)}
ID2LABEL = {i: l for l, i in LABEL2ID.items()}
NUM_LABELS = len(LABEL_LIST)


# ══════════════════════════════════════════════════════════════════════════════
# DATASET CLASS
# ══════════════════════════════════════════════════════════════════════════════

class WorkHistoryDataset(Dataset):
    def __init__(self, records: list[dict], tokenizer, max_length: int = 256):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.features = []
        
        logger.info("Tokenizing %d records ...", len(records))
        for r in records:
            text = r.get("text", "")
            entities = r.get("entities", r.get("labels", {}))
            
            # Simple whitespace tokenize
            import re
            words = re.findall(r"\S+", text)
            
            # Align labels
            word_labels = ["O"] * len(words)
            words_lower = [w.lower() for w in words]
            
            entity_map = {
                "company":   ("COMPANY", entities.get("company", "") or ""),
                "title":     ("TITLE",   entities.get("title", "") or ""),
                "start_date":("DATE",    entities.get("start_date", "") or ""),
                "end_date":  ("DATE",    entities.get("end_date", "") or ""),
                "location":  ("LOCATION",entities.get("location", "") or ""),
            }
            
            for _, (ner_label, val) in entity_map.items():
                if not val or str(val).lower() in ("none", "null", "present"): continue
                ent_tokens = str(val).split()
                ent_lower = [t.lower() for t in ent_tokens]
                n = len(ent_tokens)
                for i in range(len(words) - n + 1):
                    if words_lower[i:i+n] == ent_lower:
                        if word_labels[i] == "O":
                            word_labels[i] = f"B-{ner_label}"
                            for j in range(1, n): word_labels[i+j] = f"I-{ner_label}"

            # Subword tokenize
            enc = tokenizer(words, is_split_into_words=True, truncation=True, max_length=max_length, padding="max_length")
            w_ids = enc.word_ids()
            label_ids = []
            prev_w_id = None
            for w_id in w_ids:
                if w_id is None:
                    label_ids.append(-100)
                elif w_id != prev_w_id:
                    lbl = word_labels[w_id] if w_id < len(word_labels) else "O"
                    label_ids.append(LABEL2ID.get(lbl, 0))
                else:
                    lbl = word_labels[w_id] if w_id < len(word_labels) else "O"
                    if lbl.startswith("B-"): lbl = "I-" + lbl[2:]
                    label_ids.append(LABEL2ID.get(lbl, 0))
                prev_w_id = w_id
            
            self.features.append({
                "input_ids": torch.tensor(enc["input_ids"]),
                "attention_mask": torch.tensor(enc["attention_mask"]),
                "labels": torch.tensor(label_ids)
            })

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        return self.features[idx]


# ══════════════════════════════════════════════════════════════════════════════
# TRAINING
# ══════════════════════════════════════════════════════════════════════════════

def compute_metrics(eval_pred: Any) -> dict[str, float]:
    try:
        from seqeval.metrics import f1_score, precision_score, recall_score
        import numpy as np
    except ImportError:
        return {}

    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=2)

    true_labels, pred_labels = [], []
    for pred_seq, label_seq in zip(predictions, labels):
        t_seq, p_seq = [], []
        for p, l in zip(pred_seq, label_seq):
            if l == -100: continue
            t_seq.append(ID2LABEL.get(int(l), "O"))
            p_seq.append(ID2LABEL.get(int(p), "O"))
        true_labels.append(t_seq)
        pred_labels.append(p_seq)

    return {
        "precision": precision_score(true_labels, pred_labels),
        "recall":    recall_score(true_labels, pred_labels),
        "f1":        f1_score(true_labels, pred_labels),
    }


def train(
    train_file: str,
    output_dir: str,
    model_name: str = "microsoft/deberta-v3-small",
    max_samples: int = 50_000,
    epochs: int = 3,
    batch_size: int = 8,
    learning_rate: float = 2e-5,
    max_length: int = 256,
    hf_token: str | None = None,
    fp16: bool = False,
) -> None:
    from transformers import (
        AutoTokenizer, AutoModelForTokenClassification,
        TrainingArguments, Trainer, DataCollatorForTokenClassification,
    )

    hf_token = hf_token or os.environ.get("HF_TOKEN")
    tokenizer = AutoTokenizer.from_pretrained(model_name, token=hf_token, use_fast=True)

    records = []
    with open(train_file, encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if idx >= max_samples: break
            records.append(json.loads(line.strip()))

    import random
    random.seed(42)
    random.shuffle(records)
    split_idx = int(len(records) * 0.9)
    
    logger.info("Initializing datasets ...")
    train_ds = WorkHistoryDataset(records[:split_idx], tokenizer, max_length)
    eval_ds  = WorkHistoryDataset(records[split_idx:], tokenizer, max_length)

    model = AutoModelForTokenClassification.from_pretrained(
        model_name, num_labels=NUM_LABELS, id2label=ID2LABEL, label2id=LABEL2ID,
        token=hf_token, ignore_mismatched_sizes=True,
    )

    args = TrainingArguments(
        output_dir=output_dir, num_train_epochs=epochs,
        per_device_train_batch_size=batch_size, per_device_eval_batch_size=batch_size * 2,
        learning_rate=learning_rate, warmup_steps=100, weight_decay=0.01,
        eval_strategy="epoch", save_strategy="epoch",
        load_best_model_at_end=True, metric_for_best_model="f1",
        fp16=fp16, dataloader_num_workers=0, logging_steps=50, report_to="none",
    )

    trainer = Trainer(
        model=model, args=args, train_dataset=train_ds, eval_dataset=eval_ds,
        processing_class=tokenizer, data_collator=DataCollatorForTokenClassification(tokenizer),
        compute_metrics=compute_metrics,
    )

    logger.info("Starting training ...")
    trainer.train()

    out = Path(output_dir) / "final"
    out.mkdir(parents=True, exist_ok=True)
    trainer.save_model(str(out))
    tokenizer.save_pretrained(str(out))
    with open(out / "label_config.json", "w") as f:
        json.dump({"id2label": ID2LABEL, "label2id": LABEL2ID}, f, indent=2)

    logger.info("✅ Done! Model at: %s", out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-file", required=True)
    parser.add_argument("--output-dir", default="models/transformer-ner")
    parser.add_argument("--model-name", default="microsoft/deberta-v3-small")
    parser.add_argument("--max-samples", type=int, default=5000)
    parser.add_argument("--epochs", type=int, default=3)
    args = parser.parse_args()
    
    train(train_file=args.train_file, output_dir=args.output_dir, 
          model_name=args.model_name, max_samples=args.max_samples, epochs=args.epochs)

if __name__ == "__main__":
    main()
