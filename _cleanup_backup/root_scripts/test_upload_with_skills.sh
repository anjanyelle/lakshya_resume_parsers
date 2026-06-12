#!/bin/bash

# Test the /upload/preview-sections endpoint with skill extraction
# This should call the external skill API at http://localhost:8000/extract-skills

echo "Testing upload with skill extraction..."
echo "======================================="

# Create a test resume file
cat > /tmp/test_resume.txt << 'EOF'
ANJAN YELLE
Full Stack Developer | React.js Developer

PROFESSIONAL SUMMARY
Experienced Full Stack Developer with 4 years of experience in designing, developing, and maintaining scalable web applications. Strong expertise in React.js, JavaScript, TypeScript, Redux, Next.js, HTML5, CSS3, Tailwind CSS, Bootstrap, Node.js, Express.js, Java, Spring Boot, REST APIs, MySQL, MongoDB, AWS, Docker, Kubernetes, Git, GitHub, Jenkins, CI/CD, Agile, Scrum, and Software Development Life Cycle (SDLC).

TECHNICAL SKILLS
Frontend: React.js, Next.js, JavaScript, TypeScript, Redux, HTML5, CSS3, Tailwind CSS, Bootstrap, Material UI
Backend: Node.js, Express.js, Java, Spring Boot
Databases: MySQL, PostgreSQL, MongoDB
Cloud & DevOps: AWS, Docker, Kubernetes, Jenkins, GitHub Actions, CI/CD
Testing: Jest, Cypress, Selenium, Postman
Version Control: Git, GitHub, GitLab
Methodologies: Agile, Scrum, SDLC

WORK EXPERIENCE
Senior React Developer
- Developed enterprise-level web applications using React.js, Redux, TypeScript, and Next.js
- Implemented responsive user interfaces using HTML5, CSS3, Bootstrap, Tailwind CSS, and Material UI
- Integrated REST APIs and GraphQL APIs with frontend applications
- Worked with Node.js and Express.js backend services
- Created reusable React Hooks and custom hooks
- Implemented authentication using JWT and OAuth
- Optimized application performance using React.memo, useMemo, and useCallback
- Configured CI/CD pipelines using Jenkins and GitHub Actions
- Deployed applications on AWS using Docker and Kubernetes
- Collaborated with Agile Scrum teams using Jira

PROJECTS
CRM Application
Technologies: React.js, Redux, TypeScript, Node.js, Express.js, MongoDB, AWS
- Built customer management modules
- Implemented role-based access control (RBAC)
- Created dashboards and analytics reports

EDUCATION
Bachelor of Technology in Computer Science Engineering

SOFT SKILLS
Communication, Leadership, Problem Solving, Team Collaboration, Time Management, Analytical Thinking
EOF

echo ""
echo "Uploading resume to http://localhost:3001/api/upload/preview-sections"
echo ""

# Upload the resume
curl -X POST http://localhost:3001/api/upload/preview-sections \
  -F "file=@/tmp/test_resume.txt" \
  -F "force_ocr=false" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  | jq '.extracted_skills_from_text'

echo ""
echo "======================================="
echo "Test completed!"
