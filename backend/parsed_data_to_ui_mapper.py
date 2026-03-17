#!/usr/bin/env python3

"""
Parsed Data to UI Mapper
Extract parsed_data from parsing_jobs table and map to UI components
"""

import json
import sqlite3
from typing import Dict, Any, List
from datetime import datetime

def get_latest_parsed_data():
    """Get the latest parsed_data from parsing_jobs table"""
    try:
        conn = sqlite3.connect('resume_parser.db')
        cursor = conn.cursor()
        
        # Get the latest parsed_data
        cursor.execute("""
            SELECT id, parsed_data, created_at, status
            FROM parsing_jobs 
            ORDER BY created_at DESC 
            LIMIT 1
        """)
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'parsed_data': result[1],
                'created_at': result[2],
                'status': result[3]
            }
        else:
            return None
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return None

def parse_json_data(parsed_data_str):
    """Parse the JSON data from parsed_data column"""
    try:
        if isinstance(parsed_data_str, str):
            return json.loads(parsed_data_str)
        elif isinstance(parsed_data_str, dict):
            return parsed_data_str
        else:
            return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return None

def map_to_ui_format(parsed_json):
    """Map parsed JSON to UI-friendly format"""
    if not parsed_json:
        return None
    
    ui_data = {
        'basics': {},
        'work': [],
        'education': [],
        'skills': [],
        'certifications': [],
        'projects': [],
        'languages': [],
        'volunteer': [],
        'references': [],
        'achievements': [],
        'publications': []
    }
    
    # Map basics section
    if 'basics' in parsed_json:
        basics = parsed_json['basics']
        ui_data['basics'] = {
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
            ui_data['work'].append({
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
            ui_data['education'].append({
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
            ui_data['skills'].append({
                'name': skill.get('name', ''),
                'level': skill.get('level', ''),
                'category': skill.get('category', ''),
                'years_experience': skill.get('years_experience', ''),
                'proficiency': skill.get('proficiency', '')
            })
    
    # Map certifications
    if 'certifications' in parsed_json and isinstance(parsed_json['certifications'], list):
        for cert in parsed_json['certifications']:
            ui_data['certifications'].append({
                'name': cert.get('name', ''),
                'issuer': cert.get('issuer', ''),
                'date': cert.get('date', ''),
                'credential_id': cert.get('credential_id', ''),
                'url': cert.get('url', '')
            })
    
    # Map other sections
    for section in ['projects', 'languages', 'volunteer', 'references', 'achievements', 'publications']:
        if section in parsed_json and isinstance(parsed_json[section], list):
            ui_data[section] = parsed_json[section]
    
    return ui_data

def generate_ui_components(ui_data):
    """Generate UI component code for each section"""
    components = {}
    
    # Basics component
    if ui_data['basics']:
        components['basics'] = {
            'title': 'Basic Information',
            'data': ui_data['basics'],
            'fields': [
                {'key': 'name', 'label': 'Name', 'type': 'text'},
                {'key': 'email', 'label': 'Email', 'type': 'email'},
                {'key': 'phone', 'label': 'Phone', 'type': 'tel'},
                {'key': 'location', 'label': 'Location', 'type': 'text'},
                {'key': 'summary', 'label': 'Summary', 'type': 'textarea'},
                {'key': 'linkedin', 'label': 'LinkedIn', 'type': 'url'},
                {'key': 'github', 'label': 'GitHub', 'type': 'url'},
                {'key': 'website', 'label': 'Website', 'type': 'url'}
            ]
        }
    
    # Work experience component
    if ui_data['work']:
        components['work'] = {
            'title': 'Work Experience',
            'data': ui_data['work'],
            'fields': [
                {'key': 'company', 'label': 'Company', 'type': 'text'},
                {'key': 'title', 'label': 'Title', 'type': 'text'},
                {'key': 'location', 'label': 'Location', 'type': 'text'},
                {'key': 'startDate', 'label': 'Start Date', 'type': 'date'},
                {'key': 'endDate', 'label': 'End Date', 'type': 'date'},
                {'key': 'description', 'label': 'Description', 'type': 'textarea'},
                {'key': 'current', 'label': 'Current', 'type': 'checkbox'}
            ]
        }
    
    # Education component
    if ui_data['education']:
        components['education'] = {
            'title': 'Education',
            'data': ui_data['education'],
            'fields': [
                {'key': 'institution', 'label': 'Institution', 'type': 'text'},
                {'key': 'degree', 'label': 'Degree', 'type': 'text'},
                {'key': 'field', 'label': 'Field', 'type': 'text'},
                {'key': 'location', 'label': 'Location', 'type': 'text'},
                {'key': 'startDate', 'label': 'Start Date', 'type': 'date'},
                {'key': 'endDate', 'label': 'End Date', 'type': 'date'},
                {'key': 'gpa', 'label': 'GPA', 'type': 'text'},
                {'key': 'current', 'label': 'Current', 'type': 'checkbox'}
            ]
        }
    
    # Skills component
    if ui_data['skills']:
        components['skills'] = {
            'title': 'Skills',
            'data': ui_data['skills'],
            'fields': [
                {'key': 'name', 'label': 'Skill Name', 'type': 'text'},
                {'key': 'level', 'label': 'Level', 'type': 'select'},
                {'key': 'category', 'label': 'Category', 'type': 'text'},
                {'key': 'years_experience', 'label': 'Years Experience', 'type': 'number'},
                {'key': 'proficiency', 'label': 'Proficiency', 'type': 'select'}
            ]
        }
    
    # Certifications component
    if ui_data['certifications']:
        components['certifications'] = {
            'title': 'Certifications',
            'data': ui_data['certifications'],
            'fields': [
                {'key': 'name', 'label': 'Certification Name', 'type': 'text'},
                {'key': 'issuer', 'label': 'Issuer', 'type': 'text'},
                {'key': 'date', 'label': 'Date', 'type': 'date'},
                {'key': 'credential_id', 'label': 'Credential ID', 'type': 'text'},
                {'key': 'url', 'label': 'URL', 'type': 'url'}
            ]
        }
    
    return components

def create_frontend_code(components):
    """Generate frontend code for React components"""
    frontend_code = {
        'react_components': {},
        'api_endpoints': {},
        'data_types': {}
    }
    
    # Generate React components
    for section, component in components.items():
        component_name = section.capitalize()
        
        # React component code
        react_code = f"""
import React from 'react';

const {component_name} = ({{ data }}) => {{
  return (
    <div className="{section}-section">
      <h2>{component['title']}</h2>
      {{"""
        
        if section == 'basics':
            react_code += """
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
        {(data.linkedin || data.github || data.website) && (
          <div className="field full-width">
            <label>Links:</label>
            <div className="links">
              {data.linkedin && <a href={data.linkedin} target="_blank">LinkedIn</a>}
              {data.github && <a href={data.github} target="_blank">GitHub</a>}
              {data.website && <a href={data.website} target="_blank">Website</a>}
            </div>
          </div>
        )}
      </div>
"""
        elif section in ['work', 'education']:
            react_code += f"""
      <div className="{section}-list">
        {data.map((item, index) => (
          <div key={index} className="{section}-item">
            <h3>{item.title || item.degree}</h3>
            <p className="subtitle">
              {section === 'work' ? item.company : item.institution}
              {item.location && ` • ${item.location}`}
            </p>
            <p className="dates">
              {item.startDate} - {item.endDate || (item.current ? 'Present' : 'N/A')}
              {item.current && <span className="current-badge">Current</span>}
            </p>
            {item.description && (
              <p className="description">{item.description}</p>
            )}
            {section === 'education' && item.gpa && (
              <p className="gpa">GPA: {item.gpa}</p>
            )}
          </div>
        ))}
      </div>
"""
        elif section in ['skills', 'certifications']:
            react_code += f"""
      <div className="{section}-grid">
        {data.map((item, index) => (
          <div key={index} className="{section}-item">
            <h4>{item.name || item.title}</h4>
            {section === 'skills' ? (
              <>
                {item.level && <p className="level">Level: {item.level}</p>}
                {item.category && <p className="category">Category: {item.category}</p>}
                {item.years_experience && <p className="years">Years: {item.years_experience}</p>}
              </>
            ) : (
              <>
                {item.issuer && <p className="issuer">Issuer: {item.issuer}</p>}
                {item.date && <p className="date">Date: {item.date}</p>}
                {item.credential_id && <p className="id">ID: {item.credential_id}</p>}
              </>
            )}
          </div>
        ))}
      </div>
"""
        
        react_code += """
      </div>
    </div>
  );
};

export default """ + component_name + ";"
        
        frontend_code['react_components'][section] = react_code
    
    # API endpoint
    frontend_code['api_endpoints'] = {
        'get_latest_resume': {
            'method': 'GET',
            'url': '/api/resume/latest',
            'description': 'Get the latest parsed resume data'
        },
        'get_resume_by_id': {
            'method': 'GET',
            'url': '/api/resume/:id',
            'description': 'Get resume data by ID'
        }
    }
    
    # TypeScript types
    frontend_code['data_types'] = """
// TypeScript interfaces for resume data

interface Basics {
  name: string;
  email: string;
  phone: string;
  location: string;
  summary?: string;
  linkedin?: string;
  github?: string;
  website?: string;
}

interface WorkExperience {
  company: string;
  title: string;
  location: string;
  startDate: string;
  endDate?: string;
  description?: string;
  current: boolean;
}

interface Education {
  institution: string;
  degree: string;
  field?: string;
  location: string;
  startDate: string;
  endDate?: string;
  gpa?: string;
  current: boolean;
}

interface Skill {
  name: string;
  level: string;
  category?: string;
  years_experience?: string;
  proficiency?: string;
}

interface Certification {
  name: string;
  issuer: string;
  date?: string;
  credential_id?: string;
  url?: string;
}

interface ResumeData {
  basics: Basics;
  work: WorkExperience[];
  education: Education[];
  skills: Skill[];
  certifications: Certification[];
  projects: any[];
  languages: any[];
  volunteer: any[];
  references: any[];
  achievements: any[];
  publications: any[];
}
"""
    
    return frontend_code

def main():
    """Main function to process parsed_data and generate UI mapping"""
    print("🔍 Parsing Data to UI Mapper")
    print("=" * 60)
    
    # Get latest parsed data
    job_data = get_latest_parsed_data()
    
    if not job_data:
        print("❌ No parsed data found in database")
        print("💡 Make sure you have uploaded and processed a resume first")
        return
    
    print(f"📋 Found parsing job #{job_data['id']}")
    print(f"📅 Created: {job_data['created_at']}")
    print(f"📊 Status: {job_data['status']}")
    print()
    
    # Parse JSON data
    parsed_json = parse_json_data(job_data['parsed_data'])
    
    if not parsed_json:
        print("❌ Failed to parse JSON data")
        return
    
    print("✅ JSON data parsed successfully")
    
    # Map to UI format
    ui_data = map_to_ui_format(parsed_json)
    
    print("📊 UI Data Summary:")
    print(f"  👤 Basics: {'✅' if ui_data['basics'] else '❌'}")
    print(f"  💼 Work: {len(ui_data['work'])} positions")
    print(f"  🎓 Education: {len(ui_data['education'])} entries")
    print(f"  🔧 Skills: {len(ui_data['skills'])} skills")
    print(f"  🏆 Certifications: {len(ui_data['certifications'])} certifications")
    print()
    
    # Generate UI components
    components = generate_ui_components(ui_data)
    
    print("🎨 UI Components Generated:")
    for section in components:
        print(f"  📋 {section}: {components[section]['title']}")
    print()
    
    # Create frontend code
    frontend_code = create_frontend_code(components)
    
    # Save frontend code
    with open('resume_ui_components.js', 'w', encoding='utf-8') as f:
        f.write("// Resume UI Components - Generated from parsed_data\n\n")
        for section, code in frontend_code['react_components'].items():
            f.write(f"// {section.upper()} COMPONENT\n")
            f.write(code)
            f.write("\n\n")
    
    with open('resume_types.ts', 'w', encoding='utf-8') as f:
        f.write(frontend_code['data_types'])
    
    # Save API documentation
    with open('resume_api_docs.json', 'w', encoding='utf-8') as f:
        json.dump(frontend_code['api_endpoints'], f, indent=2)
    
    # Save UI data for reference
    with open('current_resume_ui_data.json', 'w', encoding='utf-8') as f:
        json.dump(ui_data, f, indent=2)
    
    print("📁 Files Created:")
    print("  🎨 resume_ui_components.js - React components")
    print("  📝 resume_types.ts - TypeScript interfaces")
    print("  📚 resume_api_docs.json - API documentation")
    print("  📊 current_resume_ui_data.json - Current UI data")
    print()
    
    print("🎉 UI Mapping Complete!")
    print("💡 Use the generated components in your frontend application")

if __name__ == "__main__":
    main()
