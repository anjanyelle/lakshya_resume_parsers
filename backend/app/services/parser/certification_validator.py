from __future__ import annotations

import re
from typing import Any


_FALSE_POSITIVE_RE = re.compile(
    r"\b(workshop|bootcamp|training|trainings|course|courses|seminar|webinar|program|programme|session|sessions)\b",
    flags=re.IGNORECASE,
)

_CERTIFIED_RE = re.compile(
    r"\b(certified|certification|certificate|certificates|license|licence|licensed|accredited|accreditation)\b",
    flags=re.IGNORECASE,
)


_PROVIDER_NORMALIZATION: dict[str, str] = {
    # Cloud Providers - AWS
    "aws": "Amazon Web Services",
    "amazon web services": "Amazon Web Services",
    "amazon": "Amazon Web Services",
    "aws certified": "Amazon Web Services",
    
    # Cloud Providers - Google
    "gcp": "Google Cloud",
    "google cloud": "Google Cloud",
    "google cloud platform": "Google Cloud",
    "google": "Google Cloud",
    "google professional": "Google Cloud",
    
    # Cloud Providers - Microsoft
    "azure": "Microsoft Azure",
    "microsoft azure": "Microsoft Azure",
    "ms azure": "Microsoft Azure",
    "microsoft": "Microsoft",
    "ms": "Microsoft",
    "microsoft certified": "Microsoft",
    
    # Cloud Providers - IBM
    "ibm": "IBM",
    "ibm cloud": "IBM Cloud",
    "international business machines": "IBM",
    "ibm professional": "IBM",
    
    # Cloud Providers - Oracle
    "oracle": "Oracle",
    "oracle cloud": "Oracle Cloud",
    "oci": "Oracle Cloud",
    "oracle certified": "Oracle",
    
    # Cloud Providers - Others
    "alibaba cloud": "Alibaba Cloud",
    "aliyun": "Alibaba Cloud",
    "digitalocean": "DigitalOcean",
    "do": "DigitalOcean",
    "linode": "Linode",
    "akamai": "Akamai",
    "vultr": "Vultr",
    "heroku": "Heroku",
    "salesforce": "Salesforce",
    "vmware": "VMware",
    
    # Professional Certifications - Project Management
    "pmi": "Project Management Institute",
    "project management institute": "Project Management Institute",
    "pmp": "Project Management Institute",
    "capm": "Project Management Institute",
    "pmbok": "Project Management Institute",
    
    # Professional Certifications - Scrum/Agile
    "scrum.org": "Scrum.org",
    "scrum alliance": "Scrum Alliance",
    "scaled agile": "Scaled Agile",
    "safe": "Scaled Agile",
    "icagile": "ICAgile",
    "agile alliance": "Agile Alliance",
    
    # Professional Certifications - ISACA
    "isaca": "ISACA",
    "cisa": "ISACA",
    "cism": "ISACA",
    "crisc": "ISACA",
    "cgeit": "ISACA",
    "cobit": "ISACA",
    
    # Professional Certifications - (ISC)²
    "isc2": "(ISC)²",
    "isc²": "(ISC)²",
    "isc squared": "(ISC)²",
    "cissp": "(ISC)²",
    "sscp": "(ISC)²",
    "ccsp": "(ISC)²",
    
    # Professional Certifications - CompTIA
    "comptia": "CompTIA",
    "comp tia": "CompTIA",
    "a+": "CompTIA",
    "network+": "CompTIA",
    "security+": "CompTIA",
    "linux+": "CompTIA",
    "cloud+": "CompTIA",
    "cysa+": "CompTIA",
    
    # Professional Certifications - Cisco
    "cisco": "Cisco",
    "ccna": "Cisco",
    "ccnp": "Cisco",
    "ccie": "Cisco",
    "ccent": "Cisco",
    "devnet": "Cisco",
    
    # Professional Certifications - Red Hat
    "red hat": "Red Hat",
    "redhat": "Red Hat",
    "rhcsa": "Red Hat",
    "rhce": "Red Hat",
    "rhca": "Red Hat",
    
    # Professional Certifications - Financial
    "cfa": "CFA Institute",
    "cfa institute": "CFA Institute",
    "chartered financial analyst": "CFA Institute",
    "aicpa": "AICPA",
    "cpa": "AICPA",
    "acca": "ACCA",
    "cima": "CIMA",
    "icaew": "ICAEW",
    "frm": "GARP",
    "garp": "GARP",
    "cfp": "CFP Board",
    
    # Professional Certifications - HR
    "shrm": "SHRM",
    "hrci": "HRCI",
    "phr": "HRCI",
    "sphr": "HRCI",
    "cipd": "CIPD",
    
    # Professional Certifications - Six Sigma
    "six sigma": "Six Sigma",
    "iassc": "IASSC",
    "asq": "ASQ",
    "american society for quality": "ASQ",
    
    # Professional Certifications - ITIL
    "itil": "AXELOS",
    "axelos": "AXELOS",
    "prince2": "AXELOS",
    
    # Educational Institutions - Universities
    "mit": "Massachusetts Institute of Technology",
    "massachusetts institute of technology": "Massachusetts Institute of Technology",
    "stanford": "Stanford University",
    "stanford university": "Stanford University",
    "harvard": "Harvard University",
    "harvard university": "Harvard University",
    "berkeley": "UC Berkeley",
    "uc berkeley": "UC Berkeley",
    "university of california berkeley": "UC Berkeley",
    "caltech": "California Institute of Technology",
    "california institute of technology": "California Institute of Technology",
    "ucla": "UCLA",
    "oxford": "Oxford University",
    "oxford university": "Oxford University",
    "cambridge": "Cambridge University",
    "cambridge university": "Cambridge University",
    "eth": "ETH Zurich",
    "eth zurich": "ETH Zurich",
    "imperial": "Imperial College London",
    "imperial college": "Imperial College London",
    
    # Educational Institutions - Online Learning
    "coursera": "Coursera",
    "edx": "edX",
    "udacity": "Udacity",
    "udemy": "Udemy",
    "pluralsight": "Pluralsight",
    "linkedin learning": "LinkedIn Learning",
    "lynda": "LinkedIn Learning",
    "lynda.com": "LinkedIn Learning",
    "khan academy": "Khan Academy",
    "codecademy": "Codecademy",
    "datacamp": "DataCamp",
    "skillshare": "Skillshare",
    "treehouse": "Treehouse",
    
    # Technology Companies - FAANG/MANGA
    "facebook": "Meta",
    "meta": "Meta",
    "apple": "Apple",
    "netflix": "Netflix",
    "alphabet": "Google",
    "google inc": "Google",
    "google llc": "Google",
    
    # Technology Companies - Others
    "intel": "Intel",
    "nvidia": "NVIDIA",
    "amd": "AMD",
    "qualcomm": "Qualcomm",
    "dell": "Dell",
    "dell technologies": "Dell",
    "hp": "HP",
    "hewlett packard": "HP",
    "hewlett-packard": "HP",
    "lenovo": "Lenovo",
    "samsung": "Samsung",
    "sony": "Sony",
    "tesla": "Tesla",
    "spacex": "SpaceX",
    "twitter": "X (Twitter)",
    "x": "X (Twitter)",
    
    # Software/SaaS Companies
    "sap": "SAP",
    "workday": "Workday",
    "servicenow": "ServiceNow",
    "atlassian": "Atlassian",
    "jira": "Atlassian",
    "confluence": "Atlassian",
    "slack": "Slack",
    "zoom": "Zoom",
    "dropbox": "Dropbox",
    "box": "Box",
    "adobe": "Adobe",
    "autodesk": "Autodesk",
    "tableau": "Tableau",
    "tableau software": "Tableau",
    
    # Database/Data Companies
    "mongodb": "MongoDB",
    "mongo db": "MongoDB",
    "redis labs": "Redis",
    "redis": "Redis",
    "elastic": "Elastic",
    "elasticsearch": "Elastic",
    "databricks": "Databricks",
    "snowflake": "Snowflake",
    "splunk": "Splunk",
    "teradata": "Teradata",
    "cloudera": "Cloudera",
    "hortonworks": "Cloudera",
    
    # Security Companies
    "palo alto networks": "Palo Alto Networks",
    "palo alto": "Palo Alto Networks",
    "fortinet": "Fortinet",
    "checkpoint": "Check Point",
    "check point": "Check Point",
    "crowdstrike": "CrowdStrike",
    "okta": "Okta",
    "cyberark": "CyberArk",
    "tenable": "Tenable",
    
    # DevOps/Container Companies
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "hashicorp": "HashiCorp",
    "terraform": "HashiCorp",
    "vault": "HashiCorp",
    "jenkins": "Jenkins",
    "gitlab": "GitLab",
    "github": "GitHub",
    
    # Financial Institutions
    "jp morgan": "JPMorgan Chase",
    "jpmorgan": "JPMorgan Chase",
    "jpmorgan chase": "JPMorgan Chase",
    "goldman sachs": "Goldman Sachs",
    "morgan stanley": "Morgan Stanley",
    "bank of america": "Bank of America",
    "bofa": "Bank of America",
    "citigroup": "Citigroup",
    "citi": "Citigroup",
    "wells fargo": "Wells Fargo",
    "hsbc": "HSBC",
    "barclays": "Barclays",
    "deutsche bank": "Deutsche Bank",
    
    # Consulting Firms
    "mckinsey": "McKinsey & Company",
    "mckinsey & company": "McKinsey & Company",
    "mckinsey and company": "McKinsey & Company",
    "bain": "Bain & Company",
    "bain & company": "Bain & Company",
    "bain and company": "Bain & Company",
    "bcg": "Boston Consulting Group",
    "boston consulting group": "Boston Consulting Group",
    "deloitte": "Deloitte",
    "pwc": "PwC",
    "pricewaterhousecoopers": "PwC",
    "price waterhouse coopers": "PwC",
    "ey": "EY",
    "ernst & young": "EY",
    "ernst and young": "EY",
    "kpmg": "KPMG",
    "accenture": "Accenture",
    "capgemini": "Capgemini",
    
    # Standards Organizations
    "iso": "ISO",
    "international organization for standardization": "ISO",
    "ieee": "IEEE",
    "w3c": "W3C",
    "ietf": "IETF",
    "owasp": "OWASP",
    "nist": "NIST",
    "ansi": "ANSI",
    
    # Open Source/Foundations
    "linux foundation": "Linux Foundation",
    "apache": "Apache Software Foundation",
    "apache software foundation": "Apache Software Foundation",
    "cncf": "Cloud Native Computing Foundation",
    "cloud native computing foundation": "Cloud Native Computing Foundation",
    "openstack": "OpenStack Foundation",
    "openstack foundation": "OpenStack Foundation",
    "eclipse": "Eclipse Foundation",
    "eclipse foundation": "Eclipse Foundation",
    "mozilla": "Mozilla",
    "python software foundation": "Python Software Foundation",
    
    # Marketing/Analytics
    "hubspot": "HubSpot",
    "marketo": "Marketo",
    "adobe marketing": "Adobe",
    "google analytics": "Google",
    "google ads": "Google",
}


