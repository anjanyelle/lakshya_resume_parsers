"""Train a spaCy NER model from prepared DocBin data.

This script expects `data/ner/train.spacy` and `data/ner/valid.spacy` (or paths you specify).
It will train a spaCy NER model and save it under `backend/models/resume_ner_model/model-last`
(and optionally `model-best`).

Usage:
    python scripts/train_spacy_ner.py --train data/ner/train.spacy --dev data/ner/valid.spacy

Optionally resume from existing model:
    python scripts/train_spacy_ner.py --train ... --dev ... --init-model backend/models/resume_ner_model/model-last

"""

from __future__ import annotations

import argparse
import random
from pathlib import Path

import spacy
from spacy.tokens import DocBin
from spacy.training import Example


def load_docbin(nlp: spacy.Language, path: Path) -> list[spacy.tokens.Doc]:
    db = DocBin().from_disk(path)
    return list(db.get_docs(nlp.vocab))


def main():
    parser = argparse.ArgumentParser(description="Train a spaCy NER model")
    parser.add_argument("--train", type=Path, required=True, help="Path to train.spacy")
    parser.add_argument("--dev", type=Path, required=True, help="Path to valid.spacy")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("backend/models/resume_ner_model"),
        help="Directory to write trained model",
    )
    parser.add_argument(
        "--init-model",
        type=Path,
        default=None,
        help="Optional existing spaCy model path to continue training from",
    )
    parser.add_argument("--n-iter", type=int, default=30, help="Number of training iterations")
    parser.add_argument("--dropout", type=float, default=0.25, help="Dropout during training")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    random.seed(args.seed)

    if args.init_model and args.init_model.exists():
        nlp = spacy.load(str(args.init_model))
        print(f"Loaded existing model from {args.init_model}")
    else:
        nlp = spacy.blank("en")

    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner")
    else:
        ner = nlp.get_pipe("ner")

    # Ensure label set matches train data
    train_docs = load_docbin(nlp, args.train)
    dev_docs = load_docbin(nlp, args.dev)

    labels = set()
    for doc in train_docs:
        for ent in doc.ents:
            labels.add(ent.label_)
    for label in labels:
        ner.add_label(label)

    # Convert docs to Examples for initialize and update
    train_examples = []
    for doc in train_docs:
        train_examples.append(Example.from_dict(nlp.make_doc(doc.text), {"entities": [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]}))
    
    dev_examples = []
    for doc in dev_docs:
        dev_examples.append(Example.from_dict(nlp.make_doc(doc.text), {"entities": [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]}))

    optimizer = nlp.initialize(get_examples=lambda: train_examples)

    best_f1 = 0.0
    output_path = args.output
    output_path.mkdir(parents=True, exist_ok=True)

    for itn in range(args.n_iter):
        random.shuffle(train_examples)
        losses = {}
        # Batching for speed and stability
        batches = spacy.util.minibatch(train_examples, size=spacy.util.compounding(4.0, 32.0, 1.001))
        for batch in batches:
            nlp.update(batch, drop=args.dropout, sgd=optimizer, losses=losses)
        # Eval on dev set
        scorer = nlp.evaluate(dev_examples)
        f1 = scorer.ents_f
        print(f"Iter {itn+1}/{args.n_iter}: loss={losses.get('ner', 0):.3f} | dev f1={f1:.3f}")

        # Save best model
        if f1 > best_f1:
            best_f1 = f1
            best_path = output_path / "model-best"
            nlp.to_disk(best_path)

    # Always save last model
    nlp.to_disk(output_path / "model-last")

    print(f"Training complete. Best F1 = {best_f1:.4f}")
    print(f"Saved last model to {output_path / 'model-last'}")
    if best_f1 > 0:
        print(f"Saved best model to {output_path / 'model-best'}")


if __name__ == "__main__":
    main()
