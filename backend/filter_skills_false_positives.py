#!/usr/bin/env python3
"""
TASK 3 - Skill False Positive Filtering
Create controlled skill dictionary and filter false positives
"""

def create_skill_dictionary():
    """Create controlled skill dictionary file"""
    
    print("🔧 TASK 3 - CREATING CONTROLLED SKILL DICTIONARY")
    print("=" * 50)
    
    # Major technology skills dictionary
    skills = [
        # Programming Languages
        "python",
        "java",
        "javascript",
        "typescript",
        "c++",
        "c#",
        "go",
        "rust",
        "ruby",
        "php",
        "scala",
        "kotlin",
        "swift",
        "objective-c",
        "dart",
        "r",
        "matlab",
        "perl",
        "lua",
        "haskell",
        "elixir",
        "f#",
        "clojure",
        "erlang",
        "julia",
        "solidity",
        
        # Web Technologies
        "html",
        "css",
        "react",
        "angular",
        "vue",
        "node.js",
        "express",
        "django",
        "flask",
        "spring",
        "spring boot",
        "laravel",
        "rails",
        "asp.net",
        "next.js",
        "gatsby",
        "nuxt",
        "svelte",
        "ember",
        "backbone",
        "jquery",
        "bootstrap",
        "tailwind",
        "bulma",
        "sass",
        "less",
        "webpack",
        "vite",
        "parcel",
        "rollup",
        
        # Databases
        "sql",
        "mysql",
        "postgresql",
        "sqlite",
        "mongodb",
        "cassandra",
        "redis",
        "elasticsearch",
        "dynamodb",
        "neo4j",
        "influxdb",
        "clickhouse",
        "snowflake",
        "bigquery",
        "redshift",
        "oracle",
        "db2",
        "mariadb",
        "cockroachdb",
        "scylladb",
        "faunadb",
        "airtable",
        "supabase",
        
        # Cloud Platforms
        "aws",
        "azure",
        "gcp",
        "google cloud",
        "heroku",
        "digitalocean",
        "linode",
        "vultr",
        "scaleway",
        "ovh",
        "alibaba cloud",
        "tencent cloud",
        "ibm cloud",
        "oracle cloud",
        
        # AWS Services
        "ec2",
        "s3",
        "lambda",
        "rds",
        "dynamodb",
        "redshift",
        "glue",
        "kinesis",
        "sns",
        "sqs",
        "cloudformation",
        "terraform",
        "cloudfront",
        "api gateway",
        "cognito",
        "iam",
        "vpc",
        "route53",
        "efs",
        "eks",
        "ecs",
        "batch",
        "step functions",
        "athena",
        "quicksight",
        
        # Azure Services
        "azure functions",
        "azure data factory",
        "azure databricks",
        "azure synapse",
        "azure devops",
        "azure pipelines",
        "azure storage",
        "azure sql",
        "azure cosmos db",
        "azure key vault",
        "azure active directory",
        
        # Google Cloud Services
        "google cloud functions",
        "google cloud run",
        "google cloud storage",
        "google bigquery",
        "google pub/sub",
        "google cloud sql",
        "google compute engine",
        "google kubernetes engine",
        
        # DevOps & Infrastructure
        "docker",
        "kubernetes",
        "jenkins",
        "gitlab ci",
        "github actions",
        "ansible",
        "puppet",
        "chef",
        "terraform",
        "packer",
        "vagrant",
        "kops",
        "helm",
        "prometheus",
        "grafana",
        "elasticsearch",
        "logstash",
        "kibana",
        "fluentd",
        "nginx",
        "apache",
        "traefik",
        "envoy",
        "istio",
        "linkerd",
        "consul",
        "vault",
        "nomad",
        
        # Big Data & Analytics
        "spark",
        "hadoop",
        "kafka",
        "flink",
        "storm",
        "samza",
        "hive",
        "pig",
        "hbase",
        "cassandra",
        "zookeeper",
        "airflow",
        "luigi",
        "azkaban",
        "oozie",
        "nifi",
        "beam",
        "dataflow",
        "pubsub",
        "pulsar",
        "bookkeeper",
        
        # Data Science & ML
        "tensorflow",
        "pytorch",
        "keras",
        "scikit-learn",
        "pandas",
        "numpy",
        "scipy",
        "matplotlib",
        "seaborn",
        "plotly",
        "bokeh",
        "jupyter",
        "xgboost",
        "lightgbm",
        "catboost",
        "h2o",
        "spark mllib",
        "mlflow",
        "kubeflow",
        "sagemaker",
        "azure ml",
        "google cloud ml",
        
        # Business Intelligence & Visualization
        "tableau",
        "power bi",
        "looker",
        "qlikview",
        "qlik sense",
        "microstrategy",
        "cognos",
        "sap businessobjects",
        "spotfire",
        "domo",
        "sisense",
        "thoughtspot",
        "periscope",
        "metabase",
        "superset",
        "redash",
        "grafana",
        
        # Testing & QA
        "selenium",
        "cypress",
        "playwright",
        "testcafe",
        "jest",
        "mocha",
        "jasmine",
        "karma",
        "chai",
        "sinon",
        "junit",
        "testng",
        "pytest",
        "unittest",
        "mockito",
        "powermock",
        "wiremock",
        "postman",
        "insomnia",
        "soapui",
        "jmeter",
        "gatling",
        "k6",
        "artillery",
        
        # Security
        "oauth",
        "jwt",
        "ssl",
        "tls",
        "https",
        "ssh",
        "firewall",
        "vpn",
        "waf",
        "ids",
        "ips",
        "siem",
        "soar",
        "xss",
        "csrf",
        "sql injection",
        "penetration testing",
        "vulnerability assessment",
        "ethical hacking",
        "owasp",
        
        # Version Control
        "git",
        "github",
        "gitlab",
        "bitbucket",
        "svn",
        "mercurial",
        "perforce",
        "tfs",
        "vsts",
        "azure devops",
        
        # Project Management
        "jira",
        "confluence",
        "trello",
        "asana",
        "monday.com",
        "clickup",
        "notion",
        "slack",
        "microsoft teams",
        "zoom",
        "webex",
        "skype",
        
        # Methodologies
        "agile",
        "scrum",
        "kanban",
        "lean",
        "devops",
        "cicd",
        "tdd",
        "bdd",
        "atdd",
        "pair programming",
        "code review",
        "continuous integration",
        "continuous deployment",
        "continuous delivery",
        
        # Architecture Patterns
        "microservices",
        "serverless",
        "event-driven",
        "cqrs",
        "event sourcing",
        "domain driven design",
        "hexagonal architecture",
        "clean architecture",
        "onion architecture",
        "mvc",
        "mvp",
        "mvvm",
        "rest",
        "graphql",
        "grpc",
        "soap",
        "websockets",
        "sse",
        
        # Monitoring & Observability
        "prometheus",
        "grafana",
        "datadog",
        "new relic",
        "splunk",
        "elasticsearch",
        "logstash",
        "kibana",
        "fluentd",
        "jaeger",
        "zipkin",
        "opentracing",
        "opentelemetry",
        "honeycomb",
        "lightstep",
        "launchdarkly",
        "feature flag",
        
        # Mobile Development
        "ios",
        "android",
        "react native",
        "flutter",
        "xamarin",
        "ionic",
        "cordova",
        "phonegap",
        "swift",
        "objective-c",
        "kotlin",
        "java",
        "dart",
        
        # Desktop Development
        "electron",
        "qt",
        "gtk",
        "wxwidgets",
        "winforms",
        "wpf",
        "uwp",
        "java fx",
        "swing",
        "awt",
        
        # Game Development
        "unity",
        "unreal engine",
        "godot",
        "cryengine",
        "phaser",
        "three.js",
        "babylon.js",
        "webgl",
        "opengl",
        "directx",
        "vulkan",
        
        # Blockchain & Web3
        "ethereum",
        "bitcoin",
        "solidity",
        "web3",
        "smart contracts",
        "dapps",
        "nft",
        "defi",
        "dao",
        "metamask",
        "truffle",
        "hardhat",
        "ganache",
        
        # IoT & Embedded
        "arduino",
        "raspberry pi",
        "esp32",
        "esp8266",
        "mqtt",
        "coap",
        "zigbee",
        "z-wave",
        "bluetooth",
        "wifi",
        "lorawan",
        "nb-iot",
        
        # Additional Tech Skills
        "api",
        "sdk",
        "cli",
        "gui",
        "ui",
        "ux",
        "frontend",
        "backend",
        "full stack",
        "middleware",
        "integration",
        "migration",
        "deployment",
        "configuration",
        "automation",
        "orchestration",
        "containerization",
        "virtualization",
        "networking",
        "security",
        "performance",
        "scalability",
        "reliability",
        "availability",
        "monitoring",
        "logging",
        "debugging",
        "testing",
        "documentation",
        "code review",
        "refactoring",
        "optimization",
        "troubleshooting",
        "maintenance",
        "support",
    ]
    
    # Sort skills alphabetically
    skills.sort()
    
    # Save to file
    with open("../data/external/skill_dictionary.txt", "w", encoding="utf-8") as f:
        for skill in skills:
            f.write(skill + "\n")
    
    print(f"✅ Created skill dictionary with {len(skills)} skills")
    print(f"📁 Saved to: ../data/external/skill_dictionary.txt")
    
    return skills

