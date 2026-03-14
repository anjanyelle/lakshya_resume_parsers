#!/usr/bin/env python3

import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Test the enhanced parser directly
from app.services.parser.enhanced_parser_integration import EnhancedParserIntegration

# Sample text from your resume
sample_text = """PROFESSIONAL EXPERIENCE
Cigna Health (Client: Express Scripts)   |   2022 – Present  |  Bloomfield, CT (Remote)
Principal QA Automation Architect & Test Engineering Lead
Strategic Mandate: Recruited to establish Cigna's enterprise-wide QA Automation Center of Excellence (CoE) across the pharmacy benefit management and digital health platform divisions. Lead a distributed team of 35 QA engineers across 3 time zones, accountable for HIPAA-compliant test strategy covering 80+ microservices, 12 patient-facing web portals, and 4 native mobile applications.
Key Measurable Achievements:
•	Enterprise Selenium 4 Framework (AutoCore 3.0): Architected a hybrid Selenium 4 / TestNG / Cucumber BDD framework with Page Object Model, supporting parallel execution across 500+ browser-OS-device combinations on LambdaTest Cloud Grid. Reduced regression suite runtime from 18 hours to 42 minutes.
•	HIPAA Test Data Governance: Designed a HIPAA-compliant synthetic test data pipeline using Java Faker and AWS Secrets Manager, eliminating production PII from all test environments and achieving 100% audit pass rate across 3 federal healthcare audits.

Goldman Sachs (Client: Marcus by Goldman Sachs)   |   2019 – 2022  |  New York, NY
Lead QA Automation Engineer & Framework Architect
Operational Leadership: Served as the primary QA automation authority for the Marcus consumer banking digital platform. Directed 20 senior QA engineers in building a PCI-DSS compliant automated testing ecosystem covering personal loans, savings accounts, credit card, and investment product lines serving 8M+ customers.
Key Measurable Achievements:
•	PCI-DSS Selenium Framework: Designed a Selenium WebDriver 4 + TestNG Page Factory framework for the Marcus web banking portal, implementing encrypted credential handling via AWS Secrets Manager, dynamic wait strategies eliminating flakiness, and cross-browser parallel execution on Selenium Grid reducing regression time from 12 hours to 90 minutes.
•	API Automation for Core Banking: Built RestAssured test suites validating 300+ banking API endpoints including loan origination, account funding, interest calculation, and payment processing, integrating with Goldman's internal API gateway and implementing OAuth2/JWT token management in test automation.

Walmart Global eCommerce (Client: Walmart.com)   |   2017 – 2019  |  Sunnyvale, CA
Senior QA Automation Engineer
Key Measurable Achievements:
•	Selenium Grid Scaling for Black Friday: Engineered a distributed Selenium Grid 4 cluster on AWS ECS Fargate with auto-scaling policies, supporting 300 concurrent browser sessions during Black Friday regression cycles, validating cart, checkout, payment, and order tracking flows across 15 countries and 8 locales.

Bank of America (Client: Merrill Lynch Wealth)   |   2015 – 2017  |  Charlotte, NC
QA Automation Engineer
Key Measurable Achievements:
•	SOX-Compliant Test Automation: Built a Selenium WebDriver + TestNG + Java automation suite for Merrill Lynch's wealth management portal, implementing SOX-compliant test evidence generation, timestamped execution logs, and automated test result archival in SharePoint and JIRA for regulatory audit readiness.

Anthem Inc. (Client: BlueCross BlueShield)   |   2013 – 2015  |  Indianapolis, IN
QA Automation Engineer / SDET
Key Measurable Achievements:
•	Selenium WebDriver Framework Inception: Established the first automated UI testing framework at Anthem using Selenium WebDriver 2.x + TestNG + Java, replacing 100% manual regression testing for member portal, provider lookup, and claims status web applications, achieving 65% reduction in QA cycle time.
"""

def test_parser():
    print("Testing Enhanced Resume Parser with your format...")
    print("=" * 60)
    
    parser = EnhancedParserIntegration()
    
    # Test company | dates | location format parsing
    print("Testing _parse_company_dates_location_format...")
    experiences = parser._parse_company_dates_location_format(sample_text)
    
    print(f"Found {len(experiences)} experiences:")
    for i, exp in enumerate(experiences):
        print(f"\nExperience {i+1}:")
        print(f"  Company: {exp.company}")
        print(f"  Title: {exp.title}")
        print(f"  Location: {exp.location}")
        print(f"  Start Date: {exp.start_date}")
        print(f"  End Date: {exp.end_date}")
        print(f"  Description: {exp.description[:100]}...")
    
    # Test conversion to work history
    print("\n" + "=" * 60)
    print("Testing _convert_experiences_to_work_history...")
    work_history = parser._convert_experiences_to_work_history(experiences)
    
    print(f"Converted {len(work_history)} work history entries:")
    for i, work in enumerate(work_history):
        print(f"\nWork History {i+1}:")
        print(f"  Company: {work['company_name']}")
        print(f"  Job Title: {work['job_title']}")
        print(f"  Location: {work['location']}")
        print(f"  Start Date: {work['start_date']}")
        print(f"  End Date: {work['end_date']}")
        print(f"  Description: {work['description'][:100]}...")

if __name__ == "__main__":
    test_parser()
