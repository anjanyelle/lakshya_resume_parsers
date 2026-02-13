from __future__ import annotations

import re
from typing import Any


_FALSE_POSITIVE_RE = re.compile(
    r"\b(workshop|bootcamp|training|trainings|course|courses|seminar|webinar|program|programme)\b",
    flags=re.IGNORECASE,
)

_CERTIFIED_RE = re.compile(
    r"\b(certified|certification|certificate|certificates|license|licence|licensed)\b",
    flags=re.IGNORECASE,
)



_PROVIDER_NORMALIZATION: dict[str, str] = {
    # Cloud Providers - AWS
    "aws": "Amazon Web Services",
    "amazon web services": "Amazon Web Services",
    "amazon": "Amazon Web Services",
    
    # Cloud Providers - Google
    "gcp": "Google Cloud",
    "google cloud": "Google Cloud",
    "google cloud platform": "Google Cloud",
    "google": "Google Cloud",
    
    # Cloud Providers - Microsoft
    "azure": "Microsoft Azure",
    "microsoft azure": "Microsoft Azure",
    "ms azure": "Microsoft Azure",
    "microsoft": "Microsoft",
    "ms": "Microsoft",
    
    # Cloud Providers - IBM
    "ibm": "IBM",
    "ibm cloud": "IBM Cloud",
    "international business machines": "IBM",
    
    # Cloud Providers - Oracle
    "oracle": "Oracle",
    "oracle cloud": "Oracle Cloud",
    "oci": "Oracle Cloud",
    
    # Cloud Providers - Others
    "alibaba cloud": "Alibaba Cloud",
    "aliyun": "Alibaba Cloud",
    "digitalocean": "DigitalOcean",
    "do": "DigitalOcean",
    "linode": "Linode",
    "vultr": "Vultr",
    "heroku": "Heroku",
    "salesforce": "Salesforce",
    
    # Professional Certifications - Project Management
    "pmi": "Project Management Institute",
    "project management institute": "Project Management Institute",
    "pmp": "Project Management Institute",
    "capm": "Project Management Institute",
    
    # Professional Certifications - Scrum/Agile
    "scrum.org": "Scrum.org",
    "scrum alliance": "Scrum Alliance",
    "scaled agile": "Scaled Agile",
    "safe": "Scaled Agile",
    
    # Professional Certifications - ISACA
    "isaca": "ISACA",
    "cisa": "ISACA",
    "cism": "ISACA",
    "crisc": "ISACA",
    
    # Professional Certifications - (ISC)²
    "isc2": "(ISC)²",
    "isc²": "(ISC)²",
    "cissp": "(ISC)²",
    "sscp": "(ISC)²",
    
    # Professional Certifications - CompTIA
    "comptia": "CompTIA",
    "comp tia": "CompTIA",
    "a+": "CompTIA",
    "network+": "CompTIA",
    "security+": "CompTIA",
    
    # Professional Certifications - Cisco
    "cisco": "Cisco",
    "ccna": "Cisco",
    "ccnp": "Cisco",
    "ccie": "Cisco",
    
    # Professional Certifications - Financial
    "cfa": "CFA Institute",
    "cfa institute": "CFA Institute",
    "chartered financial analyst": "CFA Institute",
    "aicpa": "AICPA",
    "cpa": "AICPA",
    "acca": "ACCA",
    "cima": "CIMA",
    "icaew": "ICAEW",
    
    # Professional Certifications - HR
    "shrm": "SHRM",
    "hrci": "HRCI",
    "phr": "HRCI",
    "sphr": "HRCI",
    
    # Professional Certifications - Six Sigma
    "six sigma": "Six Sigma",
    "iassc": "IASSC",
    "asq": "ASQ",
    
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
    "ucla": "UCLA",
    "oxford": "Oxford University",
    "cambridge": "Cambridge University",
    "eth": "ETH Zurich",
    "eth zurich": "ETH Zurich",
    
    # Educational Institutions - Online Learning
    "coursera": "Coursera",
    "edx": "edX",
    "udacity": "Udacity",
    "udemy": "Udemy",
    "pluralsight": "Pluralsight",
    "linkedin learning": "LinkedIn Learning",
    "lynda": "LinkedIn Learning",
    "khan academy": "Khan Academy",
    "codecademy": "Codecademy",
    
    # Technology Companies - FAANG/MANGA
    "facebook": "Meta",
    "meta": "Meta",
    "apple": "Apple",
    "netflix": "Netflix",
    "alphabet": "Google",
    
    # Technology Companies - Others
    "ibm": "IBM",
    "intel": "Intel",
    "nvidia": "NVIDIA",
    "amd": "AMD",
    "qualcomm": "Qualcomm",
    "cisco": "Cisco",
    "dell": "Dell",
    "hp": "HP",
    "hewlett packard": "HP",
    "lenovo": "Lenovo",
    "samsung": "Samsung",
    "sony": "Sony",
    "tesla": "Tesla",
    "spacex": "SpaceX",
    
    # Software/SaaS Companies
    "salesforce": "Salesforce",
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
    
    # Database/Data Companies
    "mongodb": "MongoDB",
    "redis labs": "Redis",
    "elastic": "Elastic",
    "elasticsearch": "Elastic",
    "databricks": "Databricks",
    "snowflake": "Snowflake",
    "splunk": "Splunk",
    
    # Security Companies
    "palo alto networks": "Palo Alto Networks",
    "fortinet": "Fortinet",
    "checkpoint": "Check Point",
    "crowdstrike": "CrowdStrike",
    "okta": "Okta",
    
    # Financial Institutions
    "jp morgan": "JPMorgan Chase",
    "jpmorgan": "JPMorgan Chase",
    "goldman sachs": "Goldman Sachs",
    "morgan stanley": "Morgan Stanley",
    "bank of america": "Bank of America",
    "bofa": "Bank of America",
    "citigroup": "Citigroup",
    "citi": "Citigroup",
    "wells fargo": "Wells Fargo",
    "hsbc": "HSBC",
    
    # Consulting Firms
    "mckinsey": "McKinsey & Company",
    "mckinsey & company": "McKinsey & Company",
    "bain": "Bain & Company",
    "bain & company": "Bain & Company",
    "bcg": "Boston Consulting Group",
    "boston consulting group": "Boston Consulting Group",
    "deloitte": "Deloitte",
    "pwc": "PwC",
    "pricewaterhousecoopers": "PwC",
    "ey": "EY",
    "ernst & young": "EY",
    "kpmg": "KPMG",
    "accenture": "Accenture",
    
    # Standards Organizations
    "iso": "ISO",
    "international organization for standardization": "ISO",
    "ieee": "IEEE",
    "w3c": "W3C",
    "ietf": "IETF",
    "owasp": "OWASP",
    
    # Open Source/Foundations
    "linux foundation": "Linux Foundation",
    "apache": "Apache Software Foundation",
    "apache software foundation": "Apache Software Foundation",
    "cncf": "Cloud Native Computing Foundation",
    "openstack": "OpenStack Foundation",
    "eclipse": "Eclipse Foundation",
}



