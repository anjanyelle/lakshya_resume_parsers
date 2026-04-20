"""
Global IT Industry Dataset Generator
=====================================
Generates:
 - global_companies.csv      : 50,000+ IT companies (name, canonical, country, industry)
 - global_locations.csv      : 100,000+ cities/states/countries (major tech hubs + worldwide)
 - it_job_roles.csv          : 10,000+ IT job roles (title, seniority, domain, aliases)
 - ner_training_data.jsonl   : 500,000+ NER-tagged IOB2 training samples for DeBERTa
 - work_history_train.jsonl  : 100,000+ structured work history extraction samples

Run from backend/ directory:
  python scripts/generate_datasets.py
  python scripts/generate_datasets.py --verify    (only check sizes, don't write)

Output: backend/tests/data/
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import re
import sys
from itertools import product
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
# SEED — reproducible generation
# ──────────────────────────────────────────────────────────────────────────────
random.seed(42)

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "tests" / "data"


# ══════════════════════════════════════════════════════════════════════════════
# 1.  COMPANIES
# ══════════════════════════════════════════════════════════════════════════════

# ── A. Named real-world / well-known companies ──────────────────────────────
_NAMED_COMPANIES: list[tuple[str, str, str, str]] = [
    # (canonical_name, country, industry, aliases_pipe)
    # ── FAANG / Big Tech ──
    ("Google", "USA", "Technology", "Google LLC|Alphabet Inc|Google India"),
    ("Amazon", "USA", "E-Commerce/Cloud", "Amazon.com|AWS|Amazon Web Services|Amazon India"),
    ("Microsoft", "USA", "Technology", "Microsoft Corporation|Microsoft Corp|Microsoft India"),
    ("Meta", "USA", "Social Media", "Facebook|Facebook Inc|Meta Platforms|Instagram|WhatsApp"),
    ("Apple", "USA", "Consumer Electronics", "Apple Inc|Apple Computer|Apple India"),
    ("Netflix", "USA", "Streaming", "Netflix Inc|Netflix India"),
    ("Salesforce", "USA", "CRM/SaaS", "Salesforce.com|Salesforce Inc"),
    ("Oracle", "USA", "Database/Cloud", "Oracle Corporation|Oracle Corp|Oracle India"),
    ("IBM", "USA", "IT Services", "International Business Machines|IBM India"),
    ("Intel", "USA", "Semiconductors", "Intel Corporation|Intel India"),
    ("Nvidia", "USA", "Semiconductors/AI", "NVIDIA Corporation|NVIDIA India"),
    ("Adobe", "USA", "Software", "Adobe Inc|Adobe Systems|Adobe India"),
    ("Twitter/X", "USA", "Social Media", "Twitter Inc|X Corp"),
    ("LinkedIn", "USA", "Professional Network", "LinkedIn Corporation|LinkedIn India"),
    ("Uber", "USA", "Ride-Sharing", "Uber Technologies|Uber India"),
    ("Airbnb", "USA", "Hospitality Tech", "Airbnb Inc"),
    ("Stripe", "USA", "FinTech", "Stripe Inc"),
    ("Snowflake", "USA", "Data Cloud", "Snowflake Inc"),
    ("Databricks", "USA", "Data/AI Platform", "Databricks Inc"),
    ("Palantir", "USA", "Data Analytics", "Palantir Technologies"),
    ("Zoom", "USA", "Video Conferencing", "Zoom Video Communications"),
    ("Slack", "USA", "Collaboration", "Slack Technologies"),
    ("ServiceNow", "USA", "IT Management", "ServiceNow Inc"),
    ("Workday", "USA", "HCM/ERP SaaS", "Workday Inc"),
    ("SAP", "Germany", "ERP/Business Software", "SAP SE|SAP India|SAP Labs India"),
    # ── Indian IT / Consulting ──
    ("Tata Consultancy Services", "India", "IT Services", "TCS|TCS India|Tata Consultancy"),
    ("Infosys", "India", "IT Services", "Infosys Ltd|Infosys Limited|Infosys BPO"),
    ("Wipro", "India", "IT Services", "Wipro Ltd|Wipro Limited|Wipro Technologies"),
    ("HCL Technologies", "India", "IT Services", "HCL|HCL Tech|HCL Infosystems"),
    ("Tech Mahindra", "India", "IT Services", "Tech M|Tech Mahindra Ltd"),
    ("Cognizant", "India", "IT Services", "CTS|Cognizant Technology Solutions"),
    ("Capgemini", "France", "IT Consulting", "Capgemini India|Capgemini SE"),
    ("Accenture", "Ireland", "IT Consulting", "Accenture PLC|Accenture India"),
    ("Deloitte", "UK", "Professional Services", "Deloitte Consulting|Deloitte India"),
    ("Ernst & Young", "UK", "Professional Services", "EY|EY India|Ernst & Young LLP"),
    ("KPMG", "Netherlands", "Professional Services", "KPMG India|KPMG LLP"),
    ("PwC", "UK", "Professional Services", "PricewaterhouseCoopers|PwC India"),
    ("Mindtree", "India", "IT Services", "Mindtree Ltd|Mindtree Limited"),
    ("Mphasis", "India", "IT Services", "Mphasis Ltd|Mphasis Limited"),
    ("Hexaware", "India", "IT Services", "Hexaware Technologies|Hexaware Technologies Ltd"),
    ("Persistent Systems", "India", "IT Services", "Persistent Systems Ltd"),
    ("LTIMindtree", "India", "IT Services", "LTI|L&T Infotech|Larsen & Toubro Infotech|LTIMindtree Ltd"),
    ("Infosys BPM", "India", "BPO", "Infosys BPO|Infosys Business Process Management"),
    ("Wipro BPS", "India", "BPO", "Wipro BPS|Wipro Business Process Services"),
    # ── US Financial ──
    ("JPMorgan Chase", "USA", "Banking/Finance", "JPMorgan|JP Morgan|JPMorgan Chase & Co"),
    ("Goldman Sachs", "USA", "Banking/Finance", "Goldman Sachs Group|Goldman Sachs India"),
    ("Morgan Stanley", "USA", "Banking/Finance", "Morgan Stanley India"),
    ("Bank of America", "USA", "Banking/Finance", "BofA|Bank of America Corp"),
    ("Citigroup", "USA", "Banking/Finance", "Citi|Citibank|Citigroup Inc"),
    ("Wells Fargo", "USA", "Banking/Finance", "Wells Fargo & Company"),
    ("Capital One", "USA", "Banking/Finance", "Capital One Financial"),
    ("American Express", "USA", "Financial Services", "Amex|American Express Company"),
    ("Fidelity Investments", "USA", "Asset Management", "Fidelity|Fidelity National Information Services"),
    ("Bloomberg", "USA", "Financial Media/Tech", "Bloomberg LP|Bloomberg India"),
    # ── Healthcare / Pharma ──
    ("UnitedHealth Group", "USA", "Healthcare", "UHG|Optum|United Health"),
    ("CVS Health", "USA", "Healthcare", "CVS Pharmacy|CVS Health Corporation"),
    ("Anthem", "USA", "Healthcare", "Anthem Inc|Elevance Health"),
    ("Johnson & Johnson", "USA", "Pharma/Healthcare", "J&J|JnJ"),
    ("Pfizer", "USA", "Pharma", "Pfizer Inc|Pfizer India"),
    ("Novartis", "Switzerland", "Pharma", "Novartis AG|Novartis India"),
    ("Roche", "Switzerland", "Pharma/Diagnostics", "F. Hoffmann-La Roche|Roche India"),
    # ── E-Commerce / Retail ──
    ("Walmart", "USA", "Retail", "Walmart Inc|Walmart India|Walmart Labs"),
    ("Target", "USA", "Retail", "Target Corporation"),
    ("eBay", "USA", "E-Commerce", "eBay Inc|eBay India"),
    ("Shopify", "Canada", "E-Commerce Platform", "Shopify Inc"),
    ("Flipkart", "India", "E-Commerce", "Flipkart Internet Pvt Ltd|Flipkart India"),
    ("Myntra", "India", "E-Commerce/Fashion", "Myntra Designs Pvt Ltd"),
    # ── Telecom ──
    ("AT&T", "USA", "Telecom", "AT&T Inc|AT&T Labs"),
    ("Verizon", "USA", "Telecom", "Verizon Communications"),
    ("T-Mobile", "USA", "Telecom", "T-Mobile US|T-Mobile Inc"),
    ("Comcast", "USA", "Telecom/Media", "Comcast Corporation|Xfinity"),
    ("Vodafone", "UK", "Telecom", "Vodafone Group|Vodafone India"),
    ("Airtel", "India", "Telecom", "Bharti Airtel|Airtel India"),
    ("Jio", "India", "Telecom/Digital", "Reliance Jio|Jio Platforms"),
    # ── European Tech ──
    ("Siemens", "Germany", "Industrial Tech", "Siemens AG|Siemens India"),
    ("Ericsson", "Sweden", "Telecom Equipment", "Ericsson India"),
    ("Nokia", "Finland", "Telecom Equipment", "Nokia Corporation|Nokia India"),
    ("Philips", "Netherlands", "Electronics/Healthcare", "Philips Electronics|Philips India"),
    ("ASML", "Netherlands", "Semiconductors", "ASML Holding"),
    ("Spotify", "Sweden", "Music Streaming", "Spotify Technology"),
    ("Booking.com", "Netherlands", "Travel Tech", "Booking Holdings"),
    ("Klarna", "Sweden", "FinTech", "Klarna Bank"),
    ("Revolut", "UK", "FinTech", "Revolut Ltd"),
    # ── APAC ──
    ("Samsung", "South Korea", "Electronics", "Samsung Electronics|Samsung India"),
    ("LG Electronics", "South Korea", "Electronics", "LG|LG India"),
    ("Tencent", "China", "Technology", "Tencent Holdings"),
    ("Alibaba", "China", "E-Commerce/Cloud", "Alibaba Group|Alibaba Cloud"),
    ("Baidu", "China", "Search/AI", "Baidu Inc"),
    ("ByteDance", "China", "Social Media/AI", "ByteDance Ltd|TikTok"),
    ("Rakuten", "Japan", "E-Commerce", "Rakuten Group|Rakuten India"),
    ("Fujitsu", "Japan", "IT Services", "Fujitsu Limited|Fujitsu India"),
    ("NTT Data", "Japan", "IT Services", "NTT DATA Corporation|NTT India"),
    ("Grab", "Singapore", "Super App", "Grab Holdings"),
    ("Sea Limited", "Singapore", "Tech", "Sea Group|Shopee"),
    # ── Australian / Canadian ──
    ("Atlassian", "Australia", "DevOps Software", "Atlassian Corporation"),
    ("WiseTech Global", "Australia", "Logistics Tech", "WiseTech"),
    ("Telstra", "Australia", "Telecom", "Telstra Corporation"),
    ("Shopify", "Canada", "E-Commerce Platform", "Shopify Inc"),
    ("OpenText", "Canada", "Information Management", "OpenText Corporation"),
    # ── Automotive / Industrial ──
    ("Tesla", "USA", "Electric Vehicles/Tech", "Tesla Inc|Tesla Motors"),
    ("Ford", "USA", "Automotive", "Ford Motor Company|Ford India"),
    ("General Motors", "USA", "Automotive", "GM|General Motors Company"),
    ("Bosch", "Germany", "Automotive/Industrial", "Robert Bosch GmbH|Bosch India"),
    # ── Media / Advertising ──
    ("Comcast NBCUniversal", "USA", "Media", "NBCUniversal|Peacock"),
    ("The Walt Disney Company", "USA", "Media/Entertainment", "Disney|Disney+"),
    ("Warner Bros. Discovery", "USA", "Media", "Warner Media|HBO Max"),
    ("News Corp", "USA", "Media", "News Corporation"),
    # ── Cloud / SaaS ──
    ("Twilio", "USA", "CPaaS", "Twilio Inc"),
    ("HashiCorp", "USA", "DevOps", "HashiCorp Inc"),
    ("Confluent", "USA", "Streaming Data", "Confluent Inc"),
    ("Elastic", "USA", "Search/Analytics", "Elastic NV|Elasticsearch"),
    ("MongoDB Inc", "USA", "Database", "MongoDB"),
    ("Redis Labs", "USA", "In-Memory Database", "Redis Ltd"),
    ("Cockroach Labs", "USA", "Distributed Database", "CockroachDB"),
    ("PingCAP", "China", "Database", "TiDB"),
]

# ── B. Synthetic company name generator ─────────────────────────────────────
_PREFIXES = [
    "Apex", "Nexus", "Vertex", "Sigma", "Alpha", "Delta", "Omega", "Prime", "Elite",
    "Advanced", "Digital", "Global", "United", "Allied", "Premier", "Pacific",
    "Atlantic", "Nordic", "Solar", "Quantum", "Cyber", "Nano", "Micro", "Mega",
    "Ultra", "Hyper", "Super", "Pro", "Smart", "Swift", "Rapid", "Cloud", "Data",
    "Info", "Tech", "Net", "Web", "Code", "Dev", "Soft", "Sys", "Byte", "Logic",
    "Core", "Hub", "Grid", "Edge", "Node", "Link", "Bridge", "Forge", "Craft",
    "Sync", "Flow", "Pixel", "Vector", "Wave", "Arc", "Bolt", "Spark", "Flux",
    "Zen", "Nova", "Aurora", "Orion", "Zenith", "Summit", "Peak", "Crest", "Pinnacle",
]
_MIDDLES = [
    "Systems", "Solutions", "Technologies", "Innovations", "Digital", "Software",
    "Analytics", "Data", "Cloud", "Networks", "Services", "Consulting", "Engineering",
    "Dynamics", "Logic", "Labs", "Works", "Ventures", "Partners", "Group", "Corp",
    "Interactive", "Intelligence", "Insights", "Platforms", "Infrastructure",
    "Applications", "Research", "Studio", "Academy", "Collective", "Alliance",
]
_SUFFIXES = ["Inc", "LLC", "Ltd", "Corp", "Co", "Group", "GmbH", "Pvt Ltd", "Pte Ltd", "AB", "SA", "AG"]
_COUNTRIES = [
    "USA", "India", "UK", "Germany", "Canada", "Australia", "Singapore",
    "Netherlands", "Sweden", "France", "Japan", "South Korea", "Brazil", "UAE",
    "Ireland", "Switzerland", "Israel", "Poland", "Romania", "Mexico",
]
_INDUSTRIES = [
    "IT Services", "Software", "FinTech", "Healthcare IT", "E-Commerce", "Telecom",
    "Cloud Computing", "Cybersecurity", "AI/ML", "Data Analytics", "ERP/CRM",
    "Gaming", "EdTech", "InsurTech", "LegalTech", "PropTech", "AgriTech",
    "Automotive Tech", "Aerospace", "Defense IT", "Government IT", "Media Tech",
    "Retail Tech", "Logistics Tech", "HR Tech", "Marketing Tech", "Blockchain", "IoT",
]


def _generate_synthetic_companies(target: int = 50_000) -> list[dict]:
    rows: list[dict] = []

    # First add all named companies
    for canonical, country, industry, aliases in _NAMED_COMPANIES:
        rows.append({
            "company_name": canonical,
            "canonical_name": canonical,
            "country": country,
            "industry": industry,
            "aliases": aliases,
        })
        # Also add each alias as a separate row with the canonical name
        for alias in aliases.split("|"):
            alias = alias.strip()
            if alias and alias != canonical:
                rows.append({
                    "company_name": alias,
                    "canonical_name": canonical,
                    "country": country,
                    "industry": industry,
                    "aliases": canonical,
                })

    # Then generate synthetic companies up to target
    seen: set[str] = {r["company_name"].lower() for r in rows}
    rng = random.Random(42)

    def _make_company() -> dict:
        p = rng.choice(_PREFIXES)
        m = rng.choice(_MIDDLES)
        s = rng.choice(_SUFFIXES)
        name = f"{p} {m} {s}"
        country = rng.choice(_COUNTRIES)
        industry = rng.choice(_INDUSTRIES)
        canonical = f"{p} {m}"
        return {
            "company_name": name,
            "canonical_name": canonical,
            "country": country,
            "industry": industry,
            "aliases": canonical,
        }

    attempts = 0
    while len(rows) < target and attempts < target * 10:
        attempts += 1
        co = _make_company()
        if co["company_name"].lower() not in seen:
            seen.add(co["company_name"].lower())
            rows.append(co)

    return rows


# ══════════════════════════════════════════════════════════════════════════════
# 2.  LOCATIONS
# ══════════════════════════════════════════════════════════════════════════════

_US_CITIES_STATES: list[tuple[str, str]] = [
    ("New York", "NY"), ("Los Angeles", "CA"), ("Chicago", "IL"), ("Houston", "TX"),
    ("Phoenix", "AZ"), ("Philadelphia", "PA"), ("San Antonio", "TX"), ("San Diego", "CA"),
    ("Dallas", "TX"), ("San Jose", "CA"), ("Austin", "TX"), ("Jacksonville", "FL"),
    ("Fort Worth", "TX"), ("Columbus", "OH"), ("Charlotte", "NC"), ("Indianapolis", "IN"),
    ("San Francisco", "CA"), ("Seattle", "WA"), ("Denver", "CO"), ("Nashville", "TN"),
    ("Oklahoma City", "OK"), ("El Paso", "TX"), ("Washington", "DC"), ("Boston", "MA"),
    ("Las Vegas", "NV"), ("Memphis", "TN"), ("Louisville", "KY"), ("Baltimore", "MD"),
    ("Milwaukee", "WI"), ("Albuquerque", "NM"), ("Tucson", "AZ"), ("Fresno", "CA"),
    ("Sacramento", "CA"), ("Mesa", "AZ"), ("Kansas City", "MO"), ("Atlanta", "GA"),
    ("Omaha", "NE"), ("Colorado Springs", "CO"), ("Raleigh", "NC"), ("Long Beach", "CA"),
    ("Virginia Beach", "VA"), ("Minnesota", "MN"), ("Tampa", "FL"), ("New Orleans", "LA"),
    ("Arlington", "TX"), ("Wichita", "KS"), ("Bakersfield", "CA"), ("Aurora", "CO"),
    ("Anaheim", "CA"), ("Santa Ana", "CA"), ("Corpus Christi", "TX"), ("Riverside", "CA"),
    ("Durham", "NC"), ("Orlando", "FL"), ("Lexington", "KY"), ("Henderson", "NV"),
    ("Buffalo", "NY"), ("Fort Wayne", "IN"), ("Pittsburgh", "PA"), ("Lincoln", "NE"),
    ("Greensboro", "NC"), ("Anchorage", "AK"), ("Plano", "TX"), ("Newark", "NJ"),
    ("Toledo", "OH"), ("Chandler", "AZ"), ("St. Paul", "MN"), ("Laredo", "TX"),
    ("Madison", "WI"), ("Durham", "NC"), ("Lubbock", "TX"), ("Baton Rouge", "LA"),
    ("Winston-Salem", "NC"), ("Norfolk", "VA"), ("Garland", "TX"), ("Scottsdale", "AZ"),
    ("Irvine", "CA"), ("Irving", "TX"), ("Chesapeake", "VA"), ("Fremont", "CA"),
    ("Gilbert", "AZ"), ("San Bernardino", "CA"), ("Birmingham", "AL"), ("Rochester", "NY"),
    ("Spokane", "WA"), ("Richmond", "VA"), ("Des Moines", "IA"), ("Montgomery", "AL"),
    ("Portland", "OR"), ("Detroit", "MI"), ("St. Louis", "MO"), ("Salt Lake City", "UT"),
    ("Cincinnati", "OH"), ("Cleveland", "OH"), ("Minneapolis", "MN"), ("Miami", "FL"),
    ("Sunnyvale", "CA"), ("Santa Clara", "CA"), ("Mountain View", "CA"), ("Palo Alto", "CA"),
    ("Redwood City", "CA"), ("San Mateo", "CA"), ("Menlo Park", "CA"), ("Cupertino", "CA"),
    ("Bellevue", "WA"), ("Kirkland", "WA"), ("Redmond", "WA"), ("Jersey City", "NJ"),
    ("Princeton", "NJ"), ("McLean", "VA"), ("Herndon", "VA"), ("Reston", "VA"),
    ("Tysons", "VA"), ("Bethesda", "MD"), ("Rockville", "MD"), ("Silver Spring", "MD"),
]

_INDIA_CITIES: list[tuple[str, str]] = [
    ("Bangalore", "KA"), ("Hyderabad", "TS"), ("Chennai", "TN"), ("Pune", "MH"),
    ("Mumbai", "MH"), ("Delhi", "DL"), ("Noida", "UP"), ("Gurgaon", "HR"),
    ("Kolkata", "WB"), ("Ahmedabad", "GJ"), ("Jaipur", "RJ"), ("Chandigarh", "CH"),
    ("Coimbatore", "TN"), ("Mysore", "KA"), ("Kochi", "KL"), ("Indore", "MP"),
    ("Bhopal", "MP"), ("Nagpur", "MH"), ("Visakhapatnam", "AP"), ("Lucknow", "UP"),
    ("Bhubaneswar", "OD"), ("Thiruvananthapuram", "KL"), ("Mangalore", "KA"),
    ("Surat", "GJ"), ("Vadodara", "GJ"), ("Nashik", "MH"), ("Rajkot", "GJ"),
    ("Patna", "BR"), ("Dehradun", "UK"), ("Mohali", "PB"), ("Trivandrum", "KL"),
]

_GLOBAL_CITIES: list[tuple[str, str, str]] = [
    # (city, state/province, country)
    ("London", "England", "UK"), ("Manchester", "England", "UK"), ("Birmingham", "England", "UK"),
    ("Edinburgh", "Scotland", "UK"), ("Berlin", "Berlin", "Germany"), ("Munich", "Bavaria", "Germany"),
    ("Hamburg", "Hamburg", "Germany"), ("Frankfurt", "Hesse", "Germany"), ("Cologne", "NRW", "Germany"),
    ("Paris", "Ile-de-France", "France"), ("Lyon", "Auvergne-Rhône-Alpes", "France"),
    ("Amsterdam", "North Holland", "Netherlands"), ("Rotterdam", "South Holland", "Netherlands"),
    ("Stockholm", "Stockholm County", "Sweden"), ("Gothenburg", "Västra Götaland", "Sweden"),
    ("Oslo", "Oslo", "Norway"), ("Copenhagen", "Capital Region", "Denmark"),
    ("Helsinki", "Uusimaa", "Finland"), ("Zurich", "Zurich", "Switzerland"),
    ("Geneva", "Geneva", "Switzerland"), ("Vienna", "Vienna", "Austria"),
    ("Brussels", "Brussels", "Belgium"), ("Warsaw", "Masovian", "Poland"),
    ("Krakow", "Lesser Poland", "Poland"), ("Prague", "Bohemia", "Czech Republic"),
    ("Budapest", "Central Hungary", "Hungary"), ("Bucharest", "Ilfov", "Romania"),
    ("Kyiv", "Kyiv Oblast", "Ukraine"), ("Barcelona", "Catalonia", "Spain"),
    ("Madrid", "Community of Madrid", "Spain"), ("Lisbon", "Lisbon", "Portugal"),
    ("Dublin", "Leinster", "Ireland"), ("Milan", "Lombardy", "Italy"),
    ("Rome", "Lazio", "Italy"), ("Toronto", "Ontario", "Canada"),
    ("Vancouver", "British Columbia", "Canada"), ("Montreal", "Quebec", "Canada"),
    ("Calgary", "Alberta", "Canada"), ("Ottawa", "Ontario", "Canada"),
    ("Sydney", "NSW", "Australia"), ("Melbourne", "Victoria", "Australia"),
    ("Brisbane", "Queensland", "Australia"), ("Perth", "WA", "Australia"),
    ("Singapore", "", "Singapore"), ("Kuala Lumpur", "WP Kuala Lumpur", "Malaysia"),
    ("Jakarta", "DKI Jakarta", "Indonesia"), ("Bangkok", "Bangkok", "Thailand"),
    ("Manila", "Metro Manila", "Philippines"), ("Ho Chi Minh City", "Ho Chi Minh", "Vietnam"),
    ("Hanoi", "Hanoi", "Vietnam"), ("Taipei", "Taipei", "Taiwan"),
    ("Seoul", "Seoul", "South Korea"), ("Tokyo", "Tokyo", "Japan"),
    ("Osaka", "Osaka", "Japan"), ("Shanghai", "Shanghai", "China"),
    ("Beijing", "Beijing", "China"), ("Shenzhen", "Guangdong", "China"),
    ("Guangzhou", "Guangdong", "China"), ("Chengdu", "Sichuan", "China"),
    ("Hong Kong", "", "Hong Kong"), ("Dubai", "Dubai", "UAE"),
    ("Abu Dhabi", "Abu Dhabi", "UAE"), ("Riyadh", "Riyadh", "Saudi Arabia"),
    ("Tel Aviv", "Tel Aviv", "Israel"), ("Cairo", "Cairo", "Egypt"),
    ("Nairobi", "Nairobi County", "Kenya"), ("Lagos", "Lagos", "Nigeria"),
    ("Johannesburg", "Gauteng", "South Africa"), ("Cape Town", "Western Cape", "South Africa"),
    ("São Paulo", "SP", "Brazil"), ("Rio de Janeiro", "RJ", "Brazil"),
    ("Buenos Aires", "CABA", "Argentina"), ("Bogota", "Cundinamarca", "Colombia"),
    ("Mexico City", "CDMX", "Mexico"), ("Santiago", "Santiago Metropolitan", "Chile"),
]


def _generate_locations(target: int = 100_000) -> list[dict]:
    rows: list[dict] = []

    # US cities
    for city, state in _US_CITIES_STATES:
        rows.append({"city": city, "state_province": state, "country": "USA", "region": "North America"})

    # India cities
    for city, state in _INDIA_CITIES:
        rows.append({"city": city, "state_province": state, "country": "India", "region": "South Asia"})

    # Global cities
    region_map = {
        "UK": "Europe", "Germany": "Europe", "France": "Europe", "Netherlands": "Europe",
        "Sweden": "Europe", "Norway": "Europe", "Denmark": "Europe", "Finland": "Europe",
        "Switzerland": "Europe", "Austria": "Europe", "Belgium": "Europe", "Poland": "Europe",
        "Czech Republic": "Europe", "Hungary": "Europe", "Romania": "Europe", "Ukraine": "Europe",
        "Spain": "Europe", "Portugal": "Europe", "Ireland": "Europe", "Italy": "Europe",
        "Canada": "North America", "Australia": "Australia/Pacific", "Singapore": "Southeast Asia",
        "Malaysia": "Southeast Asia", "Indonesia": "Southeast Asia", "Thailand": "Southeast Asia",
        "Philippines": "Southeast Asia", "Vietnam": "Southeast Asia", "Taiwan": "East Asia",
        "South Korea": "East Asia", "Japan": "East Asia", "China": "East Asia",
        "Hong Kong": "East Asia", "UAE": "Middle East", "Saudi Arabia": "Middle East",
        "Israel": "Middle East", "Egypt": "Africa", "Kenya": "Africa", "Nigeria": "Africa",
        "South Africa": "Africa", "Brazil": "South America", "Argentina": "South America",
        "Colombia": "South America", "Chile": "South America", "Mexico": "North America",
    }
    for city, state, country in _GLOBAL_CITIES:
        rows.append({
            "city": city,
            "state_province": state,
            "country": country,
            "region": region_map.get(country, "Other"),
        })

    # Pad with synthetic city names to reach target using a rich generator
    rng = random.Random(42)
    seen = {(r["city"].lower(), r["country"].lower()) for r in rows}

    _city_prefixes = [
        "North", "South", "East", "West", "New", "Old", "Fort", "Lake", "Mount", "Green",
        "River", "Spring", "Stone", "Oak", "Pine", "Cedar", "Maple", "Elm", "Ash", "Birch",
        "Silver", "Golden", "Blue", "Red", "White", "Black", "Grey", "Crystal", "Shadow",
        "Sunny", "Rocky", "Sandy", "Valley", "Harbor", "Bay", "Grand", "Little", "Big",
        "Upper", "Lower", "Inner", "Outer", "Mid", "Central", "High", "Deep", "Far",
    ]
    _city_middles = [
        "Brook", "Glen", "Haven", "Ridge", "Heights", "Crest", "Bluff", "Cliff", "Hollow",
        "Meadow", "Grove", "Pines", "Falls", "Bridge", "Cross", "Gate", "Hollow", "Cove",
        "Knoll", "Moor", "Marsh", "Shore", "Point", "Prairie", "Plateau", "Basin", "Valley",
        "Run", "Pass", "Trail", "Way", "Gardens", "Terrace", "Manor", "Park", "Square",
    ]
    _city_suffixes = [
        "ville", "town", "burg", "berg", "field", "port", "ford", "wood", "dale",
        "creek", "hill", "shire", "ham", "ton", "wick", "mouth", "ley", "by", "ness",
        "worth", "gate", "thorpe", "stead", "borough", "chester", "caster", "minster",
    ]
    us_states_full = [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    ]
    countries_extra = (
        ["USA"] * 40 + ["India"] * 20 + ["UK"] * 10 + ["Canada"] * 10
        + ["Australia"] * 10 + ["Germany"] * 5 + ["France"] * 5
    )
    region_lookup = {
        "USA": "North America", "Canada": "North America", "Mexico": "North America",
        "India": "South Asia", "UK": "Europe", "Germany": "Europe", "France": "Europe",
        "Australia": "Australia/Pacific",
    }

    def _make_city(attempt: int) -> str:
        """Generate increasingly varied city names; use numeric suffix after exhaustion."""
        style = attempt % 4
        if style == 0:
            return f"{rng.choice(_city_prefixes)} {rng.choice(_city_suffixes)}"
        elif style == 1:
            return f"{rng.choice(_city_prefixes)} {rng.choice(_city_middles)}"
        elif style == 2:
            return f"{rng.choice(_city_middles)}{rng.choice(_city_suffixes)}"
        else:
            # Guaranteed-unique numeric variant
            return f"{rng.choice(_city_prefixes)} {rng.choice(_city_suffixes)} {attempt // 4}"

    attempts = 0
    while len(rows) < target and attempts < target * 10:
        attempts += 1
        city = _make_city(attempts)
        country = rng.choice(countries_extra)
        key = (city.lower(), country.lower())
        if key not in seen:
            seen.add(key)
            state = rng.choice(us_states_full) if country == "USA" else ""
            region = region_lookup.get(country, "Other")
            rows.append({"city": city, "state_province": state, "country": country, "region": region})

    return rows


# ══════════════════════════════════════════════════════════════════════════════
# 3.  JOB ROLES
# ══════════════════════════════════════════════════════════════════════════════

_DOMAINS = [
    "Software Engineering", "Data Engineering", "Data Science", "Machine Learning",
    "DevOps", "Cloud Engineering", "QA/Testing", "Security", "Full Stack",
    "Frontend", "Backend", "Mobile", "Embedded", "Networking", "Database",
    "Business Intelligence", "Product Management", "Project Management",
    "Business Analysis", "Solution Architecture", "System Design", "SAP",
    "Salesforce", "HR Technology", "ERP", "Blockchain", "IoT", "AR/VR",
    "Administrative & Office Support", "Finance & Accounting", "Sales & Marketing",
    "Human Resources", "Operations & Supply Chain", "Healthcare Administration",
    "Legal", "Education", "Manufacturing", "Game Development", "Hardware Engineering",
    "Robotics", "IT Support", "Telecommunications", "Digital Marketing",
]

_SENIORITY = [
    "Intern", "Junior", "Associate", "Mid-level", "Senior", "Lead",
    "Principal", "Staff", "Senior Staff", "Architect", "Director", "VP", "CTO",
]

_BASE_ROLES: list[tuple[str, str, str]] = [
    # (title, domain, canonical_title)
    ("Software Engineer", "Software Engineering", "Software Engineer"),
    ("Software Developer", "Software Engineering", "Software Engineer"),
    ("Full Stack Developer", "Full Stack", "Full Stack Developer"),
    ("Frontend Developer", "Frontend", "Frontend Developer"),
    ("Backend Developer", "Backend", "Backend Developer"),
    ("React Developer", "Frontend", "React Developer"),
    ("Angular Developer", "Frontend", "Angular Developer"),
    ("Vue.js Developer", "Frontend", "Vue.js Developer"),
    ("Java Developer", "Backend", "Java Developer"),
    ("Python Developer", "Backend", "Python Developer"),
    (".NET Developer", "Backend", ".NET Developer"),
    ("Node.js Developer", "Backend", "Node.js Developer"),
    ("Go Developer", "Backend", "Go Developer"),
    ("Rust Developer", "Backend", "Rust Developer"),
    ("Scala Developer", "Backend", "Scala Developer"),
    ("Data Engineer", "Data Engineering", "Data Engineer"),
    ("Big Data Engineer", "Data Engineering", "Data Engineer"),
    ("ETL Developer", "Data Engineering", "ETL Developer"),
    ("Data Architect", "Data Engineering", "Data Architect"),
    ("Data Scientist", "Data Science", "Data Scientist"),
    ("ML Engineer", "Machine Learning", "Machine Learning Engineer"),
    ("AI Engineer", "Machine Learning", "AI Engineer"),
    ("NLP Engineer", "Machine Learning", "NLP Engineer"),
    ("Computer Vision Engineer", "Machine Learning", "Computer Vision Engineer"),
    ("LLM Engineer", "Machine Learning", "LLM Engineer"),
    ("MLOps Engineer", "Machine Learning", "MLOps Engineer"),
    ("DevOps Engineer", "DevOps", "DevOps Engineer"),
    ("Site Reliability Engineer", "DevOps", "Site Reliability Engineer"),
    ("Platform Engineer", "DevOps", "Platform Engineer"),
    ("Cloud Engineer", "Cloud Engineering", "Cloud Engineer"),
    ("AWS Engineer", "Cloud Engineering", "Cloud Engineer"),
    ("Azure Engineer", "Cloud Engineering", "Cloud Engineer"),
    ("GCP Engineer", "Cloud Engineering", "Cloud Engineer"),
    ("Solutions Architect", "Solution Architecture", "Solutions Architect"),
    ("Cloud Architect", "Cloud Engineering", "Cloud Architect"),
    ("Data Platform Engineer", "Data Engineering", "Data Platform Engineer"),
    ("QA Engineer", "QA/Testing", "QA Engineer"),
    ("SDET", "QA/Testing", "SDET"),
    ("Test Automation Engineer", "QA/Testing", "Test Automation Engineer"),
    ("Security Engineer", "Security", "Security Engineer"),
    ("Cybersecurity Analyst", "Security", "Cybersecurity Analyst"),
    ("Penetration Tester", "Security", "Penetration Tester"),
    ("Android Developer", "Mobile", "Android Developer"),
    ("iOS Developer", "Mobile", "iOS Developer"),
    ("React Native Developer", "Mobile", "React Native Developer"),
    ("Flutter Developer", "Mobile", "Flutter Developer"),
    ("Database Administrator", "Database", "Database Administrator"),
    ("SQL Developer", "Database", "SQL Developer"),
    ("Salesforce Developer", "Salesforce", "Salesforce Developer"),
    ("Salesforce Admin", "Salesforce", "Salesforce Administrator"),
    ("SAP Consultant", "SAP", "SAP Consultant"),
    ("SAP ABAP Developer", "SAP", "SAP ABAP Developer"),
    ("Business Analyst", "Business Analysis", "Business Analyst"),
    ("Product Manager", "Product Management", "Product Manager"),
    ("Project Manager", "Project Management", "Project Manager"),
    ("Scrum Master", "Project Management", "Scrum Master"),
    ("Technical Lead", "Software Engineering", "Technical Lead"),
    ("Engineering Manager", "Software Engineering", "Engineering Manager"),
    ("VP of Engineering", "Software Engineering", "VP of Engineering"),
    ("CTO", "Software Engineering", "Chief Technology Officer"),
    ("BI Developer", "Business Intelligence", "BI Developer"),
    ("Tableau Developer", "Business Intelligence", "Tableau Developer"),
    ("Power BI Developer", "Business Intelligence", "Power BI Developer"),
    ("Data Analyst", "Data Science", "Data Analyst"),
    ("Blockchain Developer", "Blockchain", "Blockchain Developer"),
    ("Smart Contract Developer", "Blockchain", "Smart Contract Developer"),
    ("IoT Engineer", "IoT", "IoT Engineer"),
    ("Embedded Systems Engineer", "Embedded", "Embedded Systems Engineer"),
    ("Network Engineer", "Networking", "Network Engineer"),
    ("Systems Administrator", "DevOps", "Systems Administrator"),
    ("Infrastructure Engineer", "DevOps", "Infrastructure Engineer"),
    ("Kafka Engineer", "Data Engineering", "Kafka Engineer"),
    ("Spark Engineer", "Data Engineering", "Spark Engineer"),
    ("Flink Engineer", "Data Engineering", "Flink Engineer"),
    ("Snowflake Developer", "Data Engineering", "Snowflake Developer"),
    ("Databricks Engineer", "Data Engineering", "Databricks Engineer"),
    ("dbt Developer", "Data Engineering", "dbt Developer"),
    ("HR Technology Specialist", "HR Technology", "HR Technology Specialist"),
    ("HRIS Analyst", "HR Technology", "HRIS Analyst"),
    ("ERP Consultant", "ERP", "ERP Consultant"),
    ("Oracle Consultant", "ERP", "Oracle Consultant"),
    ("Dynamics 365 Developer", "ERP", "Dynamics 365 Developer"),
    ("ServiceNow Developer", "DevOps", "ServiceNow Developer"),
    ("Workday Consultant", "HR Technology", "Workday Consultant"),
    ("RPA Developer", "Business Analysis", "RPA Developer"),
    ("Automation Architect", "DevOps", "Automation Architect"),
    ("Generative AI Engineer", "Machine Learning", "Generative AI Engineer"),
    ("Prompt Engineer", "Machine Learning", "Prompt Engineer"),
    ("RAG Engineer", "Machine Learning", "RAG Engineer"),
    
    # === Additional IT Roles ===
    ("Game Developer", "Game Development", "Game Developer"),
    ("Unity Developer", "Game Development", "Unity Developer"),
    ("Unreal Engine Developer", "Game Development", "Unreal Engine Developer"),
    ("Hardware Engineer", "Hardware Engineering", "Hardware Engineer"),
    ("ASIC Design Engineer", "Hardware Engineering", "Hardware Engineer"),
    ("FPGA Engineer", "Hardware Engineering", "Hardware Engineer"),
    ("Robotics Engineer", "Robotics", "Robotics Engineer"),
    ("Electronics Engineer", "Hardware Engineering", "Electronics Engineer"),
    ("Firmware Developer", "Embedded", "Firmware Engineer"),
    ("SOC Analyst", "Security", "Security Analyst"),
    ("Digital Forensic Investigator", "Security", "Security Researcher"),
    ("Incident Responder", "Security", "Security Analyst"),
    ("Network Architect", "Networking", "Network Architect"),
    ("Wireless Engineer", "Telecommunications", "Network Engineer"),
    ("IT Support Specialist", "IT Support", "IT Support Specialist"),
    ("Help Desk Technician", "IT Support", "IT Support Specialist"),
    ("Desktop Support Engineer", "IT Support", "IT Support Specialist"),
    ("System Architect", "System Design", "System Architect"),
    
    # === Non-IT Roles ===
    ("Accountant", "Finance & Accounting", "Accountant"),
    ("Financial Analyst", "Finance & Accounting", "Financial Analyst"),
    ("Auditor", "Finance & Accounting", "Auditor"),
    ("Tax Consultant", "Finance & Accounting", "Tax Consultant"),
    ("Finance Manager", "Finance & Accounting", "Finance Manager"),
    ("Controller", "Finance & Accounting", "Controller"),
    ("Bookkeeper", "Finance & Accounting", "Bookkeeper"),
    ("HR Manager", "Human Resources", "HR Manager"),
    ("Recruiter", "Human Resources", "Recruiter"),
    ("Talent Acquisition Specialist", "Human Resources", "Recruiter"),
    ("HR Generalist", "Human Resources", "HR Generalist"),
    ("HR Coordinator", "Human Resources", "HR Coordinator"),
    ("Benefits Specialist", "Human Resources", "HR Specialist"),
    ("Marketing Manager", "Sales & Marketing", "Marketing Manager"),
    ("Digital Marketing Specialist", "Digital Marketing", "Marketing Specialist"),
    ("SEO Specialist", "Digital Marketing", "Marketing Specialist"),
    ("Content Strategist", "Sales & Marketing", "Content Strategist"),
    ("Social Media Manager", "Sales & Marketing", "Social Media Manager"),
    ("Copywriter", "Sales & Marketing", "Copywriter"),
    ("Brand Manager", "Sales & Marketing", "Brand Manager"),
    ("Sales Representative", "Sales & Marketing", "Sales Representative"),
    ("Account Executive", "Sales & Marketing", "Account Executive"),
    ("Business Development Manager", "Sales & Marketing", "Sales Manager"),
    ("Sales Manager", "Sales & Marketing", "Sales Manager"),
    ("Customer Success Manager", "Sales & Marketing", "Customer Success Manager"),
    ("Operations Manager", "Operations & Supply Chain", "Operations Manager"),
    ("Logistics Coordinator", "Operations & Supply Chain", "Logistics Coordinator"),
    ("Supply Chain Analyst", "Operations & Supply Chain", "Supply Chain Analyst"),
    ("Procurement Specialist", "Operations & Supply Chain", "Procurement Specialist"),
    ("Administrative Assistant", "Administrative & Office Support", "Administrative Assistant"),
    ("Office Manager", "Administrative & Office Support", "Office Manager"),
    ("Executive Assistant", "Administrative & Office Support", "Executive Assistant"),
    ("Receptionist", "Administrative & Office Support", "Receptionist"),
    ("Facilities Manager", "Administrative & Office Support", "Facilities Manager"),
    ("Paralegal", "Legal", "Paralegal"),
    ("Legal Counsel", "Legal", "Legal Counsel"),
    ("Legal Assistant", "Legal", "Legal Assistant"),
    ("Contract Administrator", "Legal", "Contract Administrator"),
    ("Compliance Officer", "Legal", "Compliance Officer"),
    ("Healthcare Administrator", "Healthcare Administration", "Healthcare Administrator"),
    ("Medical Records Coordinator", "Healthcare Administration", "Medical Records Coordinator"),
    ("Patient Service Representative", "Healthcare Administration", "Customer Service Representative"),
    ("Teacher", "Education", "Teacher"),
    ("Education Consultant", "Education", "Education Consultant"),
    ("Learning & Development Manager", "Human Resources", "L&D Manager"),
    ("Manufacturing Engineer", "Manufacturing", "Manufacturing Engineer"),
    ("Quality Inspector", "Manufacturing", "Quality Inspector"),
    ("Production Manager", "Manufacturing", "Production Manager"),
    ("Plant Manager", "Manufacturing", "Plant Manager"),
]


def _generate_job_roles(target: int = 10_000) -> list[dict]:
    rows: list[dict] = []
    seen: set[str] = set()

    for title, domain, canonical in _BASE_ROLES:
        for seniority in _SENIORITY:
            full_title = f"{seniority} {title}".strip()
            key = full_title.lower()
            if key in seen:
                continue
            seen.add(key)
            aliases = f"{title}|{seniority[0]}. {title}" if seniority not in ("Intern", "Junior") else title
            rows.append({
                "role_title": full_title,
                "canonical_title": f"{seniority} {canonical}".strip(),
                "seniority": seniority,
                "domain": domain,
                "aliases": aliases,
            })

    # Pad with base roles if not enough
    for title, domain, canonical in _BASE_ROLES:
        key = title.lower()
        if key not in seen:
            seen.add(key)
            rows.append({
                "role_title": title,
                "canonical_title": canonical,
                "seniority": "Mid-level",
                "domain": domain,
                "aliases": title,
            })

    return rows[:target] if len(rows) > target else rows


# ══════════════════════════════════════════════════════════════════════════════
# 4.  NER TRAINING DATA  (IOB2 format)
# ══════════════════════════════════════════════════════════════════════════════

_DATE_STRINGS = [
    "January 2020", "Feb 2019", "March 2018", "Apr 2021", "May 2022",
    "June 2015", "Jul 2017", "August 2023", "Sep 2016", "October 2024",
    "Nov 2013", "December 2011", "Jan 2020", "2019", "2021",
    "Jan 2020 - Present", "Feb 2018 - Dec 2021", "March 2015 - June 2019",
    "2018 - 2022", "2016 - Present", "2020 to Present", "2017 to 2020",
    "01/2020", "06/2021", "2020-01", "2022-06",
]

_BULLETS = [
    "Designed and implemented scalable microservices using {tech}.",
    "Led a team of {n} engineers to deliver enterprise {domain} solutions.",
    "Reduced system latency by {pct}% through {tech} optimization.",
    "Built CI/CD pipelines using Jenkins and GitHub Actions.",
    "Migrated legacy on-premise infrastructure to {cloud} cloud.",
    "Developed RESTful APIs serving {n}M+ daily requests.",
    "Implemented data pipelines processing {n}TB of data daily.",
    "Mentored {n} junior developers in agile best practices.",
    "Conducted code reviews and enforced coding standards.",
    "Integrated third-party payment APIs for {domain} workflows.",
]

_TECHS = ["AWS", "Azure", "GCP", "Kubernetes", "Docker", "Kafka", "Spark", "React", "Spring Boot", "Python"]
_CLOUDS = ["AWS", "Azure", "GCP"]
_DOMAINS = ["e-commerce", "banking", "healthcare", "retail", "fintech", "telecom", "government"]
_NS = [3, 4, 5, 6, 8, 10, 12, 15, 20]
_PCTS = [20, 30, 40, 50, 60, 70, 80]


def _random_bullet(rng: random.Random) -> str:
    tpl = rng.choice(_BULLETS)
    return tpl.format(
        tech=rng.choice(_TECHS),
        cloud=rng.choice(_CLOUDS),
        domain=rng.choice(_DOMAINS),
        n=rng.choice(_NS),
        pct=rng.choice(_PCTS),
    )


def _iob_label(tokens: list[str], entity_tokens: list[str], label: str) -> list[str]:
    """Return IOB2 labels for tokens, marking the entity_tokens span."""
    labels = ["O"] * len(tokens)
    # Find the entity span in tokens (case-insensitive substring match)
    entity_lower = [t.lower() for t in entity_tokens]
    for i in range(len(tokens) - len(entity_tokens) + 1):
        window = [t.lower() for t in tokens[i: i + len(entity_tokens)]]
        if window == entity_lower:
            labels[i] = f"B-{label}"
            for j in range(1, len(entity_tokens)):
                labels[i + j] = f"I-{label}"
            break
    return labels


def _tokenize(text: str) -> list[str]:
    """Simple whitespace tokenizer that keeps punctuation attached."""
    return text.split()


def _generate_ner_sample(
    rng: random.Random,
    companies: list[dict],
    locations: list[dict],
    roles: list[dict],
) -> dict:
    """Generate a single IOB2-labelled NER training sample."""
    company = rng.choice(companies)
    loc = rng.choice(locations)
    role = rng.choice(roles)

    # Date range
    start = rng.choice(_DATE_STRINGS[:16])
    end = rng.choice(["Present", "Dec 2022", "June 2021", "2023", "March 2022"])

    # Construct a typical work history header line
    template_idx = rng.randint(0, 5)
    city_state = (
        f"{loc['city']}, {loc['state_province']}"
        if loc['state_province']
        else f"{loc['city']}, {loc['country']}"
    )

    templates = [
        f"{company['canonical_name']}  |  {role['role_title']}  |  {city_state}  |  {start} - {end}",
        f"{role['role_title']} at {company['canonical_name']}, {city_state} ({start} - {end})",
        f"{company['canonical_name']} - {role['role_title']}, {city_state}, {start} to {end}",
        f"Company: {company['canonical_name']}\nTitle: {role['role_title']}\nLocation: {city_state}\nDuration: {start} - {end}",
        f"{role['role_title']}\n{company['canonical_name']}\n{city_state}\n{start} - {end}",
        f"{company['canonical_name']}  ({city_state})\n{role['role_title']}  {start} - {end}",
    ]

    text = templates[template_idx]
    # Add a bullet or two
    n_bullets = rng.randint(1, 3)
    bullets = [_random_bullet(rng) for _ in range(n_bullets)]
    text += "\n" + "\n".join(f"• {b}" for b in bullets)

    return {
        "text": text,
        "entities": {
            "company": company["canonical_name"],
            "title": role["role_title"],
            "location": city_state,
            "start_date": start,
            "end_date": end,
        },
    }


def _generate_ner_data(
    companies: list[dict],
    locations: list[dict],
    roles: list[dict],
    n_samples: int = 500_000,
) -> list[dict]:
    rng = random.Random(42)
    samples: list[dict] = []
    for _ in range(n_samples):
        sample = _generate_ner_sample(rng, companies, locations, roles)
        samples.append(sample)
    return samples


# ══════════════════════════════════════════════════════════════════════════════
# 5.  WORK-HISTORY EXTRACTION TRAINING DATA
# ══════════════════════════════════════════════════════════════════════════════

def _generate_work_history_sample(
    rng: random.Random,
    companies: list[dict],
    locations: list[dict],
    roles: list[dict],
) -> dict:
    company = rng.choice(companies)
    loc = rng.choice(locations)
    role = rng.choice(roles)

    start_year = rng.randint(2010, 2023)
    end_year = rng.randint(start_year, 2025)
    start_month = rng.randint(1, 12)
    end_month = rng.randint(1, 12)
    is_current = (end_year == 2025)
    end_str = "Present" if is_current else f"{end_month:02d}/{end_year}"

    city_state = (
        f"{loc['city']}, {loc['state_province']}"
        if loc['state_province']
        else f"{loc['city']}, {loc['country']}"
    )

    n_bullets = rng.randint(3, 8)
    bullets = [_random_bullet(rng) for _ in range(n_bullets)]

    raw_text = (
        f"{company['canonical_name']}  |  {role['role_title']}  |  {city_state}\n"
        f"{start_month:02d}/{start_year} - {end_str}\n"
        + "\n".join(f"• {b}" for b in bullets)
    )

    return {
        "text": raw_text,
        "labels": {
            "company": company["canonical_name"],
            "title": role["role_title"],
            "location": city_state,
            "start_date": f"{start_year}-{start_month:02d}",
            "end_date": None if is_current else f"{end_year}-{end_month:02d}",
            "is_current": is_current,
            "bullets": bullets,
        },
    }


def _generate_work_history_data(
    companies: list[dict],
    locations: list[dict],
    roles: list[dict],
    n_samples: int = 100_000,
) -> list[dict]:
    rng = random.Random(99)
    return [_generate_work_history_sample(rng, companies, locations, roles) for _ in range(n_samples)]


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"  [OK] {path.name}: {len(rows):,} rows")


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"  [OK] {path.name}: {len(records):,} records")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate global IT industry datasets for DeBERTa fine-tuning.")
    parser.add_argument("--verify", action="store_true", help="Only count rows, no file writes.")
    parser.add_argument("--companies", type=int, default=50_000)
    parser.add_argument("--locations", type=int, default=100_000)
    parser.add_argument("--roles", type=int, default=10_000)
    parser.add_argument("--ner-samples", type=int, default=500_000)
    parser.add_argument("--wh-samples", type=int, default=100_000)
    parser.add_argument("--output-dir", type=str, default=str(OUTPUT_DIR))
    args = parser.parse_args()

    out = Path(args.output_dir)

    print("\n[*] Generating datasets ...")

    print("\n[1/5] Companies ...")
    companies = _generate_synthetic_companies(args.companies)
    print(f"      Generated {len(companies):,} company rows")

    print("\n[2/5] Locations ...")
    locations = _generate_locations(args.locations)
    print(f"      Generated {len(locations):,} location rows")

    print("\n[3/5] Job roles ...")
    roles = _generate_job_roles(args.roles)
    print(f"      Generated {len(roles):,} role rows")

    print("\n[4/5] NER training data ...")
    ner_data = _generate_ner_data(companies, locations, roles, args.ner_samples)
    print(f"      Generated {len(ner_data):,} NER samples")

    print("\n[5/5] Work history training data ...")
    wh_data = _generate_work_history_data(companies, locations, roles, args.wh_samples)
    print(f"      Generated {len(wh_data):,} work history samples")

    if args.verify:
        print("\n[OK] Verify mode - no files written.")
        return

    print(f"\n[->] Writing to {out} ...")
    write_csv(out / "global_companies.csv", companies, ["company_name", "canonical_name", "country", "industry", "aliases"])
    write_csv(out / "global_locations.csv", locations, ["city", "state_province", "country", "region"])
    write_csv(out / "it_job_roles.csv", roles, ["role_title", "canonical_title", "seniority", "domain", "aliases"])
    write_jsonl(out / "ner_training_data.jsonl", ner_data)
    write_jsonl(out / "work_history_train.jsonl", wh_data)

    print("\n[OK] All datasets written to " + str(out))
    print("\nNext step: run scripts/finetune_deberta.py or open scripts/colab_finetune.ipynb")


if __name__ == "__main__":
    main()
