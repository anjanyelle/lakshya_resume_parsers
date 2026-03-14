import spacy
import json
from pathlib import Path
from collections import Counter

# Paths
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "backend" / "models" / "resume_ner_model" / "model-last"
DATA_PATH = BASE_DIR / "data" / "ResumeNER" / "Entity Recognition in Resumes.json"

def evaluate_model():
    print(f"Loading model from: {MODEL_PATH}")
    if not MODEL_PATH.exists():
        print(f"Model path does not exist: {MODEL_PATH}")
        return
    
    try:
        nlp = spacy.load(MODEL_PATH)
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    if not DATA_PATH.exists():
        print(f"Data path does not exist: {DATA_PATH}")
        return

    print(f"Evaluating on {DATA_PATH.name}...")
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    stats = Counter()
    limit = min(len(lines), 100)
    
    for line in lines[:limit]:
        data = json.loads(line)
        text = data["content"]
        ground_truth = data["annotation"]
        
        doc = nlp(text)
        
        predicted_ents = {(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents}
        gt_ents = set()
        for ann in ground_truth:
            label = ann["label"][0]
            points = ann["points"][0]
            gt_ents.add((points["start"], points["end"] + 1, label))
        
        common = predicted_ents & gt_ents
        stats["tp"] += len(common)
        stats["fp"] += len(predicted_ents - gt_ents)
        stats["fn"] += len(gt_ents - predicted_ents)

    precision = stats["tp"] / (stats["tp"] + stats["fp"]) if (stats["tp"] + stats["fp"]) > 0 else 0
    recall = stats["tp"] / (stats["tp"] + stats["fn"]) if (stats["tp"] + stats["fn"]) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    print(f"\nResults over {limit} resumes:")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1-score:  {f1:.4f}")
    print(f"True Positives:  {stats['tp']}")
    print(f"False Positives: {stats['fp']}")
    print(f"False Negatives: {stats['fn']}")

if __name__ == "__main__":
    evaluate_model()
