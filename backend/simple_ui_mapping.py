#!/usr/bin/env python3

"""
Simple UI Mapping for Parsed Data
Create UI mapping from parsed_data structure
"""

import json

# Sample parsed data structure (what you'll get from parsed_data column)
sample_parsed_data = {
    "basics": {
        "name": "John Smith",
        "email": "john.smith@email.com",
        "phone": "(555) 123-4567",
        "location": "New York, NY",
        "summary": "Senior Software Engineer with 8 years of experience.",
        "linkedin": "https://linkedin.com/in/johnsmith",
        "github": "https://github.com/johnsmith",
        "website": ""
    },
    "work": [
        {
            "company": "Tech Corp",
            "title": "Senior Software Engineer",
            "location": "New York, NY",
            "startDate": "2020-01-01",
            "endDate": None,
            "description": "Led development of microservices architecture.",
            "current": True
        }
    ],
    "education": [
        {
            "institution": "MIT",
            "degree": "Bachelor of Science in Computer Science",
            "field": "Computer Science",
            "location": "Cambridge, MA",
            "startDate": "2014-09-01",
            "endDate": "2018-05-30",
            "gpa": "3.8",
            "current": False
        }
    ],
    "skills": [
        {
            "name": "Python",
            "level": "Expert",
            "category": "Programming Languages",
            "years_experience": "8",
            "proficiency": "Expert"
        },
        {
            "name": "React",
            "level": "Advanced",
            "category": "Frontend Frameworks",
            "years_experience": "5",
            "proficiency": "Advanced"
        }
    ],
    "certifications": [
        {
            "name": "AWS Certified Solutions Architect",
            "issuer": "Amazon Web Services",
            "date": "2021-03-15",
            "credential_id": "AWSA-123456",
            "url": "https://aws.amazon.com/certification/"
        }
    ]
}

# UI Mapping Structure
ui_mapping = {
    "basics": {
        "name": sample_parsed_data["basics"]["name"],
        "email": sample_parsed_data["basics"]["email"],
        "phone": sample_parsed_data["basics"]["phone"],
        "location": sample_parsed_data["basics"]["location"],
        "summary": sample_parsed_data["basics"]["summary"],
        "linkedin": sample_parsed_data["basics"]["linkedin"],
        "github": sample_parsed_data["basics"]["github"],
        "website": sample_parsed_data["basics"]["website"]
    },
    "work": [
        {
            "company": work["company"],
            "title": work["title"],
            "location": work["location"],
            "startDate": work["startDate"],
            "endDate": work["endDate"],
            "description": work["description"],
            "current": work["current"]
        }
        for work in sample_parsed_data["work"]
    ],
    "education": [
        {
            "institution": edu["institution"],
            "degree": edu["degree"],
            "field": edu["field"],
            "location": edu["location"],
            "startDate": edu["startDate"],
            "endDate": edu["endDate"],
            "gpa": edu["gpa"],
            "current": edu["current"]
        }
        for edu in sample_parsed_data["education"]
    ],
    "skills": [
        {
            "name": skill["name"],
            "level": skill["level"],
            "category": skill["category"],
            "years_experience": skill["years_experience"],
            "proficiency": skill["proficiency"]
        }
        for skill in sample_parsed_data["skills"]
    ],
    "certifications": [
        {
            "name": cert["name"],
            "issuer": cert["issuer"],
            "date": cert["date"],
            "credential_id": cert["credential_id"],
            "url": cert["url"]
        }
        for cert in sample_parsed_data["certifications"]
    ]
}

