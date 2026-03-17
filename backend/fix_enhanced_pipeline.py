#!/usr/bin/env python3
"""
Fix Enhanced Pipeline - Complete JSON Structure Issues
"""

import re
from typing import Dict, List, Any

class FixedEnhancedPipeline:
    """Fixed Enhanced Pipeline with proper extraction logic"""
    
    def _convert_work_to_enhanced_fixed(self, work_entries_raw) -> List[Dict[str, Any]]:
        """FIXED: Convert JobEntry objects to Enhanced JSON format"""
        enhanced_work = []
        
        try:
            for entry in work_entries_raw:
                # FIXED: Better company extraction
                company = getattr(entry, 'company', '') or ''
                if not company:
                    # Try to extract company from description or other fields
                    description = getattr(entry, 'description', '') or ''
                    if description:
                        # Look for company patterns in description
                        company_patterns = [
                            r'([A-Z][a-z\s&]+(?:Group|Corporation|Inc|LLC|Ltd|Co|Tech|Global|Health|Financial|Retail|Telecom|Energy|Services))',
                            r'([A-Z][a-zA-Z\s]+)\s*(?:January|February|March|April|May|June|July|August|September|October|November|December)',
                        ]
                        for pattern in company_patterns:
                            match = re.search(pattern, description)
                            if match:
                                company = match.group(1).strip()
                                break
                
                # Create date_range from start_date/end_date
                date_range = ""
                if hasattr(entry, 'start_date') and entry.start_date:
                    start_str = entry.start_date.strftime("%B %Y") if entry.start_date else ""
                    end_str = "Current" if (hasattr(entry, 'is_current') and entry.is_current) else ""
                    if hasattr(entry, 'end_date') and entry.end_date:
                        end_str = entry.end_date.strftime("%B %Y")
                    date_range = f"{start_str} - {end_str}" if start_str and end_str else start_str
                
                # Create description from bullets and description
                description = ""
                if hasattr(entry, 'description') and entry.description:
                    description = entry.description
                if hasattr(entry, 'bullets') and entry.bullets:
                    bullet_text = " ".join([f"• {bullet}" for bullet in entry.bullets])
                    description = f"{description} {bullet_text}".strip()
                
                enhanced_work.append({
                    "title": getattr(entry, 'title', '') or '',
                    "company": company,  # FIXED: Better company extraction
                    "date_range": date_range,
                    "location": getattr(entry, 'location', '') or '',
                    "description": description
                })
        except Exception as e:
            print(f"  ❌ Error converting work entries: {e}")
        
        return enhanced_work
    
    def _convert_education_to_enhanced_fixed(self, education_entries_raw) -> List[Dict[str, Any]]:
        """FIXED: Convert education objects to Enhanced JSON format"""
        enhanced_edu = []
        
        try:
            # FIXED: Handle case where education_entries_raw is empty or malformed
            if not education_entries_raw:
                return enhanced_edu
                
            for entry in education_entries_raw:
                if hasattr(entry, 'institution') and entry.institution:
                    enhanced_edu.append({
                        "degree": getattr(entry, 'degree', '') or '',
                        "university": getattr(entry, 'institution', '') or '',
                        "location": getattr(entry, 'location', '') or '',
                        "date": getattr(entry, 'graduation_year', '') or '',
                        "confidence": getattr(entry, 'confidence', 0.8)
                    })
                elif isinstance(entry, dict):
                    # FIXED: Handle dict entries
                    enhanced_edu.append({
                        "degree": entry.get('degree', ''),
                        "university": entry.get('institution', entry.get('university', '')),
                        "location": entry.get('location', ''),
                        "date": entry.get('graduation_year', entry.get('date', '')),
                        "confidence": entry.get('confidence', 0.8)
                    })
        except Exception as e:
            print(f"  ❌ Error converting education entries: {e}")
        
        return enhanced_edu
    
    def _convert_contact_to_enhanced_fixed(self, contact_raw) -> Dict[str, Any]:
        """FIXED: Convert contact to Enhanced JSON format"""
        basics = {
            "name": "",
            "email": "",
            "phone": "",
            "location": ""
        }
        
        try:
            if hasattr(contact_raw, 'name') and contact_raw.name:
                # FIXED: Better name validation
                name = contact_raw.name.strip()
                # Filter out common header texts that are mistakenly captured as names
                if not any(header in name.upper() for header in [
                    'PROFESSIONAL SUMMARY', 'SUMMARY', 'PROFILE', 'OBJECTIVE', 
                    'ABOUT', 'EXPERIENCE', 'EDUCATION', 'SKILLS'
                ]):
                    basics["name"] = name
            if hasattr(contact_raw, 'email') and contact_raw.email:
                basics["email"] = contact_raw.email
            if hasattr(contact_raw, 'phone') and contact_raw.phone:
                basics["phone"] = contact_raw.phone
            if hasattr(contact_raw, 'location') and contact_raw.location:
                # FIXED: Better location validation
                location = contact_raw.location.strip()
                # Filter out skill texts that are mistakenly captured as locations
                if not any(skill in location.upper() for skill in [
                    'PROFICIENCY', 'SKILL', 'EXPERTISE', 'KNOWLEDGE', 'ANGULAR', 'HTML'
                ]):
                    basics["location"] = location
        except Exception as e:
            print(f"  ❌ Error converting contact: {e}")
            
        return basics
    
    def _extract_education_fixed(self, text: str) -> List[Dict[str, Any]]:
        """FIXED: Extract education using multiple patterns"""
        education_entries = []
        
        # Pattern 1: Standard format - "University - Degree Date"
        pattern1 = r'([A-Z][a-z\s]+(?:University|College|Institute|Institute of Technology))\s*[-–]\s*([A-Za-z\s]+(?:Bachelor|Master|PhD|B\.Tech|M\.Tech|B\.S\.|M\.S\.))[^,]*,\s*([A-Za-z]+\s+\d{4}\s*[–-]\s*[A-Za-z]+\s+\d{4})'
        
        # Pattern 2: Pavan's format - "University - Degree Month Year to Month Year"
        pattern2 = r'([A-Z][a-z\s]+(?:University|College|Institute))\s*[-–]\s*([A-Za-z\s]+(?:Bachelor|Master|PhD|B\.Tech|M\.Tech|B\.S\.|M\.S\.)[^,]*)\s*([A-Za-z]+\s+\d{4}\s*to\s*[A-Za-z]+\s+\d{4})'
        
        # Pattern 3: Simple format - "Degree from University (Year)"
        pattern3 = r'([A-Za-z\s]+(?:Bachelor|Master|PhD|B\.Tech|M\.Tech|B\.S\.|M\.S\.))[^,]*from\s+([A-Z][a-z\s]+(?:University|College|Institute))\s*\(([A-Za-z]+\s+\d{4})\)'
        
        for pattern in [pattern1, pattern2, pattern3]:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                if len(groups) >= 3:
                    education_entries.append({
                        "degree": groups[1].strip(),
                        "university": groups[0].strip(),
                        "date": groups[2].strip(),
                        "location": "",
                        "confidence": 0.9
                    })
        
        return education_entries

# Test the fixes
if __name__ == "__main__":
    pipeline = FixedEnhancedPipeline()
    print("✅ Fixed Enhanced Pipeline loaded")
