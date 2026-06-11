import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useJobStore } from "../store/useJobStore";
import toast from "react-hot-toast";

interface Job {
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
  status?: string;
  created_at: string;
  updated_at: string;
  currency?: string;
  salary_period?: string;
  work_mode?: string;
  number_of_openings?: number;
  notice_period?: string;
  salary_min?: number;
  salary_max?: number;
  required_skills?: Array<{
    id: string;
    skill_name: string;
    skill_type: "required" | "preferred";
  } | string>;
  preferred_skills?: Array<{
    id: string;
    skill_name: string;
    skill_type: "required" | "preferred";
  } | string>;
}

interface JobFormData {
  title: string;
  department: string;
  location: string;
  employment_type: string;
  work_mode: string;
  description: string;
  required_skills: string[];
  preferred_skills: string[];
  salary_min: string;
  salary_max: string;
  currency: string;
  salary_period: string;
  experience_range: string;
  education_requirement: string;
  number_of_openings: string;
  notice_period: string;
  status: string;
}

const experienceRanges = ["0-2 years", "3-5 years", "5-8 years", "8+ years"];

const employmentTypes = [
  "Full-time",
  "Part-time",
  "Contract",
  "Internship",
  "Remote",
];
const educationRequirements = [
  "High School",
  "Associate",
  "Bachelor",
  "Master",
  "PhD",
  "None",
];
const departments = [
  "Engineering",
  "Sales",
  "Marketing",
  "HR",
  "Finance",
  "Operations",
  "Product",
  "Design",
];

