import os

file_path = r"c:\Lalataksha V Company\Main-branch\Lakshya-LLM-Resume-Parser\ai-service\main.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replacement 1: DeBERTa success block (20 spaces indentation)
target1 = """                    # Post-process skills: extract extra skills from job titles/descriptions
                    try:
                        from parsers.rule_parser import RuleBasedParser
                        rule_parser = RuleBasedParser()
                        extra_skills = []
                        for exp in work_experience:
                            title = exp.get('job_title') or exp.get('title')
                            if title:
                                title_skills = rule_parser.extract_skills(title)
                                if title_skills:
                                    extra_skills.extend(title_skills)
                            desc = exp.get('description')
                            if desc:
                                desc_skills = rule_parser.extract_skills(desc[:500])
                                if desc_skills:
                                    extra_skills.extend(desc_skills)
                        
                        if extra_skills:
                            skills = list(dict.fromkeys(skills + extra_skills))
                    except Exception as skill_err:
                        logger.warning(f"Failed to post-process skills from experience in parse-sections: {skill_err}")"""

replacement1 = """                    # Post-process skills: extract extra skills from job titles/descriptions and raw text
                    try:
                        from parsers.rule_parser import RuleBasedParser
                        rule_parser = RuleBasedParser()
                        extra_skills = []
                        for exp in work_experience:
                            title = exp.get('job_title') or exp.get('title')
                            if title:
                                title_skills = rule_parser.extract_skills(title)
                                if title_skills:
                                    extra_skills.extend(title_skills)
                            desc = exp.get('description')
                            if desc:
                                desc_skills = rule_parser.extract_skills(desc[:500])
                                if desc_skills:
                                    extra_skills.extend(desc_skills)
                        
                        if request.experience_text and request.experience_text.strip():
                            raw_exp_skills = rule_parser.extract_skills(request.experience_text)
                            if raw_exp_skills:
                                extra_skills.extend(raw_exp_skills)
                                
                        if request.projects_text and request.projects_text.strip():
                            raw_proj_skills = rule_parser.extract_skills(request.projects_text)
                            if raw_proj_skills:
                                extra_skills.extend(raw_proj_skills)
                                
                        if request.summary_text and request.summary_text.strip():
                            raw_sum_skills = rule_parser.extract_skills(request.summary_text)
                            if raw_sum_skills:
                                extra_skills.extend(raw_sum_skills)
                                
                        if extra_skills:
                            skills = list(dict.fromkeys(skills + extra_skills))
                    except Exception as skill_err:
                        logger.warning(f"Failed to post-process skills from experience in parse-sections: {skill_err}")"""

# Replacement 2: Regex fallback block (8 spaces indentation)
target2 = """        # Post-process skills: extract extra skills from job titles/descriptions
        try:
            from parsers.rule_parser import RuleBasedParser
            rule_parser = RuleBasedParser()
            extra_skills = []
            for exp in work_experience:
                title = exp.get('job_title') or exp.get('title')
                if title:
                    title_skills = rule_parser.extract_skills(title)
                    if title_skills:
                        extra_skills.extend(title_skills)
                desc = exp.get('description')
                if desc:
                    desc_skills = rule_parser.extract_skills(desc[:500])
                    if desc_skills:
                        extra_skills.extend(desc_skills)
            
            if extra_skills:
                skills = list(dict.fromkeys(skills + extra_skills))
        except Exception as skill_err:
            logger.warning(f"Failed to post-process skills from experience in parse-sections: {skill_err}")"""

replacement2 = """        # Post-process skills: extract extra skills from job titles/descriptions and raw text
        try:
            from parsers.rule_parser import RuleBasedParser
            rule_parser = RuleBasedParser()
            extra_skills = []
            for exp in work_experience:
                title = exp.get('job_title') or exp.get('title')
                if title:
                    title_skills = rule_parser.extract_skills(title)
                    if title_skills:
                        extra_skills.extend(title_skills)
                desc = exp.get('description')
                if desc:
                    desc_skills = rule_parser.extract_skills(desc[:500])
                    if desc_skills:
                        extra_skills.extend(desc_skills)
            
            if request.experience_text and request.experience_text.strip():
                raw_exp_skills = rule_parser.extract_skills(request.experience_text)
                if raw_exp_skills:
                    extra_skills.extend(raw_exp_skills)
                    
            if request.projects_text and request.projects_text.strip():
                raw_proj_skills = rule_parser.extract_skills(request.projects_text)
                if raw_proj_skills:
                    extra_skills.extend(raw_proj_skills)
                    
            if request.summary_text and request.summary_text.strip():
                raw_sum_skills = rule_parser.extract_skills(request.summary_text)
                if raw_sum_skills:
                    extra_skills.extend(raw_sum_skills)
                    
            if extra_skills:
                skills = list(dict.fromkeys(skills + extra_skills))
        except Exception as skill_err:
            logger.warning(f"Failed to post-process skills from experience in parse-sections: {skill_err}")"""

# Replace LF version
if target1 in content:
    content = content.replace(target1, replacement1)
    print("Replaced target1 LF")
elif target1.replace("\n", "\r\n") in content:
    content = content.replace(target1.replace("\n", "\r\n"), replacement1.replace("\n", "\r\n"))
    print("Replaced target1 CRLF")
else:
    print("target1 not found!")

if target2 in content:
    content = content.replace(target2, replacement2)
    print("Replaced target2 LF")
elif target2.replace("\n", "\r\n") in content:
    content = content.replace(target2.replace("\n", "\r\n"), replacement2.replace("\n", "\r\n"))
    print("Replaced target2 CRLF")
else:
    print("target2 not found!")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
