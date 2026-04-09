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
        
        # Strategy: Match entities by their position in the text
        experiences = self._match_entities_by_position(
            text, companies, roles, start_dates, end_dates, locations, clients
        )
        
        self.logger.info(f"✅ Built {len(experiences)} work experiences from DeBERTa entities")
        return experiences
    
    def _match_entities_by_position(self, text: str, companies: List[str], roles: List[str],
                                    start_dates: List[str], end_dates: List[str],
                                    locations: List[str], clients: List[str]) -> List[Dict[str, Any]]:
        """
        Match entities by their position in the text to group them into experiences.
        
        Strategy:
        1. Find position of each entity in text
        2. Group entities that appear close together (within 200 chars)
        3. Create one experience per group
        """
        # Find positions of all entities
        entity_positions = []
        
        for company in companies:
            pos = text.find(company)
            if pos != -1:
                entity_positions.append({
                    'type': 'company',
                    'value': company,
                    'position': pos
                })
        
        for role in roles:
            pos = text.find(role)
            if pos != -1:
                entity_positions.append({
                    'type': 'role',
                    'value': role,
                    'position': pos
                })
        
        for date in start_dates:
            pos = text.find(date)
            if pos != -1:
                entity_positions.append({
                    'type': 'start_date',
                    'value': date,
                    'position': pos
                })
        
        for date in end_dates:
            pos = text.find(date)
            if pos != -1:
                entity_positions.append({
                    'type': 'end_date',
                    'value': date,
                    'position': pos
                })
        
        for location in locations:
            pos = text.find(location)
            if pos != -1:
                entity_positions.append({
                    'type': 'location',
                    'value': location,
                    'position': pos
                })
        
        # Sort by position
        entity_positions.sort(key=lambda x: x['position'])
        
        # Group entities that are close together (within 300 chars = one job block)
        groups = []
        current_group = []
        last_position = -1
        
        for entity in entity_positions:
            if last_position == -1 or (entity['position'] - last_position) < 300:
                current_group.append(entity)
                last_position = entity['position']
            else:
                if current_group:
                    groups.append(current_group)
                current_group = [entity]
                last_position = entity['position']
        
        if current_group:
            groups.append(current_group)
        
        # Build experiences from groups
        experiences = []
        for group in groups:
            exp = self._build_experience_from_group(group)
            if exp:
                experiences.append(exp)
        
        return experiences
    
    def _build_experience_from_group(self, group: List[Dict]) -> Dict[str, Any]:
        """Build a single experience from a group of entities."""
        exp = {
            'job_title': '',
            'company_name': '',
            'location': '',
            'start_date': None,
            'end_date': None,
            'is_current': False,
            'clients': [],
            'description': ''
        }
        
        for entity in group:
            if entity['type'] == 'company' and not exp['company_name']:
                exp['company_name'] = entity['value']
            elif entity['type'] == 'role' and not exp['job_title']:
                exp['job_title'] = entity['value']
            elif entity['type'] == 'start_date' and not exp['start_date']:
                exp['start_date'] = self._parse_date(entity['value'])
            elif entity['type'] == 'end_date' and not exp['end_date']:
                end_date_str = entity['value'].lower()
                if 'present' in end_date_str or 'current' in end_date_str:
                    exp['is_current'] = True
                    exp['end_date'] = None
                else:
                    exp['end_date'] = self._parse_date(entity['value'])
            elif entity['type'] == 'location' and not exp['location']:
                exp['location'] = entity['value']
        
        # Only return if we have at least a company or role
        if exp['company_name'] or exp['job_title']:
            return exp
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
