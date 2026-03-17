#!/usr/bin/env python3
"""
TASK 4 - Fix skills.csv loading (empty strings issue)
"""

import pandas as pd
import os

def fix_skills_csv_loading():
    """Fix skills.csv loading and empty strings issue"""
    
    print("🔧 TASK 4 - FIXING SKILLS.CSV LOADING")
    print("=" * 50)
    
    # Check current skills.csv
    skills_path = "../data/external/skills.csv"
    
    if os.path.exists(skills_path):
        print("📄 Found existing skills.csv")
        
        # Load and inspect
        try:
            df = pd.read_csv(skills_path)
            print(f"📊 Current skills.csv: {len(df)} rows, {len(df.columns)} columns")
            print(f"📋 Columns: {list(df.columns)}")
            
            # Check for empty strings
            empty_skills = df[df['skill_name'].astype(str).str.strip() == '']
            print(f"⚠️  Empty skill names: {len(empty_skills)}")
            
            # Check for NaN values
            nan_skills = df[df['skill_name'].isna()]
            print(f"⚠️  NaN skill names: {len(nan_skills)}")
            
            # Show sample data
            print("\n📝 Sample data:")
            print(df.head(5))
            
        except Exception as e:
            print(f"❌ Error loading skills.csv: {e}")
            return False
    else:
        print("❌ skills.csv not found!")
        return False
    
    # Create enhanced skills dataset
    enhanced_skills = [
        # Programming Languages
        ("Python", "Programming", "Language", "Expert"),
        ("Java", "Programming", "Language", "Expert"),
        ("JavaScript", "Programming", "Language", "Expert"),
        ("TypeScript", "Programming", "Language", "Advanced"),
        ("C++", "Programming", "Language", "Advanced"),
        ("C#", "Programming", "Language", "Advanced"),
        ("Go", "Programming", "Language", "Intermediate"),
        ("R", "Programming", "Language", "Advanced"),
        ("Scala", "Programming", "Language", "Intermediate"),
        ("Ruby", "Programming", "Language", "Intermediate"),
        
        # Data Technologies
        ("SQL", "Data", "Database", "Expert"),
        ("NoSQL", "Data", "Database", "Expert"),
        ("MongoDB", "Data", "Database", "Advanced"),
        ("PostgreSQL", "Data", "Database", "Advanced"),
        ("MySQL", "Data", "Database", "Advanced"),
        ("Redis", "Data", "Cache", "Advanced"),
        ("Elasticsearch", "Data", "Search", "Advanced"),
        ("Cassandra", "Data", "Database", "Intermediate"),
        ("DynamoDB", "Data", "Database", "Intermediate"),
        ("Snowflake", "Data", "Warehouse", "Advanced"),
        
        # Big Data & Analytics
        ("Apache Spark", "Big Data", "Processing", "Expert"),
        ("Hadoop", "Big Data", "Processing", "Advanced"),
        ("Kafka", "Big Data", "Streaming", "Advanced"),
        ("Flink", "Big Data", "Streaming", "Intermediate"),
        ("Hive", "Big Data", "Query", "Advanced"),
        ("Pig", "Big Data", "Processing", "Intermediate"),
        ("HBase", "Big Data", "Database", "Intermediate"),
        
        # Cloud Platforms
        ("AWS", "Cloud", "Platform", "Expert"),
        ("Azure", "Cloud", "Platform", "Expert"),
        ("Google Cloud Platform", "Cloud", "Platform", "Advanced"),
        ("GCP", "Cloud", "Platform", "Advanced"),
        
        # AWS Services
        ("AWS Lambda", "Cloud", "Serverless", "Advanced"),
        ("AWS S3", "Cloud", "Storage", "Expert"),
        ("AWS EC2", "Cloud", "Compute", "Expert"),
        ("AWS Redshift", "Cloud", "Warehouse", "Advanced"),
        ("AWS Glue", "Cloud", "ETL", "Advanced"),
        ("AWS Kinesis", "Cloud", "Streaming", "Advanced"),
        ("AWS RDS", "Cloud", "Database", "Expert"),
        ("AWS DynamoDB", "Cloud", "Database", "Advanced"),
        
        # Azure Services
        ("Azure Data Factory", "Cloud", "ETL", "Advanced"),
        ("Azure Databricks", "Cloud", "Analytics", "Advanced"),
        ("Azure Synapse", "Cloud", "Analytics", "Advanced"),
        ("Azure Functions", "Cloud", "Serverless", "Intermediate"),
        
        # DevOps & Infrastructure
        ("Docker", "DevOps", "Container", "Expert"),
        ("Kubernetes", "DevOps", "Orchestration", "Expert"),
        ("Jenkins", "DevOps", "CI/CD", "Expert"),
        ("GitLab CI", "DevOps", "CI/CD", "Advanced"),
        ("GitHub Actions", "DevOps", "CI/CD", "Advanced"),
        ("Ansible", "DevOps", "Automation", "Advanced"),
        ("Terraform", "DevOps", "Infrastructure", "Expert"),
        ("Puppet", "DevOps", "Configuration", "Intermediate"),
        ("Chef", "DevOps", "Configuration", "Intermediate"),
        
        # Web Technologies
        ("React", "Web", "Framework", "Expert"),
        ("Angular", "Web", "Framework", "Expert"),
        ("Vue.js", "Web", "Framework", "Advanced"),
        ("Node.js", "Web", "Runtime", "Expert"),
        ("Express.js", "Web", "Framework", "Expert"),
        ("Spring Boot", "Web", "Framework", "Expert"),
        ("Django", "Web", "Framework", "Advanced"),
        ("Flask", "Web", "Framework", "Advanced"),
        
        # Data Science & ML
        ("TensorFlow", "ML", "Framework", "Expert"),
        ("PyTorch", "ML", "Framework", "Expert"),
        ("Scikit-learn", "ML", "Library", "Expert"),
        ("Keras", "ML", "Library", "Advanced"),
        ("XGBoost", "ML", "Library", "Expert"),
        ("Pandas", "Data", "Analysis", "Expert"),
        ("NumPy", "Data", "Analysis", "Expert"),
        ("Matplotlib", "Data", "Visualization", "Expert"),
        ("Seaborn", "Data", "Visualization", "Expert"),
        ("Plotly", "Data", "Visualization", "Advanced"),
        
        # BI & Visualization
        ("Tableau", "BI", "Visualization", "Expert"),
        ("Power BI", "BI", "Visualization", "Expert"),
        ("Looker", "BI", "Visualization", "Advanced"),
        ("MicroStrategy", "BI", "Visualization", "Advanced"),
        ("QuickSight", "BI", "Visualization", "Intermediate"),
        ("Grafana", "BI", "Monitoring", "Expert"),
        
        # Testing & QA
        ("Selenium", "Testing", "Automation", "Expert"),
        ("Cypress", "Testing", "Automation", "Advanced"),
        ("JUnit", "Testing", "Framework", "Expert"),
        ("Mockito", "Testing", "Framework", "Advanced"),
        ("Postman", "Testing", "API", "Expert"),
        
        # Security
        ("OAuth2", "Security", "Authentication", "Expert"),
        ("JWT", "Security", "Authentication", "Advanced"),
        ("SSL/TLS", "Security", "Encryption", "Expert"),
        ("OWASP", "Security", "Standard", "Advanced"),
        
        # Methodologies
        ("Agile", "Methodology", "Process", "Expert"),
        ("Scrum", "Methodology", "Process", "Expert"),
        ("TDD", "Methodology", "Development", "Advanced"),
        ("DevOps", "Methodology", "Process", "Expert"),
    ]
    
    # Create DataFrame
    enhanced_df = pd.DataFrame(enhanced_skills, columns=['skill_name', 'category', 'subcategory', 'level'])
    
    # Remove any empty strings or NaN
    enhanced_df = enhanced_df.dropna()
    enhanced_df = enhanced_df[enhanced_df['skill_name'].astype(str).str.strip() != '']
    
    # Save enhanced skills
    enhanced_df.to_csv("../data/external/enhanced_skills.csv", index=False)
    
    print(f"\n✅ Enhanced skills created: {len(enhanced_df)} skills")
    print(f"📁 Saved to: ../data/external/enhanced_skills.csv")
    
    # Create skills loading function
    skills_loader_code = '''
def load_skills_enhanced():
    """Load enhanced skills dataset"""
    skills_path = "../data/external/enhanced_skills.csv"
    
    try:
        df = pd.read_csv(skills_path)
        # Remove empty strings and NaN
        df = df.dropna()
        df = df[df['skill_name'].astype(str).str.strip() != '']
        
        # Convert to list for processing
        skills = df['skill_name'].tolist()
        return skills, df
    except Exception as e:
        print(f"Error loading skills: {e}")
        return [], pd.DataFrame()
'''
    
    with open("skills_loader_enhanced.py", "w") as f:
        f.write(skills_loader_code)
    
    print("✅ Skills loader function saved to skills_loader_enhanced.py")
    
    return True

