import logging
from typing import Any, Dict, Optional
from datetime import datetime
from pathlib import Path
import pandas as pd
from rapidfuzz import process, fuzz

logger = logging.getLogger(__name__)

class EnrichmentService:
    def __init__(self, nlp_pipeline=None):
        # Base data directory
        self.data_dir = Path(__file__).resolve().parents[3] / "data"
        self._load_local_datasets()
        
        # O*NET/ISCO Job Role Mapping (Expanded for worldwide IT/non-IT)
        self.role_taxonomy = self._load_role_taxonomy()
        
        # BERT Pipeline for entity verification (Phase 8)
        self.nlp_pipeline = nlp_pipeline
        
        # Lookup cache to handle 100k+ entries efficiently during batch processing
        self._lookup_cache: Dict[str, Optional[Dict[str, Any]]] = {}

    def _load_local_datasets(self):
        """Load local CSV datasets as a baseline for enrichment."""
        self.companies_df = self._load_csv("companies.csv")
        self.locations_df = self._load_csv("locations.csv")
        self.job_titles_df = self._load_csv("job_titles.csv")
        
        # Phase 8: Massive 100k+ Global Dataset
        self.global_100k_df = self._load_csv("global_companies_100k.csv")
        self.global_roles_100k_df = self._load_csv("global_job_titles_100k.csv")
        
        # Large worldwide datasets (Lookup tables)
        self.opencorporates_mock = self._load_csv("opencorporates_sample.csv")
        self.wikidata_mock = self._load_csv("wikidata_companies.csv")
        self.nominatim_mock = self._load_csv("nominatim_locations.csv")
        self.geonames_mock = self._load_csv("geonames_cities.csv")
        
        # Phase 7: Massive 100k+ Global Dataset
        self.global_100k_df = self._load_csv("global_companies_100k.csv")

    def _load_csv(self, filename: str) -> Optional[pd.DataFrame]:
        path = self.data_dir / filename
        if path.exists():
            try:
                return pd.read_csv(path)
            except Exception as e:
                logger.error(f"Error loading {filename}: {e}")
        return None

    def _load_role_taxonomy(self) -> Dict[str, Any]:
        # Implementation of ONET/ISCO-style taxonomy
        return {
            "SOFTWARE_ENGINEER": ["Software Engineer", "Systems Engineer", "Application Developer", "SWE", "SDE"],
            "DATA_SCIENTIST": ["Data Scientist", "ML Engineer", "Data Analyst", "AI Researcher"],
            "ACCOUNTANT": ["Accountant", "Bookkeeper", "Financial Auditor", "Tax Consultant"],
            "NURSE": ["Registered Nurse", "Clinical Nurse Specialist", "Nursing Assistant"],
            "TEACHER": ["Teacher", "Instructor", "Lecturer", "Professor", "Educator"]
        }

    def enrich_company(self, name: str) -> Dict[str, Any]:
        """
        Enrichment order: OpenCorporates → Wikidata → Companies House → SEC EDGAR.
        """
        res = {"name": name, "client_flag": False, "company_id": None, "industry": None, "confidence": 0.0}
        if not name or name == "Unknown Company":
            return res

        # 1. OpenCorporates Lookup
        match = self._fuzzy_lookup(name, self.opencorporates_mock, "company_name", expected_label="ORG")
        if match:
            res.update({
                "name": match["company_name"],
                "company_id": f"oc_{match.get('jurisdiction_code')}_{match.get('company_number')}",
                "industry": match.get("industry_code_names"),
                "confidence": 0.95
            })
            return res

        # 2. Wikidata Lookup
        match = self._fuzzy_lookup(name, self.wikidata_mock, "itemLabel", expected_label="ORG")
        if match:
            res.update({
                "name": match["itemLabel"],
                "company_id": match.get("item"), # QID
                "industry": match.get("industryLabel"),
                "confidence": 0.9
            })
            return res

        # 3. Global 100k+ Lookup (Primary Scale Layer)
        match = self._fuzzy_lookup(name, self.global_100k_df, "name", expected_label="ORG")
        if match:
            res.update({
                "name": match["name"],
                "company_id": f"global_{hash(match['name']) % 10**8}",
                "industry": match.get("industry") or ("Information Technology" if match.get("is_it") else "Not Specified"),
                "confidence": 0.85
            })
            return res

        # 4. Local/Priority Fallback
        match = self._fuzzy_lookup(name, self.companies_df, "companies", expected_label="ORG")
        if match:
            res.update({
                "name": match["companies"],
                "company_id": match.get("company_id"),
                "industry": match.get("industry") or self._detect_industry(name),
                "confidence": 0.8
            })
            return res

        res["industry"] = self._detect_industry(name)
        res["confidence"] = 0.5 if res["industry"] != "Not Specified" else 0.3
        return res

    def _detect_industry(self, company_name: str) -> str:
        it_keywords = ["tech", "software", "solutions", "systems", "ai", "digital", "consultancy", "technologies", "infosys", "wipro", "tcs", "cognizant"]
        non_it_keywords = {
            "bank": "Finance", "hospital": "Healthcare", "retail": "Retail", 
            "manufacturing": "Manufacturing", "logistics": "Logistics", 
            "education": "Education", "school": "Education", "energy": "Energy"
        }
        
        low_name = company_name.lower()
        if any(k in low_name for k in it_keywords):
            return "Information Technology"
        for k, industry in non_it_keywords.items():
            if k in low_name:
                return industry
        return "Not Specified"

    def enrich_location(self, location_str: str) -> Dict[str, Any]:
        """
        Location: Nominatim → GeoNames; prefer exact city matches.
        """
        res = {"city": None, "region": None, "country": None, "remote": False, "confidence": 0.0}
        if not location_str:
            return res
        
        lowered = location_str.lower()
        if any(w in lowered for w in ["remote", "work from home", "wfh", "anywhere"]):
            res["remote"] = True

        # 1. Nominatim Lookup (Mocked)
        match = self._fuzzy_lookup(location_str, self.nominatim_mock, "display_name", expected_label="LOC")
        if match:
            res.update({
                "city": match.get("city") or match.get("town"),
                "region": match.get("state"),
                "country": match.get("country"),
                "confidence": 0.95
            })
            return res

        # 2. GeoNames Lookup (Mocked)
        match = self._fuzzy_lookup(location_str, self.geonames_mock, "name", expected_label="LOC")
        if match:
            res.update({
                "city": match["name"],
                "region": match.get("admin1_code"),
                "country": match.get("country_code"),
                "confidence": 0.9
            })
            return res

        # Fallback split logic
        parts = [p.strip() for p in location_str.split(",")]
        if len(parts) >= 1: res["city"] = parts[0]
        if len(parts) >= 2: res["region"] = parts[1]
        if len(parts) >= 3: res["country"] = parts[2]
        res["confidence"] = 0.4 if res["city"] else 0.0
        return res

    def normalize_role(self, role: str) -> str:
        """Normalizes role name using 100k+ global taxonomy."""
        if not role or role == "Job Role":
            return "Job Role"
        
        # 0. Cache lookup
        cache_key = f"role_{role.lower()}"
        if cache_key in self._lookup_cache:
            return self._lookup_cache[cache_key]["title"] if self._lookup_cache[cache_key] else role.strip().title()

        # 1. Taxonomy check
        role_lower = role.lower()
        for standard_role, aliases in self.role_taxonomy.items():
            if any(alias.lower() in role_lower for alias in aliases):
                return standard_role.replace("_", " ").title()
        
        # 2. Global 100k Dataset Lookup (Phase 8 Priority)
        match = self._fuzzy_lookup(role, self.global_roles_100k_df, "title")
        if match:
            return match["title"]

        # 3. Local/Fallback
        if self.job_titles_df is not None:
             match = self._fuzzy_lookup(role, self.job_titles_df, "titles")
             if match:
                 return match["titles"]

        return role.strip().title()

    def bert_check(self, text: str, expected_label: str) -> bool:
        """Verify if the entity matches the expected BERT label (ORG, LOC, etc.)."""
        if not self.nlp_pipeline or not text:
            return True # Neutral if no model
            
        try:
            entities = self.nlp_pipeline(text)
            for ent in entities:
                lbl = ent.get('entity_group') or ent.get('entity')
                if lbl == expected_label:
                    return True
            return False
        except Exception:
            return True

    def _fuzzy_lookup(self, query: str, df: Optional[pd.DataFrame], column: str, expected_label: str = None) -> Optional[Dict[str, Any]]:
        if df is None or df.empty or column not in df.columns:
            return None
        
        # Cache key for performance
        cache_key = f"{query.lower()}_{column}"
        if cache_key in self._lookup_cache:
            return self._lookup_cache[cache_key]
        
        choices = df[column].dropna().unique().tolist()
        if not choices:
            self._lookup_cache[cache_key] = None
            return None
            
        # For high-scale, we use a slightly more conservative threshold
        best_match = process.extractOne(query, choices, scorer=fuzz.token_sort_ratio)
        if best_match and best_match[1] > 88:
            matched_val = best_match[0]
            
            # Additional BERT verification if label provided
            if expected_label and not self.bert_check(matched_val, expected_label):
                 # If BERT disagrees, we lower confidence or discard
                 if best_match[1] < 95: # If not an absolute exact match
                    self._lookup_cache[cache_key] = None
                    return None
            
            row = df[df[column] == matched_val].iloc[0]
            result = row.to_dict()
            self._lookup_cache[cache_key] = result
            return result
            
        self._lookup_cache[cache_key] = None
        return None

