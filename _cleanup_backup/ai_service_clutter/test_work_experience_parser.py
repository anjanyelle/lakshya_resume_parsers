#!/usr/bin/env python3
"""
Test improved work experience parser with client blocks.
Verifies proper extraction of job title, company, location, dates, and client blocks.
"""

import sys
import os
from pathlib import Path

# Add the ai-service directory to path
sys.path.append(str(Path(__file__).parent))

from parsers.work_experience_structured_parser import StructuredWorkExperienceParser

def test_work_experience_parser():
    """Test the structured work experience parser with Anjana's resume format."""
    
    # Sample work experience text from Anjana's resume
    work_text = """
Full Stack Developer
Infosys, Bangalore
June 2023 – Present
Client: Goldman Sachs
Developed internal financial dashboards for risk analysis using React.js
Built secure backend services with Node.js for transaction processing
Implemented authentication and data encryption for sensitive financial data
Client: HSBC
Created customer onboarding platform
Integrated KYC verification APIs
Improved API response time by 25%

Software Developer
Tata Consultancy Services, Hyderabad
May 2022 – May 2023
Client: Walmart
Developed e-commerce modules for product and order management
Built REST APIs for inventory tracking
Improved UI performance using React optimization techniques
Client: Target
Designed admin dashboards for managing large-scale product catalogs
Implemented advanced filtering and search features

Junior Web Developer
Wipro, Hyderabad
April 2021 – April 2022
Client: UnitedHealth Group
Developed patient management system
Built responsive UI for healthcare dashboards
Assisted in backend API development
Client: Pfizer
Worked on internal medical data tracking applications
Fixed bugs and improved system performance
"""
    
    print("🧪 TESTING WORK EXPERIENCE PARSER")
    print("=" * 70)
    
    try:
        # Initialize parser
        parser = StructuredWorkExperienceParser()
        
        # Parse work experience
        print("🔍 Parsing work experience section...")
        experiences = parser.parse_work_section(work_text)
        
        print(f"\n✅ Parsed {len(experiences)} work experiences")
        print("=" * 70)
        
        # Display results
        for i, exp in enumerate(experiences, 1):
            print(f"\n📊 EXPERIENCE {i}:")
            print("-" * 70)
            print(f"Job Title: {exp.get('job_title')}")
            print(f"Company: {exp.get('company_name')}")
            print(f"Location: {exp.get('location')}")
            print(f"Start Date: {exp.get('start_date')}")
            print(f"End Date: {exp.get('end_date') or 'Present' if exp.get('is_current') else exp.get('end_date')}")
            print(f"Is Current: {exp.get('is_current')}")
            
            clients = exp.get('clients', [])
            print(f"\nClients: {len(clients)}")
            for j, client in enumerate(clients, 1):
                print(f"\n  Client {j}:")
                print(f"    Name: {client.get('client_name')}")
                print(f"    Descriptions: {len(client.get('descriptions', []))} items")
                for desc in client.get('descriptions', [])[:3]:  # Show first 3
                    print(f"      - {desc}")
                if len(client.get('descriptions', [])) > 3:
                    print(f"      ... and {len(client.get('descriptions', [])) - 3} more")
        
        # Validation checks
        print("\n" + "=" * 70)
        print("🔍 VALIDATION CHECKS:")
        print("=" * 70)
        
        # Expected values
        expected = {
            'count': 3,
            'job_titles': ['Full Stack Developer', 'Software Developer', 'Junior Web Developer'],
            'companies': ['Infosys', 'Tata Consultancy Services', 'Wipro'],
            'locations': ['Bangalore', 'Hyderabad', 'Hyderabad'],
            'client_counts': [2, 2, 2],
            'client_names': [
                ['Goldman Sachs', 'HSBC'],
                ['Walmart', 'Target'],
                ['UnitedHealth Group', 'Pfizer']
            ]
        }
        
        # Check 1: Experience count
        if len(experiences) == expected['count']:
            print(f"✅ Experience count: {len(experiences)} (expected {expected['count']})")
        else:
            print(f"❌ Experience count: {len(experiences)} (expected {expected['count']})")
        
        # Check 2: Job titles
        actual_titles = [exp.get('job_title') for exp in experiences]
        if actual_titles == expected['job_titles']:
            print(f"✅ Job titles: {actual_titles}")
        else:
            print(f"❌ Job titles: {actual_titles}")
            print(f"   Expected: {expected['job_titles']}")
        
        # Check 3: Companies
        actual_companies = [exp.get('company_name') for exp in experiences]
        if actual_companies == expected['companies']:
            print(f"✅ Companies: {actual_companies}")
        else:
            print(f"❌ Companies: {actual_companies}")
            print(f"   Expected: {expected['companies']}")
        
        # Check 4: Locations
        actual_locations = [exp.get('location') for exp in experiences]
        if actual_locations == expected['locations']:
            print(f"✅ Locations: {actual_locations}")
        else:
            print(f"❌ Locations: {actual_locations}")
            print(f"   Expected: {expected['locations']}")
        
        # Check 5: Client counts
        actual_client_counts = [len(exp.get('clients', [])) for exp in experiences]
        if actual_client_counts == expected['client_counts']:
            print(f"✅ Client counts: {actual_client_counts}")
        else:
            print(f"❌ Client counts: {actual_client_counts}")
            print(f"   Expected: {expected['client_counts']}")
        
        # Check 6: Client names
        all_clients_correct = True
        for i, exp in enumerate(experiences):
            actual_client_names = [c.get('client_name') for c in exp.get('clients', [])]
            if actual_client_names != expected['client_names'][i]:
                all_clients_correct = False
                print(f"❌ Experience {i+1} clients: {actual_client_names}")
                print(f"   Expected: {expected['client_names'][i]}")
        
        if all_clients_correct:
            print(f"✅ All client names correct")
        
        # Check 7: Client descriptions
        has_descriptions = all(
            all(len(client.get('descriptions', [])) > 0 for client in exp.get('clients', []))
            for exp in experiences
        )
        if has_descriptions:
            print(f"✅ All clients have descriptions")
        else:
            print(f"❌ Some clients missing descriptions")
        
        # Overall success
        print("\n" + "=" * 70)
        success = (
            len(experiences) == expected['count'] and
            actual_titles == expected['job_titles'] and
            actual_companies == expected['companies'] and
            actual_locations == expected['locations'] and
            actual_client_counts == expected['client_counts'] and
            all_clients_correct and
            has_descriptions
        )
        
        if success:
            print("🎉 WORK EXPERIENCE PARSER TEST PASSED!")
            return True
        else:
            print("⚠️  Some validation checks failed")
            return False
        
    except Exception as e:
        print(f"❌ Error during parsing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_work_experience_parser()
    if not success:
        sys.exit(1)
