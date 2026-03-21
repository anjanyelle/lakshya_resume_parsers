import csv
import sys
from pathlib import Path

def clean_csv(file_path, header_name):
    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {file_path}")
        return

    items = set()
    try:
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                if not row:
                    continue
                # Some rows might have multiple items joined by ", " or " , " or even raw quotes
                line = row[0]
                # Split by various delimiters that might have been introduced during messy merging
                parts = []
                if '", "' in line:
                    parts = line.split('", "')
                elif '", "' in line:
                    parts = line.split('", "')
                else:
                    parts = [line]
                
                for p in parts:
                    cleaned = p.strip(' " \t\n\r')
                    if cleaned and cleaned.lower() != header_name.lower():
                        items.add(cleaned)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    sorted_items = sorted(list(items), key=lambda x: x.lower())
    
    try:
        with open(path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([header_name])
            for item in sorted_items:
                writer.writerow([item])
        print(f"Successfully cleaned {file_path}. Total items: {len(sorted_items)}")
    except Exception as e:
        print(f"Error writing {file_path}: {e}")

if __name__ == "__main__":
    base_dir = Path(r"c:\Lalataksha V Company\Main-branch\Lakshya-LLM-Resume-Parser\backend\data")
    clean_csv(base_dir / "global_companies.csv", "companies")
    clean_csv(base_dir / "global_job_titles.csv", "job_titles")
