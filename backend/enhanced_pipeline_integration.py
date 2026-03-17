
# Integration code for main application
from enhanced_pipeline_integration import EnhancedResumePipeline

def parse_resume_enhanced(resume_text):
    """Parse resume using enhanced pipeline"""
    pipeline = EnhancedResumePipeline()
    return pipeline.parse_resume(resume_text)

# Example usage:
if __name__ == "__main__":
    with open("resume.txt", "r") as f:
        resume_text = f.read()
    
    result = parse_resume_enhanced(resume_text)
    print(json.dumps(result, indent=2))
