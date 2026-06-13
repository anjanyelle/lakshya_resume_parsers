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
        
        # Common technology names that should NOT be treated as companies or roles
        self.tech_keywords = {
            # Mobile
            'android', 'ios', 'swift', 'kotlin', 'flutter', 'react native', 'react-native', 'xamarin',
            # Cloud & Infrastructure
            'aws', 'azure', 'gcp', 'google cloud', 'cloud', 'docker', 'kubernetes', 'k8s', 'ecs', 'eks',
            's3', 'ec2', 'lambda', 'amplify', 'firebase', 'firestore', 'supabase', 'heroku', 'netlify', 'vercel',
            # Databases
            'sql', 'mysql', 'postgresql', 'postgres', 'mongodb', 'redis', 'cassandra', 'dynamodb', 'snowflake',
            'sqlite', 'oracle', 'mssql', 'sql server', 'sqlserver', 'db2', 'neo4j',
            # Programming Languages
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust', 'scala',
            'php', 'perl', 'bash', 'powershell', 'html', 'css', 'sass', 'less',
            # Frameworks & Libraries
            'react', 'angular', 'vue', 'node', 'nodejs', 'express', 'django', 'flask', 'spring',
            'spring boot', 'springboot', 'hibernate', 'fastapi', 'nextjs', 'next.js', 'gatsby', 'nuxt',
            'svelte', 'laravel', 'symfony', 'rails', 'asp.net', 'dotnet', '.net', 'jquery', 'bootstrap',
            'tailwind', 'tailwindcss', 'material ui', 'mui',
            # ML/AI
            'tensorflow', 'pytorch', 'keras', 'pandas', 'numpy', 'spark', 'hadoop', 'nlp', 'llm',
            'langchain', 'huggingface', 'openai', 'scikit-learn',
            # Data Tools
            'tableau', 'power bi', 'looker', 'dbt', 'airflow', 'kafka', 'etl', 'elt',
            'apache', 'databricks', 'redshift', 'bigquery', 'olap',
            # DevOps & Tools
            'jenkins', 'gitlab', 'github', 'github actions', 'gitlab ci', 'jira', 'confluence', 'terraform', 'ansible',
            'git', 'ci/cd', 'cicd', 'maven', 'gradle', 'npm', 'yarn', 'pnpm', 'webpack', 'vite',
            # Testing
            'selenium', 'cypress', 'playwright', 'jest', 'mocha', 'junit', 'testng', 'nunit', 'pytest',
            # Other / Concepts
            'api', 'rest', 'graphql', 'microservices', 'agile', 'scrum', 'ml', 'ai',
            'data', 'analytics', 'bi', 'pipeline', 'workflow', 'automation',
            'pwa', 'progressive web app', 'spa', 'single page application',
            'jwt', 'oauth', 'oauth2', 'saml', 'sso', 'soap', 'restful', 'grpc',
            # Generic/Noise keywords that get misidentified
            'platform', 'system', 'framework', 'library', 'integration', 'authentication', 'authorization'
        }
    
    def build_experiences_from_entities(self, entities: Dict[str, List[str]], text: str) -> List[Dict[str, Any]]:
        """
        Build structured work experiences from DeBERTa extracted entities.
        
        Strategy: Use COMPANY names as anchors. Each company = one experience.
        Match roles, dates, and locations to the nearest company using position-based clustering.
        
        Args:
            entities: Dictionary of entity types to lists of extracted values
                     e.g., {'COMPANY': ['Google', 'Amazon'], 'ROLE': ['Engineer', 'Developer']}
                     Also includes '_positions': list of {type, text, start, end} for proximity grouping
            text: Original text for context and ordering
            
        Returns:
            List of structured work experience dictionaries
        """
        # Check if we have position data from the new extraction method
        positions_data = entities.get('_positions', [])
        
        if positions_data:
            # Use position-based clustering (NEW METHOD)
            self.logger.info(f"🎯 Using position-based entity clustering with {len(positions_data)} entities")
            experiences = self._build_experiences_by_position(positions_data, text)
        else:
            # Fallback to old method using text.find()
            self.logger.info("⚠️ No position data, using fallback text.find() method")
            companies = entities.get('COMPANY', []) or entities.get('companies', [])
            roles = entities.get('ROLE', []) or entities.get('job_titles', [])
            start_dates = entities.get('DATE_START', []) or entities.get('START_DATE', []) or []
            end_dates = entities.get('DATE_END', []) or entities.get('END_DATE', []) or []
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
    
    def _build_experiences_by_position(self, positions_data: List[Dict], text: str) -> List[Dict[str, Any]]:
        """
        Build experiences using position-based clustering (NEW METHOD).
        
        Groups entities by proximity - entities within ~150 characters of each other
        are considered part of the same job entry.
        
        Args:
            positions_data: List of {type, text, start, end} dictionaries
            text: Original text for context
            
        Returns:
            List of structured work experience dictionaries
        """
        # Separate entities by type with positions
        companies_raw = [e for e in positions_data if e['type'] == 'COMPANY']
        roles_raw = [e for e in positions_data if e['type'] == 'ROLE']
        locations = [e for e in positions_data if e['type'] == 'LOCATION']
        start_dates = [e for e in positions_data if e['type'] in ['START_DATE', 'DATE_START']]
        end_dates = [e for e in positions_data if e['type'] in ['END_DATE', 'DATE_END']]
        clients_raw = [e for e in positions_data if e['type'] == 'CLIENT']
        
        # Filter out technology keywords and generic descriptors from roles
        roles = []
        filtered_roles_count = 0
        for role in roles_raw:
            role_text = role['text'].lower().strip()
            
            # Check if it's an exact match with tech keywords
            if role_text in self.tech_keywords:
                filtered_roles_count += 1
                self.logger.debug(f"🔧 Filtered tech keyword from roles: '{role['text']}'")
                continue
                
            # Check if all words are tech keywords
            words = re.split(r'[\s/,\-\&]+', role_text)
            words = [w.strip() for w in words if w.strip()]
            if words:
                ignore_words = {'and', 'or', 'with', 'in', 'on', 'at', 'using', 'from', 'to'}
                all_tech = True
                for word in words:
                    word_clean = re.sub(r'\.js$', '', word)
                    if word_clean not in self.tech_keywords and word not in self.tech_keywords and word not in ignore_words:
                        all_tech = False
                        break
                if all_tech:
                    filtered_roles_count += 1
                    self.logger.debug(f"🔧 Filtered technology list from roles: '{role['text']}'")
                    continue
            
            roles.append(role)
            
        if filtered_roles_count > 0:
            self.logger.info(f"🔧 Filtered {filtered_roles_count} technology keywords from {len(roles_raw)} roles")
        
        # Filter out technology keywords from companies
        companies = []
        filtered_count = 0
        for company in companies_raw:
            company_text = company['text'].lower().strip()
            
            # Check if it's an exact match with tech keywords
            if company_text in self.tech_keywords:
                filtered_count += 1
                self.logger.debug(f"🔧 Filtered tech keyword: '{company['text']}'")
                continue
            
            # Check if all words are tech keywords (representing a tech list rather than a company)
            # Split by spaces, slashes, commas, ampersands, and hyphens
            words = re.split(r'[\s/,\-\&]+', company_text)
            words = [w.strip() for w in words if w.strip()]
            
            if words:
                ignore_words = {'and', 'or', 'with', 'in', 'on', 'at', 'using', 'from', 'to'}
                all_tech = True
                for word in words:
                    # Clean the word from version/JS extensions (e.g. node.js -> node)
                    word_clean = re.sub(r'\.js$', '', word)
                    if word_clean not in self.tech_keywords and word not in self.tech_keywords and word not in ignore_words:
                        all_tech = False
                        break
                if all_tech:
                    filtered_count += 1
                    self.logger.debug(f"🔧 Filtered technology list: '{company['text']}'")
                    continue
            
            # Check if it's a very short name (likely an acronym for a tech)
            if len(company_text) <= 2 and company_text not in ['ge', 'hp', 'at&t']:
                filtered_count += 1
                self.logger.debug(f"🔧 Filtered short name: '{company['text']}'")
                continue
            
            companies.append(company)
        
        if filtered_count > 0:
            self.logger.info(f"🔧 Filtered {filtered_count} technology keywords from {len(companies_raw)} companies")
            
        # Treat standalone CLIENT entities as fallback COMPANY anchors if they are:
        # 1. Far from any company (min_company_dist > 150 chars) or no companies exist, AND
        # 2. Closer to a nearby role/date than any company is.
        client_fallback_added = 0
        for client in clients_raw:
            client_pos = client['start']
            
            # Compute distance to closest company
            min_company_dist = float('inf')
            for company in companies:
                min_company_dist = min(min_company_dist, abs(company['start'] - client_pos))
            
            # If there is a company close to this client, it is not a standalone anchor
            if min_company_dist <= 150:
                continue
                
            is_anchor = False
            
            # Look at nearby roles and dates
            nearby_entities = [e for e in positions_data if e['type'] in ['ROLE', 'START_DATE', 'DATE_START', 'END_DATE', 'DATE_END']]
            
            for entity in nearby_entities:
                ent_pos = entity['start']
                dist_to_client = abs(ent_pos - client_pos)
                
                if dist_to_client <= 150:  # Reasonably close
                    # Check if any company is closer to this entity
                    company_closer = False
                    for company in companies:
                        dist_to_company = abs(ent_pos - company['start'])
                        if dist_to_company < dist_to_client:
                            company_closer = True
                            break
                    
                    if not company_closer:
                        is_anchor = True
                        break
            
            if not companies:
                is_anchor = True
                
            if is_anchor:
                # Check if this client text is already added to companies to prevent duplicates
                if not any(c['text'] == client['text'] and abs(c['start'] - client['start']) < 10 for c in companies):
                    companies.append({
                        'type': 'COMPANY',
                        'text': client['text'],
                        'start': client['start'],
                        'end': client['end'],
                        'is_fallback_client': True
                    })
                    client_fallback_added += 1
                
        if client_fallback_added > 0:
            self.logger.info(f"💼 Treated {client_fallback_added} standalone CLIENT entities as company anchors")
        
        self.logger.info(f" Position-based entities: {len(companies)} companies (after filtering), {len(roles)} roles, {len(locations)} locations")
        
        # Fallback: If no companies but we have roles, try to extract companies from text using regex
        if not companies and roles:
            self.logger.warning("⚠️ No companies extracted by DeBERTa, attempting regex fallback...")
            companies = self._extract_companies_regex(text, positions_data)
            self.logger.info(f"📝 Regex fallback found {len(companies)} companies")
        
        if not companies:
            self.logger.warning("No companies found - cannot build experiences")
            return []
        
        # Sort companies by position
        companies.sort(key=lambda x: x['start'])
        
        experiences = []
        proximity_window = 400  # Characters - entities within this range are grouped together

        # ── Entity consumption tracking (Problem 5 fix) ───────────────────────
        # Tracks entity positions that have already been claimed by a company.
        # Prevents the same ROLE / DATE / LOCATION from being assigned to two
        # adjacent companies when their proximity windows overlap.
        used_entity_positions: set = set()
        
        for i, company in enumerate(companies):
            company_pos = company['start']
            
            # Define search window around this company
            # Look backward and forward within proximity_window
            window_start = max(0, company_pos - proximity_window)
            window_end = company_pos + proximity_window
            
            # Find entities within proximity window — skipping already-consumed ones
            nearby_role = self._find_entity_in_window(
                roles, window_start, window_end, company_pos,
                exclude_positions=used_entity_positions
            )
            nearby_location = self._find_entity_in_window(
                locations, window_start, window_end, company_pos,
                exclude_positions=used_entity_positions
            )
            nearby_start_date = self._find_entity_in_window(
                start_dates, window_start, window_end, company_pos,
                exclude_positions=used_entity_positions
            )
            nearby_end_date = self._find_entity_in_window(
                end_dates, window_start, window_end, company_pos,
                exclude_positions=used_entity_positions
            )
            nearby_client = self._find_entity_in_window(
                clients_raw, window_start, window_end, company_pos,
                exclude_positions=used_entity_positions
            )

            # Mark claimed entities as consumed so adjacent companies cannot reuse them
            for matched in [nearby_role, nearby_location, nearby_start_date,
                            nearby_end_date, nearby_client]:
                if matched:
                    used_entity_positions.add(matched['start'])
            
            # Check if end date indicates current position
            is_current = False
            end_date_text = nearby_end_date['text'] if nearby_end_date else None
            if end_date_text:
                end_date_lower = end_date_text.lower()
                if 'present' in end_date_lower or 'current' in end_date_lower:
                    is_current = True
                    end_date_text = None
            
            # Detect and fix swapped company/role
            company_text = company['text']
            role_text = nearby_role['text'] if nearby_role else ''
            
            # Check if they're swapped (company looks like role, role looks like company)
            if role_text and self._looks_like_company(role_text) and self._looks_like_role(company_text):
                # Swap them
                self.logger.info(f"  🔄 Swapped: '{company_text}' (was company) ↔ '{role_text}' (was role)")
                company_text, role_text = role_text, company_text
                
            # Determine nearby client name if different from company name
            client_name = nearby_client['text'] if nearby_client and nearby_client['text'] != company_text else ''
            
            # Create experience
            exp = {
                'job_title': role_text,
                'company_name': company_text,
                'location': nearby_location['text'] if nearby_location else '',
                'start_date': self._parse_date(nearby_start_date['text']) if nearby_start_date else None,
                'end_date': self._parse_date(end_date_text) if end_date_text and not is_current else None,
                'is_current': is_current,
                'client': client_name,
                'clients': [client_name] if client_name else [],
                'description': ''
            }
            
            experiences.append(exp)
            
            # Log for debugging
            role_text = nearby_role['text'] if nearby_role else 'No role'
            start_text = nearby_start_date['text'] if nearby_start_date else 'No start'
            end_text = end_date_text or ('Present' if is_current else 'No end')
            self.logger.info(f"  ✓ Job {i+1}: {role_text} at {company['text']} ({start_text} - {end_text})")
        return experiences
    
    def _find_entity_in_window(self, entities: List[Dict], window_start: int, window_end: int, 
                                anchor_pos: int,
                                exclude_positions: set = None) -> Dict:
        """
        Find the entity closest to anchor_pos within the given window.

        Args:
            entities:          List of entity dictionaries with 'start', 'end', 'text', 'type'
            window_start:      Start of search window (character position)
            window_end:        End of search window (character position)
            anchor_pos:        Anchor position (e.g., company position) to measure distance from
            exclude_positions: Set of entity 'start' positions already consumed by another company.
                               Entities whose start is in this set are skipped.
                               (Improves Problem 5: prevents cross-record entity sharing)
            
        Returns:
            Entity dictionary if found, None otherwise
        """
        if exclude_positions is None:
            exclude_positions = set()

        candidates = []
        
        for entity in entities:
            entity_pos = entity['start']
            # Skip entities already consumed by a closer company
            if entity_pos in exclude_positions:
                continue
            # Check if entity is within window
            if window_start <= entity_pos <= window_end:
                # Calculate distance from anchor
                distance = abs(entity_pos - anchor_pos)
                candidates.append((distance, entity))
        
        if not candidates:
            return None
        
        # Return the closest entity
        candidates.sort(key=lambda x: x[0])
        return candidates[0][1]
    
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
            
            # Find the nearest client after the company
            client_positions = [(text.find(c), c) for c in clients if text.find(c) != -1]
            nearby_client = self._find_nearest_entity(client_positions, company_pos, next_company_pos)
            
            # Check if end date indicates current position
            is_current = False
            if end_date:
                end_date_lower = end_date.lower()
                if 'present' in end_date_lower or 'current' in end_date_lower:
                    is_current = True
                    end_date = None
            
            # Determine nearby client name if different from company name
            client_name = nearby_client if nearby_client and nearby_client != company_name else ''
            
            # Create experience
            exp = {
                'job_title': role or '',
                'company_name': company_name,
                'location': location or '',
                'start_date': self._parse_date(start_date) if start_date else None,
                'end_date': self._parse_date(end_date) if end_date and not is_current else None,
                'is_current': is_current,
                'client': client_name,
                'clients': [client_name] if client_name else [],
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
    
    
    def _extract_companies_regex(self, text: str, positions_data: List[Dict]) -> List[Dict]:
        """
        Regex fallback to extract company names when DeBERTa misses them.
        Looks for capitalized multi-word phrases near roles.
        """
        import re
        
        companies = []
        
        # Pattern: Capitalized words (2-5 words) that look like company names
        # e.g., "VMware", "Capgemini Technologies", "LLT Overseas"
        pattern = r'\b([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){0,4})\b'
        
        for match in re.finditer(pattern, text):
            company_text = match.group(1).strip()
            
            # Skip if it's a tech keyword
            if company_text.lower() in self.tech_keywords:
                continue
            
            # Skip single words unless they look like companies
            words = company_text.split()
            if len(words) == 1 and not self._looks_like_company(company_text):
                continue
            
            # Skip if it looks like a role
            if self._looks_like_role(company_text):
                continue
            
            # Add as company
            companies.append({
                'type': 'COMPANY',
                'text': company_text,
                'start': match.start(),
                'end': match.end()
            })
        
        return companies
    
    def _looks_like_company(self, text: str) -> bool:
        """Check if text looks like a company name."""
        if not text:
            return False
        
        text_lower = text.lower()
        
        # Company indicators
        company_keywords = ['inc', 'llc', 'ltd', 'pvt', 'corp', 'corporation', 'limited',
                           'technologies', 'solutions', 'systems', 'services', 'consulting',
                           'group', 'labs', 'software', 'enterprises']
        
        return any(keyword in text_lower for keyword in company_keywords)
    
    def _looks_like_role(self, text: str) -> bool:
        """Check if text looks like a job title."""
        if not text:
            return False
        
        text_lower = text.lower()
        
        # Job title keywords
        role_keywords = ['developer', 'engineer', 'manager', 'architect', 'analyst',
                        'designer', 'consultant', 'specialist', 'lead', 'senior',
                        'junior', 'director', 'coordinator', 'programmer', 'administrator',
                        'technician', 'principal', 'associate', 'assistant', 'intern',
                        'trainee', 'head', 'chief', 'vp', 'president', 'officer']
        
        return any(keyword in text_lower for keyword in role_keywords)
    
    def _parse_date(self, date_str: str) -> str:
        """Parse date string to year or year-month format (NO fake precision)."""
        if not date_str:
            return None
        
        import re
        
        # Remove common noise
        cleaned = date_str.strip().replace('|', '').replace('–', '-').replace('—', '-')
        
        # Pattern 1: Full date with month name (e.g., "April 2022", "Apr 2022", "Apr '22")
        month_patterns = [
            (r'(Jan|January)\s*[\'"]?(\d{2,4})', 1),
            (r'(Feb|February)\s*[\'"]?(\d{2,4})', 2),
            (r'(Mar|March)\s*[\'"]?(\d{2,4})', 3),
            (r'(Apr|April)\s*[\'"]?(\d{2,4})', 4),
            (r'(May)\s*[\'"]?(\d{2,4})', 5),
            (r'(Jun|June)\s*[\'"]?(\d{2,4})', 6),
            (r'(Jul|July)\s*[\'"]?(\d{2,4})', 7),
            (r'(Aug|August)\s*[\'"]?(\d{2,4})', 8),
            (r'(Sep|Sept|September)\s*[\'"]?(\d{2,4})', 9),
            (r'(Oct|October)\s*[\'"]?(\d{2,4})', 10),
            (r'(Nov|November)\s*[\'"]?(\d{2,4})', 11),
            (r'(Dec|December)\s*[\'"]?(\d{2,4})', 12)
        ]
        
        for pattern, month_num in month_patterns:
            match = re.search(pattern, cleaned, re.IGNORECASE)
            if match:
                year_str = match.group(2)
                # Handle 2-digit years (e.g., '22 -> 2022)
                if len(year_str) == 2:
                    year = 2000 + int(year_str) if int(year_str) < 50 else 1900 + int(year_str)
                else:
                    year = int(year_str)
                # Return year-month format (no fake day)
                return f"{year}-{month_num:02d}"
        
        # Pattern 2: Year only (e.g., "2022", "'22")
        year_match = re.search(r'[\'"]?(\d{2,4})', cleaned)
        if year_match:
            year_str = year_match.group(1)
            if len(year_str) == 2:
                year = 2000 + int(year_str) if int(year_str) < 50 else 1900 + int(year_str)
            else:
                year = int(year_str)
            # Return year only (no fake month/day)
            return str(year)
        
        return None
    
    def _extract_years_from_date_range(self, date_text: str) -> tuple:
        """
        Extract start and end years from date range strings.
        
        Handles patterns like:
        - "2011–2013", "2011-2013", "2011 - 2013"
        - "(2010-2014)", "2010 to 2014"
        - "2013" (single year)
        
        Returns:
            (start_year, end_year) as integers, or (None, None) if not found
        """
        if not date_text:
            return None, None
        
        # Remove parentheses and common separators
        cleaned = date_text.replace('(', '').replace(')', '')
        
        # Pattern 1: Year range with dash/en-dash (2011–2013, 2011-2013, 2011 - 2013)
        match = re.search(r'(\d{4})\s*[–\-—to]\s*(\d{4})', cleaned)
        if match:
            return int(match.group(1)), int(match.group(2))
        
        # Pattern 2: Single year (2013)
        match = re.search(r'(\d{4})', cleaned)
        if match:
            year = int(match.group(1))
            return year, year
        
        return None, None