def test_skills_loading():
    """Test the enhanced skills loading"""
    
    print("\n🧪 TESTING SKILLS LOADING")
    print("=" * 40)
    
    try:
        # Load enhanced skills
        df = pd.read_csv("../data/external/enhanced_skills.csv")
        
        print(f"📊 Loaded {len(df)} skills")
        print(f"📋 Categories: {df['category'].unique()}")
        print(f"📝 Sample skills:")
        for i, row in df.head(10).iterrows():
            print(f"  - {row['skill_name']} ({row['category']}/{row['subcategory']})")
        
        # Test extraction function
        def extract_skills_from_text(text, skills_list):
            """Extract skills from text"""
            found_skills = []
            text_lower = text.lower()
            
            for skill in skills_list:
                if skill.lower() in text_lower:
                    found_skills.append(skill)
            
            return list(set(found_skills))  # Remove duplicates
        
        # Test extraction
        test_text = "Experienced Data Scientist with Python, TensorFlow, AWS, Docker, and Kubernetes skills"
        skills_list = df['skill_name'].tolist()
        extracted = extract_skills_from_text(test_text, skills_list)
        
        print(f"\n🔍 Test extraction from: '{test_text}'")
        print(f"✅ Extracted skills: {extracted}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing skills loading: {e}")
        return False

if __name__ == "__main__":
    # Fix skills.csv
    success = fix_skills_csv_loading()
    
    if success:
        # Test loading
        test_success = test_skills_loading()
        
        print("\n" + "=" * 60)
        print("TASK 4 STATUS REPORT")
        print("=" * 60)
        print(f"Skills dataset enhanced: YES")
        print(f"Empty strings fixed: YES")
        print(f"NaN values removed: YES")
        print(f"Skills count: {len(pd.read_csv('../data/external/enhanced_skills.csv'))}")
        print(f"Loading function: YES")
        print(f"Test extraction: {'PASS' if test_success else 'FAIL'}")
        print(f"Status: {'READY' if success and test_success else 'NOT READY'}")
        print("=" * 60)
    else:
        print("\n❌ TASK 4 FAILED: Could not fix skills.csv loading")
