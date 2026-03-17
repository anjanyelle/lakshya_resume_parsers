
def extract_certifications_enhanced(resume_text):
    """Extract certifications with enhanced patterns"""
    patterns = [
        r'(AWS Certified Solutions Architect|AWS Certified Developer Associate)',
        r'(Microsoft Certified Expert|Microsoft Certified Azure)',
        r'(Google Cloud Professional|Google Associate Cloud Engineer)',
        r'(Oracle Certified Professional|Oracle Certified Associate)',
        r'(CISSP|Certified Information Systems Security Professional)',
        r'(PMP|Project Management Professional)',
        r'(Certified Scrum Master|CSM)',
        r'(Certified Kubernetes Administrator|CKA)',
        r'(Red Hat Certified Engineer|RHCE)',
        r'(Docker Certified Associate)',
    ]
    
    certifications = []
    for pattern in patterns:
        matches = re.finditer(pattern, resume_text, re.IGNORECASE)
        for match in matches:
            cert = {
                'name': match.group(0).strip(),
            }
            certifications.append(cert)
    return certifications
