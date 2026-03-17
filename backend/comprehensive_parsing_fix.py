
# Quick fix for comprehensive resume parsing
def extract_work_comprehensive(self, text):
    """Enhanced work extraction for comprehensive resumes"""
    work_entries = []
    
    # Pattern for company - title - location - date format
    pattern = r'^([A-Za-z0-9\s&]+(?:AI|Research|Microsoft|Facebook|IBM|Stanford|Google))\s*-\s*([A-Za-z0-9\s,]+)\n([A-Za-z0-9\s,|]+)\s*\|\s*([A-Za-z0-9\s,]+)\s*\|\s*([A-Za-z0-9\s,]+)'
    
    matches = re.findall(pattern, text, re.MULTILINE)
    for match in matches:
        if len(match) >= 5:
            company = match[0].strip()
            title = match[1].strip()
            location = match[2].strip()
            date_range = match[4].strip()
            
            work_entries.append({
                "company": company,
                "title": title,
                "location": location,
                "date_range": date_range,
                "description": ""
            })
    
    return work_entries

def extract_education_comprehensive(self, text):
    """Enhanced education extraction for comprehensive resumes"""
    education_entries = []
    
    # Pattern for university - degree - location - date format
    pattern = r'^([A-Za-z\s&]+(?:University|Institute|College|School))\s*-\s*([A-Za-z\s]+(?:Bachelor|Master|PhD|B\.S\.|M\.S\.|B\.Tech|M\.Tech|B\.E\.|M\.E\.)[A-Za-z\s]*)\n([A-Za-z\s,]+)\s*\|\s*([A-Za-z0-9\s,]+)'
    
    matches = re.findall(pattern, text, re.MULTILINE)
    for match in matches:
        if len(match) >= 4:
            institution = match[0].strip()
            degree = match[1].strip()
            location = match[2].strip()
            date_range = match[3].strip()
            
            education_entries.append({
                "institution": institution,
                "degree": degree,
                "location": location,
                "date_range": date_range,
                "description": ""
            })
    
    return education_entries
