import { useState, useEffect } from "react";
import { useJobStore } from "../store/useJobStore";
import CustomSelect from "../components/common/CustomSelect";
import toast from "react-hot-toast";
import { Briefcase, Plus, MapPin, Clock, BookOpen, Edit2, Trash2, X, Tag } from "lucide-react";

import type { Job } from "../types";

interface JobFormData {
  title: string;
  department: string;
  location: string;
  employment_type: string;
  description: string;
  required_skills: string[];
  min_experience: number;
  max_experience: number;
  education_requirement: string;
}

const employmentTypes = ["Full-time", "Part-time", "Contract", "Internship", "Remote"];
const educationRequirements = ["High School", "Associate", "Bachelor", "Master", "PhD", "None"];
const departments = ["Engineering", "Sales", "Marketing", "HR", "Finance", "Operations", "Product", "Design"];

export default function JobsPage() {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [editingJob, setEditingJob] = useState<Job | null>(null);
  const [currentSkill, setCurrentSkill] = useState("");

  const { jobs, fetchJobs, createJob, updateJob, deleteJob, isLoading: storeLoading } = useJobStore();

  const [formData, setFormData] = useState<JobFormData>({
    title: "", department: "", location: "", employment_type: "",
    description: "", required_skills: [], min_experience: 0, max_experience: 10, education_requirement: "",
  });

  useEffect(() => { loadJobs(); }, []);

  const loadJobs = async () => {
    try {
      await fetchJobs();
    } catch {
      console.error("Failed to load jobs, using dummy data");
    }
  };

  const displayJobs = jobs || [];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.title || !formData.department || !formData.employment_type) {
      toast.error("Please fill in all required fields"); return;
    }
    try {
      const payload = {
        ...formData,
        required_skills: formData.required_skills.map(skill => ({
          skill_name: skill,
          skill_type: "required" as "required" | "preferred"
        }))
      };
      if (editingJob) { await updateJob(editingJob.id, payload); toast.success("Job updated successfully!"); }
      else { await createJob(payload); toast.success("Job created successfully!"); }
      setIsCreateModalOpen(false); setEditingJob(null); resetForm(); loadJobs();
    } catch (error: any) { toast.error(error.message || "Failed to save job"); }
  };

  const resetForm = () => {
    setFormData({ title: "", department: "", location: "", employment_type: "", description: "", required_skills: [], min_experience: 0, max_experience: 10, education_requirement: "" });
    setCurrentSkill("");
  };

  const openCreateModal = () => { resetForm(); setEditingJob(null); setIsCreateModalOpen(true); };

  const openEditModal = (job: Job) => {
    setFormData({
      title: job.title, department: job.department || "", location: job.location || "",
      employment_type: job.employment_type || "", description: job.description,
      required_skills: job.required_skills?.map(s => typeof s === "string" ? s : s.skill_name) || [],
      min_experience: job.min_experience_years || 0,
      max_experience: job.max_experience_years || 10, education_requirement: job.education_requirement || "",
    });
    setEditingJob(job); setIsCreateModalOpen(true);
  };

  const handleDeleteJob = async (jobId: string) => {
    if (!confirm("Are you sure you want to delete this job?")) return;
    try { await deleteJob(jobId); toast.success("Job deleted successfully!"); loadJobs(); }
    catch (error: any) { toast.error(error.message || "Failed to delete job"); }
  };

  const addSkill = () => {
    if (currentSkill.trim() && !formData.required_skills.includes(currentSkill.trim())) {
      setFormData((prev) => ({ ...prev, required_skills: [...prev.required_skills, currentSkill.trim()] }));
      setCurrentSkill("");
    }
  };

  const removeSkill = (skillToRemove: string) =>
    setFormData((prev) => ({ ...prev, required_skills: prev.required_skills.filter((s) => s !== skillToRemove) }));

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "active": return "bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800/50";
      case "inactive": return "bg-amber-50 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 border-amber-200 dark:border-amber-800/50";
      case "closed": return "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-700";
      default: return "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-700";
    }
  };

  const formatDate = (d: string) =>
    new Date(d).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#0F172A] transition-colors duration-500">
      <div className="p-6 sm:p-8 max-w-7xl mx-auto space-y-6">

        {/* Header */}
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-4">
            <div className="p-2.5 rounded-xl shadow-sm text-white flex-shrink-0" style={{ background: 'linear-gradient(135deg, #7C3AED 0%, #9333EA 100%)' }}>
              <Briefcase className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-navy-900 dark:text-white">Job Management</h1>
              <p className="text-slate-500 dark:text-slate-400 text-sm font-medium">Create and manage job postings for AI-powered candidate matching</p>
            </div>
          </div>
          <button
            onClick={isCreateModalOpen ? () => setIsCreateModalOpen(false) : openCreateModal}
            className={`flex-shrink-0 flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-bold shadow-lg transition-all active:scale-95 border border-transparent ${isCreateModalOpen
                ? "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-700 shadow-none"
                : "text-white shadow-purple-500/25 hover:shadow-purple-500/40 hover:-translate-y-0.5"
              }`}
            style={!isCreateModalOpen ? { background: 'linear-gradient(135deg, #7C3AED 0%, #9333EA 100%)' } : {}}
          >
            {isCreateModalOpen ? <><X className="w-4 h-4" /> Close Form</> : <><Plus className="w-5 h-5" /> Create Job</>}
          </button>
        </div>

        {/* Inline Create/Edit Form */}
        {isCreateModalOpen && (
          <div className="bg-white dark:bg-slate-800/40 dark:backdrop-blur-xl rounded-2xl border border-slate-100 dark:border-slate-700/50 shadow-sm transition-all animate-in fade-in slide-in-from-top-4 duration-300">
            <div className="px-6 py-4 border-b border-slate-50 dark:border-slate-700/50">
              <h3 className="text-base font-bold text-navy-900 dark:text-white">{editingJob ? "Edit Job" : "Create New Job"}</h3>
              <p className="text-xs text-slate-400 dark:text-slate-500 mt-0.5">Fill in the job details below</p>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-5">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="space-y-5">
                  {/* Title */}
                  <div>
                    <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider mb-1.5">Job Title *</label>
                    <input type="text" value={formData.title} onChange={(e) => setFormData((p) => ({ ...p, title: e.target.value }))}
                      className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-700/50 rounded-xl text-sm focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition-all dark:text-white"
                      placeholder="e.g. Senior Software Engineer" required />
                  </div>

                  {/* Dept + Type */}
                  <div className="grid grid-cols-2 gap-4">
                    <CustomSelect
                      label="Department *"
                      options={departments.map(d => ({ value: d, label: d }))}
                      value={formData.department}
                      onChange={(val) => setFormData(p => ({ ...p, department: val }))}
                    />
                    <CustomSelect
                      label="Employment Type *"
                      options={employmentTypes.map(t => ({ value: t, label: t }))}
                      value={formData.employment_type}
                      onChange={(val) => setFormData(p => ({ ...p, employment_type: val }))}
                    />
                  </div>

                  {/* Location */}
                  <div>
                    <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider mb-1.5">Location</label>
                    <input type="text" value={formData.location} onChange={(e) => setFormData((p) => ({ ...p, location: e.target.value }))}
                      className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-700/50 rounded-xl text-sm focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition-all dark:text-white"
                      placeholder="e.g. New York, NY or Remote" />
                  </div>

                  {/* Experience */}
                  <div>
                    <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider mb-1.5">
                      Experience Range: {formData.min_experience}–{formData.max_experience} years
                    </label>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-slate-50 dark:bg-slate-900/30 p-3 rounded-xl border border-slate-100 dark:border-slate-700/50">
                        <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Minimum</span>
                        <input type="range" min="0" max="20" value={formData.min_experience}
                          onChange={(e) => setFormData((p) => ({ ...p, min_experience: Math.min(parseInt(e.target.value), p.max_experience - 1) }))}
                          className="w-full accent-purple-600" />
                      </div>
                      <div className="bg-slate-50 dark:bg-slate-900/30 p-3 rounded-xl border border-slate-100 dark:border-slate-700/50">
                        <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Maximum</span>
                        <input type="range" min="1" max="20" value={formData.max_experience}
                          onChange={(e) => setFormData((p) => ({ ...p, max_experience: Math.max(parseInt(e.target.value), p.min_experience + 1) }))}
                          className="w-full accent-purple-600" />
                      </div>
                    </div>
                  </div>
                </div>

                <div className="space-y-5">
                  {/* Description */}
                  <div>
                    <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider mb-1.5">Description</label>
                    <textarea value={formData.description} onChange={(e) => setFormData((p) => ({ ...p, description: e.target.value }))}
                      rows={4} className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-700/50 rounded-xl text-sm focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition-all resize-none dark:text-white"
                      placeholder="Job description, responsibilities, requirements..." />
                  </div>

                  {/* Skills */}
                  <div>
                    <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider mb-1.5">Required Skills</label>
                    <div className="flex gap-2 mb-2">
                      <div className="relative flex-1">
                        <Tag className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400" />
                        <input type="text" value={currentSkill} onChange={(e) => setCurrentSkill(e.target.value)}
                          onKeyPress={(e) => e.key === "Enter" && (e.preventDefault(), addSkill())}
                          className="w-full pl-9 pr-4 py-2.5 bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-700/50 rounded-xl text-sm focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition-all dark:text-white"
                          placeholder="Type skill and press Enter" />
                      </div>
                      <button type="button" onClick={addSkill}
                        className="px-4 py-2 text-white text-sm font-semibold rounded-xl transition-colors"
                        style={{ background: '#7C3AED' }}>
                        Add
                      </button>
                    </div>
                    <div className="flex flex-wrap gap-2 max-h-24 overflow-y-auto p-1">
                      {formData.required_skills.map((skill, i) => (
                        <span key={i} className="flex items-center gap-1.5 px-3 py-1 bg-purple-50 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 text-xs font-semibold rounded-lg border border-purple-100 dark:border-purple-800/50">
                          {skill}
                          <button type="button" onClick={() => removeSkill(skill)} className="text-purple-400 hover:text-purple-700 transition-colors">×</button>
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Education */}
                  <CustomSelect
                    label="Education Requirement"
                    options={educationRequirements.map(l => ({ value: l, label: l }))}
                    value={formData.education_requirement}
                    onChange={(val) => setFormData(p => ({ ...p, education_requirement: val }))}
                  />
                </div>
              </div>

              {/* Actions */}
              <div className="flex justify-end gap-3 pt-4 border-t border-slate-50 dark:border-slate-700/50">
                <button type="button" onClick={() => setIsCreateModalOpen(false)} className="px-6 py-2.5 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 text-sm font-semibold rounded-xl transition-colors">
                  Cancel
                </button>
                <button type="submit"
                  className="px-8 py-2.5 text-white text-sm font-bold rounded-xl transition-all shadow-sm hover:shadow-purple-500/20 active:scale-95"
                  style={{ background: '#7C3AED' }}>
                  {editingJob ? "Update Job Posting" : "Publish Job Posting"}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Jobs Grid */}
        {storeLoading ? (
          <div className="flex flex-col items-center justify-center h-64 bg-white rounded-2xl border border-slate-100">
            <div className="animate-spin rounded-full h-10 w-10 border-[3px] border-brand-100 border-t-brand-600 mb-3" />
            <p className="text-sm font-medium text-slate-400">Loading jobs...</p>
          </div>
        ) : displayJobs && displayJobs.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {displayJobs.map((job) => (
              <div key={job.id} className="bg-white dark:bg-slate-800/40 dark:backdrop-blur-xl rounded-2xl border border-slate-100 dark:border-slate-700/50 shadow-sm interactive-box p-5 flex flex-col transition-all">
                {/* Card Header */}
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-start gap-3 flex-1 min-w-0">
                    <div className="h-10 w-10 rounded-xl flex items-center justify-center flex-shrink-0 mt-0.5 bg-purple-50 dark:bg-purple-900/30">
                      <Briefcase className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                    </div>
                    <div className="min-w-0">
                      <h3 className="font-bold text-navy-900 dark:text-white text-sm leading-tight">{job.title}</h3>
                      <p className="text-xs text-slate-400 dark:text-slate-500 mt-0.5">{job.department}</p>
                    </div>
                  </div>
                  <span className={`flex-shrink-0 ml-2 px-2.5 py-1 text-xs font-bold rounded-full border ${getStatusBadge(job.status)}`}>
                    {job.status}
                  </span>
                </div>

                {/* Details */}
                <div className="space-y-1.5 mb-3">
                  {job.location && (
                    <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400 font-medium">
                      <MapPin className="w-3.5 h-3.5 text-slate-400 dark:text-slate-500 flex-shrink-0" />
                      <span className="truncate">{job.location}</span>
                    </div>
                  )}
                  {job.employment_type && (
                    <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400 font-medium">
                      <Clock className="w-3.5 h-3.5 text-slate-400 dark:text-slate-500 flex-shrink-0" />
                      <span>{job.employment_type}</span>
                    </div>
                  )}
                  <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400 font-medium">
                    <BookOpen className="w-3.5 h-3.5 text-slate-400 dark:text-slate-500 flex-shrink-0" />
                    <span>{job.min_experience_years || 0}–{job.max_experience_years || 10} years exp.</span>
                  </div>
                </div>

                {/* Skills */}
                {job.required_skills && job.required_skills.length > 0 && (
                  <div className="mb-4 flex-1">
                    <p className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-1.5">Required Skills</p>
                    <div className="flex flex-wrap gap-1.5">
                      {job.required_skills.slice(0, 3).map((skill, i) => (
                        <span key={i} className="px-2 py-0.5 text-xs font-semibold rounded-lg border bg-purple-50 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 border-purple-100 dark:border-purple-800/50">
                          {typeof skill === "string" ? skill : skill.skill_name}
                        </span>
                      ))}
                      {job.required_skills.length > 3 && (
                        <span className="px-2 py-0.5 bg-slate-100 dark:bg-slate-700 text-slate-500 dark:text-slate-400 text-xs font-semibold rounded-lg">
                          +{job.required_skills.length - 3}
                        </span>
                      )}
                    </div>
                  </div>
                )}

                {/* Footer */}
                <div className="flex items-center justify-between pt-3 border-t border-slate-50 dark:border-slate-700/50">
                  <span className="text-xs text-slate-400 dark:text-slate-500">Added {formatDate(job.created_at)}</span>
                  <div className="flex items-center gap-2">
                    <button onClick={() => openEditModal(job)} className="flex items-center gap-1 px-3 py-1.5 text-xs font-bold text-purple-600 dark:text-purple-400 hover:bg-purple-50 dark:hover:bg-slate-700/50 rounded-lg transition-all">
                      <Edit2 className="w-3 h-3" /> Edit
                    </button>
                    <button onClick={() => handleDeleteJob(job.id)} className="flex items-center gap-1 px-3 py-1.5 text-xs font-bold text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-all">
                      <Trash2 className="w-3 h-3" /> Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-16 text-center">
            <div className="h-16 w-16 rounded-2xl flex items-center justify-center mx-auto mb-4" style={{ background: '#f3e8ff' }}>
              <Briefcase className="h-8 w-8" style={{ color: '#7C3AED', opacity: 0.5 }} />
            </div>
            <h3 className="text-base font-bold text-navy-900 mb-1">No jobs yet</h3>
            <p className="text-sm text-slate-400 mb-5">Get started by creating your first job posting</p>
            <button onClick={openCreateModal}
              className="px-6 py-3 text-white text-sm font-bold rounded-xl transition-all shadow-lg shadow-purple-500/25 hover:shadow-purple-500/40 hover:-translate-y-0.5 active:scale-95 inline-flex items-center gap-2"
              style={{ background: 'linear-gradient(135deg, #7C3AED 0%, #9333EA 100%)' }}>
              <Plus className="w-5 h-5" /> Create First Job
            </button>
          </div>
        )}
      </div>

    </div>
  );
}
