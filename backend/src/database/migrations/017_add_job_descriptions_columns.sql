-- Add missing columns to job_descriptions table to match the job model
-- This migration adds all the columns expected by the TypeScript job model

-- Create job_skills table if it doesn't exist
CREATE TABLE IF NOT EXISTS job_skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES job_descriptions (id) ON DELETE CASCADE,
    skill_name VARCHAR(255) NOT NULL,
    skill_type VARCHAR(50) NOT NULL CHECK (skill_type IN ('required', 'preferred')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_job_skills_job_id ON job_skills (job_id);
CREATE INDEX IF NOT EXISTS idx_job_skills_skill_name ON job_skills (skill_name);
CREATE INDEX IF NOT EXISTS idx_job_skills_skill_type ON job_skills (skill_type);

-- Add location column
ALTER TABLE job_descriptions ADD COLUMN IF NOT EXISTS location VARCHAR(255);

-- Add employment_type column
ALTER TABLE job_descriptions ADD COLUMN IF NOT EXISTS employment_type VARCHAR(100);

-- Replace experience_years with min/max experience years
ALTER TABLE job_descriptions ADD COLUMN IF NOT EXISTS min_experience_years INTEGER;
ALTER TABLE job_descriptions ADD COLUMN IF NOT EXISTS max_experience_years INTEGER;

-- Add education_level column
ALTER TABLE job_descriptions ADD COLUMN IF NOT EXISTS education_level VARCHAR(255);

-- Add salary columns
ALTER TABLE job_descriptions ADD COLUMN IF NOT EXISTS salary_min DECIMAL(12,2);
ALTER TABLE job_descriptions ADD COLUMN IF NOT EXISTS salary_max DECIMAL(12,2);

-- Add custom ATS columns
ALTER TABLE job_descriptions ADD COLUMN IF NOT EXISTS education_requirement VARCHAR(255);
ALTER TABLE job_descriptions ADD COLUMN IF NOT EXISTS seniority_level VARCHAR(100);
ALTER TABLE job_descriptions ADD COLUMN IF NOT EXISTS salary_range VARCHAR(100);
ALTER TABLE job_descriptions ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'active';

-- Add preferred_skills column
ALTER TABLE job_descriptions ADD COLUMN IF NOT EXISTS preferred_skills JSONB DEFAULT '[]';

-- Add currency and salary_period columns
ALTER TABLE job_descriptions ADD COLUMN IF NOT EXISTS currency VARCHAR(10) DEFAULT 'USD';
ALTER TABLE job_descriptions ADD COLUMN IF NOT EXISTS salary_period VARCHAR(50) DEFAULT 'Yearly';

-- Add work_mode column
ALTER TABLE job_descriptions ADD COLUMN IF NOT EXISTS work_mode VARCHAR(100);

-- Add number_of_openings column
ALTER TABLE job_descriptions ADD COLUMN IF NOT EXISTS number_of_openings INTEGER DEFAULT 1;

-- Add notice_period column
ALTER TABLE job_descriptions ADD COLUMN IF NOT EXISTS notice_period VARCHAR(100);

-- Add updated_at column
ALTER TABLE job_descriptions ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Create index on location for filtering
CREATE INDEX IF NOT EXISTS idx_job_descriptions_location ON job_descriptions (location);

-- Create index on employment_type for filtering
CREATE INDEX IF NOT EXISTS idx_job_descriptions_employment_type ON job_descriptions (employment_type);

-- Create index on status for filtering
CREATE INDEX IF NOT EXISTS idx_job_descriptions_status ON job_descriptions (status);
