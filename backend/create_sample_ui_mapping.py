#!/usr/bin/env python3

"""
Create Sample UI Mapping
Generate UI mapping from sample parsed data structure
"""

import json

def create_sample_parsed_data():
    """Create sample parsed data structure based on your training"""
    return {
        "basics": {
            "name": "John Smith",
            "email": "john.smith@email.com",
            "phone": "(555) 123-4567",
            "location": "New York, NY",
            "summary": "Senior Software Engineer with 8 years of experience in full-stack development.",
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
                "description": "Led development of microservices architecture and improved system performance by 40%.",
                "current": True
            },
            {
                "company": "StartupXYZ",
                "title": "Software Engineer",
                "location": "Boston, MA",
                "startDate": "2018-06-01",
                "endDate": "2020-01-01",
                "description": "Developed RESTful APIs and web applications using React and Node.js.",
                "current": False
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
            },
            {
                "name": "AWS",
                "level": "Advanced",
                "category": "Cloud Platforms",
                "years_experience": "4",
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
        ],
        "projects": [],
        "languages": [
            {
                "language": "English",
                "fluency": "Native"
            }
        ],
        "volunteer": [],
        "references": [],
        "achievements": [],
        "publications": []
    }

def create_ui_mapping(parsed_json):
    """Create UI mapping from parsed JSON"""
    ui_mapping = {
        'basics': {},
        'work': [],
        'education': [],
        'skills': [],
        'certifications': []
    }
    
    # Map basics
    if 'basics' in parsed_json:
        basics = parsed_json['basics']
        ui_mapping['basics'] = {
            'name': basics.get('name', ''),
            'email': basics.get('email', ''),
            'phone': basics.get('phone', ''),
            'location': basics.get('location', ''),
            'summary': basics.get('summary', ''),
            'linkedin': basics.get('linkedin', ''),
            'github': basics.get('github', ''),
            'website': basics.get('website', '')
        }
    
    # Map work experience
    if 'work' in parsed_json and isinstance(parsed_json['work'], list):
        for work in parsed_json['work']:
            ui_mapping['work'].append({
                'company': work.get('company', ''),
                'title': work.get('title', ''),
                'location': work.get('location', ''),
                'startDate': work.get('startDate', ''),
                'endDate': work.get('endDate', ''),
                'description': work.get('description', ''),
                'current': work.get('current', False)
            })
    
    # Map education
    if 'education' in parsed_json and isinstance(parsed_json['education'], list):
        for edu in parsed_json['education']:
            ui_mapping['education'].append({
                'institution': edu.get('institution', ''),
                'degree': edu.get('degree', ''),
                'field': edu.get('field', ''),
                'location': edu.get('location', ''),
                'startDate': edu.get('startDate', ''),
                'endDate': edu.get('endDate', ''),
                'gpa': edu.get('gpa', ''),
                'current': edu.get('current', False)
            })
    
    # Map skills
    if 'skills' in parsed_json and isinstance(parsed_json['skills'], list):
        for skill in parsed_json['skills']:
            ui_mapping['skills'].append({
                'name': skill.get('name', ''),
                'level': skill.get('level', ''),
                'category': skill.get('category', ''),
                'years_experience': skill.get('years_experience', ''),
                'proficiency': skill.get('proficiency', '')
            })
    
    # Map certifications
    if 'certifications' in parsed_json and isinstance(parsed_json['certifications'], list):
        for cert in parsed_json['certifications']:
            ui_mapping['certifications'].append({
                'name': cert.get('name', ''),
                'issuer': cert.get('issuer', ''),
                'date': cert.get('date', ''),
                'credential_id': cert.get('credential_id', ''),
                'url': cert.get('url', '')
            })
    
    return ui_mapping

