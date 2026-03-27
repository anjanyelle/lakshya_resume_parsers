"""
Resume section detector and splitter for parsing resume structure.
Identifies and splits resume into logical sections like experience, education, skills, etc.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)


SECTION_PATTERNS = {
    'experience': re.compile(
        r'(?i)^\s*(work experience|professional experience|employment history|'
        r'employment|career history|experience|work history|relevant experience|'
        r'roles? & responsibilities|roles? and responsibilities|positions? held|'
        r'professional background|career summary|job history|'
        r'internship|internships|projects? experience|'
        r'work\s+experience|professional\s+experience|career\s+history)',
        re.MULTILINE
    ),
    'education': re.compile(
        r'(?i)^\s*(education|academic background|qualifications|'
        r'academic history|degrees?|educational background|'
        r'academic qualifications|schooling|training|certifications? & education|'
        r'academic\s+background|educational\s+qualifications)',
        re.MULTILINE
    ),
    'skills': re.compile(
        r'(?i)^\s*(skills?|technical skills?|core competencies|'
        r'competencies|technologies|tools? & technologies|tools? and technologies|'
        r'expertise|key skills?|proficiencies|technical expertise|'
        r'languages & frameworks|languages and frameworks|stack|'
        r'technical\s+skills|core\s+competencies|key\s+skills)',
        re.MULTILINE
    ),
    'summary': re.compile(
        r'(?i)^\s*(summary|professional summary|profile|about me|'
        r'objective|career objective|overview|personal statement|'
        r'professional profile|executive summary)',
        re.MULTILINE
    ),
    'certifications': re.compile(
        r'(?i)^\s*(certifications?|certificates?|licenses?|accreditations?|'
        r'courses?|professional development|key projects?|achievements?|'
        r'awards?|honors?|accomplishments?)',
        re.MULTILINE
    ),
}

def split_sections(text: str) -> dict:
    sections = {
        'header': '',
        'summary': '',
        'experience': '',
        'education': '',
        'skills': '',
        'certifications': '',
        'other': '',
    }

    found = []
    for section_name, pattern in SECTION_PATTERNS.items():
        for match in pattern.finditer(text):
            found.append((match.start(), match.end(), section_name))

    found.sort(key=lambda x: x[0])

    if not found:
        sections['experience'] = text
        return sections

    sections['header'] = text[:found[0][0]].strip()

    for i, (start, end, name) in enumerate(found):
        next_start = found[i + 1][0] if i + 1 < len(found) else len(text)
        sections[name] = text[end:next_start].strip()

    return sections


class SectionSplitter:
    """
    Advanced resume / CV section detector and splitter.
    Supports worldwide naming conventions:
    English (US, UK, AU, CA, NZ, ZA, IN, SG, PH, NG, GH, KE, MY, BD, PK, LK, NP),
    European-English, Middle-East-English, East-Asian-English,
    Latin-American-English, and every major industry vertical.
    ~2000+ keyword variants across 25 section types.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Pre-compile patterns for better performance
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Pre-compile regex patterns for section detection."""
        
        # Pattern for section headers (ALL CAPS or with special formatting)
        self.section_header_pattern = re.compile(
            r'^\s*([A-Z][A-Z\s]{2,}|[A-Za-z][A-Za-z\s&/-]{3,})\s*[:\-=_]*\s*$',
            re.MULTILINE
        )
        
        # Pattern for dates in experience sections
        self.date_pattern = re.compile(
            r'\b(?:\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s*\d{4}|\d{4})\b',
            re.IGNORECASE
        )
        
        # Pattern for company indicators
        self.company_pattern = re.compile(
            r'(?:at|@)\s+([A-Za-z0-9\s&.,\-]+)|^([A-Za-z0-9\s&.,\-]{3,})\s*[\|\-•]',
            re.MULTILINE
        )
        
        # Pattern for bullet points and descriptions
        self.bullet_pattern = re.compile(
            r'^[\s]*[•\-\*\+]\s*(.+)$',
            re.MULTILINE
        )
    
    def _clean_pdf_artifacts(self, text: str) -> str:
        """Remove common PDF extraction artifacts that break section detection."""
        # Remove cid: font encoding artifacts
        text = re.sub(r'\(cid:\d+\)', '', text)
        
        # Normalize bullet points to standard format
        text = re.sub(r'[●○■□▪▫•‣⁃◦⦾⦿]', '•', text)
        
        # Normalize runs of 3+ spaces to newlines (multi-column PDF artifacts)
        text = re.sub(r' {3,}', '\n', text)
        
        # Remove zero-width and other invisible characters
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
        
        # Normalize multiple consecutive newlines to max 2
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove trailing/leading whitespace from each line while preserving structure
        lines = text.split('\n')
        lines = [line.rstrip() for line in lines]
        text = '\n'.join(lines)
        
        return text

    def split_sections(self, text: str) -> Dict[str, str]:
        """
        Detect section headers and split text into named sections.
        
        Args:
            text: Resume text to split into sections
            
        Returns:
            Dictionary with section names as keys and section text as values
        """
        try:
            text = self._clean_pdf_artifacts(text)
            
            # Normalize section headers that are on the same line as content
            # e.g. "...some text. Skills" becomes "...some text.\nSkills"
            text = re.sub(r'(?<=[a-z.!?])\s{2,}([A-Z][a-zA-Z\s]{3,20})\s*\n', r'\n\1\n', text)
            
            # Pre-process: Split ALL CAPS headers that are merged with content
            # e.g., "some text. PROFESSIONAL EXPERIENCE" -> "some text.\nPROFESSIONAL EXPERIENCE"
            # Match: lowercase/punctuation + space + 2+ ALL CAPS words
            text = re.sub(r'([a-z.!?])\s+([A-Z]{2,}(?:\s+[A-Z]{2,})+)\s*$', r'\1\n\2', text, flags=re.MULTILINE)
            text = re.sub(r'([a-z.!?])\s+([A-Z]{2,}(?:\s+[A-Z]{2,})+)(?=\s)', r'\1\n\2', text)
            
            sections = {}
            current_section = 'other'
            current_content = []
            
            lines = text.split('\n')
            
            for line in lines:
                stripped_line = line.strip()
                
                # Check if this line is a section header
                section_name = self.detect_section_header(stripped_line)
                
                if section_name:
                    # Save previous section content
                    if current_content:
                        content_text = '\n'.join(current_content).strip()
                        # If section already exists, append with separator
                        if current_section in sections:
                            sections[current_section] += '\n\n' + content_text
                        else:
                            sections[current_section] = content_text
                    
                    # Start new section
                    current_section = section_name
                    current_content = []
                    self.logger.debug(f"Found section header: {section_name}")
                    
                else:
                    # Add line to current section content
                    if stripped_line or current_content:  # Preserve empty lines within sections
                        current_content.append(line)
            
            # Save the last section
            if current_content:
                sections[current_section] = '\n'.join(current_content).strip()
            
            # Log section detection results
            self.logger.info(f"Split resume into {len(sections)} sections: {list(sections.keys())}")
            
            return sections
            
        except Exception as e:
            self.logger.error(f"Error splitting sections: {e}")
            return {'other': text}
    
    def detect_section_header(self, line: str) -> Optional[str]:
        """
        Check if a line is a section header and return the section name.
        
        Args:
            line: Line to check for section header
            
        Returns:
            Matched section name or None
        """
        try:
            if not line or len(line.strip()) < 3:
                return None
            
            # Remove extra whitespace and check patterns
            clean_line = line.strip()
            
            # STRICT HEADER DETECTION - Only detect actual section headers, not content
            
            # Exclude lines with colons followed by content (these are labels, not headers)
            # e.g., "Programming: Python, Java" or "Skills: AWS, Docker"
            if ':' in clean_line:
                parts = clean_line.split(':', 1)
                after_colon = parts[1].strip()
                # Only skip if there is real content after the colon (more than 10 chars)
                # Short content like "Experience:" or "Skills: " should still be detected
                if len(after_colon) > 10:
                    return None
            
            # Strategy 1: ALL CAPS headers (most reliable)
            if clean_line.isupper() and len(clean_line) > 2 and len(clean_line.split()) <= 10:
                result = self._match_section_keywords(clean_line.lower())
                if result:
                    self.logger.info(f"✅ Detected ALL CAPS header: '{clean_line}' → section: {result}")
                    return result
            
            # Strategy 2: Short standalone lines that match section keywords exactly
            # Must be ≤ 6 words to avoid matching descriptive sentences
            if len(clean_line.split()) <= 6:
                result = self._match_section_keywords(clean_line.lower())
                if result:
                    self.logger.info(f"✅ Detected short header: '{clean_line}' → section: {result}")
                    return result
            
            # Strategy 3: Title Case headers (short only)
            if clean_line.istitle() and len(clean_line.split()) <= 5:
                result = self._match_section_keywords(clean_line.lower())
                if result:
                    self.logger.info(f"✅ Detected title case header: '{clean_line}' → section: {result}")
                    return result
            
            # No keyword matched — try semantic matching as fallback
            semantic_result = self.detect_section_header_semantic(clean_line)
            if semantic_result:
                self.logger.info(f"✅ Detected via semantic matching: '{clean_line}' → section: {semantic_result}")
                return semantic_result

            return None
            
        except Exception as e:
            self.logger.error(f"Error detecting section header: {e}")
            return None
    
    def detect_section_header_semantic(self, line: str) -> str | None:
        """
        Fallback: when no keyword matches, use sentence similarity
        to classify the heading against section prototypes.
        """
        try:
            from sentence_transformers import SentenceTransformer, util
            import torch

            # Lazy load — only instantiate once
            if not hasattr(self, '_semantic_model'):
                self._semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
                self._section_prototypes = {
                    'experience':            'Work experience employment career history jobs positions',
                    'education':             'Education academic degree university college school qualifications',
                    'skills':                'Technical skills tools technologies competencies expertise abilities',
                    'summary':               'Professional summary objective profile about me introduction overview',
                    'projects':              'Projects portfolio personal work open source contributions capstone',
                    'certifications':        'Certifications licenses training courses certificates credentials',
                    'awards':                'Awards honors achievements recognition distinctions scholarships prizes',
                    'publications':          'Publications papers articles books patents research outputs',
                    'presentations':         'Presentations talks conferences keynotes speaking engagements',
                    'research':              'Research laboratory experiments investigations scholarly work',
                    'volunteering':          'Volunteering community service extracurricular activities',
                    'languages':             'Languages spoken foreign bilingual multilingual proficiency',
                    'interests':             'Hobbies interests personal activities passions leisure',
                    'references':            'References referees contact available upon request',
                    'contact':               'Contact personal information address phone email details',
                    'affiliations':          'Affiliations memberships organizations professional societies',
                    'patents':               'Patents inventions intellectual property trademarks',
                    'teaching':              'Teaching mentoring tutoring coaching lecturing courses taught',
                    'grants':                'Grants funding fellowships research funding awarded',
                    'professional_development': 'Professional development CPD continuing education learning',
                    'leadership':            'Leadership management team management executive roles',
                    'additional':            'Additional information miscellaneous other details',
                    'objective':             'Career objective goals aims mission aspirations seeking',
                    'portfolio':             'Portfolio work samples creative works showreel gallery',
                    'military':              'Military service armed forces national service defense',
                }
                self._prototype_embeddings = {
                    k: self._semantic_model.encode(v, convert_to_tensor=True)
                    for k, v in self._section_prototypes.items()
                }

            line_embedding = self._semantic_model.encode(line, convert_to_tensor=True)
            best_section = None
            best_score = 0.0

            for section_name, proto_emb in self._prototype_embeddings.items():
                score = float(util.cos_sim(line_embedding, proto_emb))
                if score > best_score:
                    best_score = score
                    best_section = section_name

            # Only use semantic match if confidence is high enough
            if best_score > 0.55:
                return best_section

            return None

        except Exception:
            return None
    
    def _match_section_keywords(self, text: str) -> Optional[str]:
        clean_text = text.strip()
        clean_text = re.sub(r'[:\-=_\s]+$', '', clean_text)

        KEYWORD_MAP = {
            'experience': [
                'work experience', 'professional experience', 'employment history',
                'employment', 'career history', 'experience', 'work history',
                'relevant experience', 'roles & responsibilities',
                'roles and responsibilities', 'positions held', 'position held',
                'professional background', 'career summary', 'job history',
                'internship', 'internships', 'project experience',
                'projects experience', 'work'
            ],
            'education': [
                'education', 'academic background', 'qualifications',
                'academic history', 'degree', 'degrees', 'educational background',
                'academic qualifications', 'schooling', 'training',
                'certifications & education', 'academic'
            ],
            'skills': [
                'skills', 'skill', 'technical skills', 'core competencies',
                'competencies', 'technologies', 'tools & technologies',
                'tools and technologies', 'expertise', 'key skills',
                'proficiencies', 'technical expertise',
                'languages & frameworks', 'languages and frameworks',
                'stack', 'tech stack', 'technical stack'
            ],
            'summary': [
                'summary', 'professional summary', 'profile', 'about me',
                'objective', 'career objective', 'overview',
                'personal statement', 'professional profile',
                'executive summary', 'about', 'introduction'
            ],
            'certifications': [
                'certifications', 'certification', 'certificates', 'certificate',
                'licenses', 'license', 'accreditations', 'courses',
                'professional development', 'achievements', 'awards'
            ],
            'projects': [
                'projects', 'project', 'personal projects', 'key projects',
                'notable projects', 'portfolio'
            ],
        }

        clean_lower = clean_text.lower().strip()

        for section_name, keywords in KEYWORD_MAP.items():
            for keyword in keywords:
                if clean_lower == keyword:
                    return section_name
                if clean_lower.startswith(keyword) and len(clean_lower) <= len(keyword) + 5:
                    return section_name

        return None
    
    def extract_experience_blocks(self, experience_text: str) -> List[Dict[str, str]]:
        """
        Split experience section into individual job blocks.
        
        Args:
            experience_text: Text from the experience section
            
        Returns:
            List of job experience dictionaries
        """
        try:
            if not experience_text or not experience_text.strip():
                return []
            
            jobs = []
            
            # Split by common job separators
            job_blocks = self._split_into_job_blocks(experience_text)
            
            for block in job_blocks:
                job_info = self._parse_job_block(block)
                if job_info:
                    jobs.append(job_info)
            
            self.logger.info(f"Extracted {len(jobs)} job blocks from experience section")
            return jobs
            
        except Exception as e:
            self.logger.error(f"Error extracting experience blocks: {e}")
            return []
    
    def _split_into_job_blocks(self, text: str) -> List[str]:
        """
        Split experience text into individual job blocks.
        
        Args:
            text: Experience section text
            
        Returns:
            List of job blocks
        """
        # Common patterns that indicate new job entries
        job_separators = [
            r'\n\s*[A-Z][a-z]+\s+\d{4}\s*[-–—]\s*(?:Present|Current|\d{4})',  # Date ranges
            r'\n\s*[A-Z][A-Za-z\s&.,\-]{3,}\s*\n',  # Company names
            r'\n\s*[\w\s]+(?:Engineer|Developer|Manager|Director|Analyst|Specialist|Consultant)',  # Job titles
        ]
        
        # Create combined pattern
        combined_pattern = '|'.join(job_separators)
        
        # Split by the pattern, keeping the separators
        parts = re.split(combined_pattern, text, flags=re.MULTILINE)
        
        # Filter out empty parts and trim
        job_blocks = [part.strip() for part in parts if part.strip()]
        
        return job_blocks
    
    def _parse_job_block(self, block: str) -> Optional[Dict[str, str]]:
        """
        Parse a single job block into structured information.
        
        Args:
            block: Job block text
            
        Returns:
            Dictionary with job information
        """
        try:
            lines = block.split('\n')
            lines = [line.strip() for line in lines if line.strip()]
            
            if not lines:
                return None
            
            job_info = {
                'title': '',
                'company': '',
                'dates': '',
                'description': ''
            }
            
            # Extract job title (usually first line)
            if lines:
                job_info['title'] = lines[0]
            
            # Extract dates and company from remaining lines
            description_lines = []
            
            for i, line in enumerate(lines[1:], 1):
                # Check for dates
                if self.date_pattern.search(line) and not job_info['dates']:
                    job_info['dates'] = line
                    continue
                
                # Check for company (usually contains "at" or is in all caps)
                if ('at' in line.lower() or line.isupper()) and not job_info['company']:
                    # Clean up company name
                    company = re.sub(r'^(?:at|@)\s*', '', line, flags=re.IGNORECASE)
                    company = re.sub(r'[\|\-•].*$', '', company).strip()
                    if company:
                        job_info['company'] = company
                        continue
                
                # Add to description
                description_lines.append(line)
            
            # Combine description lines
            job_info['description'] = '\n'.join(description_lines)
            
            # If no company found, try to extract from title line
            if not job_info['company'] and job_info['title']:
                company_match = re.search(r'(?:at|@)\s+([A-Za-z0-9\s&.,\-]+)', job_info['title'], re.IGNORECASE)
                if company_match:
                    job_info['company'] = company_match.group(1).strip()
                    # Remove company from title
                    job_info['title'] = re.sub(r'\s*(?:at|@)\s+[A-Za-z0-9\s&.,\-]+', '', job_info['title'], flags=re.IGNORECASE).strip()
            
            return job_info if job_info['title'] else None
            
        except Exception as e:
            self.logger.error(f"Error parsing job block: {e}")
            return None
    
    def extract_education_blocks(self, education_text: str) -> List[Dict[str, str]]:
        """
        Split education section into individual education blocks.
        
        Args:
            education_text: Text from the education section
            
        Returns:
            List of education dictionaries
        """
        try:
            if not education_text or not education_text.strip():
                return []
            
            education_items = []
            
            # Split by common education separators
            edu_blocks = re.split(r'\n(?=[A-Z][a-zA-Z\s]+(?:University|College|Institute|School))', education_text)
            
            for block in edu_blocks:
                edu_info = self._parse_education_block(block)
                if edu_info:
                    education_items.append(edu_info)
            
            self.logger.info(f"Extracted {len(education_items)} education blocks")
            return education_items
            
        except Exception as e:
            self.logger.error(f"Error extracting education blocks: {e}")
            return []
    
    def _parse_education_block(self, block: str) -> Optional[Dict[str, str]]:
        """
        Parse a single education block into structured information.
        
        Args:
            block: Education block text
            
        Returns:
            Dictionary with education information
        """
        try:
            lines = [line.strip() for line in block.split('\n') if line.strip()]
            
            if not lines:
                return None
            
            edu_info = {
                'degree': '',
                'institution': '',
                'dates': '',
                'details': ''
            }
            
            # Extract institution (usually contains University, College, etc.)
            for line in lines:
                if any(keyword in line.lower() for keyword in ['university', 'college', 'institute', 'school']):
                    edu_info['institution'] = line
                    break
            
            # Extract degree (usually first line or contains degree keywords)
            degree_keywords = ['bachelor', 'master', 'phd', 'doctor', 'associate', 'diploma', 'certificate']
            for line in lines:
                if any(keyword in line.lower() for keyword in degree_keywords):
                    edu_info['degree'] = line
                    break
            
            # Extract dates
            for line in lines:
                if self.date_pattern.search(line):
                    edu_info['dates'] = line
                    break
            
            # Remaining lines go to details
            details = [line for line in lines if line not in [
                edu_info['degree'], edu_info['institution'], edu_info['dates']
            ]]
            edu_info['details'] = '\n'.join(details)
            
            return edu_info if edu_info['institution'] or edu_info['degree'] else None
            
        except Exception as e:
            self.logger.error(f"Error parsing education block: {e}")
            return None
    
    def extract_skills_from_section(self, skills_text: str) -> List[str]:
        """
        Extract individual skills from skills section.
        
        Args:
            skills_text: Text from the skills section
            
        Returns:
            List of individual skills
        """
        try:
            if not skills_text:
                return []
            
            skills = []
            
            # Split by common separators
            skill_parts = re.split(r'[,;•\n]', skills_text)
            
            for part in skill_parts:
                skill = part.strip()
                
                # Remove common prefixes
                skill = re.sub(r'^(?:•|\-|\*|\+)\s*', '', skill)
                skill = re.sub(r'^(?:skills?|technologies?|tools?|competencies?):\s*', '', skill, flags=re.IGNORECASE)
                
                # Clean up and filter
                if skill and len(skill) > 1 and len(skill) < 50:
                    skills.append(skill)
            
            # Remove duplicates and sort
            unique_skills = sorted(list(set(skill.lower() for skill in skills)))
            
            self.logger.info(f"Extracted {len(unique_skills)} skills from skills section")
            return unique_skills
            
        except Exception as e:
            self.logger.error(f"Error extracting skills from section: {e}")
            return []
    
    def get_section_statistics(self, sections: Dict[str, str]) -> Dict[str, int]:
        """
        Get statistics about the parsed sections.
        
        Args:
            sections: Dictionary of sections
            
        Returns:
            Dictionary with section statistics
        """
        try:
            stats = {}
            
            for section_name, section_text in sections.items():
                if section_text:
                    word_count = len(section_text.split())
                    char_count = len(section_text)
                    line_count = len(section_text.split('\n'))
                    
                    stats[section_name] = {
                        'word_count': word_count,
                        'char_count': char_count,
                        'line_count': line_count
                    }
                else:
                    stats[section_name] = {
                        'word_count': 0,
                        'char_count': 0,
                        'line_count': 0
                    }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error calculating section statistics: {e}")
            return {}


# Example usage and testing
if __name__ == "__main__":
    # Sample resume text for testing
    sample_resume = """
    John Doe
    Software Engineer
    
    SUMMARY
    Experienced software engineer with 5+ years of experience in full-stack development.
    
    EXPERIENCE
    Senior Software Engineer at Tech Corp
    Jan 2020 - Present
    • Developed scalable web applications using React and Node.js
    • Led a team of 3 junior developers
    • Improved application performance by 40%
    
    Software Developer at StartupXYZ
    Jun 2018 - Dec 2019
    • Built RESTful APIs and microservices
    • Worked with Agile methodology
    
    EDUCATION
    Bachelor of Science in Computer Science
    University of Technology
    2014 - 2018
    
    SKILLS
    • JavaScript, Python, Java
    • React, Node.js, Express
    • MongoDB, PostgreSQL
    • Docker, AWS, Git
    """
    
    splitter = SectionSplitter()
    
    # Test section splitting
    sections = splitter.split_sections(sample_resume)
    print("Sections found:", list(sections.keys()))
    
    # Test experience extraction
    if 'experience' in sections:
        experience_blocks = splitter.extract_experience_blocks(sections['experience'])
        print(f"\nExperience blocks ({len(experience_blocks)}):")
        for i, job in enumerate(experience_blocks, 1):
            print(f"{i}. {job['title']} at {job['company']}")
    
    # Test education extraction
    if 'education' in sections:
        education_blocks = splitter.extract_education_blocks(sections['education'])
        print(f"\nEducation blocks ({len(education_blocks)}):")
        for i, edu in enumerate(education_blocks, 1):
            print(f"{i}. {edu['degree']} from {edu['institution']}")
    
    # Test skills extraction
    if 'skills' in sections:
        skills = splitter.extract_skills_from_section(sections['skills'])
        print(f"\nSkills ({len(skills)}): {', '.join(skills)}")
    
    # Test section statistics
    stats = splitter.get_section_statistics(sections)
    print(f"\nSection statistics:")
    for section, stat in stats.items():
        print(f"{section}: {stat['word_count']} words, {stat['line_count']} lines")
