import sys
sys.path.append('backend')
from app.services.parser.work_experience_parser import WorkExperienceParser

# Test the parser with Vaishnavi's resume format
text = '''Cardinal Health Location: Dublin, OH
DevOps Engineer October 2022 - Current
Responsibilities:
- Led enterprise-wide migration from Apigee Edge to Apigee Hybrid for a healthcare provider, designing a secure hybrid cloud architecture enabling compliant access across 15+ clinical systems using Apigee Hybrid, Hybrid Cloud, and HIPAA Compliance.

Huntington Location: Columbus, OH
DevOps Engineer December 2019 - September 2022
Responsibilities:
- Led technical implementation and management of Apigee Hybrid for a banking institution, designing runtime plane architecture supporting 200+ TPS while enforcing regulatory controls using Apigee Hybrid, Hybrid Cloud, PCI-DSS, and SOX Compliance.

Allstate Location: Northbrook,IL
DevOps Engineer February 2017 - November 2019
Responsibilities:
- Led technical implementation and management of Apigee Hybrid runtimes for an insurance provider, engineering scalable runtime plane architecture processing 5M+ daily transactions while ensuring compliance with Apigee Hybrid, Kubernetes, PCI-DSS, and GDPR.

Equifax Location: Atlanta, GA
Cloud DevOps Engineer January 2016 - January 2017
Responsibilities:
- Implemented CI/CD pipelines using Jenkins, Git, and Bitbucket for seamless version control. Automated processes in AWS for enhanced deployment efficiency within the credit reporting ecosystem.

Inno Minds Location: Pune, India
Linux System Administrator May 2014 - November 2015
Responsibilities:
- Expert in creating depot for patches and installing packages using depot in HP-UX and building RPM using RPMBuild in Linux. Streamlined software deployment processes for enterprise-level applications.'''

parser = WorkExperienceParser()
job_chunks = parser.extract_individual_jobs(text)

print(f'Extracted {len(job_chunks)} job chunks:')
for i, chunk in enumerate(job_chunks, 1):
    print(f'\n--- JOB {i} ---')
    print(chunk)
    print('--- END JOB ---')
