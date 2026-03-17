import sys
sys.path.append('backend')
from app.services.parser.work_experience_parser import WorkExperienceParser

# Simulate the actual resume structure based on UI output
text = '''Cardinal Health Location: Dublin, OH
DevOps Engineer October 2022 - Current
Responsibilities:
Led enterprise-wide migration from Apigee Edge to Apigee Hybrid for a healthcare provider, designing a secure hybrid cloud architecture enabling compliant access across 15+ clinical systems using Apigee Hybrid, Hybrid Cloud, and HIPAA Compliance. Engineered secure integration design patterns for Apigee Hybrid, standardizing connectivity between legacy healthcare platforms and modern microservices while integrating Kubernetes toolsets and enforcing regulatory controls using API Engineering, Kubernetes, and HITECH Standards. Established enterprise Dev Ops automation pipelines managing Apigee API Proxies and Policies, enabling automated deployments, version control, and approvals while reducing release timelines using Jenkins, Argo CD, Terraform, and CI/CD.

Huntington Location: Columbus, OH
DevOps Engineer December 2019 - September 2022
Responsibilities:
Led technical implementation and management of Apigee Hybrid for a banking institution, designing runtime plane architecture supporting 200+ TPS while enforcing regulatory controls using Apigee Hybrid, Hybrid Cloud, PCI-DSS, and SOX Compliance. Engineered migration from Apigee Edge to Apigee Hybrid, maintaining zero downtime while automating deployment of 350+ AP Is through production-grade orchestration using Kubernetes, Git Lab CI/CD, and API Proxy Automation.

Allstate Location: Northbrook,IL
DevOps Engineer February 2017 - November 2019
Responsibilities:
Led technical implementation and management of Apigee Hybrid runtimes for an insurance provider, engineering scalable runtime plane architecture processing 5 M+ daily transactions while ensuring compliance with Apigee Hybrid, Kubernetes, PCI-DSS, and GDPR. Designed enterprise API engineering solutions for claims processing, integrating legacy mainframe systems with microservices through secure patterns using Apigee API Proxies, Policies, Secure Integration Design, and HIPAA Compliance.

Equifax Location: Atlanta, GA
Cloud DevOps Engineer January 2016 - January 2017
Responsibilities:
Implemented CI/CD pipelines using Jenkins, Git, and Bitbucket for seamless version control. Automated processes in AWS for enhanced deployment efficiency within the credit reporting ecosystem. Managed Kubernetes orchestration with Helm, ensuring consistent application deployment and scalability. Improved microservices architecture reliability for consumer credit data processing.

Inno Minds Location: Pune, India
Linux System Administrator May 2014 - November 2015
Responsibilities:
Expert in creating depot for patches and installing packages using depot in HP-UX and building RPM using RPMBuild in Linux. Streamlined software deployment processes for enterprise-level applications. Demonstrated excellent knowledge in installation, configuration, file system, and RAID volume management through VXVM and Solaris Volume Manager (SVM) in Solaris and LVM in Linux and HP-UX.'''

parser = WorkExperienceParser()
job_chunks = parser.extract_individual_jobs(text)

print(f'Extracted {len(job_chunks)} job chunks:')
for i, chunk in enumerate(job_chunks, 1):
    print(f'\n--- JOB {i} ---')
    print(f'Length: {len(chunk)} characters')
    print(chunk[:200] + ('...' if len(chunk) > 200 else ''))
    print('--- END JOB ---')
