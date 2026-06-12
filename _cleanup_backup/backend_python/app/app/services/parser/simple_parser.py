#!/usr/bin/env python3
"""
Simple resume parser for development
"""
import re
from typing import Dict, Any

class SimpleResumeParser:
    """Basic resume parser that extracts key information"""
    
    def parse(self, content: str) -> Dict[str, Any]:
        """Parse resume content and extract basic information"""
        lines = content.split('\n')
        content_lower = content.lower()
        
        result = {
            'full_name': self._extract_name(content),
            'email': self._extract_email(content),
            'phone': self._extract_phone(content),
            'summary': self._extract_summary(content),
            'skills': self._extract_skills(content),
            'experience': self._extract_experience(content),
            'education': self._extract_education(content)
        }
        
        return result
    
    def _extract_name(self, content: str) -> str:
        """Extract candidate name from resume"""
        lines = content.split('\n')
        
        # Look for name at the beginning (common pattern)
        for i, line in enumerate(lines[:5]):  # Check first 5 lines
            line = line.strip()
            if line and len(line) < 50 and not any(char in line for char in '@.()'):
                # Skip lines that look like contact info or headers
                if not re.search(r'\d', line) and '@' not in line and 'www' not in line.lower():
                    return line
        
        return ""
    
    def _extract_email(self, content: str) -> str:
        """Extract email address"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, content)
        return match.group(0) if match else ""
    
    def _extract_phone(self, content: str) -> str:
        """Extract phone number"""
        # Various phone number patterns
        patterns = [
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',  # 123-456-7890, 123.456.7890, 123 456 7890
            r'\b\(\d{3}\)\s?\d{3}[-.\s]?\d{4}\b',  # (123) 456-7890
            r'\b\d{10}\b'  # 1234567890
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(0)
        
        return ""
    
    def _extract_summary(self, content: str) -> str:
        """Extract summary/objective section"""
        lines = content.split('\n')
        summary_lines = []
        capturing = False
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Look for summary section headers
            if any(keyword in line_lower for keyword in ['summary', 'objective', 'profile', 'about']):
                capturing = True
                continue
            
            # Stop capturing at next section
            if capturing and any(keyword in line_lower for keyword in 
                              ['experience', 'education', 'skills', 'employment', 'work']):
                break
            
            if capturing and line.strip():
                summary_lines.append(line.strip())
        
        return ' '.join(summary_lines[:3])  # First 3 lines of summary
    
    def _extract_skills(self, content: str) -> list:
        """Extract skills from resume"""
        # Common technical skills
        common_skills = [
            'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'html', 'css',
            'aws', 'docker', 'kubernetes', 'git', 'linux', 'mongodb', 'postgresql',
            'machine learning', 'data analysis', 'project management', 'agile'
        ]
        
        found_skills = []
        content_lower = content.lower()
        
        for skill in common_skills:
            if skill in content_lower:
                found_skills.append(skill.title())
        
        return found_skills[:10]  # Limit to 10 skills
    
    def _extract_experience(self, content: str) -> list:
        """Extract work experience"""
        lines = content.split('\n')
        experience = []
        current_exp = {}
        capturing = False
        
        for line in lines:
            line_stripped = line.strip()
            line_lower = line_stripped.lower()
            
            # Look for experience section
            if any(keyword in line_lower for keyword in ['experience', 'employment', 'work']):
                capturing = True
                continue
            
            # Stop at next section
            if capturing and any(keyword in line_lower for keyword in 
                              ['education', 'skills', 'summary', 'objective']):
                break
            
            if capturing and line_stripped:
                # Simple heuristic: if line contains years or looks like a job title
                if re.search(r'\d{4}', line_stripped) or any(word in line_lower for word in 
                    ['manager', 'developer', 'engineer', 'analyst', 'director', 'senior', 'junior']):
                    if current_exp:
                        experience.append(current_exp)
                    current_exp = {'title': line_stripped}
                elif current_exp and 'company' not in current_exp:
                    current_exp['company'] = line_stripped
        
        if current_exp:
            experience.append(current_exp)
        
        return experience[:5]  # Limit to 5 experiences
    
    def _extract_education(self, content: str) -> list:
        """Extract education information"""
        lines = content.split('\n')
        education = []
        current_edu = {}
        capturing = False
        
        for line in lines:
            line_stripped = line.strip()
            line_lower = line_stripped.lower()
            
            # Look for education section
            if any(keyword in line_lower for keyword in ['education', 'academic', 'university', 'college']):
                capturing = True
                continue
            
            # Stop at next section
            if capturing and any(keyword in line_lower for keyword in 
                              ['experience', 'skills', 'summary', 'objective']):
                break
            
            if capturing and line_stripped:
                # Look for degree patterns
                if any(degree in line_lower for degree in 
                      ['bachelor', 'master', 'phd', 'degree', 'diploma']):
                    if current_edu:
                        education.append(current_edu)
                    current_edu = {'degree': line_stripped}
                elif current_edu and 'school' not in current_edu:
                    current_edu['school'] = line_stripped
        
        if current_edu:
            education.append(current_edu)
        
        return education[:3]  # Limit to 3 education entries