class CertificationValidator:
    """Validator for cleaning, normalizing, and deduplicating certification data."""
    
    def remove_false_positives(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Remove items that look like courses/workshops but aren't actual certifications.
        
        Args:
            items: List of certification dictionaries
            
        Returns:
            Filtered list with false positives removed
        """
        cleaned: list[dict[str, Any]] = []
        
        for item in items:
            if not isinstance(item, dict):
                continue
                
            name = str(item.get("name") or "").strip()
            issuing = str(item.get("issuing_organization") or "").strip()
            text = f"{name} {issuing}".strip()
            
            if not text:
                continue
            
            # Skip if it contains false positive keywords but no certification keywords
            if _FALSE_POSITIVE_RE.search(text) and not _CERTIFIED_RE.search(text):
                continue
            
            # Additional validation: skip if name is too short (likely incomplete extraction)
            if len(name) < 3:
                continue
                
            cleaned.append(item)
            
        return cleaned

    def normalize_providers(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Normalize issuing organization names to standard forms.
        
        Args:
            items: List of certification dictionaries
            
        Returns:
            List with normalized issuing_organization values
        """
        out: list[dict[str, Any]] = []
        
        for item in items:
            if not isinstance(item, dict):
                continue
                
            issuing = item.get("issuing_organization")
            issuing_str = str(issuing) if issuing is not None else ""
            issuing_norm = self._normalize_provider(issuing_str)
            
            if issuing_norm:
                # Create new dict with normalized provider
                item = {**item, "issuing_organization": issuing_norm}
                
            out.append(item)
            
        return out

    def deduplicate_certifications(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Remove duplicate certifications, keeping the one with highest confidence.
        
        Args:
            items: List of certification dictionaries
            
        Returns:
            Deduplicated list
        """
        merged: dict[str, dict[str, Any]] = {}
        
        for item in items:
            if not isinstance(item, dict):
                continue
                
            name = str(item.get("name") or "").strip()
            if not name:
                continue
                
            provider = str(item.get("issuing_organization") or "").strip()
            key = self._dedupe_key(name, provider)
            
            existing = merged.get(key)
            if not existing:
                merged[key] = item
                continue
            
            # Compare confidence scores
            existing_conf = self._to_float(existing.get("confidence"), default=0.0)
            incoming_conf = self._to_float(item.get("confidence"), default=0.0)
            
            # Keep the one with higher confidence
            if incoming_conf > existing_conf:
                merged[key] = item
            # If confidence is equal, prefer the one with more complete data
            elif incoming_conf == existing_conf:
                existing_fields = sum(1 for v in existing.values() if v)
                incoming_fields = sum(1 for v in item.values() if v)
                if incoming_fields > existing_fields:
                    merged[key] = item
                    
        return list(merged.values())

    def detect_mismatches(
        self,
        *,
        section_confidence: float | None,
        extracted_items: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Detect potential issues between section detection and item extraction.
        
        Args:
            section_confidence: Confidence that a certification section was detected
            extracted_items: List of extracted certification items
            
        Returns:
            Dictionary with mismatch analysis
        """
        sec_conf = self._to_float(section_confidence, default=0.0)
        count = len(extracted_items)
        avg_item_conf = 0.0
        
        if extracted_items:
            vals = [
                self._to_float(item.get("confidence"), default=0.0)
                for item in extracted_items
                if isinstance(item, dict)
            ]
            avg_item_conf = (sum(vals) / len(vals)) if vals else 0.0

        reasons: list[str] = []
        
        # Check for various mismatch scenarios
        if sec_conf >= 0.7 and count == 0:
            reasons.append("high_section_confidence_but_no_items")
            
        if sec_conf == 0.0 and count > 0:
            reasons.append("no_section_detected_but_items_present")
            
        if sec_conf < 0.4 and count >= 2:
            reasons.append("low_section_confidence_but_multiple_items")
            
        if count > 0 and avg_item_conf < 0.55:
            reasons.append("low_average_item_confidence")
            
        if count > 10:
            reasons.append("unusually_high_item_count")

        return {
            "section_confidence": round(sec_conf, 4),
            "extracted_count": int(count),
            "avg_item_confidence": round(float(avg_item_conf), 4),
            "mismatch": bool(reasons),
            "reasons": reasons,
        }

    @staticmethod
    def _normalize_provider(value: str) -> str:
        """
        Normalize provider name to standard form.
        
        Args:
            value: Raw provider name
            
        Returns:
            Normalized provider name
        """
        # Clean whitespace and common separators
        cleaned = re.sub(r"\s+", " ", (value or "").strip()).strip("-–—:|")
        if not cleaned:
            return ""
            
        key = cleaned.lower()
        
        # Check exact match in normalization dict
        mapped = _PROVIDER_NORMALIZATION.get(key)
        if mapped:
            return mapped
        
        # Special handling for common variations
        if "amazon web services" in key or (key == "amazon" and "cloud" not in cleaned.lower()):
            return "Amazon Web Services"
            
        if key in {"google", "google inc", "google llc"} and "cloud" not in cleaned.lower():
            return "Google"
            
        if "microsoft" in key and "azure" not in key:
            return "Microsoft"
            
        # Return cleaned version if no match found
        return cleaned

    @staticmethod
    def _dedupe_key(name: str, provider: str) -> str:
        """
        Create a normalized key for deduplication.
        
        Args:
            name: Certification name
            provider: Provider name
            
        Returns:
            Normalized key for deduplication
        """
        def norm(s: str) -> str:
            s = (s or "").lower().strip()
            # Normalize whitespace
            s = re.sub(r"\s+", " ", s)
            # Remove special characters, keep alphanumeric and spaces
            s = re.sub(r"[^a-z0-9 ]+", "", s)
            return s.strip()

        return f"{norm(name)}|{norm(provider)}"

    @staticmethod
    def _to_float(value: Any, default: float = 0.0) -> float:
        """
        Safely convert value to float.
        
        Args:
            value: Value to convert
            default: Default value if conversion fails
            
        Returns:
            Float value or default
        """
        if value is None:
            return default
            
        try:
            return float(value)
        except (TypeError, ValueError):
            return float(default)
    
    def validate_and_clean(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Complete validation pipeline: remove false positives, normalize, and deduplicate.
        
        Args:
            items: Raw certification items
            
        Returns:
            Cleaned and validated certification items
        """
        # Step 1: Remove false positives
        cleaned = self.remove_false_positives(items)
        
        # Step 2: Normalize provider names
        normalized = self.normalize_providers(cleaned)
        
        # Step 3: Deduplicate
        deduplicated = self.deduplicate_certifications(normalized)
        
        return deduplicated