class CertificationValidator:
    def remove_false_positives(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        cleaned: list[dict[str, Any]] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name") or "").strip()
            issuing = str(item.get("issuing_organization") or "").strip()
            text = f"{name} {issuing}".strip()
            if not text:
                continue
            if _FALSE_POSITIVE_RE.search(text) and not _CERTIFIED_RE.search(text):
                continue
            cleaned.append(item)
        return cleaned

    def normalize_providers(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            issuing = item.get("issuing_organization")
            issuing_norm = self._normalize_provider(str(issuing) if issuing is not None else "")
            if issuing_norm:
                item = {**item, "issuing_organization": issuing_norm}
            out.append(item)
        return out

    def deduplicate_certifications(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
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
            existing_conf = self._to_float(existing.get("confidence"), default=0.0)
            incoming_conf = self._to_float(item.get("confidence"), default=0.0)
            if incoming_conf > existing_conf:
                merged[key] = item
        return list(merged.values())

    def detect_mismatches(
        self,
        *,
        section_confidence: float | None,
        extracted_items: list[dict[str, Any]],
    ) -> dict[str, Any]:
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
        if sec_conf >= 0.7 and count == 0:
            reasons.append("high_section_confidence_but_no_items")
        if sec_conf == 0.0 and count > 0:
            reasons.append("no_section_detected_but_items_present")
        if sec_conf < 0.4 and count >= 2:
            reasons.append("low_section_confidence_but_multiple_items")
        if count > 0 and avg_item_conf < 0.55:
            reasons.append("low_average_item_confidence")

        return {
            "section_confidence": round(sec_conf, 4),
            "extracted_count": int(count),
            "avg_item_confidence": round(float(avg_item_conf), 4),
            "mismatch": bool(reasons),
            "reasons": reasons,
        }

    @staticmethod
    def _normalize_provider(value: str) -> str:
        cleaned = re.sub(r"\s+", " ", (value or "").strip()).strip("-–—:|")
        if not cleaned:
            return ""
        key = cleaned.lower()
        mapped = _PROVIDER_NORMALIZATION.get(key)
        if mapped:
            return mapped
        if "amazon web services" in key or key == "amazon":
            return "Amazon Web Services"
        if key in {"google", "google inc", "google llc"}:
            return "Google"
        return cleaned

    @staticmethod
    def _dedupe_key(name: str, provider: str) -> str:
        def norm(s: str) -> str:
            s = (s or "").lower().strip()
            s = re.sub(r"\s+", " ", s)
            s = re.sub(r"[^a-z0-9 ]+", "", s)
            return s.strip()

        return f"{norm(name)}|{norm(provider)}"

    @staticmethod
    def _to_float(value: Any, default: float = 0.0) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return float(default)
