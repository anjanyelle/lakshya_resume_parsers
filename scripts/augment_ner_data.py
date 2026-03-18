import json
import random
import argparse
from pathlib import Path

def apply_ocr_noise(text, noise_level=0.05):
    """Apply OCR-like noise to text without changing its length to preserve indices."""
    confusion_map = {
        '0': 'O', 'O': '0',
        '1': 'l', 'l': '1', 'I': 'l',
        'S': '5', '5': 'S',
        'B': '8', '8': 'B',
        'm': 'rn',  # This changes length! I'll avoid it for now or handle it.
    }
    
    # Simple character swaps that preserve length
    chars = list(text)
    for i in range(len(chars)):
        if random.random() < noise_level:
            c = chars[i]
            if c in confusion_map and len(confusion_map[c]) == 1:
                chars[i] = confusion_map[c]
            elif c.isalpha() and random.random() < 0.5:
                # Case swap
                chars[i] = c.swapcase()
            elif random.random() < 0.1:
                # Random char swap
                chars[i] = random.choice("!@#$%^&*()")
                
    return "".join(chars)

def main():
    parser = argparse.ArgumentParser(description="Augment NER JSONL data with OCR noise")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--noise-level", type=float, default=0.03)
    args = parser.parse_args()

    augmented_records = []
    with open(args.input, "r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            # Original
            augmented_records.append(record)
            
            # Augmented copy
            new_record = record.copy()
            text = record.get("content") or record.get("text")
            field_name = "content" if "content" in record else "text"
            
            if text:
                new_record[field_name] = apply_ocr_noise(text, args.noise_level)
                augmented_records.append(new_record)

    with open(args.output, "w", encoding="utf-8") as f:
        for r in augmented_records:
            json.dump(r, f, ensure_ascii=False)
            f.write("\n")

    print(f"Augmented {len(augmented_records)//2} records. Total: {len(augmented_records)}")

if __name__ == "__main__":
    main()
