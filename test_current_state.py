import sys
sys.path.append('backend')
from app.services.parser.work_experience_parser import WorkExperienceParser

# Test the current parser with merged job text
text = '''Cardinal Health Location: Dublin, OH
DevOps Engineer October 2022 - Current
Responsibilities:
Led enterprise-wide migration from Apigee Edge to Apigee Hybrid for a healthcare provider, designing a secure hybrid cloud architecture enabling compliant access across 15+ clinical systems using Apigee Hybrid, Hybrid Cloud, and HIPAA Compliance. Environment: Terraform, CI/CD, Grafana, Argo CD, Apigee Analytics & Monitoring, Apigee, GIT, Ansible, Prometheus, Jenkins, Kubernetes, Hashicorp Vault, Istio, Apigee Edge, Docker. Huntington: Location: Columbus, OH
Dev Ops Engineer December 2019 - September 2022
Led technical implementation and management of Apigee Hybrid for a banking institution, designing runtime plane architecture supporting 200+ TPS while enforcing regulatory controls using Apigee Hybrid, Hybrid Cloud, PCI-DSS, and SOX Compliance. Environment: Podman, ELK Stack, Kubernetes, PUPPET, Cloudformation, Datadog, Envoy, Github Actions, Snyk, FLUX, APIGEE EDGE, Gitlab, Apigee Runtime Plane Architecture, Apigee API Proxies & Policies, Apigee Hybrid, Apigee Analytics & Monitoring, CI/CD
Allstate: Location: Northbrook,IL
Dev Ops Engineer February 2017 - November 2019
Led technical implementation and management of Apigee Hybrid runtimes for an insurance provider, engineering scalable runtime plane architecture processing 5M+ daily transactions while ensuring compliance with Apigee Hybrid, Kubernetes, PCI-DSS, and GDPR. Environment: Gitlab CI, Kubernetes, Apigee Analytics & Monitoring, Aqua Security, Bitbucket, New Relic, Splunk, Apigee Runtime Plane Architecture, Apigee Hybrid, Containerd, Spinnaker, PULUMI, Apigee, Apigee API Proxies & Policies, CI/CD, CHEF
Equifax: Location: Atlanta, GA
Cloud DevOps Engineer January 2016 - January 2017
Implemented CI/CD pipelines using Jenkins, Git, and Bitbucket for seamless version control. Environment:AWS,Jenkins,Bitbucket,Git,SVN,Docker,Kubernetes,Helm,Ant,Terrraform,Ansible,AWS Cloud Watch,Nagios,Oracle,Linux,Jira,Python,Shell,Perl,Jfrog.
Inno Minds: Location: Pune, India
Linux System Administrator May 2014 - November 2015
Expert in creating depot for patches and installing packages using depot in HP-UX and building RPM using RPMBuild in Linux. Environment: Linux, Solaris and HP-UX, Web Logic, Web Sphere, Solaris 10, DNS & NTP, My SQL, Nagios, Postgre SQL database 8.3.1, IPMI, J Boss'''

parser = WorkExperienceParser()
job_chunks = parser.extract_individual_jobs(text)

print(f'Current parser extracted {len(job_chunks)} job chunks:')
for i, chunk in enumerate(job_chunks, 1):
    print(f'\n--- JOB {i} ---')
    print(f'Length: {len(chunk)} characters')
    print(chunk[:150] + ('...' if len(chunk) > 150 else ''))
    print('--- END JOB ---')
