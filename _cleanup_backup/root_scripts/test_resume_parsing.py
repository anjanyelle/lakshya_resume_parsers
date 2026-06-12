#!/usr/bin/env python3
"""
Test script to debug why only 1 work experience is extracted instead of 3.
"""

from parsers.experience_extractor import extract_experience

# Resume text from user
resume_text = """
PROFESSIONAL EXPERIENCE
Senior Network Engineer
Tech Mahindra
Hyderabad, India
February 2021 to Present
Responsibilities:
Designed and implemented enterprise network architecture.
Configured routers, switches, and firewalls for large-scale systems.
Implemented secure VPN solutions for remote employees.
Monitored network performance using SolarWinds tools.
Performed network troubleshooting and root cause analysis.
Achievements:
Reduced network downtime by 50 percent.
Improved system performance and reliability.

Network Engineer
HCL Technologies
Bangalore, India
March 2018 to January 2021
Responsibilities:
Managed LAN and WAN infrastructure.
Configured Cisco networking devices.
Handled network troubleshooting and incident management.
Maintained network documentation and reports.

Junior Network Engineer
Wipro Ltd
Pune, India
July 2016 to February 2018
Responsibilities:
Assisted in installation and configuration of network devices.
Monitored network traffic and resolved connectivity issues.
Supported senior engineers in maintaining uptime.
"""

print("=" * 80)
print("TESTING EXPERIENCE EXTRACTION")
print("=" * 80)

# Extract experiences
experiences = extract_experience(resume_text)

print(f"\n✅ Extracted {len(experiences)} work experiences:\n")

for i, exp in enumerate(experiences, 1):
    print(f"\n--- Experience {i} ---")
    print(f"Title: {exp.get('title', 'N/A')}")
    print(f"Company: {exp.get('company', 'N/A')}")
    print(f"Start Date: {exp.get('start_date', 'N/A')}")
    print(f"End Date: {exp.get('end_date', 'N/A')}")
    print(f"Is Current: {exp.get('is_current', False)}")
    print(f"Description: {exp.get('description', 'N/A')[:100]}...")

print("\n" + "=" * 80)
print(f"EXPECTED: 3 experiences")
print(f"ACTUAL: {len(experiences)} experiences")
print("=" * 80)
