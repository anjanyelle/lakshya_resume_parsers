import os
import json
from pathlib import Path
from datetime import date
from app.services.parser.work_experience_parser import WorkExperienceParser
from app.services.parser.extract_text import extract_text

def test_new_schema():
    parser = WorkExperienceParser()
    resumes_dir = Path(r"C:\Lalataksha V Company\Main-branch\Lakshya-LLM-Resume-Parser\resumes")
    
    # Test with a few representative resumes
    test_files = [
        "01_Marcus_Chen_DevOps_Engineer.docx",
    ]
    
    results = []
    
    for filename in test_files:
        print(f"Testing {filename}...")
        file_path = resumes_dir / filename
        if not file_path.exists():
            print(f"File not found: {file_path}")
            continue
            
        try:
            # Pass Path object and access .text attribute
            extracted = extract_text(file_path)
            text = extracted.text
            # Mock person_id
            output = parser.parse_to_standardized_json(text, person_id="test_user_123")
            
            # Basic validation of the new schema
            if "work_history" not in output:
                 print(f"FAILED: 'work_history' key missing in output for {filename}")
                 continue
                 
            for entry in output["work_history"]:
                # Check for required fields
                required_fields = ["id", "person_id", "role", "company_or_client", "location", "start_date", "end_date", "currently_working", "description"]
                missing = [f for f in required_fields if f not in entry]
                if missing:
                    print(f"FAILED: Missing fields {missing} in entry for {filename}")
                
                # Check company_or_client structure
                if not isinstance(entry.get("company_or_client"), dict) or "name" not in entry["company_or_client"] or "is_client" not in entry["company_or_client"]:
                    print(f"FAILED: 'company_or_client' structure invalid for {filename}")
                
                # Check date formats (YYYY-MM-DD)
                for d_field in ["start_date", "end_date"]:
                    val = entry.get(d_field)
                    if val and not (isinstance(val, str) and len(val) == 10 and "-" in val):
                         # If it's "Present", it should be converted to current date string by the parser now
                         print(f"FAILED: Date field {d_field} format invalid: {val} for {filename}")

            results.append({"file": filename, "output": output})
            print(f"SUCCESS: {filename} parsed and validated.")
            
        except Exception as e:
            print(f"ERROR processing {filename}: {e}")
            import traceback
            traceback.print_exc()

    # Save results for review
    with open("tmp_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nTest results saved to tmp_test_results.json")

if __name__ == "__main__":
    test_new_schema()
