"""
Enhanced Certifications Parser - Filters Invalid Entries
Fixes certification parsing to remove incorrect entries and normalize valid ones
"""

import re
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from app.services.parser.utils.enhanced_dataset_loader import unified_loader

logger = logging.getLogger(__name__)

@dataclass
class EnhancedCertificationEntry:
    """Enhanced certification entry with validation"""
    name: str = ""
    issuing_organization: str = ""
    issue_date: str = ""
    expiry_date: str = ""
    credential_id: str = ""
    confidence: float = 0.0
    sources_used: List[str] = None
    
    def __post_init__(self):
        if self.sources_used is None:
            self.sources_used = []

class EnhancedCertificationsParser:
    """
    Enhanced certifications parser that:
    1. Filters out incorrect entries
    2. Validates against certification datasets
    3. Normalizes certification names
    4. Ensures clean certification extraction
    """
    
    def __init__(self):
        self.unified_loader = unified_loader
        
        # Load valid certifications from datasets
        self.valid_certifications = self._load_valid_certifications()
        
        # Compile validation patterns
        self._compile_validation_patterns()
        
        logger.info("Enhanced Certifications Parser initialized")
        logger.info(f"Loaded {len(self.valid_certifications)} valid certifications")
    
    def _load_valid_certifications(self) -> set:
        """Load valid certifications from unified datasets"""
        valid_certs = set()
        
        try:
            cert_data = self.unified_loader.get_unified_dataset('certifications')
            for cert in cert_data:
                # Check multiple possible name fields
                for field in ['name', 'certification', 'certificate']:
                    cert_name = cert.get(field, '')
                    if cert_name:
                        valid_certs.add(cert_name.lower().strip())
            
            logger.info(f"Loaded {len(valid_certs)} valid certifications from datasets")
        except Exception as e:
            logger.warning(f"Failed to load valid certifications: {e}")
        
        return valid_certs
    
    def _compile_validation_patterns(self):
        """Compile patterns to validate certifications"""
        
        # Invalid certification patterns (too long, sentences, etc.)
        self.invalid_patterns = [
            r'^.{60,}$',  # Too long
            r'^[a-z]',    # Starts with lowercase (likely sentence)
            r'\s+[a-z]\s+[a-z]\s+[a-z]',  # Contains sentence pattern
            r'[.!?]$',      # Ends with sentence punctuation
            r'\b(?:and|the|or|but|with|for|in|on|at|to|of|from|by|was|were|is|are)\s+[a-z]',  # Contains sentence words
        ]
        
        # Valid certification indicators
        self.valid_indicators = [
            r'\b(?:certified|certification|certificate)\b',
            r'\b(?:licensed|license)\b',
            r'\b(?:aws|azure|gcp|google|microsoft|oracle|salesforce)\b',
            r'\b(?:pmp|csm|csa|cisa|cissp)\b',
            r'\b(?:professional|technical|associate|senior|junior)\s+(?:certified|certification)\b',
        ]
        
        # Compile regex patterns
        self.compiled_invalid_patterns = []
        for pattern in self.invalid_patterns:
            try:
                self.compiled_invalid_patterns.append(re.compile(pattern, re.IGNORECASE))
            except Exception as e:
                logger.warning(f"Failed to compile invalid pattern: {pattern} - {e}")
        
        self.compiled_valid_indicators = []
        for pattern in self.valid_indicators:
            try:
                self.compiled_valid_indicators.append(re.compile(pattern, re.IGNORECASE))
            except Exception as e:
                logger.warning(f"Failed to compile valid pattern: {pattern} - {e}")
    
    def is_valid_certification(self, cert_text: str) -> bool:
        """Check if certification text is valid"""
        if not cert_text:
            return False
        
        cert_text = cert_text.strip()
        
        # Check against invalid patterns
        for pattern in self.compiled_invalid_patterns:
            if pattern.search(cert_text):
                return False
        
        # Check if it's too short
        if len(cert_text) < 3:
            return False
        
        # Check if it's just numbers/symbols
        if re.match(r'^[\d\s\-\.]+$', cert_text):
            return False
        
        # Check against valid certifications dataset
        cert_lower = cert_text.lower()
        if cert_lower in self.valid_certifications:
            return True
        
        # Check partial matches
        for valid_cert in self.valid_certifications:
            if cert_lower in valid_cert or valid_cert in cert_lower:
                return True
        
        # Check for valid indicators
        for pattern in self.compiled_valid_indicators:
            if pattern.search(cert_text):
                return True
        
        # Check for common certification keywords
        cert_keywords = [
            'certified', 'certificate', 'certification', 'licensed', 'license',
            'aws certified', 'azure certified', 'google certified',
            'pmp', 'csm', 'cisa', 'cissp', 'cfa', 'cpa',
            'salesforce certified', 'oracle certified',
            'microsoft certified', 'cisco certified',
            'comptia', 'isc2', 'pmi'
        ]
        
        return any(keyword in cert_lower for keyword in cert_keywords)
    
    def normalize_certification(self, cert_text: str) -> str:
        """Normalize certification name using unified datasets"""
        if not cert_text:
            return cert_text
        
        # Try exact match in datasets
        lookup = self.unified_loader.lookup_certification(cert_text)
        if lookup:
            for field in ['name', 'certification']:
                if lookup.get(field):
                    return lookup[field]
        
        # Apply basic normalization
        normalized = cert_text.strip()
        
        # Capitalize properly (title case for certifications)
        normalized = ' '.join(word.capitalize() for word in normalized.split())
        
        # Common certification normalizations
        cert_mappings = {
            'aws certified solutions architect': 'AWS Certified Solutions Architect',
            'aws certified developer': 'AWS Certified Developer',
            'azure certified': 'Microsoft Azure Certified',
            'google certified': 'Google Cloud Certified',
            'pmp': 'Project Management Professional (PMP)',
            'csm': 'Certified ScrumMaster (CSM)',
            'cisa': 'Certified Information Systems Auditor (CISA)',
            'cissp': 'Certified Information Systems Security Professional (CISSP)',
            'cfa': 'Chartered Financial Analyst (CFA)',
            'cpa': 'Certified Public Accountant (CPA)',
        }
        
        # Apply mappings
        for cert, full in cert_mappings.items():
            if normalized.lower() == cert.lower():
                normalized = full
                break
            elif f' {cert.lower()} ' in f' {normalized.lower()} ':
                normalized = re.sub(rf'\b{cert}\b', full, normalized, flags=re.IGNORECASE)
                break
        
        return normalized
    
    def extract_certifications_from_text(self, text: str) -> List[EnhancedCertificationEntry]:
        """Extract certifications from raw text"""
        if not text:
            return []
        
        # Split by common separators
        separators = [',', ';', '|', '•', '·', '\n']
        
        # Replace all separators with comma for consistent splitting
        normalized_text = text
        for sep in separators:
            normalized_text = normalized_text.replace(sep, ',')
        
        # Split and clean
        raw_certs = [cert.strip() for cert in normalized_text.split(',') if cert.strip()]
        
        enhanced_certs = []
        for raw_cert in raw_certs:
            if self.is_valid_certification(raw_cert):
                normalized = self.normalize_certification(raw_cert)
                
                cert_entry = EnhancedCertificationEntry()
                cert_entry.name = normalized
                cert_entry.sources_used = ['enhanced_parser']
                cert_entry.confidence = 0.8 if normalized.lower() in self.valid_certifications else 0.6
                
                enhanced_certs.append(cert_entry)
                logger.debug(f"Extracted valid certification: {normalized}")
            else:
                logger.debug(f"Filtered invalid certification: {raw_cert}")
        
        return enhanced_certs
    
    def enhance_existing_certifications(self, existing_certs: List[Dict]) -> List[EnhancedCertificationEntry]:
        """Enhance existing certifications with validation and normalization"""
        enhanced_certs = []
        
        for cert_dict in existing_certs:
            if not isinstance(cert_dict, dict):
                continue
            
            # Get certification name from multiple possible fields
            cert_name = (cert_dict.get('name') or 
                        cert_dict.get('certification') or 
                        cert_dict.get('certificate') or '')
            
            if not cert_name:
                continue
            
            # Validate and normalize
            if self.is_valid_certification(cert_name):
                normalized = self.normalize_certification(cert_name)
                
                cert_entry = EnhancedCertificationEntry()
                cert_entry.name = normalized
                cert_entry.issuing_organization = cert_dict.get('issuing_organization') or cert_dict.get('issuer', '')
                cert_entry.issue_date = cert_dict.get('issue_date') or cert_dict.get('issueDate', '')
                cert_entry.expiry_date = cert_dict.get('expiry_date') or cert_dict.get('expiryDate', '')
                cert_entry.credential_id = cert_dict.get('credential_id') or cert_dict.get('credentialId', '')
                cert_entry.confidence = cert_dict.get('confidence', 0.7)
                cert_entry.sources_used = ['enhanced_parser', 'existing']
                
                enhanced_certs.append(cert_entry)
            else:
                logger.debug(f"Filtered invalid certification: {cert_name}")
        
        return enhanced_certs
    
    def parse_certifications_section(self, certifications_data: Any) -> List[EnhancedCertificationEntry]:
        """
        Main parsing method for certifications section
        Handles both raw text and structured data
        """
        logger.info("Starting enhanced certifications parsing")
        
        enhanced_certs = []
        
        if isinstance(certifications_data, str):
            # Raw text parsing
            enhanced_certs = self.extract_certifications_from_text(certifications_data)
            
        elif isinstance(certifications_data, list):
            # Structured data enhancement
            enhanced_certs = self.enhance_existing_certifications(certifications_data)
            
        elif isinstance(certifications_data, dict):
            # Handle dict with content field
            content = certifications_data.get('content', '')
            if content:
                enhanced_certs = self.extract_certifications_from_text(content)
        
        # Remove duplicates and sort by confidence
        unique_certs = {}
        for cert in enhanced_certs:
            key = cert.name.lower()
            if key not in unique_certs or cert.confidence > unique_certs[key].confidence:
                unique_certs[key] = cert
        
        final_certs = list(unique_certs.values())
        final_certs.sort(key=lambda x: x.confidence, reverse=True)
        
        logger.info(f"Enhanced certifications parsing complete: {len(final_certs)} valid certifications")
        return final_certs
    
    def convert_to_standard_format(self, enhanced_certs: List[EnhancedCertificationEntry]) -> List[Dict[str, Any]]:
        """Convert enhanced certifications to standard JSON format"""
        standard_certs = []
        
        for cert in enhanced_certs:
            standard_cert = {
                "name": cert.name,
                "issuing_organization": cert.issuing_organization,
                "confidence": cert.confidence
            }
            
            # Add optional fields only if present
            if cert.issue_date:
                standard_cert["issue_date"] = cert.issue_date
            if cert.expiry_date:
                standard_cert["expiry_date"] = cert.expiry_date
            if cert.credential_id:
                standard_cert["credential_id"] = cert.credential_id
            
            standard_certs.append(standard_cert)
        
        return standard_certs

# Global instance
enhanced_certifications_parser = EnhancedCertificationsParser()
