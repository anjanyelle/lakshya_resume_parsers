import json
import spacy
from spacy.tokens import DocBin
from tqdm import tqdm
import os

def convert_to_spacy(json_file, output_path):
    nlp = spacy.blank("en")
    db = DocBin()
    
    # Load dataset. Note: This specific dataset is often a list of JSON objects per line
    with open(json_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for line in tqdm(lines, desc="Converting JSON to DocBin"):
        try:
            data = json.loads(line)
            text = data["content"]
            entities = []
            
            if data["annotation"]:
                for ann in data["annotation"]:
                    # Extraction and label formatting
                    points = ann["points"][0]
                    start = points["start"]
                    end = points["end"] + 1 # SpaCy end offset is exclusive
                    label = ann["label"][0]
                    entities.append((start, end, label))
            
            doc = nlp.make_doc(text)
            ents = []
            seen_tokens = set()
            
            # Sort entries by start offset
            entities.sort(key=lambda x: x[0])
            
            for start, end, label in entities:
                span = doc.char_span(start, end, label=label, alignment_mode="contract")
                if span is None:
                    continue
                
                # Simple check for overlapping spans
                overlap = False
                for i in range(span.start, span.end):
                    if i in seen_tokens:
                        overlap = True
                        break
                
                if not overlap:
                    ents.append(span)
                    for i in range(span.start, span.end):
                        seen_tokens.add(i)
            
            doc.ents = ents
            db.add(doc)
        except Exception as e:
            print(f"Error processing line: {e}")

    db.to_disk(output_path)
    print(f"Saved {len(db)} documents to {output_path}")

if __name__ == "__main__":
    input_file = r"c:\Lalataksha V Company\Main-branch\Lakshya-LLM-Resume-Parser\data\ResumeNER\Entity Recognition in Resumes.json"
    output_file = r"c:\Lalataksha V Company\Main-branch\Lakshya-LLM-Resume-Parser\data\ResumeNER\train.spacy"
    
    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))
        
    convert_to_spacy(input_file, output_file)
