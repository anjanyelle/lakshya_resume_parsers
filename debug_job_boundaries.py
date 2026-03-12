#!/usr/bin/env python3
"""
Debug Work Experience Job Boundary Detection
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def debug_job_boundary_detection():
    """Debug why only 1 job is being detected instead of 5"""
    print("🔍 DEBUGGING JOB BOUNDARY DETECTION")
    print("=" * 50)
    
    try:
        from app.services.parser.work_experience_parser import WorkExperienceParser
        parser = WorkExperienceParser()
        
        # Your actual resume text
        resume_text = """
PROFESSIONAL EXPERIENCE
Cardinal Health                                                                                                                                   Location: Dublin, OH
DevOps Engineer                                                                                                                               October 2022 – Current
Responsibilities:
•	Led enterprise-wide migration from Apigee Edge to Apigee Hybrid for a healthcare provider, designing a secure hybrid cloud architecture enabling compliant access across 15+ clinical systems using Apigee Hybrid, Hybrid Cloud, and HIPAA Compliance.
•	Engineered secure integration design patterns for Apigee Hybrid, standardizing connectivity between legacy healthcare platforms and modern microservices while integrating Kubernetes toolsets and enforcing regulatory controls using API Engineering, Kubernetes, and HITECH Standards.
Environment: Terraform, CI/CD, Grafana, Argo CD, Apigee Analytics & Monitoring, Apigee, GIT, Ansible, Prometheus, Jenkins, Kubernetes, Hashicorp Vault, Istio, Apigee Edge, Docker.

Huntington:                                                                                                                                          Location: Columbus, OH
DevOps Engineer    								     December 2019 - September 2022
Responsibilities:
•	Led technical implementation and management of Apigee Hybrid for a banking institution, designing runtime plane architecture supporting 200+ TPS while enforcing regulatory controls using Apigee Hybrid, Hybrid Cloud, PCI-DSS, and SOX Compliance.
Environment: Podman, ELK Stack, Kubernetes, PUPPET, Cloudformation, Datadog, Envoy, Github Actions, Snyk, FLUX, APIGEE EDGE, Gitlab, Apigee Runtime Plane Architecture, Apigee API Proxies & Policies, Apigee Hybrid, Apigee Analytics & Monitoring, CI/CD

Allstate:                                                                                                                                              Location: Northbrook,IL
DevOps Engineer                                                                                                                    February 2017 - November 2019
Responsibilities:
•	Led technical implementation and management of Apigee Hybrid runtimes for an insurance provider, engineering scalable runtime plane architecture processing 5M+ daily transactions while ensuring compliance with Apigee Hybrid, Kubernetes, PCI-DSS, and GDPR.
Environment: Gitlab CI, Kubernetes, Apigee Analytics & Monitoring, Aqua Security, Bitbucket, New Relic, Splunk, Apigee Runtime Plane Architecture, Apigee Hybrid, Containerd, Spinnaker, PULUMI, Apigee, Apigee API Proxies & Policies, CI/CD, CHEF

Equifax:                                                                                                                                                 Location: Atlanta, GA
Cloud DevOps Engineer                                  			       	       	  January 2016 - January 2017
Responsibilities:   
•	Implemented CI/CD pipelines using Jenkins, Git, and Bitbucket for seamless version control. Automated processes in AWS for enhanced deployment efficiency within the credit reporting ecosystem.
Environment:AWS,Jenkins,Bitbucket,Git,SVN,Docker,Kubernetes,Helm,Ant,Terrraform,Ansible,AWSCloudWatch,Nagios,Oracle,Linux,Jira,Python,Shell,Perl,Jfrog.

Inno Minds:                                                                                                                                                  Location: Pune, India
Linux System Administrator                                                                                                                May 2014 - November 2015
•	Expert in creating depot for patches and installing packages using depot in HP-UX and building RPM using RPMBuild in Linux. Streamlined software deployment processes for enterprise-level applications.
        Environment: Linux, Solaris and HP-UX, WebLogic, WebSphere, Solaris 10, DNS & NTP, MySQL, Nagios, PostgreSQL    database 8.3.1, IPMI, JBoss
"""
        
        print("📊 TESTING JOB EXTRACTION:")
        print("-" * 30)
        
        # Test extract_individual_jobs
        job_chunks = parser.extract_individual_jobs(resume_text)
        print(f"Total job chunks found: {len(job_chunks)}")
        
        for i, chunk in enumerate(job_chunks, 1):
            print(f"\n--- Job Chunk {i} ---")
            lines = chunk.split('\n')[:5]  # Show first 5 lines
            for line in lines:
                if line.strip():
                    print(f"  '{line.strip()}'")
            if len(chunk.split('\n')) > 5:
                print(f"  ... ({len(chunk.split('\n')) - 5} more lines)")
        
        print("\n🎯 ANALYSIS:")
        print("-" * 20)
        if len(job_chunks) == 1:
            print("❌ PROBLEM: Only 1 job chunk detected!")
            print("🔍 EXPECTED: 5 job chunks (Cardinal Health, Huntington, Allstate, Equifax, Inno Minds)")
            print("\n🔧 LIKELY ISSUES:")
            print("1. Job boundary detection not working")
            print("2. Date patterns not recognized as separators")
            print("3. Company name changes not detected")
            print("4. Empty lines not used as separators")
        else:
            print(f"✅ SUCCESS: {len(job_chunks)} job chunks detected!")
        
        # Test parsing each chunk
        print(f"\n📋 TESTING INDIVIDUAL JOB PARSING:")
        print("-" * 40)
        
        for i, chunk in enumerate(job_chunks[:2], 1):  # Test first 2 chunks
            print(f"\n--- Parsing Job {i} ---")
            try:
                job = parser._parse_chunk(chunk)
                if hasattr(job, 'company') and hasattr(job, 'title'):
                    print(f"✅ Company: '{job.company}'")
                    print(f"✅ Title: '{job.title}'")
                    print(f"✅ Start: '{job.start_date}'")
                    print(f"✅ End: '{job.end_date}'")
                else:
                    print(f"❌ Job object: {job}")
            except Exception as e:
                print(f"❌ Error parsing job {i}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_job_boundary_detection()
