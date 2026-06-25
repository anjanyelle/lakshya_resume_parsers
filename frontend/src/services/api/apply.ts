import { apiClient, aiServiceClient } from "./client";
import type { ApplicationData } from "../../features/apply/types/application";

export interface PreviewSectionsResponse {
  filename: string;
  extraction_method: string;
  raw_text_length: number;
  raw_text: string;
  total_sections: number;
  sections: {
    [key: string]: {
      text: string;
      char_count: number;
    };
  };
  detected_sections: string[];
  missing_sections: string[];
  validation_metadata: {
    spacy_available: boolean;
    validation_ran: boolean;
    sections_corrected: string[];
    sections_split: string[];
    sections_resolved: string[];
    warnings: string[];
    summary: any;
  };
}

export interface ParseSectionsResponse {
  summary?: string;
  work_experience?: Array<{
    company_name?: string;
    client_name?: string;
    job_title?: string;
    start_date?: string;
    end_date?: string;
    is_current?: boolean;
    location?: string;
    description?: string;
  }>;
  education?: Array<{
    institution?: string;
    degree?: string;
    field_of_study?: string;
    start_date?: string;
    end_date?: string;
    gpa?: number;
    description?: string;
  }>;
  skills?: string[];
  certifications?: Array<{
    name?: string;
    issuing_organization?: string;
    issue_date?: string;
    expiry_date?: string;
    credential_id?: string;
  }>;
  projects?: Array<{
    name?: string;
    description?: string;
    technologies?: string;
    duration?: string;
    role?: string;
    client?: string;
    url?: string;
  }>;
  contact?: {
    name?: string;
    email?: string;
    phone?: string;
    linkedin?: string;
    portfolio?: string;
    portfolio_url?: string;
    website?: string;
  };
}

export interface SaveCandidatePayload {
  name: string;
  email: string;
  phone?: string;
  linkedin?: string;
  portfolio?: string;
  summary?: string;
  skills?: string[];
  work_experience?: Array<{
    company_name?: string;
    client_name?: string;
    job_title?: string;
    start_date?: string;
    end_date?: string;
    is_current?: boolean;
    location?: string;
    description?: string;
  }>;
  education?: Array<{
    institution?: string;
    degree?: string;
    field_of_study?: string;
    start_date?: string;
    end_date?: string;
    gpa?: number;
    description?: string;
  }>;
  certifications?: Array<{
    name?: string;
    issuing_organization?: string;
    issue_date?: string;
    expiry_date?: string;
    credential_id?: string;
  }>;
  projects?: Array<{
    name?: string;
    description?: string;
    technologies?: string;
    duration?: string;
    role?: string;
    client?: string;
    url?: string;
  }>;
  force_save?: boolean;
}

export const previewSections = async (
  file: File,
  forceOcr: boolean = false
): Promise<PreviewSectionsResponse> => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("force_ocr", forceOcr ? "true" : "false");

  const response = await aiServiceClient.post<PreviewSectionsResponse>(
    "/preview-sections",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return response.data;
};

export const parseSections = async (
  sections: PreviewSectionsResponse,
  model: string = "deberta"
): Promise<ParseSectionsResponse> => {
  const payload = {
    model,
    summary_text: sections.sections.summary?.text || "",
    experience_text: sections.sections.experience?.text || "",
    education_text: sections.sections.education?.text || "",
    skills_text: sections.sections.skills?.text || "",
    certifications_text: sections.sections.certifications?.text || "",
    projects_text: sections.sections.projects?.text || "",
    contact_text: sections.sections.contact?.text || "",
    raw_text: sections.raw_text || "",
  };

  const response = await aiServiceClient.post<ParseSectionsResponse>(
    "/parse-sections",
    payload
  );

  return response.data;
};

export const saveCandidate = async (
  payload: SaveCandidatePayload
): Promise<{ id: string; message: string }> => {
  const response = await apiClient.post<{ id: string; message: string }>(
    "/api/candidates",
    payload
  );

  return response.data;
};

export const transformApplicationToCandidate = (
  application: ApplicationData,
  parsedData?: ParseSectionsResponse
): SaveCandidatePayload => {
  const { personalInfo, experiences, education, skills, certifications, projects } = application;

  const fullName = [personalInfo.firstName, personalInfo.middleName, personalInfo.lastName]
    .filter(Boolean)
    .join(" ")
    .trim();

  return {
    name: fullName || parsedData?.contact?.name || "",
    email: personalInfo.email || application.account.email,
    phone: personalInfo.phone || personalInfo.mobile || parsedData?.contact?.phone,
    linkedin: personalInfo.linkedIn || parsedData?.contact?.linkedin,
    portfolio: personalInfo.portfolio || personalInfo.website || parsedData?.contact?.portfolio || parsedData?.contact?.website,
    summary: parsedData?.summary,
    skills: skills.length > 0 ? skills : parsedData?.skills,
    work_experience: experiences
      .filter((exp) => exp.company || exp.jobTitle)
      .map((exp) => ({
        company_name: exp.company,
        job_title: exp.jobTitle,
        start_date: exp.startMonth && exp.startYear ? `${exp.startYear}-${exp.startMonth}` : undefined,
        end_date: exp.currentlyWorking ? undefined : (exp.endMonth && exp.endYear ? `${exp.endYear}-${exp.endMonth}` : undefined),
        is_current: exp.currentlyWorking,
        location: exp.location || [exp.city, exp.state, exp.country].filter(Boolean).join(", "),
        description: exp.roleDescription,
      })),
    education: education
      .filter((edu) => edu.institution || edu.degree)
      .map((edu) => ({
        institution: edu.institution,
        degree: edu.degree,
        field_of_study: edu.fieldOfStudy,
        start_date: edu.startYear,
        end_date: edu.endYear,
        gpa: edu.cgpa ? parseFloat(edu.cgpa) : undefined,
        description: edu.description,
      })),
    certifications: certifications
      .filter((cert) => cert.certificationName)
      .map((cert) => ({
        name: cert.certificationName,
        issuing_organization: cert.organization,
        issue_date: cert.issueDate,
        expiry_date: cert.expiryDate,
        credential_id: cert.credentialId,
      })),
    projects: projects
      .filter((proj) => proj.projectName)
      .map((proj) => ({
        name: proj.projectName,
        description: proj.description,
        technologies: proj.technologies,
        duration: proj.duration,
        role: proj.role,
        client: proj.client,
        url: proj.projectUrl,
      })),
    force_save: true,
  };
};
