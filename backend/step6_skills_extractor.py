#!/usr/bin/env python3
"""
STEP 6 — EXTEND SKILLS EXTRACTOR
"""

def extend_skills_extractor():
    """Add new skills extraction formats to skill_extractor.py"""
    
    print("=" * 120)
    print("🔍 STEP 6 — EXTEND SKILLS EXTRACTOR")
    print("=" * 120)
    
    print("\n📋 FORMATS TO ADD:")
    
    formats = {
        "COMMA_SEPARATED": {
            "pattern": r'^([^,]+(?:,\s*([^,]+))*$',
            "example": "Python, Java, Spring Boot, AWS, Docker",
            "description": "Extract comma-separated skills"
        },
        
        "BULLET_POINTS": {
            "patterns": [
                r'^[\s]*[•\-*–—·]\s*(.+?)$',
                r'^[\s]*[-*]\s*(.+?)$',
                r'^[\s]*\d+\.\s*(.+?)$'
            ],
            "example": "• Python • Java • Spring Boot",
            "description": "Extract bullet point skills"
        },
        
        "PIPE_SEPARATED": {
            "pattern": r'^([^|]+(?:\s*\|\s*([^|]+))*$',
            "example": "Python | Java | AWS | Docker",
            "description": "Extract pipe-separated skills"
        },
        
        "SLASH_SEPARATED": {
            "pattern": r'^([^/]+(?:\s*/\s*([^/]+))*$',
            "example": "Python/Java/AWS/Docker",
            "description": "Extract slash-separated skills"
        },
        
        "SEMICOLON_SEPARATED": {
            "pattern": r'^([^;]+(?:\s*;\s*([^;]+))*$',
            "example": "Python; Java; AWS; Docker",
            "description": "Extract semicolon-separated skills"
        },
        
        "CATEGORY_COLON_SKILLS": {
            "pattern": r'^([^:]+):\s*(.+?)$',
            "example": "Programming: Python, Java, C++",
            "description": "Extract category and skills from colon format"
        },
        
        "TABLE_FORMAT": {
            "pattern": r'^\|([^|]+)\|([^|]+)\|([^|]*)\|$',
            "example": "| Skill | Proficiency |",
            "description": "Extract from table format, ignore proficiency column"
        },
        
        "PARAGRAPH_FORMAT": {
            "pattern": r'\b(Python|Java|JavaScript|TypeScript|C|C\+\+|Go|Rust|Ruby|PHP|Swift|Kotlin|Scala|R|MATLAB|Perl|Shell|PowerShell|VBA|COBOL|Fortran|Dart|Lua|Haskell|Clojure|Erlang|F\#|Julia|Groovy|Assembly|SQL|PL/SQL|T-SQL|Spring Boot|Spring MVC|Hibernate|Django|Flask|FastAPI|Angular|React|Vue\.js|Next\.js|Nuxt\.js|Express|Node\.js|Laravel|Rails|\.NET|ASP\.NET|Svelte|Gatsby|jQuery|Backbone|Ember|Meteor|Struts|JSF|Docker|Kubernetes|Jenkins|GitLab CI|GitHub Actions|CircleCI|Travis CI|ArgoCD|Helm|Terraform|Ansible|Puppet|Chef|Vagrant|Packer|Prometheus|Grafana|ELK Stack|Splunk|Nagios|Zabbix|New Relic|Datadog|PagerDuty|Nginx|Apache|HAProxy|Istio|Envoy|CI/CD|DevOps|GitOps|Infrastructure as Code|Kafka|Apache Kafka|Spark|Apache Spark|Hadoop|Flink|Storm|Samza|NiFi|Airflow|Luigi|Databricks|Delta Lake|Hive|Pig|Sqoop|Flume|Zookeeper|HDFS|MapReduce|YARN|Presto|Trino|Druid|Pinot|Kylin|dbt|Fivetran|Stitch|Talend|Informatica|Tableau|Power BI|Grafana|Looker|Kibana|Metabase|QlikView|Qlik Sense|Cognos|MicroStrategy|SAP BusinessObjects|Superset|D3\.js|Plotly|Matplotlib|Seaborn|ggplot|Google Data Studio|Redash|AWS QuickSight)\b',
            "example": "Proficient in Python and Java with 5 years experience in cloud platforms including AWS, Azure and GCP",
            "description": "Extract known tech terms from paragraph text"
        },
        
        "SKILLS_WITH_YEARS": {
            "pattern": r'([^()]+)\s*\((\d+)\s+years?\)',
            "example": "Python (5 years), Java (3 years)",
            "description": "Extract skill name and years of experience"
        },
        
        "SKILLS_WITH_PROFICIENCY": {
            "pattern": r'([^–—]+)\s*[-–—]\s*(.+?)$',
            "example": "Python – Expert, Java – Advanced",
            "description": "Extract skill name and proficiency level"
        },
        
        "SKILLS_WITH_VERSIONS": {
            "pattern": r'([^0-9]+)\s*([0-9.]+)',
            "example": "Python 3.9, Java 11, Spring Boot 2.5",
            "description": "Extract skill name and version"
        },
        
        "ENVIRONMENT_LINE": {
            "patterns": [
                r'^(?:Environment|Technologies|Tech Stack|Tools)\s*:\s*(.+?)$',
                r'^(?:Environment|Technologies|Tech Stack|Tools)\s*[-–—]\s*(.+?)$'
            ],
            "example": "Environment: Java, Spring Boot, AWS, Docker, Kubernetes",
            "description": "Extract tech stack from environment lines in work section"
        },
        
        "NESTED_CATEGORIES": {
            "pattern": r'^\s+([^:]+):\s*(.+?)$',
            "example": "  Frontend: React, Angular, Vue.js\n  State Management: Redux, MobX",
            "description": "Handle indented sub-categories"
        },
        
        "RATING_BASED": {
            "pattern": r'([^★☆]+)\s*([★☆]+)$',
            "example": "Python ★★★★★",
            "description": "Extract skill name and map stars to proficiency"
        }
    }
    
    for format_name, format_info in formats.items():
        print(f"\n  FORMAT {format_name}:")
        print(f"    Pattern: {format_info.get('pattern', format_info.get('patterns', 'Multiple patterns'))}")
        print(f"    Example: {format_info['example']}")
        print(f"    Description: {format_info['description']}")
    
    print("\n📋 SKILL CATEGORY MAPPING:")
    categories = {
        "Programming Languages": [
            "Python", "Java", "JavaScript", "TypeScript", "C", "C++", "C#", "Go", "Rust", "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "MATLAB", "Perl", "Shell", "Bash", "PowerShell", "VBA", "COBOL", "Fortran", "Dart", "Lua", "Haskell", "Clojure", "Erlang", "F#", "Julia", "Groovy", "Assembly", "SQL", "PL/SQL", "T-SQL"
        ],
        "Frameworks": [
            "Spring Boot", "Spring MVC", "Hibernate", "Django", "Flask", "FastAPI", "Angular", "React", "Vue.js", "Next.js", "Nuxt.js", "Express", "Node.js", "Laravel", "Rails", ".NET", "ASP.NET", "Svelte", "Gatsby", "Redux", "Bootstrap", "Tailwind", "jQuery", "Backbone", "Ember", "Meteor", "Struts", "JSF"
        ],
        "Cloud": [
            "AWS", "Azure", "GCP", "Google Cloud", "Amazon Web Services", "Azure AD", "AWS S3", "AWS Lambda", "AWS EC2", "AWS RDS", "Azure DevOps", "Azure Functions", "GCP BigQuery", "Heroku", "DigitalOcean", "Linode", "IBM Cloud", "Oracle Cloud", "Alibaba Cloud", "CloudFlare"
        ],
        "Databases": [
            "MySQL", "PostgreSQL", "Oracle", "SQL Server", "SQLite", "MongoDB", "Cassandra", "DynamoDB", "Redis", "Elasticsearch", "Couchbase", "HBase", "Neo4j", "InfluxDB", "TimescaleDB", "Snowflake", "BigQuery", "Redshift", "Vertica", "Teradata", "MariaDB", "CockroachDB"
        ],
        "DevOps": [
            "Docker", "Kubernetes", "Jenkins", "GitLab CI", "GitHub Actions", "CircleCI", "Travis CI", "ArgoCD", "Helm", "Terraform", "Ansible", "Puppet", "Chef", "Vagrant", "Packer", "Prometheus", "Grafana", "ELK Stack", "Splunk", "Nagios", "Zabbix"
        ]
    }
    
    for category, skills in categories.items():
        print(f"\n  {category}:")
        for skill in skills[:5]:  # Show first 5
            print(f"    • {skill}")
        if len(skills) > 5:
            print(f"    • ... and {len(skills) - 5} more")
    
    print("\n📝 SKILL CLEANING RULES:")
    cleaning_rules = [
        "Remove duplicates (case insensitive)",
        "Remove generic non-skills: and, with, using, experience, knowledge, proficient, familiar, understanding, ability, skills, expertise, background",
        "Keep abbreviations: AWS, GCP, SQL, API, REST, SOAP",
        "Normalize common variations:",
        "  Javascript → JavaScript",
        "  Kubernetes → Kubernetes", 
        "  PostgreSQL → PostgreSQL",
        "  Dynamo DB → DynamoDB",
        "  My SQL → MySQL",
        "  Type Script → TypeScript",
        "  Node JS → Node.js",
        "  React JS → React",
        "  Angular JS → AngularJS",
        "  Spring boot → Spring Boot",
        "  J Unit → JUnit",
        "  Power BI → Power BI",
        "  dot net → .NET"
    ]
    
    for rule in cleaning_rules:
        print(f"  • {rule}")
    
    print("\n🎯 IMPLEMENTATION LOCATION:")
    print("File: backend/app/services/parser/skill_extractor.py")
    print("Function: extract_skills() [around line 100]")
    print("Add these patterns before existing skill detection logic")
    
    return formats

if __name__ == "__main__":
    extend_skills_extractor()
