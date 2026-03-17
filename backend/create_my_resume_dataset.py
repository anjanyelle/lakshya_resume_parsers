#!/usr/bin/env python3

"""
Create Your Own Resume Dataset
Use your actual resume text to create perfect training data
"""

import json
from datetime import datetime
from app.services.enhanced_pipeline_final import EnhancedResumePipelineFinal

def create_my_resume_dataset():
    """Create dataset from your own resume"""
    
    print("🎯 Creating Your Own Resume Dataset")
    print("=" * 50)
    
    # STEP 1: Add your resume text here
    my_resume_text = """JULIAN T. VANCE
Senior Director of Cyber-Physical Security & Infrastructure Resilience
Houston, TX • (281) 555-0842 • j.vance.security@cyberinfrastructure.net
linkedin.com/in/julian-t-vance-ics-security • US Citizen • Q-Cleared / TS/SCI Eligible
PROFESSIONAL SUMMARY
Technically elite and strategically driven Cyber-Physical Security Executive with over12
years of specialized experience safeguarding global critical infrastructure, renewable en
ergy grids, and large-scale industrial automation systems. Recognized expert in the con
vergence of Information Technology (IT) and Operational Technology (OT), with a defini
tive record of defending multi-billion dollar asset portfolios against advanced persistent
threats (APTs) and sophisticated nation-state actors. Distinguished for architecting the
"Resilient Grid 2030" framework, which integrated cutting-edge zero-trust architecture
into legacy SCADA/ICS environments for the largest utility providers in the ERCOT region.
Julian has a proven ability to lead high-stakes, large-scale incident response missions
in sensitive air-gapped environments. He has successfully managedannualsecurity bud
gets exceeding $180M and directed cross-functional teams of 120+ cyber-physical engi
neers. He possesses deep expertise in navigating complex regulatory landscapes, in
cluding NERC CIP, NIST SP 800-82, and IEC 62443, ensuring 100% compliance across 45+
high-voltage substations and 12 major generation facilities. As a strategic advisor to the
DepartmentofEnergy(DOE)ongridmodernization, heis afrequent contributor to inter
national standards on industrial protocol security and critical infrastructure protection.
He is highly regarded for his unique ability to translate high-level cyber risk into opera
tional reality for C-Suite executivesandBoardDirectors, fosteringacultureof"Safety-First
Security."
CORECOMPETENCIES
• Cyber-Physical Security Strategy: OT/ICS Risk Management, Grid Modernization,
SCADA Security, Industrial Zero Trust, Threat Landscape Analysis.
• OperationalExcellence: NERCCIPCompliance,NISTCybersecurityFramework(CSF),
ISA/IEC 62443 Standards, Threat Modeling, Security Orchestration.
• Incident Response & Resilience: Cyber-Physical Forensic Analysis, Disaster Recov
ery for ICS, Business Continuity, Root Cause Analysis, Post-Breach Remediation.
• Infrastructure Leadership: Multi-Site Security Operations (SecOps), Strategic Asset
Protection, CapEx/OpEx Budgeting ($100M+), Executive Stakeholder Management.
• TechnicalInnovation: SoftwareDefinedNetworking(SDN)forOT,ICS-SpecificIDS/IPS
Deployment, Blockchain for Grid Integrity, Edge Computing Security.
• Regulatory Navigation: FERC/NERC Audit Management, Federal Information Secu
rity Modernization Act (FISMA), Supply Chain Risk Management (SCRM).
• AdvancedThreatDefense: APTHuntinginOTNetworks,FirmwareSecurityAnalysis,
Protocol Deep Packet Inspection (DPI), Honeypot Deployment in Industrial Webs.
TECHNICAL SKILLS
Industrial Control Systems (ICS) & SCADA Architecture
• PLCs&RTUs: Expert-levelconfigurationandsecurityhardeningforSiemensS7-1500,
Allen-Bradley ControlLogix, Schneider Electric Modicon, Emerson DeltaV, Honeywell
Experion, and Yokogawa Centum VP.
• Industrial Protocols: Mastery of Modbus TCP/RTU, DNP3, IEC 60870-5-104, BACnet,
Profinet, OPC UA, EtherNet/IP, GOOSE (IEC 61850), and S7Comm.
• HumanMachineInterfaces(HMI):AdvanceddeploymentofWonderwareInTouch,
Ignition by Inductive Automation, GE Digital iFIX, Rockwell FactoryTalk, and VTScada.
Security Platforms & Visibility Tools
• OTVisibility&ThreatDetection: DragosPlatform(Expert),NozomiNetworksGuardian,
Claroty Continuous Threat Detection (CTD), Microsoft Defender for IoT (CyberX), and
Armis.
• IndustrialNetworkSecurity: PaloAltoNetworks(IndustrialFirewalls&Strata),Fortinet
FortiGate Rugged, Waterfall Unidirectional Gateways, and Owl Cyber Defense Data
Diodes.
• SIEM, SOAR, & XDR: Splunk Enterprise Security (OT Add-on), Exabeam, IBM QRadar,
Palo Alto Cortex XSOAR, and Phantom.
Systems, Cloud, & Network Architecture
• Virtualization&Containerization: VMwarevSphere(ESXi),MicrosoftHyper-V,Docker,
Kubernetes for Edge Gateway Management, and Proxmox.
• Hardened Operating Systems: Windows Server (OT Hardened), RHEL (Industrial),
QNX, VxWorks, FreeRTOS, and various embedded Linux distributions.
• Digital Forensics: SANS SIFT Workstation, Mandiant Redline, EnCase Forensic, Wire
shark (Custom Dissectors for Proprietary Industrial Protocols), and Volatility.
Development, Automation, & Orchestration
• Programming Languages: Python (Security Tooling & Scripting), C++ (Embedded
Security), PowerShell, Bash, Structured Text (IEC 61131-3).
• Security Automation: Ansible for OT Hardening, Terraform for Infrastructure-as
Code (IaC), Jenkins for Secure CI/CD in Edge Computing, and SaltStack for configura
tion management.
PROFESSIONAL EXPERIENCE
Senior Director of Infrastructure Cybersecurity | Sentinel Grid Solu
tions | 2021– Present
Houston, TX (Global Leader in Grid Automation & Critical Infrastructure | Revenue: $12B)
StrategicLeadership&OperationalMandate: Julianwasrecruitedtoleadtheglobal
Cyber-Physical Security Division, where he oversees the defense of a critical client asset
portfolio that includes 18% of the U.S. electrical transmission grid and 22 major inter
national hydroelectric facilities. He manages an annual budget of $185M and leads a
diverse, high-performing workforce of 140 engineers, forensic analysts, and physical se
curity specialists.
Key Strategic Achievements:
• Grid Modernization Initiative (Project Sentinel Shield): Led a $400M, multi-year
digital transformation program that replaced 15,000 legacy serial-based RTUs with
secure-by-design IEC 62443 certified components across 250 substations. This initia
tive reduced the overall attack surface by 68% and improved operational uptime by
12%through proactive health monitoring.
• CriticalIncidentResponse: Directedtheremediationofasophisticatednation-state
supply chain breach that targeted firmware in localized grid controllers. Mobilized
an 80-person rapid response team that successfully identified, tested, and patched
12,000 units in 14 days without a single localized blackout, preventing an estimated
$1.2B in potential economic disruption.
• OT-SOCEstablishment: Builtandoperationalizedthefirstindustry-specific OTSecu
rity Operations Center (SOC). This SOC utilizes custom AI-driven anomaly detection
models to monitor 4.5 million telemetry points per second. Since its launch, Julian
has seen threat detection speeds improve by 400% and false positive rates drop by
85%.
• Regulatory Compliance & Governance: Achieved "Zero Non-Compliance" status
across14simultaneousNERCCIPVersion7audits. Hedevelopedaproprietary"Com
pliance Automation Engine" (CAE) that reduced audit preparation time by 1,200 man
hours annually by automating evidence collection from disconnected ICS assets.
• Executive Advising & Board Presence: Serves as the primary security liaison to
the Board of Directors. Julian successfully secured an additional $50M in funding
for "Cyber-Resilience-as-a-Service" (CRaaS) aimed at municipal utility clients who lack
specialized OT security staff.
• Strategic M&A Operations: Led the cybersecurity due diligence for the $2.4B ac
quisition of "Vortex Power Systems." He identified $15M in critical security debt and
successfully integrated their vast OT assets into the Sentinel core framework within
120 days.
Director of OT Security & Automation | Meridian Energy Systems |
2017– 2021
Dallas, TX (Integrated Energy Utility | Annual Revenue: $7.5B)
Operational Mandate: Julian directed the security operations for a sprawling energy
portfolio comprising thermal, wind, and solar generation. He was responsible for the
lifecycle security of Distributed Energy Resources (DERs) and the primary SCADA control
center for the entire Southwest region.
Key Measurable Achievements:
• Zero Trust for ICS Architecture: Architected and deployed the first full-scale Zero
Trust Network Access (ZTNA) modelforathermalpowerplantenvironment. Byelim
inating all VPN-based lateral movement risks, he reduced unauthorized access at
tempts and internal reconnaissance by 99.7%.
• Supply Chain Security Program: Established a "Trusted Component Vendor" (TCV)
program that mandated hardware-root-of-trust for all new equipment. Julian's team
discovered and blocked 4 critical vulnerabilities in pre-release firmware from a Tier-1
vendor, resulting in a global product recall and saving the firm from massive liability.
• Asset Visibility Project (Operation Lens): Deployed a passive monitoring solution
(Nozomi Guardian) across 100% of the generation fleet. The project discovered 15%
more "ghost assets" than previously documented in manual inventory, leading to a
comprehensive hardening of the network perimeter.
• Cyber-Physical Red Teaming: Designed and executed the industry's most realistic
"Grid-Down" simulation in a controlled lab environment. This project identified 12
critical logic flaws in the automatic load-shedding sequence that could have caused
catastrophic equipment damage during a real cyber-physical event.
• OperationalCostReduction: Automatedthevulnerabilitymanagementprocessfor
OTassetsusingcustomizedAnsibleplaybooks. Thisreducedthecost-per-remediation
from $450 to $180 and cut the window from disclosure to patch-testing by 60%.
• Public-Private Partnership: Acted as the Meridian lead for the Department of En
ergy's "Project CyTrus," sharing real-time threat intelligence with the Electricity Infor
mation Sharing and Analysis Center (E-ISAC).
SeniorCyber-PhysicalSecurityEngineer|IronwoodAutomation|2014– 2017
Chicago, IL (Industrial Automation & Systems Integrator)
Strategic Mandate & Engineering Leadership: Julian acted as the lead security ar
chitect forlarge-scaleautomationprojectsinthepetrochemicalandpharmaceuticalman
ufacturing sectors. He was pivotal in bridging the gap between mechanical engineering
teams and IT security departments.
Key Measurable Achievements:
• Petrochemical Plant Hardening: Lead the security design for a $1.5B refinery ex
pansionforfictionalclient"CrestwoodRefining."Heimplementedunidirectionalgate
ways (data diodes) to protect the Safety Instrumented Systems (SIS), ensuring phys
ical safety even during a complete network compromise.
• PLC Hardening Framework (The Ironwood Standard): Authored a 200-page con
figuration manual for PLC hardening, which became the mandatory standard for all
subsequent systems integration projects at the company. This standard reduced
post-deployment security tickets by 55% across all clients.
• Training & Workforce Development: Created a "Cyber-Aware Operator" curricu
lumspecifically for plant floor workers. He trained 1,200+ employees on recognizing
physical signs of cyber interference, which led to the early detection of two localized
system malfunctions that were subsequently identified as unauthorized configuration
changes.
• Secure Remote Access Re-Architecture: Developed a hardened jump-host archi
tecture for third-party maintenance contractors. By implementing multi-factor au
thentication (MFA) and full session recording in a protocol-isolated environment, he
eliminated the most common vector for industrial malware entry.
• AdvancedNetworkSegmentation: RedesignedthePurdueModelimplementation
for a major pharmaceutical manufacturer, separating the manufacturing execution
system (MES) from the enterprise ERP using high-availability industrial firewalls and
custom-tailored ACLs.
Cyber-Physical Systems Analyst | CoreStream Power | 2011– 2014
Charlotte, NC (Transmission & Distribution Specialist)
EarlyCareerFoundations: Julianfocusedonthetechnicalanalysisofindustrialproto
cols andthephysicalsecurityofremotesubstationassets. Hewasoneofthefirstanalysts
in the company to apply IT security principles to legacy serial communication devices.
Key Measurable Achievements:
• DNP3ProtocolDeep-Dive: DevelopedacustomWiresharkdissectortoidentifymal
formed DNP3packets used in potential denial-of-service attacks against older RTUs.
This tool was later shared with the open-source community.
• Substation Security Audits: Personally conducted 45 physical and logical security
audits across the Eastern Interconnect. He identified and remediated 120+ critical
findings related to exposed serial-to-ethernet converters and insecure cabinet locks.
• BaselineConfigurationManagement: ImplementedaTripwire-basedintegritymon
itoring systemforWindows-basedHMIstations. Thisinitiativereducedunauthorized
configuration changes by 90% and provided the first reliable audit trail for operator
actions.
• NERCCIPv3tov5Transition Taskforce: Acted as a key member of the compliance
task forceduringthemassiveNERCCIPv5overhaul. Hemappedtechnicalcontrolsto
the newregulatory requirements for over 500 assets, ensuring a seamless transition
without fines or warnings.
EDUCATION
Master of Science in Cybersecurity Policy & Grid Engineering
Carnegie Mellon University, Pittsburgh, PA
• Focus Areas: Security of Cyber-Physical Systems, Cryptography for Embedded Sys
tems, Policy Frameworks for Critical Infrastructure.
• Thesis: "Mitigating Cascading Failures in Electrical Grids via Distributed Anomaly De
tection."
• Honors: CMUExcellence in Engineering Research Award.
Bachelor of Science in Electrical Engineering & Computer Science (EECS)
University of California, Berkeley, CA
• Concentration: Control Systems, Power Electronics, Network Security.
• Honors: Eta Kappa Nu (HKN) Electrical Engineering Honor Society; Dean's List for 7
consecutive semesters.
CERTIFICATIONS
• GICSP: Global Industrial Cyber Security Professional– GIAC
• GRID: GIAC Response and Industrial Defense– GIAC
• CISSP-ISSAP: Information Systems Security Architecture Professional
• CISM: Certified Information Security Manager– ISACA
• PMP:Project Management Professional– PMI
• ISA/IEC 62443 Cybersecurity Expert Certification
• SCADASecurity Architect (CSSA)– IACRB
• CEH: Certified Ethical Hacker (Industrial Focus)"""
    
    # STEP 2: Parse your resume with Enhanced Pipeline
    print("🔍 Parsing your resume...")
    
    enhanced_pipeline = EnhancedResumePipelineFinal()
    parsed_result = enhanced_pipeline.parse_resume_complete(my_resume_text)
    
    print("✅ Resume parsed successfully!")
    print(f"📊 Sections found: {list(parsed_result.keys())}")
    print(f"💼 Work entries: {len(parsed_result.get('work', []))}")
    print(f"🎓 Education entries: {len(parsed_result.get('education', []))}")
    print(f"🔧 Skills entries: {len(parsed_result.get('skills', []))}")
    print(f"🏆 Certifications: {len(parsed_result.get('certifications', []))}")
    
    # STEP 3: Create training dataset
    training_sample = {
        "id": 1,
        "resume_text": my_resume_text.strip(),
        "expected_output": parsed_result,
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "source": "my_own_resume",
            "quality_score": 1.0,
            "verified": True,
            "format_type": "my_resume",
            "industry": "my_industry"
        }
    }
    
    # STEP 4: Save dataset
    dataset = [training_sample]
    
    with open('my_resume_dataset.json', 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Dataset saved to 'my_resume_dataset.json'")
    
    # STEP 5: Show the structure
    print("\n📋 Your Perfect JSON Structure:")
    print("-" * 30)
    print(json.dumps(parsed_result, indent=2)[:1000] + "...")
    
    return dataset

def create_multiple_resume_samples():
    """Create multiple samples from your resume variations"""
    
    print("\n🎯 Creating Multiple Resume Samples")
    print("=" * 50)
    
    # Add different versions of your resume
    resume_variations = [
        """
        # Version 1: Standard format
        JOHN DOE
        Senior Software Engineer
        San Francisco, CA • (555) 555-5555 • john.doe@example.com
        
        PROFESSIONAL SUMMARY
        Experienced software engineer with 5+ years...
        """,
        
        """
        # Version 2: Different format
        Jane Smith
        Data Scientist
        New York, NY • (555) 555-5555 • jane.smith@example.com
        
        SUMMARY
        Data scientist with expertise in machine learning...
        """,
        
        """
        # Version 3: Add your other resume versions
        [ADD YOUR OTHER RESUME VERSIONS HERE]
        """
    ]
    
    enhanced_pipeline = EnhancedResumePipelineFinal()
    dataset = []
    
    for i, resume_text in enumerate(resume_variations, 1):
        if not resume_text.strip() or resume_text.startswith("#"):
            continue
            
        print(f"\n📊 Processing Resume {i}...")
        
        try:
            parsed_result = enhanced_pipeline.parse_resume_complete(resume_text)
            
            sample = {
                "id": i,
                "resume_text": resume_text.strip(),
                "expected_output": parsed_result,
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "source": "my_resume_collection",
                    "quality_score": 1.0,
                    "verified": True,
                    "format_type": f"resume_version_{i}",
                    "industry": "my_industry"
                }
            }
            
            dataset.append(sample)
            print(f"✅ Resume {i} processed successfully")
            
        except Exception as e:
            print(f"❌ Error processing resume {i}: {e}")
    
    # Save all samples
    if dataset:
        with open('my_resume_collection.json', 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Collection saved to 'my_resume_collection.json'")
        print(f"📊 Total samples: {len(dataset)}")
    
    return dataset

def validate_my_dataset(dataset):
    """Validate your dataset structure"""
    
    print("\n🔍 Validating Your Dataset")
    print("=" * 30)
    
    required_keys = ['basics', 'work', 'education', 'skills', 'certifications', 'projects', 'languages', 'volunteer', 'references', 'achievements', 'publications']
    
    for i, sample in enumerate(dataset, 1):
        expected_output = sample.get('expected_output', {})
        
        print(f"\n📋 Sample {i} Validation:")
        
        # Check required keys
        missing_keys = []
        for key in required_keys:
            if key not in expected_output:
                missing_keys.append(key)
        
        if missing_keys:
            print(f"  ❌ Missing keys: {missing_keys}")
        else:
            print(f"  ✅ All required keys present")
        
        # Check data quality
        basics = expected_output.get('basics', {})
        if basics.get('name'):
            print(f"  ✅ Name: {basics['name']}")
        else:
            print(f"  ❌ Name missing")
        
        work = expected_output.get('work', [])
        print(f"  ✅ Work entries: {len(work)}")
        
        education = expected_output.get('education', [])
        print(f"  ✅ Education entries: {len(education)}")
        
        skills = expected_output.get('skills', [])
        print(f"  ✅ Skills entries: {len(skills)}")

def main():
    """Main function"""
    print("🎯 Create Your Own Resume Dataset")
    print("=" * 60)
    
    # Create single resume dataset
    dataset1 = create_my_resume_dataset()
    
    # Create multiple resume samples
    dataset2 = create_multiple_resume_samples()
    
    # Combine datasets
    combined_dataset = dataset1 + dataset2
    
    # Validate combined dataset
    validate_my_dataset(combined_dataset)
    
    print("\n✅ Dataset Creation Complete!")
    print("📊 Your datasets:")
    print("  • my_resume_dataset.json - Your main resume")
    print("  • my_resume_collection.json - Multiple versions")
    print("  • Ready for training your resume parser")

if __name__ == "__main__":
    main()
