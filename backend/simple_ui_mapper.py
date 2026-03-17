#!/usr/bin/env python3

"""
Simple Parsed Data to UI Mapper
Extract parsed_data from parsing_jobs table and create UI mapping
"""

import json
import sqlite3
from typing import Dict, Any

def get_latest_parsed_data():
    """Get the latest parsed_data from parsing_jobs table"""
    try:
        conn = sqlite3.connect('resume_parser.db')
        cursor = conn.cursor()
        
        # Get the latest parsed_data - try different column names
        try:
            cursor.execute("""
                SELECT id, parsed_data, created_at, status
                FROM parsing_jobs 
                ORDER BY created_at DESC 
                LIMIT 1
            """)
        except:
            cursor.execute("""
                SELECT id, parsed_data, status
                FROM parsing_jobs 
                ORDER BY id DESC 
                LIMIT 1
            """)
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            if len(result) == 4:
                return {
                    'id': result[0],
                    'parsed_data': result[1],
                    'created_at': result[2],
                    'status': result[3]
                }
            else:
                return {
                    'id': result[0],
                    'parsed_data': result[1],
                    'created_at': 'Unknown',
                    'status': result[2]
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

def create_ui_mapping(parsed_json):
    """Create UI mapping from parsed JSON"""
    if not parsed_json:
        return None
    
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
        body { font-family: Arial, sans-serif; margin: 20px; }
        .section { margin-bottom: 30px; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
        .section h2 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
        .basics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }
        .field { margin-bottom: 10px; }
        .field label { font-weight: bold; display: block; margin-bottom: 5px; }
        .field span, .field p { color: #555; }
        .work-item, .education-item { margin-bottom: 20px; padding: 15px; background: #f8f9fa; border-radius: 5px; }
        .work-item h3, .education-item h3 { color: #007bff; margin: 0 0 5px 0; }
        .subtitle { color: #666; font-style: italic; margin: 5px 0; }
        .dates { color: #28a745; font-weight: bold; }
        .skills-grid, .certifications-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; }
        .skill-item, .certification-item { padding: 10px; background: #e9ecef; border-radius: 5px; }
        .current-badge { background: #28a745; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.8em; }
        .links a { margin-right: 15px; color: #007bff; text-decoration: none; }
        .links a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>Resume Data Display</h1>
"""
    
    # Basics section
    if ui_mapping['basics']:
        html += """
    <div class="section">
        <h2>Basic Information</h2>
        <div class="basics-grid">
            <div class="field">
                <label>Name:</label>
                <span>{name}</span>
            </div>
            <div class="field">
                <label>Email:</label>
                <span>{email}</span>
            </div>
            <div class="field">
                <label>Phone:</label>
                <span>{phone}</span>
            </div>
            <div class="field">
                <label>Location:</label>
                <span>{location}</span>
            </div>
        </div>
        {summary}
        {links}
    </div>
""".format(
            name=ui_mapping['basics']['name'],
            email=ui_mapping['basics']['email'],
            phone=ui_mapping['basics']['phone'],
            location=ui_mapping['basics']['location'],
            summary=f'<div class="field"><label>Summary:</label><p>{ui_mapping["basics"]["summary"]}</p></div>' if ui_mapping['basics']['summary'] else '',
            links='<div class="field"><label>Links:</label><div class="links">{links}</div></div>'.format(
                links=' '.join([f'<a href="{ui_mapping["basics"]["linkedin"]}" target="_blank">LinkedIn</a>' if ui_mapping['basics']['linkedin'] else '',
                              f'<a href="{ui_mapping["basics"]["github"]}" target="_blank">GitHub</a>' if ui_mapping['basics']['github'] else '',
                              f'<a href="{ui_mapping["basics"]["website"]}" target="_blank">Website</a>' if ui_mapping['basics']['website'] else ''])
            ) if ui_mapping['basics']['linkedin'] or ui_mapping['basics']['github'] or ui_mapping['basics']['website'] else ''
        )
    
    # Work experience section
    if ui_mapping['work']:
        html += '<div class="section"><h2>Work Experience</h2>'
        for work in ui_mapping['work']:
            html += f"""
        <div class="work-item">
            <h3>{work['title']}</h3>
            <p class="subtitle">{work['company']} {work['location'] and f'• {work["location"]}'}</p>
            <p class="dates">{work['startDate']} - {work['endDate'] or ('Present' if work['current'] else 'N/A')} {'<span class="current-badge">Current</span>' if work['current'] else ''}</p>
            {f'<p>{work["description"]}</p>' if work['description'] else ''}
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
            {f'<p>GPA: {edu["gpa"]}</p>' if edu['gpa'] else ''}
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
            {f'<p>Level: {skill["level"]}</p>' if skill['level'] else ''}
            {f'<p>Category: {skill["category"]}</p>' if skill['category'] else ''}
            {f'<p>Years: {skill["years_experience"]}</p>' if skill['years_experience'] else ''}
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
            {f'<p>Issuer: {cert["issuer"]}</p>' if cert['issuer'] else ''}
            {f'<p>Date: {cert["date"]}</p>' if cert['date'] else ''}
            {f'<p>ID: {cert["credential_id"]}</p>' if cert['credential_id'] else ''}
        </div>
"""
        html += '</div></div>'
    
    html += """
</body>
</html>
"""
    
    return html

def main():
    """Main function to process parsed_data and create UI mapping"""
    print("🔍 Simple Parsed Data to UI Mapper")
    print("=" * 50)
    
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
    
    # Create UI mapping
    ui_mapping = create_ui_mapping(parsed_json)
    
    print("📊 UI Data Summary:")
    print(f"  👤 Basics: {'✅' if ui_mapping['basics'] else '❌'}")
    print(f"  💼 Work: {len(ui_mapping['work'])} positions")
    print(f"  🎓 Education: {len(ui_mapping['education'])} entries")
    print(f"  🔧 Skills: {len(ui_mapping['skills'])} skills")
    print(f"  🏆 Certifications: {len(ui_mapping['certifications'])} certifications")
    print()
    
    # Generate HTML template
    html_template = generate_html_template(ui_mapping)
    
    # Save HTML template
    with open('resume_display.html', 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    # Save UI mapping as JSON
    with open('resume_ui_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(ui_mapping, f, indent=2)
    
    # Create JavaScript for dynamic UI
    js_code = f"""
// Resume UI Data - Generated from parsed_data
const resumeData = {json.dumps(ui_mapping, indent=2)};

// Function to render resume data
function renderResume(data) {{
    // Basics
    if (data.basics.name) {{
        document.getElementById('name').textContent = data.basics.name;
        document.getElementById('email').textContent = data.basics.email;
        document.getElementById('phone').textContent = data.basics.phone;
        document.getElementById('location').textContent = data.basics.location;
    }}
    
    // Work Experience
    const workContainer = document.getElementById('work-experience');
    workContainer.innerHTML = '';
    data.work.forEach(work => {{
        const workDiv = document.createElement('div');
        workDiv.className = 'work-item';
        workDiv.innerHTML = `
            <h3>${{work.title}}</h3>
            <p class="subtitle">${{work.company}} ${{work.location ? '• ' + work.location : ''}}</p>
            <p class="dates">${{work.startDate}} - ${{work.endDate || (work.current ? 'Present' : 'N/A')}} ${{work.current ? '<span class="current-badge">Current</span>' : ''}}</p>
            ${{work.description ? `<p>${{work.description}}</p>` : ''}}
        `;
        workContainer.appendChild(workDiv);
    }});
    
    // Education
    const eduContainer = document.getElementById('education');
    eduContainer.innerHTML = '';
    data.education.forEach(edu => {{
        const eduDiv = document.createElement('div');
        eduDiv.className = 'education-item';
        eduDiv.innerHTML = `
            <h3>${{edu.degree}}</h3>
            <p class="subtitle">${{edu.institution}} ${{edu.location ? '• ' + edu.location : ''}}</p>
            <p class="dates">${{edu.startDate}} - ${{edu.endDate || (edu.current ? 'Present' : 'N/A')}} ${{edu.current ? '<span class="current-badge">Current</span>' : ''}}</p>
            ${{edu.gpa ? `<p>GPA: ${{edu.gpa}}</p>` : ''}}
        `;
        eduContainer.appendChild(eduDiv);
    }});
    
    // Skills
    const skillsContainer = document.getElementById('skills');
    skillsContainer.innerHTML = '';
    data.skills.forEach(skill => {{
        const skillDiv = document.createElement('div');
        skillDiv.className = 'skill-item';
        skillDiv.innerHTML = `
            <h4>${{skill.name}}</h4>
            ${{skill.level ? `<p>Level: ${{skill.level}}</p>` : ''}}
            ${{skill.category ? `<p>Category: ${{skill.category}}</p>` : ''}}
            ${{skill.years_experience ? `<p>Years: ${{skill.years_experience}}</p>` : ''}}
        `;
        skillsContainer.appendChild(skillDiv);
    }});
    
    // Certifications
    const certsContainer = document.getElementById('certifications');
    certsContainer.innerHTML = '';
    data.certifications.forEach(cert => {{
        const certDiv = document.createElement('div');
        certDiv.className = 'certification-item';
        certDiv.innerHTML = `
            <h4>${{cert.name}}</h4>
            ${{cert.issuer ? `<p>Issuer: ${{cert.issuer}}</p>` : ''}}
            ${{cert.date ? `<p>Date: ${{cert.date}}</p>` : ''}}
            ${{cert.credential_id ? `<p>ID: ${{cert.credential_id}}</p>` : ''}}
        `;
        certsContainer.appendChild(certDiv);
    }});
}}

// Load resume data when page loads
document.addEventListener('DOMContentLoaded', function() {{
    renderResume(resumeData);
}});
"""
    
    with open('resume_ui_script.js', 'w', encoding='utf-8') as f:
        f.write(js_code)
    
    print("📁 Files Created:")
    print("  🎨 resume_display.html - HTML template")
    print("  📊 resume_ui_mapping.json - UI data mapping")
    print("  🚀 resume_ui_script.js - JavaScript for dynamic UI")
    print()
    
    print("🎉 UI Mapping Complete!")
    print("💡 Use these files to display resume data in your UI")
    print("📱 Open resume_display.html in browser to see the result")

if __name__ == "__main__":
    main()
