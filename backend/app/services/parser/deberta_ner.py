"""
DeBERTa NER Inference Module
==============================
Production-ready CPU inference module for work history entity extraction.
Uses the fine-tuned microsoft/deberta-v3-small model.

Usage:
    from app.services.parser.deberta_ner import DeBERTaNER

    ner = DeBERTaNER("models/deberta-ner/final")   # load once at startup
    entities = ner.extract_entities(work_experience_text)
    # Returns: [{"company": "...", "title": "...", "location": "...", ...}, ...]

Graceful degradation: if the model is not yet trained, returns [] and the
existing heuristic parser continues to work unchanged.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# IOB2 label schema — must match finetune_deberta.py
LABEL_LIST = [
    "O",
    "B-COMPANY", "I-COMPANY",
    "B-TITLE",   "I-TITLE",
    "B-DATE",    "I-DATE",
    "B-LOCATION", "I-LOCATION",
]
LABEL2ID = {l: i for i, l in enumerate(LABEL_LIST)}
ID2LABEL  = {i: l for l, i in LABEL2ID.items()}


@dataclass
class NEREntity:
    label: str
    text: str
    start_idx: int
    end_idx: int
    confidence: float


@dataclass
class WorkHistoryEntities:
    company: str | None = None
    title: str | None = None
    location: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    raw_entities: list[NEREntity] = field(default_factory=list)


class TransformerNER:
    """
    CPU-optimized Transformer NER inference for work history entity extraction.
    Supports DeBERTa, RoBERTa (JobBERTa), and BERT architectures.

    Features
    --------
    - **Lazy loading**: model is only loaded on first use
    - **Chunking**: handles long texts (>256 tokens) by splitting on newlines
    - **IOB2 decoding**: reconstructs entity spans from per-token predictions
    - **Graceful degradation**: returns [] when model not found; heuristic
      parser continues unaffected
    """

    def __init__(self, model_dir: str) -> None:
        self.model_dir = Path(model_dir)
        self._model = None
        self._tokenizer = None
        self._available = False
        self._max_length = 256

    # ── Public API ────────────────────────────────────────────────────────────

    @property
    def is_available(self) -> bool:
        if self._available:
            return True
        try:
            self._load_model()
        except Exception:
            pass
        return self._available

    def extract_entities(self, text: str) -> list[dict[str, Any]]:
        """
        Extract work-history entities from *text*.

        Returns a list of entry dicts (one per job detected):
        ::

            [
              {"company": "...", "title": "...", "location": "...",
               "start_date": "...", "end_date": "..."},
              ...
            ]
        """
        if not text or not text.strip():
            return []
        if not self.is_available:
            return []
        try:
            return self._extract_impl(text)
        except Exception as exc:
            logger.warning("Transformer NER inference failed: %s", exc)
            return []

    # ── Private helpers ───────────────────────────────────────────────────────

    def _load_model(self) -> None:
        if self._model is not None:
            return

        if not self.model_dir.exists():
            logger.warning(
                "Transformer model not found at '%s'. "
                "Run: python scripts/finetune_deberta.py to train a model. "
                "Heuristic parser will be used.",
                self.model_dir,
            )
            return

        try:
            from transformers import (
                AutoModelForTokenClassification,
                AutoTokenizer,
            )

            logger.info("Loading Transformer NER model from %s …", self.model_dir)
            self._tokenizer = AutoTokenizer.from_pretrained(
                str(self.model_dir), use_fast=True
            )
            self._model = AutoModelForTokenClassification.from_pretrained(
                str(self.model_dir),
                num_labels=len(LABEL_LIST),
                id2label=ID2LABEL,
                label2id=LABEL2ID,
                ignore_mismatched_sizes=True,
            )
            self._model.eval()
            self._available = True
            model_type = getattr(self._model.config, "model_type", "transformer")
            logger.info("✓ Transformer NER ready (%s, CPU mode)", model_type)

        except ImportError:
            logger.warning(
                "transformers / torch not installed. "
                "pip install transformers[torch] to enable Transformer NER."
            )
        except Exception as exc:
            logger.warning("Transformer load error: %s", exc)

    def _extract_impl(self, text: str) -> list[dict[str, Any]]:
        import torch

        chunks = self._chunk_lines(text.split("\n"), max_tokens=self._max_length - 10)
        all_entities: list[NEREntity] = []
        offset = 0

        for chunk_text in chunks:
            encoding = self._tokenizer(
                chunk_text,
                return_tensors="pt",
                truncation=True,
                max_length=self._max_length,
                return_offsets_mapping=True,
            )
            offset_mapping = encoding.pop("offset_mapping")[0].tolist()

            with torch.no_grad():
                outputs = self._model(**encoding)

            logits = outputs.logits[0]
            probs  = torch.softmax(logits, dim=-1)
            pred_ids   = torch.argmax(logits, dim=-1).tolist()
            pred_probs = probs.max(dim=-1).values.tolist()

            ents = self._decode_iob2(
                chunk_text, pred_ids, pred_probs, offset_mapping, offset
            )
            all_entities.extend(ents)
            offset += len(chunk_text) + 1

        return self._build_work_entries(all_entities)

    @staticmethod
    def _chunk_lines(lines: list[str], max_tokens: int = 200) -> list[str]:
        chunks: list[str] = []
        current: list[str] = []
        current_len = 0
        for line in lines:
            n = len(line.split())
            if current_len + n > max_tokens and current:
                chunks.append("\n".join(current))
                current, current_len = [], 0
            current.append(line)
            current_len += n
        if current:
            chunks.append("\n".join(current))
        return chunks or [""]

    @staticmethod
    def _decode_iob2(
        text: str,
        pred_ids: list[int],
        pred_probs: list[float],
        offset_mapping: list[tuple[int, int]],
        global_offset: int,
    ) -> list[NEREntity]:
        entities: list[NEREntity] = []
        cur_label: str | None = None
        cur_start = cur_end = 0
        cur_parts: list[str] = []
        cur_conf = 0.0

        def _flush() -> None:
            nonlocal cur_label, cur_parts, cur_conf
            if cur_label:
                entities.append(NEREntity(
                    label=cur_label,
                    text=" ".join(cur_parts).strip(),
                    start_idx=global_offset + cur_start,
                    end_idx=global_offset + cur_end,
                    confidence=cur_conf,
                ))
            cur_label = None
            cur_parts.clear()

        for token_id, prob, (cs, ce) in zip(pred_ids, pred_probs, offset_mapping):
            if cs == ce:       # special / padding token
                _flush()
                continue
            lbl = ID2LABEL.get(token_id, "O")
            tok = text[cs:ce]

            if lbl.startswith("B-"):
                _flush()
                cur_label = lbl[2:]
                cur_start = cs
                cur_end   = ce
                cur_parts = [tok]
                cur_conf  = prob
            elif lbl.startswith("I-") and cur_label == lbl[2:]:
                cur_end = ce
                cur_parts.append(tok)
                cur_conf = (cur_conf + prob) / 2.0
            else:
                _flush()

        _flush()
        return entities

    @staticmethod
    def _build_work_entries(entities: list[NEREntity]) -> list[dict[str, Any]]:
        """Group IOB2 entities into per-job dicts (a new COMPANY → new entry)."""
        entries: list[dict[str, Any]] = []
        current: dict[str, Any] = {}

        for ent in sorted(entities, key=lambda e: e.start_idx):
            if ent.label == "COMPANY":
                if current:
                    entries.append(TransformerNER._finalise(current))
                current = {"company": ent.text, "_conf": ent.confidence}
            elif ent.label == "TITLE":
                current.setdefault("title", ent.text)
            elif ent.label == "LOCATION":
                current.setdefault("location", ent.text)
            elif ent.label == "DATE":
                if "start_date" not in current:
                    current["start_date"] = ent.text
                else:
                    current["end_date"] = ent.text

        if current:
            entries.append(TransformerNER._finalise(current))

        return entries

    @staticmethod
    def _finalise(d: dict[str, Any]) -> dict[str, Any]:
        return {
            "company":    d.get("company"),
            "title":      d.get("title"),
            "location":   d.get("location"),
            "start_date": d.get("start_date"),
            "end_date":   d.get("end_date"),
            "_ner_confidence": round(d.get("_conf", 0.0), 3),
        }


# ── Backward-compat alias ────────────────────────────────────────────────────
# JobBERTa, DeBERTa-v3, RoBERTa — all use the same TransformerNER class.
DeBERTaNER = TransformerNER

# ── Module-level singleton ────────────────────────────────────────────────────

_ner_instance: TransformerNER | None = None


def get_ner(model_dir: str = "models/deberta-ner/final") -> TransformerNER:
    """Return (and lazily load) the shared TransformerNER singleton."""
    global _ner_instance
    if _ner_instance is None:
        _ner_instance = TransformerNER(model_dir)
    return _ner_instance
