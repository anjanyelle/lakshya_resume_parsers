import { useState } from "react";
import { User, Briefcase, Building, Calendar } from "lucide-react";
import type { Candidate } from "../../types/candidate";
import { calculateTotalExperience } from "../../utils/experienceCalculator";

type CandidateCardProps = {
  candidate: Candidate;
  onViewProfile?: (id: string) => void;
};

export default function CandidateCard({ candidate, onViewProfile }: CandidateCardProps) {
  const [showAllSkills, setShowAllSkills] = useState(false);

  const fullName = candidate.full_name || (candidate as any).name || "Unnamed candidate";
  const initials = fullName
    .split(' ')
    .map((n: string) => n[0])
    .join('')
    .substring(0, 2)
    .toUpperCase();

  const email = candidate.email || "";

  // Formatting skills
  const skills = candidate.skills || [];
  const displaySkills = skills.slice(0, 4);
  const remainingSkillsCount = skills.length > 4 ? skills.length - 4 : 0;

  // Format added date
  const addedDate = candidate.created_at ? new Date(candidate.created_at).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric"
  }) : "Unknown Date";

  // Parsing score mock if unavailable
  const parseScore = (candidate as any).parsing_status?.confidence_score 
    ? Math.round((candidate as any).parsing_status.confidence_score * 100) 
    : 93;

  const workExperience = candidate.work_history || (candidate as any).work_experience || [];
  const currentCompany = workExperience.find((e: any) => e.is_current)?.company_name || "N/A";
  const jobTitle = workExperience.find((e: any) => e.is_current)?.job_title || "N/A";

  // Total Experience calculations
  const { total } = calculateTotalExperience(workExperience);
  const totalExp = total.total_records > 0 && total.formatted_string !== "0 Days" 
                   ? total.formatted_string 
                   : (candidate.total_years_exp?.formatted_string || 
                     (candidate.years_experience ? `${candidate.years_experience} Years` : "N/A"));
  const expEntries = total.total_records > 0 
                     ? total.total_records 
                     : (candidate.total_years_exp?.total_records || workExperience.length || 0);

  return (
    <div className="rounded-2xl border border-purple-200 bg-gradient-to-br from-white to-purple-50 p-6 shadow-md hover:shadow-xl transition-all flex flex-col h-full">
      {/* Top Header Section */}
      <div className="flex items-start justify-between mb-5 gap-2">
        <div className="flex gap-3 sm:gap-4 items-center min-w-0 flex-1">
          <div className="w-14 h-14 sm:w-16 sm:h-16 rounded-full bg-gradient-to-br from-purple-600 to-purple-700 flex items-center justify-center border-2 border-purple-200 text-white font-bold text-lg sm:text-xl shrink-0 shadow-md">
            {initials ? initials : <User className="w-6 h-6" />}
          </div>
          <div className="min-w-0">
            <h3 className="text-lg sm:text-xl font-bold text-purple-900 uppercase tracking-wide break-words leading-tight">
              {fullName}
            </h3>
            <p className="text-xs sm:text-sm text-purple-600 mt-1 break-words">
              {email}
            </p>
          </div>
        </div>
        <div className="flex flex-col items-end shrink-0 ml-2">
          <div className="flex items-center gap-1.5 px-4 py-2 bg-gradient-to-r from-purple-600 to-purple-700 rounded-full shadow-md">
            <span className="text-xs font-medium text-purple-100">Parse:</span>
            <span className="text-sm font-bold text-white">{parseScore}%</span>
          </div>
        </div>
      </div>

      {/* Skills Section */}
      <div className="mb-5">
        <p className="text-sm font-bold text-purple-800 mb-3">Top Skills</p>
        <div className="flex flex-wrap gap-2">
          {(showAllSkills ? skills : displaySkills).map((skill, idx) => (
            <span
              key={skill.id || idx}
              className="px-3 py-1.5 bg-gradient-to-r from-purple-100 to-purple-50 text-purple-800 rounded-lg text-xs sm:text-sm font-semibold border border-purple-200 shadow-sm break-words"
            >
              {(skill as any).skill_name || skill.name}
            </span>
          ))}
          {remainingSkillsCount > 0 && (
            <button
              onClick={() => setShowAllSkills(!showAllSkills)}
              className="px-3 py-1.5 bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-lg text-xs sm:text-sm font-semibold shadow-md hover:shadow-lg transition-all cursor-pointer"
            >
              {showAllSkills ? `Show less` : `+${remainingSkillsCount} more`}
            </button>
          )}
        </div>
      </div>

      <hr className="border-purple-200 mb-5 mt-auto" />

      {/* Experience & Company Section */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-full bg-gradient-to-br from-purple-100 to-purple-50 flex items-center justify-center shrink-0 border border-purple-200">
            <Briefcase className="w-5 h-5 sm:w-6 sm:h-6 text-purple-600" />
          </div>
          <div className="min-w-0">
            <p className="text-xs font-semibold text-purple-600 mb-1">Total Experience</p>
            <p className="text-sm font-bold text-purple-900 leading-snug break-words">{totalExp}</p>
            {expEntries > 0 && (
              <p className="text-xs text-purple-500 mt-1 leading-tight">Calc from {expEntries} entries</p>
            )}
          </div>
        </div>

        <div className="flex flex-col sm:flex-row gap-3">
          <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-full bg-gradient-to-br from-purple-100 to-purple-50 flex items-center justify-center shrink-0 border border-purple-200">
            <Building className="w-5 h-5 sm:w-6 sm:h-6 text-purple-600" />
          </div>
          <div className="min-w-0">
            <p className="text-xs font-semibold text-purple-600 mb-1">Current Company</p>
            <p className="text-xs sm:text-sm font-bold text-purple-900 leading-snug break-words">
              {jobTitle !== "N/A" ? `${jobTitle} at ${currentCompany}` : currentCompany}
            </p>
          </div>
        </div>
      </div>

      <hr className="border-purple-200 mb-5" />

      {/* Footer */}
      <div className="flex items-center justify-between mt-auto">
        <button
          onClick={() => onViewProfile && onViewProfile(candidate.id)}
          className="px-6 py-2.5 sm:px-8 sm:py-3 bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white rounded-xl text-xs sm:text-sm font-bold shadow-md hover:shadow-lg transition-all cursor-pointer"
        >
          View Profile
        </button>
        <div className="flex items-center gap-1.5 text-purple-600 shrink-0 pl-2">
          <Calendar className="w-4 h-4 sm:w-5 sm:h-5" />
          <span className="text-xs sm:text-sm font-medium">Added {addedDate}</span>
        </div>
      </div>
    </div>
  );
}
