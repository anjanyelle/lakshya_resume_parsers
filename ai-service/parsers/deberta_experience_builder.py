#!/usr/bin/env python3
"""
DeBERTa Experience Builder - Converts DeBERTa NER entities into structured work experiences.

This module takes the raw entities extracted by the trained DeBERTa model and groups them
into structured work experience entries with proper company-role-date associations.
"""

import logging
from typing import Dict, List, Any
from collections import defaultdict
import re

logger = logging.getLogger(__name__)


class DeBERTaExperienceBuilder:
    """
    Builds structured work experience entries from DeBERTa NER entities.
    
    The DeBERTa model extracts:
    - COMPANY: Company names
    - ROLE: Job titles
    - DATE_START: Start dates
    - DATE_END: End dates
    - LOCATION: Work locations
    - CLIENT: Client names (for consulting roles)
    
    This class groups these entities into complete work experience entries.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def build_experiences_from_entities(self, entities: Dict[str, List[str]], text: str) -> List[Dict[str, Any]]:
        """
        Build structured work experiences from DeBERTa extracted entities.
        
        Strategy: Use COMPANY names as anchors. Each company = one experience.
        Match roles, dates, and locations to the nearest company.
        
        Args:
            entities: Dictionary of entity types to lists of extracted values
                     e.g., {'COMPANY': ['Google', 'Amazon'], 'ROLE': ['Engineer', 'Developer']}
            text: Original text for context and ordering
            
        Returns:
            List of structured work experience dictionaries
        """
        companies = entities.get('COMPANY', []) or entities.get('companies', [])
        roles = entities.get('ROLE', []) or entities.get('job_titles', [])
        start_dates = entities.get('DATE_START', []) or []
        end_dates = entities.get('DATE_END', []) or []
        locations = entities.get('LOCATION', []) or entities.get('locations', [])
        clients = entities.get('CLIENT', []) or entities.get('clients', [])
        
        self.logger.info(f"📊 DeBERTa entities: {len(companies)} companies, {len(roles)} roles, {len(start_dates)} start dates, {len(end_dates)} end dates")
        
        # If no companies or roles found, return empty
        if not companies and not roles:
            self.logger.warning("No companies or roles found in DeBERTa entities")
            return []
        
        # Strategy: Use companies as anchors - each company is a separate experience
        experiences = self._build_experiences_by_company(
            text, companies, roles, start_dates, end_dates, locations, clients
        )
        
        self.logger.info(f"✅ Built {len(experiences)} work experiences from DeBERTa entities")
        return experiences
    
    def _build_experiences_by_company(self, text: str, companies: List[str], roles: List[str],
                                      start_dates: List[str], end_dates: List[str],
                                      locations: List[str], clients: List[str]) -> List[Dict[str, Any]]:
        """
        Build experiences using COMPANY names as anchors.
        Each company represents a separate work experience.
        
        Strategy:
        1. For each company, find its position in text
        2. Find the closest role, dates, and location AFTER that company
        3. Create one experience per company
        """
        experiences = []
        
        # Find positions of all entities
        company_positions = [(text.find(c), c) for c in companies if text.find(c) != -1]
        role_positions = [(text.find(r), r) for r in roles if text.find(r) != -1]
        start_date_positions = [(text.find(d), d) for d in start_dates if text.find(d) != -1]
        end_date_positions = [(text.find(d), d) for d in end_dates if text.find(d) != -1]
        location_positions = [(text.find(l), l) for l in locations if text.find(l) != -1]
        
        # Sort companies by position
        company_positions.sort(key=lambda x: x[0])
        
        self.logger.info(f"🏢 Found {len(company_positions)} companies in text at positions: {[pos for pos, _ in company_positions]}")
        
        # For each company, find the nearest entities
        for i, (company_pos, company_name) in enumerate(company_positions):
            # Define search window: from company position to next company (or end of text)
            window_start = company_pos
            window_end = company_positions[i + 1][0] if i + 1 < len(company_positions) else len(text)
            
            # Find entities within this window
            role = self._find_nearest_entity(role_positions, window_start, window_end)
            start_date = self._find_nearest_entity(start_date_positions, window_start, window_end)
            end_date = self._find_nearest_entity(end_date_positions, window_start, window_end)
            location = self._find_nearest_entity(location_positions, window_start, window_end)
            
            # Check if end date indicates current position
            is_current = False
            if end_date:
                end_date_lower = end_date.lower()
                if 'present' in end_date_lower or 'current' in end_date_lower:
                    is_current = True
                    end_date = None
            
            # Create experience
            exp = {
                'job_title': role or '',
                'company_name': company_name,
                'location': location or '',
                'start_date': self._parse_date(start_date) if start_date else None,
                'end_date': self._parse_date(end_date) if end_date and not is_current else None,
                'is_current': is_current,
                'clients': [],
                'description': ''
            }
            
            experiences.append(exp)
            self.logger.info(f"  ✓ Experience {i+1}: {role or 'No role'} at {company_name} ({start_date or 'No start'} - {end_date or 'Present' if is_current else 'No end'})")
        
        return experiences
    
    def _find_nearest_entity(self, entity_positions: List[tuple], window_start: int, window_end: int) -> str:
        """
        Find the nearest entity within the given window.
        
        Args:
            entity_positions: List of (position, value) tuples
            window_start: Start of search window
            window_end: End of search window
            
        Returns:
            Entity value if found within window, None otherwise
        """
        for pos, value in entity_positions:
            if window_start <= pos < window_end:
                return value
        return None
    
    
    def _parse_date(self, date_str: str) -> str:
        """Parse date string to ISO format."""
        if not date_str:
            return None
        
        try:
            import dateparser
            result = dateparser.parse(date_str, settings={'PREFER_DAY_OF_MONTH': 'first'})
            return result.date().isoformat() if result else None
        except:
            return None
