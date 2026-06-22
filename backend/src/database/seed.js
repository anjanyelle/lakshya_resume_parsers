/**
 * RESUME PARSER - DATABASE SEED SCRIPT
 * 
 * This script seeds realistic test data for the current database schema.
 * It maintains foreign key relationships and uses realistic data.
 * 
 * Note: This script is adapted for the current production database schema (10 tables).
 * The full schema.sql file contains 22 tables but has not been applied yet.
 * 
 * Usage:
 *   node src/database/seed.js
 * 
 * Or via npm (after adding to package.json scripts):
 *   npm run db:seed
 */

const { Pool } = require('pg');
const bcrypt = require('bcryptjs');
const { v4: uuidv4 } = require('uuid');

// Database connection
const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME || 'resume_parser',
  user: process.env.DB_USER || 'resume_user',
  password: process.env.DB_PASSWORD || 'Anjan$123',
});

// Helper: Generate random date within range
function randomDate(start, end) {
  return new Date(start.getTime() + Math.random() * (end.getTime() - start.getTime()));
}

// Helper: Generate random item from array
function randomItem(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

// Helper: Generate random subset of array
function randomSubset(arr, min = 1, max = arr.length) {
  const count = Math.floor(Math.random() * (max - min + 1)) + min;
  const shuffled = [...arr].sort(() => 0.5 - Math.random());
  return shuffled.slice(0, count);
}

// Realistic data arrays
const FIRST_NAMES = ['James', 'Sarah', 'Michael', 'Emily', 'David', 'Jennifer', 'Robert', 'Amanda', 'William', 'Jessica', 'Christopher', 'Ashley', 'Daniel', 'Stephanie', 'Matthew', 'Nicole', 'Andrew', 'Melissa', 'Joshua', 'Elizabeth'];
const LAST_NAMES = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin'];
const COMPANIES = ['Google', 'Microsoft', 'Amazon', 'Meta', 'Apple', 'Netflix', 'Salesforce', 'Adobe', 'IBM', 'Oracle', 'Intel', 'Cisco', 'VMware', 'SAP', 'Workday', 'ServiceNow', 'Snowflake', 'Databricks', 'Stripe', 'Square'];
const JOB_TITLES = ['Senior Software Engineer', 'Full Stack Developer', 'Backend Engineer', 'Frontend Developer', 'DevOps Engineer', 'Data Engineer', 'Machine Learning Engineer', 'Product Manager', 'Technical Lead', 'Engineering Manager', 'Software Architect', 'Cloud Architect', 'Security Engineer', 'QA Engineer', 'Site Reliability Engineer'];
const SKILLS = ['JavaScript', 'TypeScript', 'Python', 'Java', 'Go', 'Rust', 'React', 'Node.js', 'Angular', 'Vue.js', 'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'PostgreSQL', 'MongoDB', 'Redis', 'GraphQL', 'REST APIs', 'Git', 'CI/CD', 'Linux', 'Terraform', 'Ansible'];
const INSTITUTIONS = ['MIT', 'Stanford', 'Harvard', 'UC Berkeley', 'Carnegie Mellon', 'Georgia Tech', 'University of Michigan', 'University of Washington', 'Cornell', 'Princeton', 'Yale', 'Columbia', 'Duke', 'Northwestern', 'University of Texas', 'University of Illinois', 'Purdue', 'University of Wisconsin', 'University of Maryland', 'University of California'];
const DEGREES = ['Bachelor of Science in Computer Science', 'Master of Science in Computer Science', 'Bachelor of Science in Software Engineering', 'Master of Science in Data Science', 'Bachelor of Science in Information Technology', 'PhD in Computer Science', 'Master of Business Administration', 'Bachelor of Arts in Computer Science'];
const LOCATIONS = ['San Francisco, CA', 'New York, NY', 'Seattle, WA', 'Austin, TX', 'Boston, MA', 'Los Angeles, CA', 'Chicago, IL', 'Denver, CO', 'Portland, OR', 'Atlanta, GA', 'Miami, FL', 'Phoenix, AZ', 'Dallas, TX', 'Houston, TX', 'San Diego, CA'];
const CERTIFICATIONS = ['AWS Solutions Architect', 'Google Cloud Professional', 'Azure Administrator', 'Kubernetes Administrator', 'Docker Certified', 'Scrum Master', 'PMP', 'CISSP', 'CEH', 'CompTIA Security+', 'CCNA', 'VMware Certified', 'Red Hat Certified', 'Oracle Certified', 'Salesforce Certified'];

// Seed data storage
const seedData = {
  users: [],
  candidates: [],
  skills: [],
  jobDescriptions: [],
  parsingJobs: [],
  workHistory: [],
  education: [],
  certifications: [],
  candidateSkills: [],
  matchScores: [],
  labeledData: []
};

async function seed() {
  console.log('🌱 Starting database seed...');
  
  const client = await pool.connect();
  
  try {
    await client.query('BEGIN');
    
    // 1. USERS
    console.log('📝 Seeding users...');
    const hashedPassword = await bcrypt.hash('password123', 10);
    
    const users = [
      { email: 'admin@resume-parser.com', role: 'admin', full_name: 'Admin User' },
      { email: 'recruiter1@company.com', role: 'recruiter', full_name: 'Sarah Johnson' },
      { email: 'recruiter2@company.com', role: 'recruiter', full_name: 'Michael Smith' },
      { email: 'viewer@company.com', role: 'viewer', full_name: 'Emily Davis' },
      { email: 'recruiter3@company.com', role: 'recruiter', full_name: 'Robert Wilson' }
    ];
    
    for (const user of users) {
      const result = await client.query(
        `INSERT INTO users (email, hashed_password, role) 
         VALUES ($1, $2, $3) 
         ON CONFLICT (email) DO NOTHING 
         RETURNING id`,
        [user.email, hashedPassword, user.role]
      );
      if (result.rows.length > 0) {
        seedData.users.push({ ...user, id: result.rows[0].id });
      }
    }
    console.log(`✅ Seeded ${seedData.users.length} users`);
    
    // 2. SYSTEM SETTINGS
    console.log('📝 Seeding system settings...');
    const settings = [
      { key: 'max_file_size_mb', value: { value: 10 } },
      { key: 'allowed_file_types', value: { types: ['pdf', 'docx', 'txt'] } },
      { key: 'ai_confidence_threshold', value: { threshold: 0.75 } },
      { key: 'default_review_status', value: { status: 'pending' } },
      { key: 'enable_duplicate_detection', value: { enabled: true } }
    ];
    
    for (const setting of settings) {
      await client.query(
        `INSERT INTO system_settings (key, value) 
         VALUES ($1, $2) 
         ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value`,
        [setting.key, setting.value]
      );
    }
    console.log('✅ Seeded system settings');
    
    // 4. CANDIDATES
    console.log('📝 Seeding candidates...');
    const candidateCount = 25;
    const now = new Date();
    const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
    
    for (let i = 0; i < candidateCount; i++) {
      const firstName = randomItem(FIRST_NAMES);
      const lastName = randomItem(LAST_NAMES);
      const fullName = `${firstName} ${lastName}`;
      const email = `${firstName.toLowerCase()}.${lastName.toLowerCase()}@example.com`;
      const location = randomItem(LOCATIONS);
      const createdDate = randomDate(thirtyDaysAgo, now);
      
      const status = randomItem(['completed', 'completed', 'completed', 'pending', 'processing', 'failed', 'deleted']);
      const reviewStatus = randomItem(['pending', 'in_review', 'approved', 'rejected']);
      
      const result = await client.query(
        `INSERT INTO candidates (
          full_name, email, phone, location, linkedin_url, github_url,
          summary, raw_resume_text, file_path, file_type, status, review_status,
          created_at, updated_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
        RETURNING id`,
        [
          fullName,
          email,
          `+1-${Math.floor(Math.random() * 900) + 100}-${Math.floor(Math.random() * 9000) + 1000}`,
          location,
          `https://linkedin.com/in/${firstName.toLowerCase()}.${lastName.toLowerCase()}`,
          `https://github.com/${firstName.toLowerCase()}${lastName.toLowerCase()}`,
          `Results-driven ${randomItem(JOB_TITLES)} with ${Math.floor(Math.random() * 10) + 3} years of experience in building scalable applications. Proficient in ${randomSubset(SKILLS, 3, 5).join(', ')}. Strong problem-solving skills and experience with agile methodologies.`,
          `Raw resume text for ${fullName}...`,
          `/uploads/resumes/${uuidv4()}.pdf`,
          'pdf',
          status,
          reviewStatus,
          createdDate,
          createdDate
        ]
      );
      
      seedData.candidates.push({
        id: result.rows[0].id,
        fullName,
        email,
        status,
        reviewStatus,
        createdDate
      });
    }
    console.log(`✅ Seeded ${seedData.candidates.length} candidates`);
    
    // 5. WORK EXPERIENCE
    console.log('📝 Seeding work experience...');
    for (const candidate of seedData.candidates) {
      const workCount = Math.floor(Math.random() * 4) + 1;
      
      for (let j = 0; j < workCount; j++) {
        const startDate = randomDate(
          new Date(candidate.createdDate.getTime() - 5 * 365 * 24 * 60 * 60 * 1000),
          candidate.createdDate
        );
        const endDate = Math.random() > 0.3 ? randomDate(startDate, candidate.createdDate) : null;
        
        await client.query(
          `INSERT INTO work_experience (
            candidate_id, job_title, company_name, start_date, end_date,
            location, description
          ) VALUES ($1, $2, $3, $4, $5, $6, $7)`,
          [
            candidate.id,
            randomItem(JOB_TITLES),
            randomItem(COMPANIES),
            startDate,
            endDate,
            randomItem(LOCATIONS),
            `Developed and maintained ${randomItem(['microservices', 'web applications', 'mobile apps', 'APIs', 'data pipelines'])} using ${randomSubset(SKILLS, 2, 4).join(', ')}. Improved system performance by ${Math.floor(Math.random() * 40) + 10}%.`
          ]
        );
      }
    }
    console.log('✅ Seeded work experience');
    
    // 6. EDUCATION
    console.log('📝 Seeding education...');
    for (const candidate of seedData.candidates) {
      const eduCount = Math.floor(Math.random() * 2) + 1;
      
      for (let j = 0; j < eduCount; j++) {
        const startDate = randomDate(
          new Date(candidate.createdDate.getTime() - 8 * 365 * 24 * 60 * 60 * 1000),
          new Date(candidate.createdDate.getTime() - 2 * 365 * 24 * 60 * 60 * 1000)
        );
        const endDate = new Date(startDate.getTime() + (Math.floor(Math.random() * 4) + 2) * 365 * 24 * 60 * 60 * 1000);
        
        await client.query(
          `INSERT INTO education (
            candidate_id, institution, degree, field_of_study,
            start_date, end_date, gpa
          ) VALUES ($1, $2, $3, $4, $5, $6, $7)`,
          [
            candidate.id,
            randomItem(INSTITUTIONS),
            randomItem(DEGREES),
            'Computer Science',
            startDate,
            endDate,
            parseFloat((Math.random() * 1.0 + 3.0).toFixed(2))
          ]
        );
      }
    }
    console.log('✅ Seeded education');
    
    // 7. SKILLS (linked to candidates)
    console.log('📝 Seeding skills...');
    for (const candidate of seedData.candidates) {
      const skillCount = Math.floor(Math.random() * 8) + 5;
      const candidateSkills = randomSubset(SKILLS, skillCount, skillCount);
      
      for (const skill of candidateSkills) {
        const category = ['JavaScript', 'TypeScript', 'Python', 'Java', 'Go', 'Rust', 'React', 'Node.js', 'Angular', 'Vue.js', 'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'PostgreSQL', 'MongoDB', 'Redis', 'GraphQL', 'REST APIs', 'Git', 'CI/CD', 'Linux', 'Terraform', 'Ansible'].includes(skill) ? 'technical' : 'soft';
        
        await client.query(
          `INSERT INTO skills (candidate_id, skill_name, category, proficiency_level, years_experience, confidence_score) 
           VALUES ($1, $2, $3, $4, $5, $6)`,
          [
            candidate.id,
            skill,
            category,
            randomItem(['beginner', 'intermediate', 'advanced', 'expert']),
            parseFloat((Math.random() * 8 + 1).toFixed(1)),
            parseFloat((Math.random() * 0.3 + 0.7).toFixed(4))
          ]
        );
      }
    }
    console.log('✅ Seeded skills');
    
    // 8. PARSING JOBS
    console.log('📝 Seeding parsing jobs...');
    for (const candidate of seedData.candidates) {
      const jobCount = Math.floor(Math.random() * 3) + 1;
      
      for (let j = 0; j < jobCount; j++) {
        const status = randomItem(['pending', 'processing', 'completed', 'failed']);
        const startedAt = randomDate(candidate.createdDate, new Date());
        const completedAt = status === 'completed' || status === 'failed' 
          ? new Date(startedAt.getTime() + Math.random() * 60000) 
          : null;
        
        const result = await client.query(
          `INSERT INTO parsing_jobs (
            candidate_id, filename, status,
            confidence_score, error_message, started_at, completed_at,
            created_at, updated_at
          ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
          RETURNING id`,
          [
            candidate.id,
            `${candidate.fullName.replace(/\s/g, '_')}_Resume.pdf`,
            status,
            status === 'completed' ? parseFloat((Math.random() * 0.3 + 0.7).toFixed(4)) : null,
            status === 'failed' ? 'OCR processing failed: Unable to extract text from document' : null,
            startedAt,
            completedAt,
            candidate.createdDate,
            startedAt
          ]
        );
        
        seedData.parsingJobs.push({
          id: result.rows[0].id,
          candidateId: candidate.id,
          status
        });
      }
    }
    console.log(`✅ Seeded ${seedData.parsingJobs.length} parsing jobs`);
    
    // 9. JOB DESCRIPTIONS
    console.log('📝 Seeding job descriptions...');
    const jobDescriptions = [
      { title: 'Senior Software Engineer', department: 'Engineering', min_exp: 5, max_exp: 10, seniority: 'Senior' },
      { title: 'Full Stack Developer', department: 'Engineering', min_exp: 3, max_exp: 7, seniority: 'Mid-Level' },
      { title: 'Backend Engineer', department: 'Engineering', min_exp: 3, max_exp: 8, seniority: 'Mid-Level' },
      { title: 'Frontend Developer', department: 'Engineering', min_exp: 2, max_exp: 6, seniority: 'Mid-Level' },
      { title: 'DevOps Engineer', department: 'Infrastructure', min_exp: 4, max_exp: 9, seniority: 'Senior' },
      { title: 'Data Engineer', department: 'Data', min_exp: 3, max_exp: 8, seniority: 'Mid-Level' },
      { title: 'Machine Learning Engineer', department: 'AI/ML', min_exp: 4, max_exp: 10, seniority: 'Senior' },
      { title: 'Product Manager', department: 'Product', min_exp: 5, max_exp: 12, seniority: 'Senior' },
      { title: 'Engineering Manager', department: 'Engineering', min_exp: 8, max_exp: 15, seniority: 'Leadership' },
      { title: 'Software Architect', department: 'Engineering', min_exp: 10, max_exp: 20, seniority: 'Principal' }
    ];
    
    for (const job of jobDescriptions) {
      const requiredSkills = randomSubset(SKILLS, 4, 6);
      const preferredSkills = randomSubset(SKILLS.filter(s => !requiredSkills.includes(s)), 2, 4);
      
      const result = await client.query(
        `INSERT INTO job_descriptions (
          title, department, description, required_skills, preferred_skills,
          min_experience_years, max_experience_years, seniority_level,
          location, employment_type, status, created_at, updated_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
        RETURNING id`,
        [
          job.title,
          job.department,
          `We are looking for a ${job.title} to join our team. The ideal candidate will have strong experience in ${requiredSkills.slice(0, 3).join(', ')}. You will be responsible for designing, developing, and maintaining scalable software solutions.`,
          JSON.stringify(requiredSkills),
          JSON.stringify(preferredSkills),
          job.min_exp,
          job.max_exp,
          job.seniority,
          randomItem(LOCATIONS),
          randomItem(['Full-time', 'Contract', 'Full-time']),
          'active',
          randomDate(thirtyDaysAgo, now),
          now
        ]
      );
      
      seedData.jobDescriptions.push({
        id: result.rows[0].id,
        ...job,
        requiredSkills,
        preferredSkills
      });
    }
    console.log(`✅ Seeded ${seedData.jobDescriptions.length} job descriptions`);
    
    // 10. MATCH SCORES
    console.log('📝 Seeding match scores...');
    for (const candidate of seedData.candidates) {
      if (candidate.status === 'completed' && Math.random() > 0.3) {
        const jobCount = Math.floor(Math.random() * 3) + 1;
        const jobs = randomSubset(seedData.jobDescriptions, jobCount, jobCount);
        
        for (const job of jobs) {
          const overallScore = parseFloat((Math.random() * 40 + 50).toFixed(2));
          const skillScore = parseFloat((Math.random() * 30 + 50).toFixed(2));
          const experienceScore = parseFloat((Math.random() * 30 + 50).toFixed(2));
          const educationScore = parseFloat((Math.random() * 20 + 70).toFixed(2));
          
          const matchingSkills = randomSubset(SKILLS, 3, 6);
          const missingSkills = randomSubset(SKILLS.filter(s => !matchingSkills.includes(s)), 0, 3);
          const extraSkills = randomSubset(SKILLS.filter(s => !matchingSkills.includes(s) && !missingSkills.includes(s)), 0, 3);
          
          await client.query(
            `INSERT INTO match_scores (
              candidate_id, job_id, overall_score, skill_score, experience_score,
              education_score, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)`,
            [
              candidate.id,
              job.id,
              overallScore,
              skillScore,
              experienceScore,
              educationScore,
              randomDate(candidate.createdDate, now)
            ]
          );
          
          seedData.matchScores.push({
            candidateId: candidate.id,
            jobId: job.id,
            score: overallScore
          });
        }
      }
    }
    console.log(`✅ Seeded ${seedData.matchScores.length} match scores`);
    
    // 11. LABELED DATA (for AI training)
    console.log('📝 Seeding labeled data...');
    for (const candidate of seedData.candidates) {
      if (candidate.status === 'completed' && Math.random() > 0.7) {
        const correctedFields = {};
        const fieldsToCorrect = ['email', 'phone', 'location'];
        const numCorrections = Math.floor(Math.random() * 3);
        
        for (let i = 0; i < numCorrections; i++) {
          const field = randomItem(fieldsToCorrect);
          correctedFields[field] = {
            original: 'Auto-detected value',
            corrected: 'Human verified value',
            confidence: 0.95
          };
        }
        
        await client.query(
          `INSERT INTO labeled_data (
            candidate_id, corrected_fields, action, created_at
          ) VALUES ($1, $2, $3, $4)`,
          [
            candidate.id,
            JSON.stringify(correctedFields),
            randomItem(['corrected', 'skipped', 'approved']),
            randomDate(candidate.createdDate, now)
          ]
        );
      }
    }
    console.log('✅ Seeded labeled data');
    
    await client.query('COMMIT');
    console.log('\n✅ Database seeded successfully!\n');
    
    // Print summary
    console.log('📊 SEED SUMMARY:');
    console.log('================');
    console.log(`Users: ${seedData.users.length}`);
    console.log(`Candidates: ${seedData.candidates.length}`);
    console.log(`Skills: ${seedData.skills.length}`);
    console.log(`Job Descriptions: ${seedData.jobDescriptions.length}`);
    console.log(`Parsing Jobs: ${seedData.parsingJobs.length}`);
    console.log(`Match Scores: ${seedData.matchScores.length}`);
    console.log('================');
    console.log('\n🎉 All tables seeded with realistic test data!');
    
  } catch (error) {
    await client.query('ROLLBACK');
    console.error('❌ Error seeding database:', error);
    throw error;
  } finally {
    client.release();
  }
}

// Run seed
seed()
  .then(() => {
    console.log('✅ Seed completed successfully');
    process.exit(0);
  })
  .catch((error) => {
    console.error('❌ Seed failed:', error);
    process.exit(1);
  });