# HTML Template
html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resume Data Display</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
        .section { margin-bottom: 30px; padding: 20px; border: 1px solid #ddd; border-radius: 8px; background: #fafafa; }
        .section h2 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
        .basics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }
        .field { margin-bottom: 15px; }
        .field label { font-weight: bold; display: block; margin-bottom: 5px; color: #555; }
        .field span { color: #333; }
        .work-item, .education-item { margin-bottom: 20px; padding: 20px; background: #fff; border-radius: 8px; border-left: 4px solid #007bff; }
        .work-item h3, .education-item h3 { color: #007bff; margin: 0 0 8px 0; }
        .subtitle { color: #666; font-style: italic; margin: 5px 0; }
        .dates { color: #28a745; font-weight: bold; margin: 8px 0; }
        .skills-grid, .certifications-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }
        .skill-item, .certification-item { padding: 15px; background: #fff; border-radius: 8px; border: 1px solid #ddd; }
        .current-badge { background: #28a745; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.8em; margin-left: 10px; }
        .links a { margin-right: 15px; color: #007bff; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Resume Data Display</h1>
        
        <div class="section">
            <h2>Basic Information</h2>
            <div class="basics-grid">
                <div class="field">
                    <label>Name:</label>
                    <span>""" + ui_mapping['basics']['name'] + """</span>
                </div>
                <div class="field">
                    <label>Email:</label>
                    <span>""" + ui_mapping['basics']['email'] + """</span>
                </div>
                <div class="field">
                    <label>Phone:</label>
                    <span>""" + ui_mapping['basics']['phone'] + """</span>
                </div>
                <div class="field">
                    <label>Location:</label>
                    <span>""" + ui_mapping['basics']['location'] + """</span>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>Work Experience</h2>
""" + ''.join([f"""
            <div class="work-item">
                <h3>{work['title']}</h3>
                <p class="subtitle">{work['company']} • {work['location']}</p>
                <p class="dates">{work['startDate']} - {work['endDate'] or 'Present'} {'<span class="current-badge">Current</span>' if work['current'] else ''}</p>
                <p>{work['description']}</p>
            </div>
""" for work in ui_mapping['work']]) + """
        </div>
        
        <div class="section">
            <h2>Education</h2>
""" + ''.join([f"""
            <div class="education-item">
                <h3>{edu['degree']}</h3>
                <p class="subtitle">{edu['institution']} • {edu['location']}</p>
                <p class="dates">{edu['startDate']} - {edu['endDate']}</p>
                <p>GPA: {edu['gpa']}</p>
            </div>
""" for edu in ui_mapping['education']]) + """
        </div>
        
        <div class="section">
            <h2>Skills</h2>
            <div class="skills-grid">
""" + ''.join([f"""
                <div class="skill-item">
                    <h4>{skill['name']}</h4>
                    <p><strong>Level:</strong> {skill['level']}</p>
                    <p><strong>Category:</strong> {skill['category']}</p>
                    <p><strong>Years:</strong> {skill['years_experience']}</p>
                </div>
""" for skill in ui_mapping['skills']]) + """
            </div>
        </div>
        
        <div class="section">
            <h2>Certifications</h2>
            <div class="certifications-grid">
""" + ''.join([f"""
                <div class="certification-item">
                    <h4>{cert['name']}</h4>
                    <p><strong>Issuer:</strong> {cert['issuer']}</p>
                    <p><strong>Date:</strong> {cert['date']}</p>
                    <p><strong>ID:</strong> {cert['credential_id']}</p>
                </div>
""" for cert in ui_mapping['certifications']]) + """
            </div>
        </div>
    </div>
</body>
</html>"""

# React Components
react_basics = """
import React from 'react';

const Basics = ({ data }) => {
  return (
    <div className="basics-section">
      <h2>Basic Information</h2>
      <div className="basics-grid">
        <div className="field">
          <label>Name:</label>
          <span>{data.name || 'N/A'}</span>
        </div>
        <div className="field">
          <label>Email:</label>
          <span>{data.email || 'N/A'}</span>
        </div>
        <div className="field">
          <label>Phone:</label>
          <span>{data.phone || 'N/A'}</span>
        </div>
        <div className="field">
          <label>Location:</label>
          <span>{data.location || 'N/A'}</span>
        </div>
        {data.summary && (
          <div className="field full-width">
            <label>Summary:</label>
            <p>{data.summary}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Basics;
"""

react_work = """
import React from 'react';

const WorkExperience = ({ data }) => {
  return (
    <div className="work-section">
      <h2>Work Experience</h2>
      <div className="work-list">
        {data.map((item, index) => (
          <div key={index} className="work-item">
            <h3>{item.title}</h3>
            <p className="subtitle">
              {item.company} {item.location && `• ${item.location}`}
            </p>
            <p className="dates">
              {item.startDate} - {item.endDate || (item.current ? 'Present' : 'N/A')}
              {item.current && <span className="current-badge">Current</span>}
            </p>
            {item.description && (
              <div className="description">{item.description}</div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default WorkExperience;
"""

react_skills = """
import React from 'react';

const Skills = ({ data }) => {
  return (
    <div className="skills-section">
      <h2>Skills</h2>
      <div className="skills-grid">
        {data.map((item, index) => (
          <div key={index} className="skill-item">
            <h4>{item.name}</h4>
            {item.level && <p><strong>Level:</strong> {item.level}</p>}
            {item.category && <p><strong>Category:</strong> {item.category}</p>}
            {item.years_experience && <p><strong>Years:</strong> {item.years_experience}</p>}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Skills;
"""

# Save files
with open('resume_ui_mapping.json', 'w', encoding='utf-8') as f:
    json.dump(ui_mapping, f, indent=2)

with open('sample_parsed_data.json', 'w', encoding='utf-8') as f:
    json.dump(sample_parsed_data, f, indent=2)

with open('resume_display.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

with open('ReactBasics.js', 'w', encoding='utf-8') as f:
    f.write(react_basics)

with open('ReactWork.js', 'w', encoding='utf-8') as f:
    f.write(react_work)

with open('ReactSkills.js', 'w', encoding='utf-8') as f:
    f.write(react_skills)

# API Documentation
api_docs = {
    "get_parsed_data": {
        "method": "GET",
        "url": "/api/resume/latest",
        "description": "Get the latest parsed resume data from parsed_data column",
        "sql_query": "SELECT parsed_data FROM parsing_jobs ORDER BY id DESC LIMIT 1",
        "response_format": ui_mapping
    },
    "database_info": {
        "table": "parsing_jobs",
        "column": "parsed_data",
        "data_type": "JSON",
        "sample_structure": sample_parsed_data
    }
}

with open('resume_api_docs.json', 'w', encoding='utf-8') as f:
    json.dump(api_docs, f, indent=2)

print("🎨 UI Mapping Complete!")
print("=" * 50)
print("📁 Files Created:")
print("  📊 resume_ui_mapping.json - UI data mapping")
print("  📋 sample_parsed_data.json - Sample parsed data")
print("  🎨 resume_display.html - HTML template")
print("  ⚛️ ReactBasics.js - React basics component")
print("  ⚛️ ReactWork.js - React work component")
print("  ⚛️ ReactSkills.js - React skills component")
print("  📚 resume_api_docs.json - API documentation")
print()
print("🎯 How to use:")
print("  1. Query: SELECT parsed_data FROM parsing_jobs ORDER BY id DESC LIMIT 1")
print("  2. Parse JSON response")
print("  3. Use UI mapping to display in your frontend")
print("  4. Open resume_display.html to see example")
print()
print("📱 Open resume_display.html in browser to see the result!")