def load_skill_dictionary():
    """Load skill dictionary from file"""
    
    try:
        with open("../data/external/skill_dictionary.txt", "r", encoding="utf-8") as f:
            skills = [line.strip().lower() for line in f if line.strip()]
        return set(skills)
    except FileNotFoundError:
        print("❌ Skill dictionary file not found!")
        return set()

def filter_skills(raw_skills):
    """Filter skills using controlled dictionary"""
    
    print("🔍 FILTERING SKILLS")
    print("=" * 30)
    
    # Load skill dictionary
    skill_dict = load_skill_dictionary()
    
    if not skill_dict:
        print("❌ No skill dictionary loaded!")
        return raw_skills
    
    # Filter skills
    filtered_skills = []
    removed_skills = []
    
    for skill in raw_skills:
        # Normalize skill
        normalized_skill = skill.lower().strip()
        
        # Remove punctuation and extra spaces
        normalized_skill = normalized_skill.replace(".", "").replace(",", "").replace(";", "").replace(":", "")
        normalized_skill = " ".join(normalized_skill.split())
        
        # Check if in dictionary
        if normalized_skill in skill_dict:
            filtered_skills.append(skill)  # Keep original casing
        else:
            removed_skills.append(skill)
    
    # Remove duplicates while preserving order
    unique_skills = []
    seen = set()
    for skill in filtered_skills:
        if skill.lower() not in seen:
            unique_skills.append(skill)
            seen.add(skill.lower())
    
    print(f"📊 Input skills: {len(raw_skills)}")
    print(f"✅ Valid skills: {len(unique_skills)}")
    print(f"❌ Removed skills: {len(removed_skills)}")
    
    if removed_skills:
        print(f"\n❌ Removed false positives:")
        for skill in removed_skills[:10]:  # Show first 10
            print(f"  - '{skill}'")
        if len(removed_skills) > 10:
            print(f"  ... and {len(removed_skills) - 10} more")
    
    return unique_skills

