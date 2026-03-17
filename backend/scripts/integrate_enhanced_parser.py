#!/usr/bin/env python3
"""
Integrate Enhanced Work Experience Parser into Main System
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def integrate_enhanced_parser():
    """Integrate enhanced parser into main work experience parser"""
    
    print("🔧 Integrating Enhanced Work Experience Parser")
    print("=" * 60)
    
    # Path to main parser file
    main_parser_path = Path("app/services/parser/work_experience_parser.py")
    enhanced_parser_path = Path("app/services/parser/work_experience_enhanced.py")
    
    if not main_parser_path.exists():
        print(f"❌ Main parser not found: {main_parser_path}")
        return False
    
    if not enhanced_parser_path.exists():
        print(f"❌ Enhanced parser not found: {enhanced_parser_path}")
        return False
    
    # Read the main parser
    with open(main_parser_path, 'r') as f:
        main_content = f.read()
    
    # Check if already integrated
    if "EnhancedWorkExperienceParser" in main_content:
        print("✅ Enhanced parser already integrated")
        return True
    
    # Add import for enhanced parser
    import_line = "from app.services.parser.work_experience_enhanced import EnhancedWorkExperienceParser\n"
    
    # Find where to insert the import (after other imports)
    lines = main_content.split('\n')
    insert_index = 0
    for i, line in enumerate(lines):
        if line.startswith('from app.services.parser') and i > 0:
            insert_index = i + 1
            break
    
    # Insert import
    lines.insert(insert_index, import_line.rstrip())
    
    # Add enhanced parser method to WorkExperienceParser class
    enhanced_method = '''
    def parse_experience_section_enhanced(self, text: str) -> list[JobEntry]:
        """Enhanced parsing with 100% format coverage"""
        try:
            # Use enhanced parser
            enhanced_parser = EnhancedWorkExperienceParser()
            return enhanced_parser.parse_experience_section_enhanced(text)
        except Exception as e:
            print(f"Enhanced parser failed, falling back to original: {e}")
            # Fall back to original parsing
            return self.parse_experience_section(text)
'''
    
    # Find the end of the WorkExperienceParser class
    class_end_index = -1
    brace_count = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('class WorkExperienceParser'):
            brace_count = line.count('{') - line.count('}')
        elif brace_count > 0:
            brace_count += line.count('{') - line.count('}')
            if brace_count == 0:
                class_end_index = i
                break
    
    if class_end_index > 0:
        # Insert enhanced method before the class ends
        lines.insert(class_end_index, enhanced_method)
    else:
        print("❌ Could not find WorkExperienceParser class end")
        return False
    
    # Write the updated file
    with open(main_parser_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print("✅ Enhanced parser integrated successfully")
    return True

def integrate_company_standardizer():
    """Integrate company standardizer into main parser"""
    
    print("\n🏢 Integrating Company Standardizer")
    print("-" * 40)
    
    # Path to main parser file
    main_parser_path = Path("app/services/parser/work_experience_parser.py")
    
    # Read the main parser
    with open(main_parser_path, 'r') as f:
        main_content = f.read()
    
    # Check if already integrated
    if "CompanyStandardizer" in main_content:
        print("✅ Company standardizer already integrated")
        return True
    
    # Add import for company standardizer
    import_line = "from app.services.parser.company_standardizer import CompanyStandardizer\n"
    
    # Find where to insert the import
    lines = main_content.split('\n')
    insert_index = 0
    for i, line in enumerate(lines):
        if line.startswith('from app.services.parser') and i > 0:
            insert_index = i + 1
            break
    
    # Insert import
    lines.insert(insert_index, import_line.rstrip())
    
    # Add company standardizer to WorkExperienceParser __init__
    init_method_found = False
    for i, line in enumerate(lines):
        if 'def __init__(self' in line:
            init_method_found = True
            # Find the end of __init__ method
            for j in range(i + 1, len(lines)):
                if lines[j].strip() and not lines[j].startswith(' ') and not lines[j].startswith('\t'):
                    # Insert company standardizer initialization before this line
                    lines.insert(j, "        self.company_standardizer = CompanyStandardizer()")
                    break
            break
    
    if not init_method_found:
        print("❌ Could not find __init__ method in WorkExperienceParser")
        return False
    
    # Write the updated file
    with open(main_parser_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print("✅ Company standardizer integrated successfully")
    return True

def update_pipeline_to_use_enhanced():
    """Update pipeline to use enhanced parser"""
    
    print("\n🔄 Updating Pipeline to Use Enhanced Parser")
    print("-" * 40)
    
    # Path to pipeline file
    pipeline_path = Path("app/workers/pipeline.py")
    
    if not pipeline_path.exists():
        print("❌ Pipeline file not found")
        return False
    
    # Read the pipeline file
    with open(pipeline_path, 'r') as f:
        pipeline_content = f.read()
    
    # Check if already updated
    if "parse_experience_section_enhanced" in pipeline_content:
        print("✅ Pipeline already updated")
        return True
    
    # Find and replace the parsing call
    lines = pipeline_content.split('\n')
    updated = False
    
    for i, line in enumerate(lines):
        if 'work_experience_parser.parse_experience_section(' in line:
            # Replace with enhanced version
            lines[i] = line.replace('parse_experience_section(', 'parse_experience_section_enhanced(')
            updated = True
            break
    
    if not updated:
        print("❌ Could not find work experience parsing call in pipeline")
        return False
    
    # Write the updated file
    with open(pipeline_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print("✅ Pipeline updated successfully")
    return True

def main():
    """Main integration function"""
    
    print("🚀 Integrating Enhanced Work Experience Parser")
    print("=" * 60)
    
    # Change to backend directory
    os.chdir(Path(__file__).resolve().parent)
    
    success = True
    
    # Integrate enhanced parser
    if not integrate_enhanced_parser():
        success = False
    
    # Integrate company standardizer
    if not integrate_company_standardizer():
        success = False
    
    # Update pipeline
    if not update_pipeline_to_use_enhanced():
        success = False
    
    if success:
        print("\n🎉 Integration completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Run: python tests/test_enhanced_coverage.py")
        print("2. Test with your resume formats")
        print("3. Check UI output for correct mapping")
    else:
        print("\n❌ Integration failed. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
