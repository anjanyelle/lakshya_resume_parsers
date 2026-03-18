import os
import glob
import torch
from pathlib import Path
from transformers import LayoutLMConfig, LayoutLMForTokenClassification, LayoutLMTokenizer
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset

class DocBankDataset(Dataset):
    def __init__(self, txt_files, tokenizer, label_map, max_seq_length=512):
        self.txt_files = txt_files
        self.tokenizer = tokenizer
        self.label_map = label_map
        self.max_seq_length = max_seq_length

    def __len__(self):
        return len(self.txt_files)

    def __getitem__(self, idx):
        path = self.txt_files[idx]
        words = []
        boxes = []
        labels = []
        
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) < 10: continue
                word = parts[0]
                # DocBank uses [x1, y1, x2, y2]
                # LayoutLM expects normalized [x1, y1, x2, y2] in range [0, 1000]
                box = [int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])]
                label = parts[9]
                
                words.append(word)
                boxes.append(box)
                labels.append(self.label_map.get(label, 0))

        # Simple truncation/padding for a stub/demo
        encoding = self.tokenizer(
            words,
            boxes=boxes,
            truncation=True,
            padding="max_length",
            max_length=self.max_seq_length,
            is_split_into_words=True,
            return_tensors="pt"
        )
        
        if "bbox" not in encoding:
            # Fallback or debug
            print(f"DEBUG: Encoding keys: {encoding.keys()}")
            # If bbox is missing, LayoutLM will fail. 
            # Often it's because normalized boxes are needed or version issues.
            # We'll normalize to [0, 1000] if needed.
            validated_boxes = []
            for b in boxes:
                # Clamp to 0-1000
                validated_boxes.append([max(0, min(1000, x)) for x in b])
            encoding = self.tokenizer(
                words,
                boxes=validated_boxes,
                truncation=True,
                padding="max_length",
                max_length=self.max_seq_length,
                is_split_into_words=True,
                return_tensors="pt"
            )

        return {
            "input_ids": encoding["input_ids"].flatten(),
            "attention_mask": encoding["attention_mask"].flatten(),
            "bbox": encoding["bbox"].squeeze(0),
            "labels": torch.tensor([0] * self.max_seq_length) # Placeholder for labels
        }

def train():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Load DocBank samples
    base_dir = Path("data/extracted/DocBank/DocBank-master/DocBank_samples/DocBank_samples")
    txt_files = list(base_dir.glob("*.txt"))
    
    label_list = ["abstract", "author", "caption", "date", "equation", "figure", "footer", "list", "paragraph", "reference", "section", "table", "title"]
    label_map = {label: i for i, label in enumerate(label_list)}

    tokenizer = LayoutLMTokenizer.from_pretrained("microsoft/layoutlm-base-uncased")
    dataset = DocBankDataset(txt_files, tokenizer, label_map)
    dataloader = DataLoader(dataset, batch_size=2, shuffle=True)

    config = LayoutLMConfig.from_pretrained("microsoft/layoutlm-base-uncased", num_labels=len(label_list))
    model = LayoutLMForTokenClassification.from_pretrained("microsoft/layoutlm-base-uncased", config=config)
    model.to(device)

    optimizer = AdamW(model.parameters(), lr=5e-5)

    print("Starting LayoutLM fine-tuning (demo)...")
    model.train()
    for epoch in range(1): # Low for demo
        for i, batch in enumerate(dataloader):
            input_ids = batch["input_ids"].to(device)
            bbox = batch["bbox"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            outputs = model(input_ids=input_ids, bbox=bbox, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
            
            if i % 10 == 0:
                print(f"Step {i}, Loss: {loss.item()}")
            
            if i > 50: break # Truncate for demo

    output_dir = Path("backend/models/layoutlm_robust_model")
    output_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    print(f"LayoutLM model saved to {output_dir}")

if __name__ == "__main__":
    train()
