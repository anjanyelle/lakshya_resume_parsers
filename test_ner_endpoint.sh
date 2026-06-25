#!/bin/bash

# Test script for NER Post-Processor Endpoint
# This tests the new /test-ner-postprocessor endpoint with sample resume data

echo "========================================="
echo "Testing NER Post-Processor Endpoint"
echo "========================================="
echo ""

# Test data - same as your curl command
curl -X POST 'http://localhost:8000/test-ner-postprocessor' \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "model": "own-model",
    "experience_text": "Software Engineer\n\nTata Consultancy Services\nJuly 2023 – Present\n\nClient: Banking & Financial Services\n\nRoles & Responsibilities:\n\nDeveloped enterprise-level web applications using React.js, TypeScript, and Redux Toolkit.\nDesigned reusable UI components and integrated RESTful APIs.\nWorked closely with backend teams for API integration and data management.\nImplemented role-based authentication and authorization modules.\nOptimized application performance using lazy loading, code splitting, and memoization techniques.\nParticipated in Agile ceremonies including Sprint Planning, Daily Standups, Sprint Reviews, and Retrospectives.\nCollaborated with QA teams to resolve production issues and improve application stability.\nUsed Git, Jira, and CI/CD pipelines for version control and deployment.\n\nEnvironment:\nReact.js, TypeScript, JavaScript, Redux Toolkit, Material UI, HTML5, CSS3, REST APIs, Git, Jira.\n\nAssociate Software Engineer\n\nInfosys\nMay 2022 – June 2023\n\nClient: Retail & E-Commerce\n\nRoles & Responsibilities:\n\nDeveloped responsive user interfaces using React.js and JavaScript.\nIntegrated third-party APIs and payment gateway services.\nCreated reusable components and custom hooks to improve code maintainability.\nWorked on bug fixing, feature enhancements, and application optimization.\nCollaborated with business analysts and stakeholders to gather requirements.\nParticipated in code reviews and maintained coding standards.\nAssisted in deployment and production support activities.\n\nEnvironment:\nReact.js, JavaScript, HTML5, CSS3, Bootstrap, Redux, REST APIs, GitHub.",
    "education_text": "Education\nBachelor of Technology (B.Tech)\n\nComputer Science and Engineering\n\nJawaharlal Nehru Technological University Hyderabad\n\n2018 – 2022\n\nRelevant Subjects:\n\nData Structures & Algorithms\nDatabase Management Systems\nOperating Systems\nComputer Networks\nSoftware Engineering\nObject-Oriented Programming\nWeb Technologies\n\nAcademic Project:\nOnline Employee Management System using React.js, Node.js, Express.js, and MySQL."
  }' | jq '.'

echo ""
echo "========================================="
echo "Test Complete"
echo "========================================="
