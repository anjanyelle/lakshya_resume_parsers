
def extract_work_client_format(self, text):
    """Extract work experience from client-based format"""
    work_entries = []
    
    # Split by CLIENT: pattern
    client_sections = re.split(r'CLIENT:', text)
    
    for section in client_sections[1:]:  # Skip first empty section
        lines = section.strip().split('\n')
        if len(lines) >= 3:
            # Extract company, location, role, date
            company = lines[0].strip() if lines[0].strip() else "Unknown"
            
            # Look for Location line
            location = ""
            role = ""
            date_range = ""
            
            for i, line in enumerate(lines):
                if 'Location:' in line:
                    location = line.replace('Location:', '').strip()
                elif 'ROLE:' in line:
                    role_line = line.replace('ROLE:', '').strip()
                    # Extract date from role line
                    role_parts = role_line.split()
                    if len(role_parts) >= 2:
                        date_range = ' '.join(role_parts[-2:])  # Last 2 parts are usually date
                        role = ' '.join(role_parts[:-2])  # Everything before date
                    else:
                        role = role_line
                elif 'Responsibilities:' in line:
                    # Start of responsibilities, everything before this is header
                    break
            
            if company and role:
                work_entries.append({
                    "company": company,
                    "title": role,
                    "location": location,
                    "date_range": date_range,
                    "description": ""
                })
    
    return work_entries

def extract_education_simple(self, text):
    """Extract education from simple format"""
    education_entries = []
    
    # Look for education patterns
    edu_patterns = [
        r'(Bachelor|Master|PhD|B\.Tech|M\.Tech|B\.S\.|M\.S\.)\s*([A-Za-z\s]+)\s*([A-Za-z0-9\s,]*\d{4}\s*[-–]?\s*\d{4})',
        r'([A-Za-z\s&]+(?:University|Institute|College|School))\s*[-–]?\s*([A-Za-z\s]+(?:Bachelor|Master|PhD|B\.S\.|M\.S\.|B\.Tech|M\.Tech|B\.E\.|M\.E\.)[A-Za-z\s]*)\s*([A-Za-z]+\s*\d{4}\s*[-–]?\s*[A-Za-z]*\s*\d{4}|\d{4}\s*[-–]?\s*\d{4})'
    ]
    
    for pattern in edu_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            if len(match) >= 3:
                if match[0] in ['Bachelor', 'Master', 'PhD', 'B.Tech', 'M.Tech', 'B.S.', 'M.S.']:
                    degree = match[0] + ' ' + match[1]
                    institution = "Unknown"
                    date_range = match[2]
                else:
                    institution = match[0]
                    degree = match[1]
                    date_range = match[2] if len(match) > 2 else ""
                
                education_entries.append({
                    "institution": institution,
                    "degree": degree,
                    "location": "",
                    "date_range": date_range,
                    "description": ""
                })
    
    return education_entries

def extract_certifications_simple(self, text):
    """Extract certifications from simple format"""
    cert_entries = []
    
    # Look for certification section
    cert_section_match = re.search(r'Certifications\s*:(.*?)(?=\n\n|\n[A-Z][A-Z]|$)', text, re.IGNORECASE | re.DOTALL)
    
    if cert_section_match:
        cert_text = cert_section_match.group(1)
        
        # Look for certification patterns
        cert_patterns = [
            r'(AWS|Azure|Google|Microsoft|Oracle|Cisco|CompTIA|PMP|Scrum|ITIL)\s+([A-Za-z0-9\s]+)\s*[-–]?\s*(\d{4}[-–]?\d{4})',
            r'([A-Za-z0-9\s]+(?:Certified|Certificate|Certification))\s*(?:of|in)?\s*([A-Za-z0-9\s&]+)',
        ]
        
        for pattern in cert_patterns:
            matches = re.findall(pattern, cert_text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if isinstance(match, tuple):
                    if len(match) == 3:
                        cert_name = f"{match[0]} {match[1]} {match[2]}"
                    else:
                        cert_name = f"{match[0]} {match[1]}"
                else:
                    cert_name = match
                
                cert_entries.append({
                    "name": cert_name.strip(),
                    "issuer": "",
                    "date": "",
                    "description": ""
                })
    
    return cert_entries