export default function JobsPage() {
  const navigate = useNavigate();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [editingJob, setEditingJob] = useState<Job | null>(null);
  const [currentSkill, setCurrentSkill] = useState("");
  const [currentPreferredSkill, setCurrentPreferredSkill] = useState("");

  const parseExperience = (range: string) => {
    switch (range) {
      case "0-2 years": return { min: 0, max: 2 };
      case "3-5 years": return { min: 3, max: 5 };
      case "5-8 years": return { min: 5, max: 8 };
      case "8+ years": return { min: 8, max: 20 };
      default: return { min: 0, max: 2 };
    }
  };

  const formatExperience = (min?: number, max?: number) => {
    if (min === 0 && max === 2) return "0-2 years";
    if (min === 3 && max === 5) return "3-5 years";
    if (min === 5 && max === 8) return "5-8 years";
    if (min === 8 && max === 20) return "8+ years";
    return "0-2 years";
  };

  const normalizeSkill = (skill: string) => {
    const trimmed = skill.trim();
    if (!trimmed) return "";
    
    const lower = trimmed.toLowerCase();
    const commonCasings: Record<string, string> = {
      javascript: "JavaScript",
      typescript: "TypeScript",
      react: "React",
      nodejs: "Node.js",
      "node.js": "Node.js",
      api: "API",
      ui: "UI",
      ux: "UX",
      html: "HTML",
      css: "CSS",
      aws: "AWS",
      sql: "SQL",
      php: "PHP",
    };
    
    if (commonCasings[lower]) return commonCasings[lower];
    return trimmed.charAt(0).toUpperCase() + trimmed.slice(1).toLowerCase();
  };

  const {
    jobs,
    fetchJobs,
    createJob,
    updateJob,
    deleteJob,
    isLoading: storeLoading,
  } = useJobStore();

  const [formData, setFormData] = useState<JobFormData>({
    title: "",
    department: "",
    location: "",
    employment_type: "",
    work_mode: "Onsite",
    description: "",
    required_skills: [],
    preferred_skills: [],
    salary_min: "",
    salary_max: "",
    currency: "USD",
    salary_period: "Yearly",
    experience_range: "0-2 years",
    education_requirement: "",
    number_of_openings: "1",
    notice_period: "",
    status: "active",
  });

  useEffect(() => {
    loadJobs();
  }, []);

  const loadJobs = async () => {
    try {
      await fetchJobs();
    } catch (error) {
      toast.error("Failed to load jobs");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.title || !formData.department || !formData.employment_type || !formData.experience_range) {
      toast.error("Please fill in all required fields");
      return;
    }

    if (formData.description.length < 50) {
      toast.error("Description must be at least 50 characters long");
      return;
    }

    if (formData.required_skills.length === 0) {
      toast.error("At least one required skill is required");
      return;
    }

    const sMin = formData.salary_min ? parseInt(formData.salary_min) : 0;
    const sMax = formData.salary_max ? parseInt(formData.salary_max) : 0;
    if (sMin && sMax && sMin >= sMax) {
      toast.error("Salary minimum must be less than maximum");
      return;
    }

    const numOpenings = parseInt(formData.number_of_openings) || 1;
    if (numOpenings <= 0) {
      toast.error("Number of openings must be greater than 0");
      return;
    }

    try {
      const exp = parseExperience(formData.experience_range);
      const jobData: Partial<Job> = {
        title: formData.title,
        department: formData.department,
        location: formData.location,
        employment_type: formData.employment_type,
        work_mode: formData.work_mode,
        description: formData.description,
        required_skills: formData.required_skills.map(skill => ({
          id: crypto.randomUUID(),
          skill_name: skill,
          skill_type: "required" as const
        })),
        preferred_skills: formData.preferred_skills.map(skill => ({
          id: crypto.randomUUID(),
          skill_name: skill,
          skill_type: "preferred" as const
        })),
        min_experience_years: exp.min,
        max_experience_years: exp.max,
        salary_min: sMin || undefined,
        salary_max: sMax || undefined,
        currency: formData.currency,
        salary_period: formData.salary_period,
        education_requirement: formData.education_requirement,
        number_of_openings: numOpenings,
        notice_period: formData.notice_period,
        status: formData.status,
      };

      if (editingJob) {
        await updateJob(editingJob.id, jobData);
        toast.success("Job updated successfully!");
      } else {
        await createJob(jobData);
        toast.success("Job created successfully!");
      }

      setIsCreateModalOpen(false);
      setEditingJob(null);
      resetForm();
      loadJobs();
    } catch (error: any) {
      toast.error(error.message || "Failed to save job");
    }
  };

  const resetForm = () => {
    setFormData({
      title: "",
      department: "",
      location: "",
      employment_type: "",
      work_mode: "Onsite",
      description: "",
      required_skills: [],
      preferred_skills: [],
      salary_min: "",
      salary_max: "",
      currency: "USD",
      salary_period: "Yearly",
      experience_range: "0-2 years",
      education_requirement: "",
      number_of_openings: "1",
      notice_period: "",
      status: "active",
    });
    setCurrentSkill("");
    setCurrentPreferredSkill("");
  };

  const openCreateModal = () => {
    resetForm();
    setEditingJob(null);
    setIsCreateModalOpen(true);
  };

  const openEditModal = (job: Job) => {
    setFormData({
      title: job.title,
      department: job.department || "",
      location: job.location || "",
      employment_type: job.employment_type || "",
      work_mode: job.work_mode || "Onsite",
      description: job.description,
      required_skills: job.required_skills?.map(s => typeof s === 'string' ? s : s.skill_name) || [],
      preferred_skills: job.preferred_skills?.map(s => typeof s === 'string' ? s : s.skill_name) || [],
      salary_min: job.salary_min ? String(job.salary_min) : "",
      salary_max: job.salary_max ? String(job.salary_max) : "",
      currency: job.currency || "USD",
      salary_period: job.salary_period || "Yearly",
      experience_range: formatExperience(job.min_experience_years, job.max_experience_years),
      education_requirement: job.education_requirement || "",
      number_of_openings: job.number_of_openings ? String(job.number_of_openings) : "1",
      notice_period: job.notice_period || "",
      status: job.status || "active",
    });
    setEditingJob(job);
    setIsCreateModalOpen(true);
  };

  const handleDeleteJob = async (jobId: string) => {
    if (!confirm("Are you sure you want to close/deactivate this job?")) return;

    try {
      await updateJob(jobId, { status: "closed" });
      toast.success("Job deactivated successfully!");
      loadJobs();
    } catch (error: any) {
      toast.error(error.message || "Failed to deactivate job");
    }
  };

  const addSkill = () => {
    const normalized = normalizeSkill(currentSkill);
    if (!normalized) return;
    
    const existsInRequired = formData.required_skills.some(
      s => s.toLowerCase() === normalized.toLowerCase()
    );
    const existsInPreferred = formData.preferred_skills.some(
      s => s.toLowerCase() === normalized.toLowerCase()
    );
    
    if (!existsInRequired && !existsInPreferred) {
      setFormData((prev) => ({
        ...prev,
        required_skills: [...prev.required_skills, normalized],
      }));
      setCurrentSkill("");
    } else {
      if (existsInPreferred) {
        toast.error("Skill is already in preferred skills");
      }
      setCurrentSkill("");
    }
  };

  const removeSkill = (skillToRemove: string) => {
    setFormData((prev) => ({
      ...prev,
      required_skills: prev.required_skills.filter(
        (skill) => skill !== skillToRemove,
      ),
    }));
  };

  const addPreferredSkill = () => {
    const normalized = normalizeSkill(currentPreferredSkill);
    if (!normalized) return;
    
    const existsInRequired = formData.required_skills.some(
      s => s.toLowerCase() === normalized.toLowerCase()
    );
    const existsInPreferred = formData.preferred_skills.some(
      s => s.toLowerCase() === normalized.toLowerCase()
    );
    
    if (!existsInRequired && !existsInPreferred) {
      setFormData((prev) => ({
        ...prev,
        preferred_skills: [...prev.preferred_skills, normalized],
      }));
      setCurrentPreferredSkill("");
    } else {
      if (existsInRequired) {
        toast.error("Skill is already in required skills");
      }
      setCurrentPreferredSkill("");
    }
  };

  const removePreferredSkill = (skillToRemove: string) => {
    setFormData((prev) => ({
      ...prev,
      preferred_skills: prev.preferred_skills.filter(
        (skill) => skill !== skillToRemove,
      ),
    }));
  };

  const getStatusColor = (status?: string) => {
    switch (status) {
      case "active":
        return "bg-green-100 text-green-800";
      case "inactive":
        return "bg-yellow-100 text-yellow-800";
      case "closed":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Job Management</h1>
          <p className="text-gray-600">Create and manage job postings</p>
        </div>
        {!isCreateModalOpen && (
          <button
            onClick={openCreateModal}
            className="px-4 py-2 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition-colors flex items-center"
          >
            <svg
              className="h-5 w-5 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Create Job
          </button>
        )}
      </div>

      {/* Inline Create/Edit Form */}
      {isCreateModalOpen && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden mb-8">
          <form onSubmit={handleSubmit}>
            <div className="p-6 sm:p-8">
              <div className="mb-6 flex justify-between items-center border-b border-gray-100 pb-4">
                <h3 className="text-2xl font-bold text-gray-900">
                  {editingJob ? "Edit Job" : "Create New Job"}
                </h3>
                <button
                  type="button"
                  onClick={() => setIsCreateModalOpen(false)}
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="space-y-6">
                {/* Title */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Job Title *</label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData((prev) => ({ ...prev, title: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder="e.g. Senior Software Engineer"
                    required
                  />
                </div>

                {/* Grid 1 */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Department *</label>
                    <select
                      value={formData.department}
                      onChange={(e) => setFormData((prev) => ({ ...prev, department: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                      required
                    >
                      <option value="">Select Department</option>
                      {departments.map((dept) => <option key={dept} value={dept}>{dept}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Employment Type *</label>
                    <select
                      value={formData.employment_type}
                      onChange={(e) => setFormData((prev) => ({ ...prev, employment_type: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                      required
                    >
                      <option value="">Select Type</option>
                      {employmentTypes.map((type) => <option key={type} value={type}>{type}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Work Mode</label>
                    <select
                      value={formData.work_mode}
                      onChange={(e) => setFormData((prev) => ({ ...prev, work_mode: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="Onsite">Onsite</option>
                      <option value="Remote">Remote</option>
                      <option value="Hybrid">Hybrid</option>
                    </select>
                  </div>
                </div>

                {/* Grid 2 */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
                    <input
                      type="text"
                      value={formData.location}
                      onChange={(e) => setFormData((prev) => ({ ...prev, location: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                      placeholder="e.g. New York, NY"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Experience Range *</label>
                    <select
                      value={formData.experience_range}
                      onChange={(e) => setFormData((prev) => ({ ...prev, experience_range: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                      required
                    >
                      {experienceRanges.map((range) => <option key={range} value={range}>{range}</option>)}
                    </select>
                  </div>
                </div>

                {/* Grid 3 - Salary */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Salary Min</label>
                    <input
                      type="number"
                      value={formData.salary_min}
                      onChange={(e) => setFormData((prev) => ({ ...prev, salary_min: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                      placeholder="e.g. 100000"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Salary Max</label>
                    <input
                      type="number"
                      value={formData.salary_max}
                      onChange={(e) => setFormData((prev) => ({ ...prev, salary_max: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                      placeholder="e.g. 150000"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Currency</label>
                    <select
                      value={formData.currency}
                      onChange={(e) => setFormData((prev) => ({ ...prev, currency: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="USD">USD ($)</option>
                      <option value="EUR">EUR (€)</option>
                      <option value="GBP">GBP (£)</option>
                      <option value="INR">INR (₹)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Salary Period</label>
                    <select
                      value={formData.salary_period}
                      onChange={(e) => setFormData((prev) => ({ ...prev, salary_period: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="Yearly">Yearly</option>
                      <option value="Monthly">Monthly</option>
                      <option value="Hourly">Hourly</option>
                    </select>
                  </div>
                </div>

                {/* Grid 4 */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Education Requirement</label>
                    <select
                      value={formData.education_requirement}
                      onChange={(e) => setFormData((prev) => ({ ...prev, education_requirement: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select Education</option>
                      {educationRequirements.map((req) => <option key={req} value={req}>{req}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Number of Openings</label>
                    <input
                      type="number"
                      min="1"
                      value={formData.number_of_openings}
                      onChange={(e) => setFormData((prev) => ({ ...prev, number_of_openings: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Notice Period</label>
                    <select
                      value={formData.notice_period}
                      onChange={(e) => setFormData((prev) => ({ ...prev, notice_period: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select Notice Period</option>
                      <option value="Immediate">Immediate</option>
                      <option value="15 Days">15 Days</option>
                      <option value="30 Days">30 Days</option>
                      <option value="60 Days">60 Days</option>
                      <option value="90 Days">90 Days</option>
                    </select>
                  </div>
                </div>

                {/* Status (Only on Edit) */}
                {editingJob && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Job Status</label>
                    <select
                      value={formData.status}
                      onChange={(e) => setFormData((prev) => ({ ...prev, status: e.target.value }))}
                      className="w-full md:w-1/3 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="active">Active</option>
                      <option value="draft">Draft</option>
                      <option value="on hold">On Hold</option>
                      <option value="closed">Closed</option>
                    </select>
                  </div>
                )}

                {/* Description */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Description *</label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData((prev) => ({ ...prev, description: e.target.value }))}
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder="Job description, responsibilities, requirements... (min 50 chars)"
                    required
                    minLength={50}
                  />
                </div>

                {/* Required Skills */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Required Skills *</label>
                  <div className="flex gap-2 mb-2">
                    <input
                      type="text"
                      value={currentSkill}
                      onChange={(e) => setCurrentSkill(e.target.value)}
                      onKeyPress={(e) => e.key === "Enter" && (e.preventDefault(), addSkill())}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                      placeholder="Type required skill and press Enter"
                    />
                    <button
                      type="button"
                      onClick={addSkill}
                      className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
                    >
                      Add
                    </button>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {formData.required_skills.map((skill, index) => (
                      <span key={index} className="px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full flex items-center">
                        {skill}
                        <button type="button" onClick={() => removeSkill(skill)} className="ml-2 text-blue-600 hover:text-blue-800">×</button>
                      </span>
                    ))}
                  </div>
                </div>

                {/* Preferred Skills */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Preferred Skills (Good to Have)</label>
                  <div className="flex gap-2 mb-2">
                    <input
                      type="text"
                      value={currentPreferredSkill}
                      onChange={(e) => setCurrentPreferredSkill(e.target.value)}
                      onKeyPress={(e) => e.key === "Enter" && (e.preventDefault(), addPreferredSkill())}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                      placeholder="Type preferred skill and press Enter"
                    />
                    <button
                      type="button"
                      onClick={addPreferredSkill}
                      className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
                    >
                      Add
                    </button>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {formData.preferred_skills.map((skill, index) => (
                      <span key={index} className="px-3 py-1 bg-purple-100 text-purple-800 text-sm font-medium rounded-full flex items-center">
                        {skill}
                        <button type="button" onClick={() => removePreferredSkill(skill)} className="ml-2 text-purple-600 hover:text-purple-800">×</button>
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Form Actions */}
              <div className="mt-8 flex items-center justify-end space-x-3 pt-6 border-t border-gray-100">
                <button
                  type="button"
                  onClick={() => setIsCreateModalOpen(false)}
                  className="px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  {editingJob ? "Save Changes" : "Create Job"}
                </button>
              </div>
            </div>
          </form>
        </div>
      )}

      {/* Jobs List */}
      {storeLoading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>
      ) : jobs && jobs.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {jobs.map((job) => (
            <div
              key={job.id}
              className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow p-6 flex flex-col h-full"
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="text-lg font-semibold text-gray-900">{job.title}</h3>
                    <span className="text-xs text-gray-400">#{job.id.substring(0, 8)}</span>
                  </div>
                  <p className="text-sm text-gray-600">{job.department}</p>
                </div>
                <button
                  onClick={() => updateJob(job.id, { status: job.status === "active" ? "closed" : "active" })}
                  className={`px-2 py-1 text-xs font-medium rounded-full transition-colors cursor-pointer hover:opacity-80 ${getStatusColor(job.status)}`}
                  title="Click to toggle status"
                >
                  {job.status}
                </button>
              </div>

              {/* Description Preview */}
              {job.description && (
                <p className="text-sm text-gray-600 mb-4 line-clamp-2">{job.description}</p>
              )}

              {/* Job Details Grid */}
              <div className="grid grid-cols-2 gap-y-2 gap-x-4 mb-4">
                <div className="flex items-center text-xs text-gray-600">
                  <svg className="h-4 w-4 mr-1.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                  <span className="truncate">{job.location || "Location not set"}</span>
                </div>
                <div className="flex items-center text-xs text-gray-600">
                  <svg className="h-4 w-4 mr-1.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>
                  <span className="truncate">{job.employment_type || "Type not set"}</span>
                </div>
                <div className="flex items-center text-xs text-gray-600">
                  <svg className="h-4 w-4 mr-1.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                  <span className="truncate">{job.min_experience_years}-{job.max_experience_years} years</span>
                </div>
                <div className="flex items-center text-xs text-gray-600">
                  <svg className="h-4 w-4 mr-1.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg>
                  <span className="truncate">{job.education_requirement || "Education not set"}</span>
                </div>
                {job.work_mode && (
                  <div className="flex items-center text-xs text-gray-600">
                    <svg className="h-4 w-4 mr-1.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/></svg>
                    <span className="truncate">{job.work_mode}</span>
                  </div>
                )}
                {(job.salary_min || job.salary_max) && (
                  <div className="flex items-center text-xs text-gray-600 col-span-2">
                    <svg className="h-4 w-4 mr-1.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                    <span className="truncate">
                      {job.salary_min ? job.salary_min : '0'} - {job.salary_max ? job.salary_max : '0'} {job.currency || 'USD'} {job.salary_period ? `/${job.salary_period}` : ''}
                    </span>
                  </div>
                )}
              </div>

              {/* Skills */}
              <div className="mb-4 space-y-3 flex-1">
                {job.required_skills && job.required_skills.length > 0 && (
                  <div>
                    <p className="text-xs text-gray-500 mb-1 uppercase tracking-wider font-semibold">Must Have</p>
                    <div className="flex flex-wrap gap-1">
                      {job.required_skills.slice(0, 3).map((skill, index) => (
                        <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded">
                          {typeof skill === 'string' ? skill : skill.skill_name}
                        </span>
                      ))}
                      {job.required_skills.length > 3 && (
                        <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs font-medium rounded">
                          +{job.required_skills.length - 3}
                        </span>
                      )}
                    </div>
                  </div>
                )}
                {job.preferred_skills && job.preferred_skills.length > 0 && (
                  <div>
                    <p className="text-xs text-gray-500 mb-1 uppercase tracking-wider font-semibold">Good to Have</p>
                    <div className="flex flex-wrap gap-1">
                      {job.preferred_skills.slice(0, 3).map((skill, index) => (
                        <span key={index} className="px-2 py-1 bg-purple-100 text-purple-800 text-xs font-medium rounded">
                          {typeof skill === 'string' ? skill : skill.skill_name}
                        </span>
                      ))}
                      {job.preferred_skills.length > 3 && (
                        <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs font-medium rounded">
                          +{job.preferred_skills.length - 3}
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Card Footer */}
              <div className="flex justify-between items-center text-xs text-gray-400 mb-3">
                <span>Created: {formatDate(job.created_at)}</span>
              </div>

              {/* Actions */}
              <div className="flex items-center justify-between pt-4 border-t border-gray-200 mt-auto">
                <button
                  onClick={() => navigate("/matching", { state: { jobId: job.id } })}
                  className="text-indigo-600 hover:text-indigo-800 text-sm font-medium flex items-center bg-indigo-50 px-3 py-1.5 rounded-md transition-colors"
                >
                  <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  Match
                </button>
                <div className="flex space-x-3">
                  <button onClick={() => openEditModal(job)} className="text-indigo-600 hover:text-indigo-700 text-sm font-medium transition-colors">
                    Edit
                  </button>
                  <button onClick={() => handleDeleteJob(job.id)} className="text-red-600 hover:text-red-700 text-sm font-medium transition-colors">
                    Close
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm p-12 text-center">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No jobs found</h3>
          <p className="mt-1 text-sm text-gray-500">Get started by creating your first job posting</p>
        </div>
      )}
    </div>
  );
}
