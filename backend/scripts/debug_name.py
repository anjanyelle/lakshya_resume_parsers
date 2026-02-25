import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.parser.contact_extractor import ContactExtractor
from app.services.parser.extract_text import extract_text

def test_name():
    pdf_path = Path('storage/resumes/default/00e7a215-52d6-4b85-bf9b-e8c076a0f2a0/8f3cb2a4-8f36-48d8-b971-5c5e68de0f61/original.pdf')
    text = extract_text(pdf_path).text
    extractor = ContactExtractor()
    
    print("--- RAW TEXT (TOP 20 LINES) ---")
    lines = [L.strip() for L in text.splitlines() if L.strip()]
    for L in lines[:20]:
        print(f"[{L}]")
        
    result = extractor.extract_name(text)
    print(f"\nExtracted Name: '{result.name}' (Confidence: {result.confidence})")
    
    test_val = "Spring Boot"
    is_prob = extractor._is_probable_name(test_val)
    print(f"Is '{test_val}' a probable name? {is_prob}")

if __name__ == "__main__":
    test_name()