def generate_html_template(ui_mapping):
    """Generate HTML template for displaying resume data"""
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resume Data Display</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .section { margin-bottom: 30px; padding: 20px; border: 1px solid #ddd; border-radius: 8px; background: #fafafa; }
        .section h2 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; margin-top: 0; }
        .basics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }
        .field { margin-bottom: 15px; }
        .field label { font-weight: bold; display: block; margin-bottom: 5px; color: #555; }
        .field span, .field p { color: #333; line-height: 1.6; }
        .work-item, .education-item { margin-bottom: 20px; padding: 20px; background: #fff; border-radius: 8px; border-left: 4px solid #007bff; }
        .work-item h3, .education-item h3 { color: #007bff; margin: 0 0 8px 0; font-size: 1.2em; }
        .subtitle { color: #666; font-style: italic; margin: 5px 0; font-size: 0.95em; }
        .dates { color: #28a745; font-weight: bold; margin: 8px 0; }
        .skills-grid, .certifications-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }
        .skill-item, .certification-item { padding: 15px; background: #fff; border-radius: 8px; border: 1px solid #ddd; }
        .skill-item h4, .certification-item h4 { color: #333; margin: 0 0 10px 0; font-size: 1.1em; }
        .current-badge { background: #28a745; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.8em; margin-left: 10px; }
        .links a { margin-right: 15px; color: #007bff; text-decoration: none; padding: 5px 10px; border: 1px solid #007bff; border-radius: 4px; }
        .links a:hover { background: #007bff; color: white; }
        .description { margin-top: 10px; padding: 10px; background: #f8f9fa; border-radius: 4px; border-left: 3px solid #17a2b8; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Resume Data Display</h1>
"""
    
    # Basics section
    if ui_mapping['basics']:
        basics = ui_mapping['basics']
        html += f"""
        <div class="section">
            <h2>Basic Information</h2>
            <div class="basics-grid">
                <div class="field">
                    <label>Name:</label>
                    <span>{basics['name']}</span>
                </div>
                <div class="field">
                    <label>Email:</label>
                    <span>{basics['email']}</span>
                </div>
                <div class="field">
                    <label>Phone:</label>
                    <span>{basics['phone']}</span>
                </div>
                <div class="field">
                    <label>Location:</label>
                    <span>{basics['location']}</span>
                </div>
            </div>
            {f'<div class="field"><label>Summary:</label><p>{basics["summary"]}</p></div>' if basics['summary'] else ''}
            {f'<div class="field"><label>Links:</label><div class="links">{links_str}</div></div>' if (links_str := ' '.join([f'<a href="{basics["linkedin"]}" target="_blank">LinkedIn</a>' if basics['linkedin'] else '',
                              f'<a href="{basics["github"]}" target="_blank">GitHub</a>' if basics['github'] else '',
                              f'<a href="{basics["website"]}" target="_blank">Website</a>' if basics['website'] else ''])) else ''}
        </div>
"""
    
    # Work experience section
    if ui_mapping['work']:
        html += '<div class="section"><h2>Work Experience</h2>'
        for work in ui_mapping['work']:
            html += f"""
            <div class="work-item">
                <h3>{work['title']}</h3>
                <p class="subtitle">{work['company']} {work['location'] and f'• {work["location"]}'}</p>
                <p class="dates">{work['startDate']} - {work['endDate'] or ('Present' if work['current'] else 'N/A')} {'<span class="current-badge">Current</span>' if work['current'] else ''}</p>
                {f'<div class="description">{work["description"]}</div>' if work['description'] else ''}
            </div>
"""
        html += '</div>'
    
    # Education section
    if ui_mapping['education']:
        html += '<div class="section"><h2>Education</h2>'
        for edu in ui_mapping['education']:
            html += f"""
            <div class="education-item">
                <h3>{edu['degree']}</h3>
                <p class="subtitle">{edu['institution']} {edu['location'] and f'• {edu["location"]}'}</p>
                <p class="dates">{edu['startDate']} - {edu['endDate'] or ('Present' if edu['current'] else 'N/A')} {'<span class="current-badge">Current</span>' if edu['current'] else ''}</p>
                {f'<p><strong>GPA:</strong> {edu["gpa"]}</p>' if edu['gpa'] else ''}
            </div>
"""
        html += '</div>'
    
    # Skills section
    if ui_mapping['skills']:
        html += '<div class="section"><h2>Skills</h2><div class="skills-grid">'
        for skill in ui_mapping['skills']:
            html += f"""
            <div class="skill-item">
                <h4>{skill['name']}</h4>
                {f'<p><strong>Level:</strong> {skill["level"]}</p>' if skill['level'] else ''}
                {f'<p><strong>Category:</strong> {skill["category"]}</p>' if skill['category'] else ''}
                {f'<p><strong>Years:</strong> {skill["years_experience"]}</p>' if skill['years_experience'] else ''}
            </div>
"""
        html += '</div></div>'
    
    # Certifications section
    if ui_mapping['certifications']:
        html += '<div class="section"><h2>Certifications</h2><div class="certifications-grid">'
        for cert in ui_mapping['certifications']:
            html += f"""
            <div class="certification-item">
                <h4>{cert['name']}</h4>
                {f'<p><strong>Issuer:</strong> {cert["issuer"]}</p>' if cert['issuer'] else ''}
                {f'<p><strong>Date:</strong> {cert["date"]}</p>' if cert['date'] else ''}
                {f'<p><strong>ID:</strong> {cert["credential_id"]}</p>' if cert['credential_id'] else ''}
                {f'<p><strong>URL:</strong> <a href="{cert["url"]}" target="_blank">{cert["url"]}</a></p>' if cert['url'] else ''}
            </div>
"""
        html += '</div></div>'
    
    html += """
    </div>
</body>
</html>
"""
    
    return html

def generate_react_components(ui_mapping):
    """Generate React components for each section"""
    components = {}
    
    # Basics component
    basics = ui_mapping['basics']
    components['basics'] = f"""
import React from 'react';

const Basics = {{ data }} => {{
  return (
    <div className="basics-section">
      <h2>Basic Information</h2>
      <div className="basics-grid">
        <div className="field">
          <label>Name:</label>
          <span>{{data.name || 'N/A'}}</span>
        </div>
        <div className="field">
          <label>Email:</label>
          <span>{{data.email || 'N/A'}}</span>
        </div>
        <div className="field">
          <label>Phone:</label>
          <span>{{data.phone || 'N/A'}}</span>
        </div>
        <div className="field">
          <label>Location:</label>
          <span>{{data.location || 'N/A'}}</span>
        </div>
        {{data.summary && (
          <div className="field full-width">
            <label>Summary:</label>
            <p>{{data.summary}}</p>
          </div>
        )}
        {{(data.linkedin || data.github || data.website) && (
          <div className="field full-width">
            <label>Links:</label>
            <div className="links">
              {{data.linkedin && <a href={{data.linkedin}} target="_blank">LinkedIn</a>}}
              {{data.github && <a href={{data.github}} target="_blank">GitHub</a>}}
              {{data.website && <a href={{data.website}} target="_blank">Website</a>}}
            </div>
          </div>
        )}}
      </div>
    </div>
  );
}};

export default Basics;
"""
    
    # Work component
    components['work'] = f"""
import React from 'react';

const WorkExperience = {{ data }} => {{
  return (
    <div className="work-section">
      <h2>Work Experience</h2>
      <div className="work-list">
        {{data.map((item, index) => (
          <div key={{index}} className="work-item">
            <h3>{{item.title}}</h3>
            <p className="subtitle">
              {{item.company}} {{item.location && `• {{item.location}}`}}
            </p>
            <p className="dates">
              {{item.startDate}} - {{item.endDate || (item.current ? 'Present' : 'N/A')}}
              {{item.current && <span className="current-badge">Current</span>}}
            </p>
            {{item.description && (
              <div className="description">{{item.description}}</div>
            )}}
          </div>
        ))}}
      </div>
    </div>
  );
}};

export default WorkExperience;
"""
    
    # Skills component
    components['skills'] = f"""
import React from 'react';

const Skills = {{ data }} => {{
  return (
    <div className="skills-section">
      <h2>Skills</h2>
      <div className="skills-grid">
        {{data.map((item, index) => (
          <div key={{index}} className="skill-item">
            <h4>{{item.name}}</h4>
            {{item.level && <p><strong>Level:</strong> {{item.level}}</p>}}
            {{item.category && <p><strong>Category:</strong> {{item.category}}</p>}}
            {{item.years_experience && <p><strong>Years:</strong> {{item.years_experience}}</p>}}
          </div>
        ))}}
      </div>
    </div>
  );
}};

export default Skills;
"""
    
    return components

def main():
    """Main function to create sample UI mapping"""
    print("🎨 Creating Sample UI Mapping")
    print("=" * 50)
    
    # Create sample parsed data
    sample_data = create_sample_parsed_data()
    print("✅ Sample parsed data created")
    
    # Create UI mapping
    ui_mapping = create_ui_mapping(sample_data)
    print("✅ UI mapping created")
    
    print("📊 UI Data Summary:")
    print(f"  👤 Basics: {'✅' if ui_mapping['basics'] else '❌'}")
    print(f"  💼 Work: {len(ui_mapping['work'])} positions")
    print(f"  🎓 Education: {len(ui_mapping['education'])} entries")
    print(f"  🔧 Skills: {len(ui_mapping['skills'])} skills")
    print(f"  🏆 Certifications: {len(ui_mapping['certifications'])} certifications")
    print()
    
    # Generate HTML template
    html_template = generate_html_template(ui_mapping)
    
    # Generate React components
    react_components = generate_react_components(ui_mapping)
    
    # Save files
    with open('sample_resume_display.html', 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    with open('sample_resume_ui_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(ui_mapping, f, indent=2)
    
    with open('sample_parsed_data.json', 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, indent=2)
    
    # Save React components
    for section, component in react_components.items():
        with open(f'React{section.capitalize()}.js', 'w', encoding='utf-8') as f:
            f.write(component)
    
    # Create API endpoint documentation
    api_docs = {
        'get_parsed_data': {
            'method': 'GET',
            'url': '/api/resume/latest',
            'description': 'Get the latest parsed resume data from parsed_data column',
            'response_format': ui_mapping,
            'sql_query': 'SELECT parsed_data FROM parsing_jobs ORDER BY id DESC LIMIT 1'
        },
        'get_by_id': {
            'method': 'GET', 
            'url': '/api/resume/:id',
            'description': 'Get resume data by specific job ID',
            'sql_query': 'SELECT parsed_data FROM parsing_jobs WHERE id = ?'
        }
    }
    
    with open('resume_api_documentation.json', 'w', encoding='utf-8') as f:
        json.dump(api_docs, f, indent=2)
    
    print("📁 Files Created:")
    print("  🎨 sample_resume_display.html - HTML template")
    print("  📊 sample_resume_ui_mapping.json - UI data mapping")
    print("  📋 sample_parsed_data.json - Sample parsed data")
    print("  ⚛️ ReactBasics.js - React basics component")
    print("  ⚛️ ReactWork.js - React work component")
    print("  ⚛️ ReactSkills.js - React skills component")
    print("  📚 resume_api_documentation.json - API docs")
    print()
    
    print("🎉 Sample UI Mapping Complete!")
    print("💡 This shows exactly how your parsed_data will map to UI components")
    print("📱 Open sample_resume_display.html in browser to see the result")
    print("🔧 Use React components in your frontend application")

if __name__ == "__main__":
    main()
