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
            # Define search windows
            prev_company_pos = company_positions[i - 1][0] if i > 0 else 0
            next_company_pos = company_positions[i + 1][0] if i + 1 < len(company_positions) else len(text)
            
            # Smart role detection - handle multiple formats:
            # Format 1: "Job Title\nCompany Name\nDates" (most common)
            # Format 2: "Company Name\nJob Title\nDates"
            # Format 3: "Job Title - Company Name" (same line)
            
            # Search BEFORE company (within 200 chars)
            role_search_start = max(prev_company_pos, company_pos - 200)
            role_before = self._find_nearest_entity_before(role_positions, role_search_start, company_pos)
            
            # Search AFTER company (within 200 chars)
            role_search_end = min(next_company_pos, company_pos + 200)
            role_after = self._find_nearest_entity(role_positions, company_pos, role_search_end)
            
            # Determine which role to use based on proximity
            role = self._choose_best_role(role_before, role_after, company_pos, role_positions, text)
            
            # Search for dates and location AFTER the company
            start_date = self._find_nearest_entity(start_date_positions, company_pos, next_company_pos)
            end_date = self._find_nearest_entity(end_date_positions, company_pos, next_company_pos)
            location = self._find_nearest_entity(location_positions, company_pos, next_company_pos)
            
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
    
    def _find_nearest_entity_before(self, entity_positions: List[tuple], window_start: int, window_end: int) -> str:
        """
        Find the nearest entity BEFORE the window_end position (for job titles before company).
        
        Args:
            entity_positions: List of (position, value) tuples
            window_start: Start of search window
            window_end: End of search window (typically company position)
            
        Returns:
            Entity value if found within window, None otherwise
        """
        # Find all entities in the window, return the one closest to window_end
        candidates = [(pos, value) for pos, value in entity_positions if window_start <= pos < window_end]
        if candidates:
            # Sort by position descending (closest to company first)
            candidates.sort(key=lambda x: x[0], reverse=True)
            return candidates[0][1]
        return None
    
    def _choose_best_role(self, role_before: str, role_after: str, company_pos: int, 
                         role_positions: List[tuple], text: str) -> str:
        """
        Intelligently choose the best role based on resume format detection.
        
        Handles multiple formats:
        - Format 1: "Job Title\nCompany Name\nDates" (role before company)
        - Format 2: "Company Name\nJob Title\nDates" (role after company)
        - Format 3: "Job Title - Company Name" (same line)
        
        Args:
            role_before: Role found before company (if any)
            role_after: Role found after company (if any)
            company_pos: Position of company in text
            role_positions: All role positions for distance calculation
            text: Full text for context analysis
            
        Returns:
            Best matching role or empty string
        """
        # If only one exists, use it
        if role_before and not role_after:
            return role_before
        if role_after and not role_before:
            return role_after
        if not role_before and not role_after:
            return ''
        
        # Both exist - need to determine which is correct
        # Strategy: Check which one is closer and analyze the text structure
        
        # Find positions
        role_before_pos = None
        role_after_pos = None
        for pos, value in role_positions:
            if value == role_before and pos < company_pos:
                role_before_pos = pos
            if value == role_after and pos > company_pos:
                role_after_pos = pos
                break
        
        # Calculate distances
        dist_before = company_pos - role_before_pos if role_before_pos is not None else float('inf')
        dist_after = role_after_pos - company_pos if role_after_pos is not None else float('inf')
        
        # Prefer the closer one, but with some heuristics:
        # 1. If role is within 100 chars before company, likely Format 1 (most common)
        # 2. If role is within 50 chars after company, likely Format 2
        # 3. If distances are similar, prefer before (more common format)
        
        if dist_before <= 100:
            # Very close before - likely correct (Format 1)
            return role_before
        elif dist_after <= 50:
            # Very close after - likely Format 2
            return role_after
        elif dist_before < dist_after:
            # Closer before
            return role_before
        else:
            # Closer after or equal - prefer before for tie-breaking
            return role_before if dist_before == dist_after else role_after
    
    
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
