
def parse_client_based_format(resume_text):
    """Parse CLIENT: ROLE: format resumes"""
    patterns = [
        r'CLIENT:\\s*([^\\n]+)\\s*\\nROLE:\\s*([A-Za-z\\s]+?)\\s+([A-Za-z]+\\s+\\d{4})\\s*-\\s*([A-Za-z]+\\s+\\d{4}|Present)',
        r'CLIENT:\\s*([^\\n]+)\\s*\\nROLE:\\s*([A-Za-z\\s]+)\\s*\\n([A-Za-z]+\\s+\\d{4})\\s*-\\s*([A-Za-z]+\\s+\\d{4}|Present)',
        r'CLIENT:\\s*([^\\n]+)\\s*\\nROLE:\\s*([A-Za-z\\s]+?)\\s+([A-Za-z]+\\s+\\d{4})\\s*-\\s*Current',
        r'CLIENT:\\s*([^\\n]+)\\s*\\nROLE:\\s*([A-Za-z\\s]+)',
    ]
    
    jobs = []
    for pattern in patterns:
        matches = re.finditer(pattern, resume_text, re.MULTILINE | re.IGNORECASE)
        for match in matches:
            groups = match.groups()
            if len(groups) >= 2:
                job = {
                    'company': groups[0].strip(),
                    'title': groups[1].strip(),
                }
                if len(groups) >= 4:
                    job['start_date'] = groups[2].strip()
                    job['end_date'] = groups[3].strip()
                elif len(groups) >= 3:
                    job['start_date'] = groups[2].strip()
                    job['end_date'] = 'Present'
                jobs.append(job)
    return jobs
