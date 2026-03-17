#!/usr/bin/env python3
"""
TASK 1 - Generate 200+ NER training samples - SPACY 3.X FIX
"""

import spacy
import json
import os
import random
from spacy.training import Example

def make_example(text, entity_text, label):
    """Make training example with char_span for spaCy 3.x"""
    start = text.find(entity_text)
    if start == -1:
        return None, f"entity '{entity_text}' not found in text"
    
    end = start + len(entity_text)
    doc = spacy.blank("en").make_doc(text)
    
    # Use char_span with alignment_mode="expand" for spaCy 3.x
    span = doc.char_span(start, end, label=label, alignment_mode="expand")
    
    if span is None:
        return None, f"span not alignable for '{entity_text}' in '{text}'"
    
    return (text, {"entities": [(span.start_char, span.end_char, label)]}), None

def generate_ner_training_spacy3():
    """Generate 200+ NER training samples for spaCy 3.x"""
    
    print("🔧 TASK 1 - GENERATING 200+ NER TRAINING SAMPLES (SPACY 3.X FIX)")
    print("=" * 60)
    
    # SKILL examples (60)
    skill_sentences = [
        ("Used Python for data processing", "Python"),
        ("Built pipeline with PySpark", "PySpark"),
        ("Deployed application on AWS", "AWS"),
        ("Configured Docker containers", "Docker"),
        ("Managed Kubernetes clusters", "Kubernetes"),
        ("Queried database using Snowflake", "Snowflake"),
        ("Built with Spring Boot framework", "Spring Boot"),
        ("Used Apache Kafka for streaming", "Apache Kafka"),
        ("Created Tableau dashboards", "Tableau"),
        ("Wrote SQL queries for analysis", "SQL"),
        ("Processed data using Apache Spark", "Apache Spark"),
        ("Built Angular frontend application", "Angular"),
        ("Developed React components", "React"),
        ("Used Java for backend services", "Java"),
        ("Deployed with Jenkins CI CD", "Jenkins"),
        ("Monitored using Grafana dashboards", "Grafana"),
        ("Used Redis for caching data", "Redis"),
        ("Built infrastructure with Terraform", "Terraform"),
        ("Processed arrays with NumPy", "NumPy"),
        ("Created Power BI reports", "Power BI"),
        ("Used Azure Data Factory pipelines", "Azure Data Factory"),
        ("Streamed data with AWS Kinesis", "AWS Kinesis"),
        ("Built models with TensorFlow", "TensorFlow"),
        ("Used Scikit-learn for ML", "Scikit-learn"),
        ("Processed with Pandas dataframes", "Pandas"),
        ("Used PostgreSQL database", "PostgreSQL"),
        ("Queried with MongoDB", "MongoDB"),
        ("Used MySQL for storage", "MySQL"),
        ("Deployed on Azure Kubernetes Service", "Azure Kubernetes Service"),
        ("Used Git for version control", "Git"),
        ("Automated with GitHub Actions", "GitHub Actions"),
        ("Used Bitbucket for code review", "Bitbucket"),
        ("Built with Node.js backend", "Node.js"),
        ("Used TypeScript for frontend", "TypeScript"),
        ("Built microservices with Go", "Go"),
        ("Used Scala for Spark jobs", "Scala"),
        ("Queried with GraphQL API", "GraphQL"),
        ("Built REST APIs with FastAPI", "FastAPI"),
        ("Used Airflow for orchestration", "Airflow"),
        ("Transformed data using dbt", "dbt"),
        ("Used Databricks for analytics", "Databricks"),
        ("Processed with Hadoop cluster", "Hadoop"),
        ("Used Hive for querying", "Hive"),
        ("Streamed with Apache Flink", "Apache Flink"),
        ("Used Cassandra database", "Cassandra"),
        ("Built with DynamoDB tables", "DynamoDB"),
        ("Used Elasticsearch for search", "Elasticsearch"),
        ("Monitored with Prometheus metrics", "Prometheus"),
        ("Logged with ELK Stack", "ELK Stack"),
        ("Used Splunk for monitoring", "Splunk"),
        ("Built CI CD with GitLab", "GitLab"),
        ("Used Ansible for automation", "Ansible"),
        ("Managed with Puppet scripts", "Puppet"),
        ("Used Chef for configuration", "Chef"),
        ("Deployed on Google Cloud Platform", "Google Cloud Platform"),
        ("Used BigQuery for analytics", "BigQuery"),
        ("Built with Angular Material", "Angular Material"),
        ("Used Redux for state management", "Redux"),
        ("Built with Vue.js framework", "Vue.js"),
        ("Used Spring MVC framework", "Spring MVC"),
        ("Built with Hibernate ORM", "Hibernate"),
        ("Used Maven for build management", "Maven"),
        ("Built with Gradle automation", "Gradle"),
        ("Used JUnit for testing", "JUnit"),
        ("Tested with Mockito framework", "Mockito"),
        ("Used Selenium for automation", "Selenium"),
        ("Tested with Cypress framework", "Cypress"),
        ("Used Postman for API testing", "Postman"),
        ("Built with RabbitMQ messaging", "RabbitMQ"),
        ("Used IBM MQ for messaging", "IBM MQ"),
        ("Built with Apache Beam pipeline", "Apache Beam"),
        ("Used Delta Lake for storage", "Delta Lake"),
        ("Built lakehouse with Apache Iceberg", "Apache Iceberg"),
        ("Used Parquet file format", "Parquet"),
        ("Built with AWS Glue ETL", "AWS Glue"),
        ("Used AWS Lambda functions", "AWS Lambda"),
        ("Built with AWS S3 storage", "AWS S3"),
        ("Used AWS Redshift warehouse", "AWS Redshift"),
        ("Built with Azure Synapse Analytics", "Azure Synapse Analytics"),
        ("Used Azure Databricks platform", "Azure Databricks"),
        ("Built with GCP Pub Sub", "GCP Pub Sub"),
        ("Used Looker for visualization", "Looker"),
        ("Built with MicroStrategy platform", "MicroStrategy"),
        ("Used QuickSight dashboards", "QuickSight"),
        ("Containerized with OpenShift", "OpenShift"),
        ("Used Nginx for load balancing", "Nginx"),
        ("Built with Apache Tomcat server", "Apache Tomcat"),
        ("Used Swagger for API docs", "Swagger"),
        ("Built OAuth2 authentication", "OAuth2"),
        ("Used SonarQube for code quality", "SonarQube"),
        ("Built with JIRA tracking", "JIRA"),
        ("Used Confluence for documentation", "Confluence"),
        ("Processed with R programming", "R"),
        ("Used MATLAB for computation", "MATLAB"),
        ("Built PyTorch models", "PyTorch"),
        ("Used XGBoost for prediction", "XGBoost"),
        ("Built with Keras neural nets", "Keras"),
    ]
    
    # TITLE examples (50)
    title_sentences = [
        ("Working as Senior Data Analyst", "Senior Data Analyst"),
        ("Hired as Sr Data Analyst", "Sr Data Analyst"),
        ("Title is Principal Data Analyst", "Principal Data Analyst"),
        ("Senior Java Developer needed", "Senior Java Developer"),
        ("Sr Java Developer position", "Sr Java Developer"),
        ("Senior Software Engineer", "Senior Software Engineer"),
        ("Sr Software Engineer job", "Sr Software Engineer"),
        ("Machine Learning Engineer", "Machine Learning Engineer"),
        ("ML Engineer position", "ML Engineer"),
        ("Senior ML Engineer role", "Senior ML Engineer"),
        ("Sr ML Engineer needed", "Sr ML Engineer"),
        ("DevOps Engineer position", "DevOps Engineer"),
        ("Data Scientist role", "Data Scientist"),
        ("Senior Data Scientist position", "Senior Data Scientist"),
        ("Sr Data Scientist needed", "Sr Data Scientist"),
        ("Business Analyst job", "Business Analyst"),
        ("Senior Business Analyst role", "Senior Business Analyst"),
        ("Software Engineer position", "Software Engineer"),
        ("Full Stack Developer needed", "Full Stack Developer"),
        ("Backend Developer role", "Backend Developer"),
        ("Frontend Developer position", "Frontend Developer"),
        ("Data Engineer job", "Data Engineer"),
        ("Senior Data Engineer needed", "Senior Data Engineer"),
        ("Product Manager position", "Product Manager"),
        ("Senior Product Manager role", "Senior Product Manager"),
        ("Project Manager needed", "Project Manager"),
        ("Technical Lead position", "Technical Lead"),
        ("Engineering Manager role", "Engineering Manager"),
        ("Solutions Architect needed", "Solutions Architect"),
        ("Cloud Architect position", "Cloud Architect"),
        ("Security Engineer job", "Security Engineer"),
        ("QA Engineer position", "QA Engineer"),
        ("Data Analyst internship", "Data Analyst"),
        ("Junior Developer position", "Junior Developer"),
        ("Entry Level Engineer role", "Entry Level Engineer"),
    ]
    
    # COMPANY examples (40)
    company_sentences = [
        ("Worked at Bank of America North Carolina", "Bank of America"),
        ("Employed by Starbucks in California", "Starbucks"),
        ("CLIENT Home Depot Location Atlanta", "Home Depot"),
        ("CLIENT Huntington Location Columbus", "Huntington"),
        ("Worked at Amazon in Hyderabad", "Amazon"),
        ("Joined Google in Mountain View", "Google"),
        ("Position at Microsoft in Seattle", "Microsoft"),
        ("Worked at Credit Karma San Francisco", "Credit Karma"),
        ("Employed at ADP in Hyderabad", "ADP"),
        ("CLIENT Walgreens Location Deerfield", "Walgreens"),
        ("Worked at T-Mobile in Bellevue", "T-Mobile"),
        ("Joined TCS in Hyderabad India", "TCS"),
        ("Employed at Infosys in Bangalore", "Infosys"),
        ("Worked at Facebook in Menlo Park", "Facebook"),
        ("Position at Netflix in Los Gatos", "Netflix"),
        ("Worked at Apple in Cupertino", "Apple"),
        ("Joined Wipro in Hyderabad India", "Wipro"),
        ("Employed at HCL in Noida India", "HCL"),
        ("Worked at Cognizant in Chennai", "Cognizant"),
        ("Position at Accenture in Mumbai", "Accenture"),
        ("CLIENT Ceva Logistics Location Mumbai", "Ceva Logistics"),
        ("Worked at JPMorgan Chase New York", "JPMorgan Chase"),
        ("Joined Goldman Sachs New York", "Goldman Sachs"),
        ("Employed at Walmart in Bentonville", "Walmart"),
        ("Worked at Target in Minneapolis", "Target"),
        ("Position at Uber in San Francisco", "Uber"),
        ("Worked at Lyft in San Francisco", "Lyft"),
        ("Joined Airbnb in San Francisco", "Airbnb"),
        ("Employed at Twitter in San Francisco", "Twitter"),
        ("Worked at LinkedIn in Sunnyvale", "LinkedIn"),
        ("CLIENT IBM Location New York", "IBM"),
        ("Worked at Oracle in Redwood City", "Oracle"),
        ("Joined SAP in Walldorf Germany", "SAP"),
        ("Employed at Salesforce in San Francisco", "Salesforce"),
        ("Worked at Adobe in San Jose", "Adobe"),
        ("Position at PayPal in San Jose", "PayPal"),
        ("Worked at Cisco in San Jose", "Cisco"),
        ("Joined Intel in Santa Clara", "Intel"),
        ("Employed at NVIDIA in Santa Clara", "NVIDIA"),
        ("Worked at Qualcomm in San Diego", "Qualcomm"),
    ]
    
    # DATE examples (30)
    date_sentences = [
        ("Worked from July 2021 to Present", "July 2021"),
        ("Worked from July 2021 to Present", "Present"),
        ("Joined in January 2020 at company", "January 2020"),
        ("Left in June 2021 from company", "June 2021"),
        ("Started August 2020 at firm", "August 2020"),
        ("Employed from October 2017 onwards", "October 2017"),
        ("Started December 2015 at role", "December 2015"),
        ("Worked until May 2014 there", "May 2014"),
        ("From June 2023 to Current role", "June 2023"),
        ("From June 2023 to Current role", "Current"),
        ("Period August 2020 to May 2023", "August 2020"),
        ("Period August 2020 to May 2023", "May 2023"),
        ("From October 2017 to July 2020", "October 2017"),
        ("From October 2017 to July 2020", "July 2020"),
        ("From December 2015 to September 2017", "December 2015"),
        ("From December 2015 to September 2017", "September 2017"),
        ("From May 2014 to October 2015", "May 2014"),
        ("From May 2014 to October 2015", "October 2015"),
        ("Education from 2010 to 2014", "2010"),
        ("Education from 2010 to 2014", "2014"),
        ("Valid from 2024 to 2027", "2024"),
        ("Valid from 2024 to 2027", "2027"),
        ("Graduated in May 2014", "May 2014"),
        ("Certified in 2020 successfully", "2020"),
        ("Joined February 2018 at firm", "February 2018"),
        ("Left December 2019 from role", "December 2019"),
        ("Started March 2022 new role", "March 2022"),
        ("Ended November 2023 contract", "November 2023"),
        ("From April 2016 to August 2018", "April 2016"),
        ("From April 2016 to August 2018", "August 2018"),
    ]
    
    # EDUCATION examples (25)
    education_sentences = [
        ("Completed Bachelor of Technology degree", "Bachelor of Technology"),
        ("Earned Master of Science degree", "Master of Science"),
        ("Finished Bachelor of Engineering course", "Bachelor of Engineering"),
        ("Completed MBA from university", "MBA"),
        ("Earned B.Tech from college", "B.Tech"),
        ("Completed M.Tech program", "M.Tech"),
        ("Finished Bachelor of Science degree", "Bachelor of Science"),
        ("Earned Master of Computer Science", "Master of Computer Science"),
        ("Completed Ph.D in Machine Learning", "Ph.D"),
        ("Finished Master of Business Administration", "Master of Business Administration"),
        ("Bharath University Bachelor of Technology 2010", "Bachelor of Technology"),
        ("Completed B.E Computer Engineering", "B.E"),
        ("Earned BCA from university", "BCA"),
        ("Completed MCA program", "MCA"),
        ("Finished B.Sc Computer Science", "B.Sc"),
        ("Earned M.Sc Data Science", "M.Sc"),
        ("Completed Bachelor of Commerce", "Bachelor of Commerce"),
        ("Earned Master of Arts degree", "Master of Arts"),
        ("Finished Associate Degree program", "Associate Degree"),
        ("Completed Diploma in IT", "Diploma in IT"),
        ("Stanford University Master of Science 2018", "Master of Science"),
        ("IIT Bombay Bachelor of Technology 2015", "Bachelor of Technology"),
        ("IIM Ahmedabad MBA 2017", "MBA"),
        ("MIT Master of Science in CS", "Master of Science in CS"),
        ("Anna University B.Tech Computer Science", "B.Tech"),
        ("Osmania University M.Tech Software", "M.Tech"),
        ("BITS Pilani Bachelor of Engineering", "Bachelor of Engineering"),
        ("NIT Warangal B.Tech Electronics", "B.Tech"),
        ("VIT University M.Tech CSE", "M.Tech"),
        ("Pune University Bachelor of Engineering", "Bachelor of Engineering"),
    ]
    
    # CERTIFICATION examples (25)
    cert_sentences = [
        ("Holds AWS Certified Developer Associate cert", "AWS Certified Developer Associate"),
        ("Earned Azure Certified Developer Associate", "Azure Certified Developer Associate"),
        ("Completed Oracle Gen AI Certified program", "Oracle Gen AI Certified"),
        ("Obtained PMP certification recently", "PMP"),
        ("Holds AWS Certified Solutions Architect cert", "AWS Certified Solutions Architect"),
        ("Completed Google Cloud Professional cert", "Google Cloud Professional"),
        ("Earned Microsoft Certified Expert badge", "Microsoft Certified Expert"),
        ("Holds Kubernetes Certified Administrator", "Kubernetes Certified Administrator"),
        ("Obtained CISSP certification", "CISSP"),
        ("Completed CKA certification program", "CKA"),
        ("Earned Oracle Certified Professional status", "Oracle Certified Professional"),
        ("Holds Red Hat Certified Engineer title", "Red Hat Certified Engineer"),
        ("Obtained ITIL Foundation certification", "ITIL Foundation"),
        ("Completed Certified Scrum Master course", "Certified Scrum Master"),
        ("Holds Certified Kubernetes Application Developer", "Certified Kubernetes Application Developer"),
        ("Earned AWS Certified Data Analytics cert", "AWS Certified Data Analytics"),
        ("Completed Google Associate Cloud Engineer", "Google Associate Cloud Engineer"),
        ("Holds Azure Solutions Architect Expert", "Azure Solutions Architect Expert"),
        ("Obtained CompTIA Security Plus cert", "CompTIA Security Plus"),
        ("Completed Certified Information Systems Security", "Certified Information Systems Security"),
    ]
    
    # Build all examples
    all_raw = []
    for text, entity in skill_sentences:
        all_raw.append((text, entity, "SKILL"))
    for text, entity in title_sentences:
        all_raw.append((text, entity, "TITLE"))
    for text, entity in company_sentences:
        all_raw.append((text, entity, "COMPANY"))
    for text, entity in date_sentences:
        all_raw.append((text, entity, "DATE"))
    for text, entity in education_sentences:
        all_raw.append((text, entity, "EDUCATION"))
    for text, entity in cert_sentences:
        all_raw.append((text, entity, "CERTIFICATION"))
    
    print(f"🎯 Generated {len(all_raw)} training examples")
    
    # Validate and create training data
    TRAIN_DATA = []
    skipped_list = []
    
    for text, entity_text, label in all_raw:
        result, error = make_example(text, entity_text, label)
        if result:
            TRAIN_DATA.append(result)
        else:
            skipped_list.append((text, entity_text, label, error))
    
    print(f"✅ Valid examples: {len(TRAIN_DATA)}")
    print(f"❌ Skipped examples: {len(skipped_list)}")
    print(f"📊 Total: {len(all_raw)}")
    
    # Save training data
    os.makedirs("training_data", exist_ok=True)
    
    with open("training_data/ner_train.json", "w", encoding="utf-8") as f:
        json.dump(TRAIN_DATA, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved {len(TRAIN_DATA)} training examples to training_data/ner_train.json")
    
    if skipped_list:
        print("\nSKIPPED ITEMS:")
        for text, ent, lbl, err in skipped_list:
            print(f"  [{lbl}] '{ent}' in '{text}' → {err}")
    
    return len(TRAIN_DATA)

def train_ner_model():
    """Train NER model with generated data"""
    
    print("\n🚀 TRAINING NER MODEL")
    print("=" * 40)
    
    # Load training data
    try:
        with open("training_data/ner_train.json", "r", encoding="utf-8") as f:
            raw = json.load(f)
    except:
        print("❌ No training data found!")
        return 0, float('inf'), False
    
    TRAIN_DATA = raw
    
    print(f"Loaded {len(TRAIN_DATA)} training examples")
    
    # Train model
    nlp = spacy.blank("en")
    ner = nlp.add_pipe("ner")
    
    for label in ["SKILL","TITLE","COMPANY","DATE","EDUCATION","CERTIFICATION"]:
        ner.add_label(label)
    
    optimizer = nlp.begin_training()
    optimizer.learn_rate = 0.001
    best_loss = float("inf")
    
    for itn in range(30):
        random.shuffle(TRAIN_DATA)
        losses = {}
        for text, annotations in TRAIN_DATA:
            doc = nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            nlp.update([example], sgd=optimizer, drop=0.35, losses=losses)
        loss = losses["ner"]
        print(f"Iteration {itn:02d}, Loss: {loss:.2f}")
        if loss < best_loss:
            best_loss = loss
            nlp.to_disk("skills_ner_trained/")
    
    print(f"\nBest loss: {best_loss:.2f}")
    print("Model saved to skills_ner_trained/")
    
    return len(TRAIN_DATA), best_loss, best_loss < 1000

def test_ner_model():
    """Test trained NER model"""
    
    print("\n🧪 TESTING NER MODEL")
    print("=" * 40)
    
    try:
        nlp = spacy.load("skills_ner_trained/")
    except:
        print("❌ No trained model found!")
        return False
    
    test_sentences = [
        "Senior Data Analyst at Bank of America using Python and Snowflake",
        "ROLE Senior Data Analyst CLIENT Home Depot June 2023 Current",
        "Worked at Starbucks California from January 2020 to June 2021",
        "Bachelor of Technology from Bharath University 2010 to 2014",
        "AWS Certified Developer Associate and Azure Certified Developer Associate",
        "Built microservices with Spring Boot Docker and Kubernetes",
        "Sr Full Stack Developer at Credit Karma February 2018",
        "Completed MBA from IIM Ahmedabad in 2017",
        "Used Python PySpark Snowflake and AWS Glue for data pipeline",
        "Joined Amazon Hyderabad India as SDE-II in October 2015",
    ]
    
    print("=== NER TEST RESULTS ===")
    working_labels = set()
    
    for sent in test_sentences:
        doc = nlp(sent)
        print(f"\nText: {sent}")
        if doc.ents:
            for ent in doc.ents:
                print(f"  [{ent.label_}] {ent.text}")
                working_labels.add(ent.label_)
        else:
            print("  NO ENTITIES FOUND")
    
    return working_labels

if __name__ == "__main__":
    valid_count = generate_ner_training_spacy3()
    
    # Train model if we have enough data
    if valid_count >= 200:
        train_count, final_loss, success = train_ner_model()
        working_labels = test_ner_model()
        
        print("\n" + "=" * 60)
        print("FINAL STATUS REPORT")
        print("=" * 60)
        print(f"Data Generation:")
        print(f"  Valid examples generated: {valid_count}")
        print(f"  Training examples used: {train_count}")
        print(f"\nTraining:")
        print(f"  Iterations run: 30")
        print(f"  Final loss: {final_loss:.2f}")
        print(f"  Model saved: YES")
        print(f"  Training success: {success}")
        print(f"\nTest Results:")
        print(f"  SKILL working: {'YES' if 'SKILL' in working_labels else 'NO'}")
        print(f"  TITLE working: {'YES' if 'TITLE' in working_labels else 'NO'}")
        print(f"  COMPANY working: {'YES' if 'COMPANY' in working_labels else 'NO'}")
        print(f"  DATE working: {'YES' if 'DATE' in working_labels else 'NO'}")
        print(f"  EDUCATION working: {'YES' if 'EDUCATION' in working_labels else 'NO'}")
        print(f"  CERTIFICATION working: {'YES' if 'CERTIFICATION' in working_labels else 'NO'}")
        print(f"\nOVERALL STATUS: {'READY' if success and final_loss < 1000 else 'NOT READY'}")
        print("=" * 60)
    else:
        print(f"\n❌ INSUFFICIENT DATA: {valid_count} examples (need 200+)")
        print("Please fix entity alignment issues before training.")
