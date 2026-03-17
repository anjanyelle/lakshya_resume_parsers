
def extract_education_enhanced(resume_text):
    """Extract education with enhanced patterns"""
    patterns = [
        r'(Bachelor of Technology|B\.Tech|BTech).*?in\\s*([A-Za-z\\s]+)',
        r'(Bachelor of Engineering|B\.E|BE).*?in\\s*([A-Za-z\\s]+)',
        r'(Bachelor of Science|B\.Sc|BSc).*?in\\s*([A-Za-z\\s]+)',
        r'(Master of Technology|M\.Tech|MTech).*?in\\s*([A-Za-z\\s]+)',
        r'(Master of Business Administration|MBA)',
        r'(Ph\.D|PhD|Doctor of Philosophy).*?in\\s*([A-Za-z\\s]+)',
        r'([A-Za-z\\s]+University)',
        r'(IIT|IIM|NIT|BITS|VIT|Anna|Osmania|JNTU|Pune)\\s+([A-Za-z\\s]+)',
        r'(\\d{4})\\s*-\\s*(\\d{4})',
    ]
    
    education = []
    for pattern in patterns:
        matches = re.finditer(pattern, resume_text, re.IGNORECASE)
        for match in matches:
            groups = match.groups()
            if 'Bachelor' in pattern or 'Master' in pattern or 'Ph.D' in pattern:
                edu = {
                    'degree': groups[0].strip(),
                    'field': groups[1].strip() if len(groups) > 1 else '',
                }
                education.append(edu)
    return education
