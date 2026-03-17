import sys
import os
# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend'))

from app.services.parser.work_experience_parser import WorkExperienceParser
import json

def test_company_client_format():
    """Test parsing of Company (Client: Client Name) format"""
    
    # Company (Client: Client Name) format resume text
    text = """
PROFESSIONAL EXPERIENCE
Cigna Health (Client: Express Scripts)   |   2022 – Present  |  Bloomfield, CT (Remote)
Principal QA Automation Architect & Test Engineering Lead
Strategic Mandate: Recruited to establish Cigna's enterprise-wide QA Automation Center of Excellence (CoE) across the pharmacy benefit management and digital health platform divisions. Lead a distributed team of 35 QA engineers across 3 time zones, accountable for HIPAA-compliant test strategy covering 80+ microservices, 12 patient-facing web portals, and 4 native mobile applications.
Key Measurable Achievements:
•	Enterprise Selenium 4 Framework (AutoCore 3.0): Architected a hybrid Selenium 4 / TestNG / Cucumber BDD framework with Page Object Model, supporting parallel execution across 500+ browser-OS-device combinations on LambdaTest Cloud Grid. Reduced regression suite runtime from 18 hours to 42 minutes.
•	HIPAA Test Data Governance: Designed a HIPAA-compliant synthetic test data pipeline using Java Faker and AWS Secrets Manager, eliminating production PII from all test environments and achieving 100% audit pass rate across 3 federal healthcare audits.
•	API Contract Testing at Scale: Implemented Pact consumer-driven contract testing across 45 microservice pairs using RestAssured and Pact Broker on AWS ECS, catching 120+ breaking API changes before they reached integration environments, eliminating critical regression escapes.
•	CI/CD Pipeline Integration: Built Jenkins Declarative Pipeline stages and GitHub Actions workflows triggering Selenium regression suites, RestAssured API tests, and JMeter performance benchmarks automatically on every pull request, with Allure Reports published to S3 and Slack notifications for failures.
•	Visual AI Regression Testing: Deployed Applitools Eyes across 8 patient portal applications, implementing AI-powered baseline visual comparisons eliminating 200+ hours/sprint of manual UI verification across Chrome, Firefox, Safari, and Edge.
•	Mobile Automation for Cigna+ App: Built Appium 2.x test suites for iOS and Android pharmacy mobile applications, integrating with BrowserStack App Automate for real-device execution across 40+ device-OS configurations, achieving 92% mobile regression automation coverage.
•	Performance Baseline Program: Led JMeter and Gatling performance testing initiative establishing SLA baselines for patient eligibility, prior authorization, and pharmacy claims APIs, identifying 15 critical performance bottlenecks preventing production releases.
•	Shift-Left Testing Leadership: Embedded QA automation engineers within 8 Scrum squads, introducing developer-written Selenium smoke tests, mandatory contract test coverage gates in CI, and real-time quality dashboards in ReportPortal for engineering leadership visibility.
•	Zero-Defect Release Cadence: Achieved a 94% reduction in post-release P1/P2 defects across pharmacy digital products by enforcing automated quality gates (coverage thresholds, mutation testing, contract tests) before any production deployment.
Environment: Selenium WebDriver 4.x, TestNG, Cucumber BDD, Java 17, RestAssured, Pact, Appium 2.x, Applitools Eyes, JMeter, Gatling, Jenkins, GitHub Actions, AWS ECS, AWS S3, LambdaTest, BrowserStack, Docker, Selenoid, Allure Reports, JIRA + Zephyr, PostgreSQL
Goldman Sachs (Client: Marcus by Goldman Sachs)   |   2019 – 2022  |  New York, NY
Lead QA Automation Engineer & Framework Architect
Operational Leadership: Served as the primary QA automation authority for the Marcus consumer banking digital platform. Directed 20 senior QA engineers in building a PCI-DSS compliant automated testing ecosystem covering personal loans, savings accounts, credit card, and investment product lines serving 8M+ customers.
Key Measurable Achievements:
•	PCI-DSS Selenium Framework: Designed a Selenium WebDriver 4 + TestNG Page Factory framework for the Marcus web banking portal, implementing encrypted credential handling via AWS Secrets Manager, dynamic wait strategies eliminating flakiness, and cross-browser parallel execution on Selenium Grid reducing regression time from 12 hours to 90 minutes.
•	API Automation for Core Banking: Built RestAssured test suites validating 300+ banking API endpoints including loan origination, account funding, interest calculation, and payment processing, integrating with Goldman's internal API gateway and implementing OAuth2/JWT token management in test automation.
•	Chaos & Resilience Testing: Introduced chaos engineering validation using custom Selenium test scenarios simulating network throttling, session timeouts, and payment processing failures, validating graceful degradation and customer error messaging across all Marcus digital touchpoints.
•	Accessibility Compliance: Led WCAG 2.1 AA automated accessibility testing using axe-core integrated with Selenium Java, validating 100% of customer-facing Marcus UI components for screen reader compatibility, keyboard navigation, and color contrast, achieving ADA compliance certification.
•	Azure DevOps Test Pipeline: Built Azure DevOps YAML pipelines orchestrating Selenium UI tests, RestAssured API tests, and Gatling load tests as mandatory quality gates, publishing ExtentReports to Azure Blob Storage and integrating JIRA Zephyr Scale for automated test result synchronization.
•	Security Regression Automation: Integrated OWASP ZAP passive scanning into Selenium test sessions, automating detection of XSS, CSRF, and SQL injection vulnerabilities in banking web flows, reducing manual security testing effort by 75% and eliminating 3 critical OWASP vulnerabilities before production release.
•	Test Data Factory: Designed a Java-based test data factory generating synthetic PCI-DSS compliant customer profiles, loan applications, and transaction histories, enabling deterministic end-to-end test execution without dependency on production data clones.
Environment: Selenium WebDriver 4, TestNG, Java 11, RestAssured, Gatling, Appium, OWASP ZAP, axe-core, Azure DevOps, Azure AKS, AWS Secrets Manager, Selenoid, Docker, Kubernetes, ExtentReports, JIRA Zephyr Scale, BrowserStack, Sauce Labs, PostgreSQL, Oracle
Walmart Global eCommerce (Client: Walmart.com)   |   2017 – 2019  |  Sunnyvale, CA
Senior QA Automation Engineer
Key Measurable Achievements:
•	Selenium Grid Scaling for Black Friday: Engineered a distributed Selenium Grid 4 cluster on AWS ECS Fargate with auto-scaling policies, supporting 300 concurrent browser sessions during Black Friday regression cycles, validating cart, checkout, payment, and order tracking flows across 15 countries and 8 locales.
•	Cucumber BDD Framework for Cross-Team Collaboration: Built a Cucumber + Selenium + Java hybrid framework enabling 50+ business analysts to write Gherkin scenarios without Java knowledge, achieving 3x increase in test scenario creation velocity and full traceability from user stories to automated test cases in JIRA.
•	Checkout Performance Validation: Led JMeter performance test campaigns simulating 500K concurrent shoppers across Walmart.com checkout flows, identifying database connection pool exhaustion issues preventing catastrophic failure on peak shopping events.
•	Mobile Web Automation: Built Appium test suites for the Walmart iOS and Android shopping applications, integrating with Sauce Labs real device cloud for execution across 60+ device configurations, achieving 88% mobile regression coverage for search, cart, and payment flows.
•	API Test Coverage Initiative: Developed RestAssured test suites covering 200+ Walmart.com product catalog, inventory, pricing, and promotion APIs, implementing schema validation, response time SLA assertions, and negative test scenarios for all critical commerce endpoints.
•	CI/CD Quality Gates: Integrated Selenium, RestAssured, and JMeter pipelines into Jenkins with mandatory pass/fail quality gates, publishing Allure Reports and blocking deployment when critical regression suites failed, reducing production defect escape rate by 68%.
Environment: Selenium WebDriver 4, Cucumber BDD, Java 11, TestNG, RestAssured, Appium, JMeter, Jenkins, AWS ECS, AWS S3, Sauce Labs, Docker, Selenoid, Allure Reports, JIRA, MySQL, MongoDB
Bank of America (Client: Merrill Lynch Wealth)   |   2015 – 2017  |  Charlotte, NC
QA Automation Engineer
Key Measurable Achievements:
•	SOX-Compliant Test Automation: Built a Selenium WebDriver + TestNG + Java automation suite for Merrill Lynch's wealth management portal, implementing SOX-compliant test evidence generation, timestamped execution logs, and automated test result archival in SharePoint and JIRA for regulatory audit readiness.
•	Data-Driven Investment Testing: Developed a data-driven Selenium framework using Apache POI for Excel-based test data management, validating portfolio rebalancing, trade order entry, and account statement generation workflows across 500+ client account types.
•	WebServices API Automation: Built SoapUI and RestAssured test suites for Merrill Lynch's trade execution and portfolio management web services, validating fix protocol message handling, real-time price feed integration, and account balance calculation APIs.
•	Cross-Browser Regression Suite: Delivered a comprehensive cross-browser Selenium suite covering Chrome, Firefox, IE11, and Safari for banking portal compliance, achieving 78% automation coverage of 2,400+ manual regression test cases and reducing QA cycle from 3 weeks to 4 days.
•	TestRail Integration: Implemented automated TestRail test result synchronization from Selenium execution reports via REST API integration, providing real-time test execution dashboards for QA managers and business stakeholders during release cycles.
Environment: Selenium WebDriver 3/4, TestNG, Java 8/11, SoapUI, RestAssured, Apache POI, Jenkins, Maven, TestRail, JIRA, SQL Server, Oracle, Docker, ExtentReports
Anthem Inc. (Client: BlueCross BlueShield)   |   2013 – 2015  |  Indianapolis, IN
QA Automation Engineer / SDET
Key Measurable Achievements:
•	Selenium WebDriver Framework Inception: Established the first automated UI testing framework at Anthem using Selenium WebDriver 2.x + TestNG + Java, replacing 100% manual regression testing for member portal, provider lookup, and claims status web applications, achieving 65% reduction in QA cycle time.
•	Healthcare Claims Automation: Built end-to-end Selenium test scenarios validating 835/837 EDI claims submission, adjudication status tracking, and Explanation of Benefits (EOB) document generation workflows across Chrome, Firefox, and IE for HIPAA-compliant member portal releases.
•	Database Validation Automation: Developed Java + JDBC test utilities validating claims data integrity between UI submissions and Oracle backend databases, implementing automated reconciliation checks for member eligibility records, claim line items, and payment amounts.
•	Jenkins CI Integration Pioneer: Introduced the organization's first Jenkins CI automated test execution pipeline triggering nightly Selenium regression suites, reducing overnight manual QA effort by 40 engineer-hours per week and providing next-morning test result dashboards for release managers.
Environment: Selenium WebDriver 2.x/3.x, TestNG, Java 8, JDBC, Oracle, Jenkins, Maven, ExtentReports, JIRA, SoapUI, Apache POI
"""
    
    print("=" * 60)
    print("TESTING COMPANY (CLIENT: CLIENT NAME) FORMAT")
    print("=" * 60)
    
    work_parser = WorkExperienceParser()
    
    # Parse the entire experience section
    print("\nTESTING FULL PARSING")
    print("-" * 40)
    parsed_jobs = work_parser.parse_experience_section(text)
    
    print(f"\nNumber of parsed jobs: {len(parsed_jobs)}")
    
    # Convert to UI format
    ui_data = []
    for i, job in enumerate(parsed_jobs):
        job_dict = {
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "start_date": job.start_date.isoformat() if job.start_date else None,
            "end_date": job.end_date.isoformat() if job.end_date else None,
            "is_current": job.is_current,
            "description": job.description,
            "bullets": job.bullets,
            "confidence": job.confidence
        }
        ui_data.append(job_dict)
        
        print(f"\n--- Job {i+1} ---")
        print(f"Company: {job.company}")
        print(f"Title: {job.title}")
        print(f"Location: {job.location}")
        print(f"Start Date: {job.start_date}")
        print(f"End Date: {job.end_date}")
        print(f"Is Current: {job.is_current}")
        print(f"Description length: {len(job.description) if job.description else 0}")
        print(f"Bullets count: {len(job.bullets) if job.bullets else 0}")
    
    # Show JSON output that UI would receive
    print("\n" + "=" * 60)
    print("JSON OUTPUT FOR UI:")
    print("=" * 60)
    print(json.dumps({"work_experience": ui_data}, indent=2))

if __name__ == "__main__":
    test_company_client_format()
