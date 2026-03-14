
import csv
import os
from pathlib import Path
import random

# Base data for generation
# Base data for generation
titile_levels = [
    "Junior", "Senior", "Lead", "Principal", "Staff", "Associate", "Executive", "Director", "VP", "Manager", 
    "Head of", "Chief", "Intern", "Graduate", "Trainee", "Assistant", "Senior Associate", "Managing Director",
    "Global", "Regional", "District", "Area", "Group", "Divisional", "National"
]
tech_fields = [
    "Software", "Data", "Security", "DevOps", "Cloud", "Front-end", "Back-end", "Fullstack", "Mobile", "Android", 
    "iOS", "Machine Learning", "AI", "NLP", "Blockchain", "Infrastructure", "Systems", "Network", "QA", "Testing",
    "Finance", "Investment", "Audit", "Risk", "Compliance", "Accounting", "Tax", "Human Resources", "HR", 
    "Recruitment", "Marketing", "Sales", "Business Development", "Customer Success", "Product", "Project", 
    "Program", "Operations", "Supply Chain", "Logistics", "Legal", "Corporate", "Public Relations", "PR",
    "Engineering", "Manufacturing", "Healthcare", "Medical", "Clinical", "Pharma", "Retail", "Ecommerce", 
    "Consulting", "Strategy", "Creative", "Design", "Research", "Education", "Government", "Non-profit"
]
roles = [
    "Engineer", "Developer", "Analyst", "Architect", "Scientist", "Consultant", "Specialist", "Administrator", 
    "Lead", "Manager", "Coordinator", "Designer", "Officer", "Expert", "Researcher", "Assessor", "Auditor",
    "Strategist", "Representative", "Associate", "Fellow", "Counsel", "Partner", "Technician", "Owner",
    "Controller", "Architect", "President", "VP", "Director", "CFO", "CTO", "CEO", "COO", "CISO", "CIO", "CMO"
]

industries = [
    "Technologies", "Solutions", "Systems", "Health", "Bank", "Financial", "Global", "Soft", "Digital", 
    "Interactive", "Creative", "Logistics", "Energy", "Pharma", "Analytics", "Intelligence", "Advisory",
    "Investments", "Capital", "Partners", "Holdings", "Ventures", "Enterprises", "Industries", "Group",
    "Consulting", "Services", "Media", "Communications", "Retail", "Food", "Beverages", "Auto", "Aviation",
    "Defense", "Government", "Real Estate", "Hospitality", "Infrastructure", "Construction", "Education"
]
suffixes = [
    "Inc.", "LLC", "Ltd.", "Corp.", "Corporation", "Limited", "S.A.", "GmbH", "Group", "Enterprises",
    "Pvt Ltd", "Pty Ltd", "S.p.A.", "A.G.", "plc", "Co.", "Company", "Incorporated", "Worldwide", "International"
]
adjectives = [
    "Global", "Apex", "Next", "Fusion", "Quantum", "Cyber", "Data", "Tech", "Smart", "Infinite", "Stellar", 
    "Core", "Prime", "Blue", "Green", "Cloud", "Agile", "Dynamic", "Pacific", "Atlantic", "Universal", 
    "Strategic", "Operational", "Integrated", "Innovative", "Advanced", "Superior", "Elite", "Pro", 
    "Future", "Neo", "Omni", "Multi", "Inter", "Trans", "Ultra", "Hyper", "Vantage", "Zenith", "Summit"
]

def generate_global_titles(path):
    print(f"Writing titles to {path}...")
    titles = set(
        [f"{lvl} {fld} {rol}".strip() for lvl in titile_levels + [""] for fld in tech_fields for rol in roles]
    )
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["job_titles"])
        for t in sorted(list(titles)):
            writer.writerow([t])

def generate_global_companies(path, count=100000):
    print(f"Writing {count} companies to {path}...")
    companies = set()
    # Add generated names
    for adj in adjectives:
        for ind in industries:
            for suf in suffixes:
                companies.add(f"{adj} {ind} {suf}")
                companies.add(f"{adj}{ind}")
            companies.add(f"{ind} {random.choice(suffixes)}")
    
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["companies"])
        written = 0
        sorted_comps = sorted(list(companies))
        for c in sorted_comps:
            writer.writerow([c])
            written += 1
        
        # Fill rest with random enterprise names to reach count
        base_words = adjectives + industries
        while written < count:
            c_name = f"{random.choice(base_words)} {random.choice(base_words)} {random.choice(suffixes)}"
            writer.writerow([c_name])
            written += 1
            if written % 100000 == 0:
                print(f"  Generated {written} companies...")

def main():
    # Use current directory 'data' if running from 'backend'
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    generate_global_titles(data_dir / "global_job_titles.csv")
    generate_global_companies(data_dir / "global_companies.csv", count=1000000)
    
    locations = [
        "San Francisco, CA", "New York, NY", "London, UK", "Berlin, DE", "Bangalore, IN", 
        "Hyderabad, IN", "Seattle, WA", "Austin, TX", "Toronto, CA", "Paris, FR",
        "Sydney, AU", "Tokyo, JP", "Singapore, SG", "Dubai, AE", "Mumbai, IN",
        "Chennai, IN", "Pune, IN", "Delhi, IN", "Gurgaon, IN", "Noida, IN",
        "Mountain View, CA", "Palo Alto, CA", "San Jose, CA", "Boston, MA", "Chicago, IL",
        "Los Angeles, CA", "Atlanta, GA", "Dallas, TX", "Houston, TX", "Portland, OR",
        "Vancouver, CA", "Montreal, CA", "Dublin, IE", "Amsterdam, NL", "Munich, DE",
        "Stockholm, SE", "Zurich, CH", "Barcelona, ES", "Madrid, ES", "Hong Kong, HK",
        "Shanghai, CN", "Beijing, CN", "Seoul, KR", "Tel Aviv, IL", "Sao Paulo, BR",
        "Mexico City, MX", "Cape Town, ZA", "Johannesburg, ZA"
    ]
    # Add states and countries
    locations += ["California, US", "Texas, US", "New York, US", "Washington, US", "Ontario, CA", "Karnataka, IN", "Maharashtra, IN", "Tamil Nadu, IN", "Telangana, IN"]
    locations += ["United States", "India", "United Kingdom", "Germany", "Canada", "Australia", "Japan", "France", "Singapore", "United Arab Emirates", "Brazil", "South Africa"]
    
    with open(data_dir / "global_locations.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["locations"])
        for l in sorted(list(set(locations))): writer.writerow([l])
        
    keywords = [
        "Work Experience", "Professional Experience", "Employment History", "Work History", "Experience",
        "Career History", "Career Summary", "Employment", "Professional Background", "Job History",
        "Relevant Experience", "Work Summary", "Organizational Experience"
    ]
    with open(data_dir / "experience_keywords.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["experience_keywords"])
        for k in sorted(list(set(keywords))): writer.writerow([k])
    
    print("Success.")

if __name__ == "__main__":
    main()
