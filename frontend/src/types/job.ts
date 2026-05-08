export interface JobSkill {
  id?: string;
  skill_name: string;
  skill_type: "required" | "preferred";
}

export interface Job {
  id: string;
  title: string;
  description: string;
  min_experience_years?: number;
  max_experience_years?: number;
  education_requirement?: string;
  employment_type?: string;
  seniority_level?: string;
  location?: string;
  salary_range?: string;
  department?: string;
  status: "active" | "inactive" | "closed";
  created_at: string;
  updated_at: string;
  required_skills?: JobSkill[];
  preferred_skills?: JobSkill[];
}

export interface MatchResult {
  id: string;
  job_id: string;
  job_title?: string;
  candidate_id: string;
  candidate_name: string;
  candidate_email: string;
  candidate_location: string;
  overall_score: number;
  skill_score: number;
  experience_score: number;
  education_score: number;
  matching_skills: string[];
  missing_skills: string[];
  extra_skills: string[];
  experience_gap_years: number;
  recommendation:
    | "Strong Match"
    | "Good Match"
    | "Partial Match"
    | "Not Recommended";
  reason: string;
  created_at: string;
}
