
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
