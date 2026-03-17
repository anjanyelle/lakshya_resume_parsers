#!/usr/bin/env python3
"""
Debug work experience regex
"""

import re

rahul_work_text = """
UnitedHealth Group (Client: Optum Analytics): October 2023 – Current (Location: Eden Prairie, MN (Remote))
Role: Sr. Data Engineer
Responsibilities:
•	Designed and deployed HIPAA-compliant AWS Glue and Apache Spark ETL pipelines ingesting 50M+ daily healthcare claims, member eligibility records, and clinical encounter data from HL7 FHIR APIs and EDI 837/835 feeds into an AWS S3 data lake partitioned by payer, date, and claim type.
•	Built real-time streaming pipelines using AWS Kinesis Data Streams and Apache Kafka, processing prior authorization events and pharmacy benefit transactions with sub-500ms latency, triggering downstream Lambda enrichment functions and Redshift Streaming Ingestion for live dashboards.
JP Morgan Chase & Co.: June 2021 – September 2023 (Location: Columbus, OH)
Role: Sr. Data Engineer
Responsibilities:
•	Built PCI-DSS and SOX-compliant Apache Kafka event streaming pipelines ingesting real-time payment card transactions, wire transfers, and ACH events from 40+ source systems, processing 8M+ daily events into S3 data lake and Redshift for fraud analytics and regulatory capital reporting.
•	Designed Snowflake data warehouse on AWS with multi-cluster configurations, implementing data vault 2.0 modeling for customer 360, account hierarchy, and transaction history, creating role-based access controls for 1,500+ analytics consumers across risk, compliance, and business intelligence teams.
"""

print("🔍 DEBUGGING WORK EXPERIENCE REGEX")
print("=" * 50)

# Test different patterns
patterns = [
    r'([A-Za-z\s&\(\)\-]+(?:Group|Corporation|Inc|LLC|Ltd|Co|Tech|Global|Health|Financial|Retail|Telecom|Energy|Services))\s*:\s*([A-Za-z]+\s+\d{4}\s*–\s*[A-Za-z]+\s+\d{4}|[A-Za-z]+\s+\d{4}\s*–\s*Current)\s*\(([^)]+)\)',
    r'([A-Za-z\s&\(\)\-]+(?:Group|Corporation|Inc|LLC|Ltd|Co|Tech|Global|Health|Financial|Retail|Telecom|Energy|Services))\s*:\s*([A-Za-z]+\s+\d{4}\s*–\s*[A-Za-z]+\s+\d{4}|[A-Za-z]+\s+\d{4}\s*–\s*Current)',
    r'([A-Za-z\s&\(\)\-]+(?:Group|Corporation|Inc|LLC|Ltd|Co|Tech|Global|Health|Financial|Retail|Telecom|Energy|Services))\s*:',
]

for i, pattern in enumerate(patterns):
    print(f"\n🔍 Pattern {i+1}: {pattern}")
    matches = re.findall(pattern, rahul_work_text)
    print(f"  Matches: {len(matches)}")
    for j, match in enumerate(matches):
        print(f"    Match {j+1}: {match}")

print("\n🎯 TESTING SPLIT BY COMPANY:")
companies = re.split(r'(?:UnitedHealth Group|JP Morgan Chase & Co\.|Walmart Global Tech|AT&T|Exxon Mobil Corporation|Infosys Limited)', rahul_work_text)
for i, part in enumerate(companies):
    if part.strip():
        print(f"Part {i}: {part.strip()[:100]}...")
