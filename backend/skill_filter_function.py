
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