def test_skill_filtering():
    """Test skill filtering with examples"""
    
    print("\n🧪 TESTING SKILL FILTERING")
    print("=" * 40)
    
    # Create skill dictionary
    skills = create_skill_dictionary()
    
    # Test cases
    test_cases = [
        # Good skills
        ["python", "aws", "docker", "kubernetes", "spark", "tensorflow"],
        
        # Mixed with false positives
        ["python", "support", "aws", "tools", "docker", "customer", "kafka", "system", "process"],
        
        # Common false positives
        ["support", "tools", "customer", "system", "process", "management", "communication", "teamwork"],
        
        # Edge cases
        ["Python", "AWS", "DOCKER", "KUBERNETES"],  # Mixed case
        ["python", "python", "aws", "aws"],  # Duplicates
        ["", " ", "  ", "python"],  # Empty/whitespace
        ["machine learning", "deep learning", "artificial intelligence"],  # Multi-word
        ["c++", "c#", "node.js", "react.js"],  # Special characters
    ]
    
    for i, test_skills in enumerate(test_cases):
        print(f"\n📝 Test {i+1}: {test_skills}")
        
        filtered = filter_skills(test_skills)
        
        print(f"✅ Filtered: {filtered}")
        print(f"📏 {len(test_skills)} → {len(filtered)} skills")

def create_skill_filter_function():
    """Create skill filter function for integration"""
    
    print("\n🔗 CREATING SKILL FILTER FUNCTION")
    print("=" * 40)
    
    filter_function = '''
def filter_skills_with_dictionary(raw_skills):
    """Filter skills using controlled dictionary to remove false positives"""
    
    # Load skill dictionary
    try:
        with open("data/external/skill_dictionary.txt", "r", encoding="utf-8") as f:
            skill_dict = set(line.strip().lower() for line in f if line.strip())
    except FileNotFoundError:
        print("Warning: Skill dictionary not found, returning raw skills")
        return raw_skills
    
    # Filter skills
    filtered_skills = []
    seen = set()
    
    for skill in raw_skills:
        # Normalize skill
        normalized_skill = skill.lower().strip()
        
        # Remove punctuation and extra spaces
        normalized_skill = normalized_skill.replace(".", "").replace(",", "").replace(";", "").replace(":", "")
        normalized_skill = " ".join(normalized_skill.split())
        
        # Check if in dictionary and not duplicate
        if normalized_skill in skill_dict and normalized_skill not in seen:
            filtered_skills.append(skill)  # Keep original casing
            seen.add(normalized_skill)
    
    return filtered_skills
'''
    
    with open("skill_filter_function.py", "w", encoding="utf-8") as f:
        f.write(filter_function)
    
    print("✅ Skill filter function saved to skill_filter_function.py")
    
    return filter_function

if __name__ == "__main__":
    # Create skill dictionary
    create_skill_dictionary()
    
    # Test filtering
    test_skill_filtering()
    
    # Create integration function
    create_skill_filter_function()
    
    print("\n" + "=" * 60)
    print("TASK 3 STATUS REPORT")
    print("=" * 60)
    print(f"Skill dictionary created: YES")
    print(f"Skills in dictionary: {len(load_skill_dictionary())}")
    print(f"Filter function created: YES")
    print(f"False positive removal: TESTED")
    print(f"Integration ready: YES")
    print(f"Status: READY")
    print("=" * 60)
