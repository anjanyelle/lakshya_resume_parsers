import { User, Briefcase, Building, Calendar } from "lucide-react";
import type { Candidate } from "../../types/candidate";
import { calculateTotalExperience } from "../../utils/experienceCalculator";

type CandidateCardProps = {
  candidate: Candidate;
  onViewProfile?: (id: string) => void;
};

export default function CandidateCard({ candidate, onViewProfile }: CandidateCardProps) {
  const fullName = candidate.full_name || (candidate as any).name || "Unnamed candidate";
  const initials = fullName
    .split(' ')
    .map((n: string) => n[0])
    .join('')
    .substring(0, 2)
    .toUpperCase();
    
  const email = candidate.email || "";
  const displayEmail = email.length > 25 ? email.substring(0, 22) + "..." : email;

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
    <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm hover:shadow-md transition-shadow flex flex-col h-full">
      {/* Top Header Section */}
      <div className="flex items-start justify-between mb-5 gap-2">
        <div className="flex gap-3 sm:gap-4 items-center min-w-0 flex-1">
          <div className="w-12 h-12 sm:w-14 sm:h-14 rounded-full bg-purple-50 flex items-center justify-center border-2 border-purple-100 text-purple-600 font-bold text-lg sm:text-xl shrink-0">
            {initials ? initials : <User className="w-6 h-6" />}
          </div>
          <div className="min-w-0">
            <h3 className="text-lg sm:text-xl font-medium text-slate-800 uppercase tracking-wide truncate">
              {fullName}
            </h3>
            <p className="text-xs sm:text-sm text-slate-500 mt-0.5 truncate">
              {displayEmail}
            </p>
          </div>
        </div>
        <div className="flex flex-col items-end shrink-0 ml-2">
          <div className="flex items-center gap-1.5 px-3 py-1 bg-purple-50 border border-purple-100 rounded-full">
            <span className="text-xs font-medium text-purple-600">Parse:</span>
            <span className="text-sm font-bold text-purple-700">{parseScore}%</span>
          </div>
        </div>
      </div>

      {/* Skills Section */}
      <div className="mb-5">
        <p className="text-sm font-semibold text-slate-700 mb-3">Top Skills</p>
        <div className="flex flex-wrap gap-2">
          {displaySkills.map((skill, idx) => (
            <span
              key={skill.id || idx}
              className="px-2.5 py-1 sm:px-3 sm:py-1 bg-purple-50 text-purple-700 rounded-lg text-xs sm:text-sm font-medium border border-purple-100"
            >
              {(skill as any).skill_name || skill.name}
            </span>
          ))}
          {remainingSkillsCount > 0 && (
            <span className="px-2.5 py-1 sm:px-3 sm:py-1 bg-purple-600 text-white rounded-lg text-xs sm:text-sm font-medium shadow-sm">
              +{remainingSkillsCount} more
            </span>
          )}
        </div>
      </div>

      <hr className="border-gray-100 mb-5 mt-auto" />

      {/* Experience & Company Section */}
      <div className="grid grid-cols-2 gap-3 sm:gap-4 mb-6">
        <div className="flex flex-col sm:flex-row gap-2 sm:gap-3">
          <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-purple-50 flex items-center justify-center shrink-0 border border-purple-100">
            <Briefcase className="w-4 h-4 sm:w-5 sm:h-5 text-purple-600" />
          </div>
          <div className="min-w-0">
            <p className="text-[11px] sm:text-xs text-slate-500 mb-0.5">Total Experience</p>
            <p className="text-sm font-bold text-purple-800 leading-snug">{totalExp}</p>
            {expEntries > 0 && (
              <p className="text-[10px] text-slate-400 mt-1 leading-tight">Calc from {expEntries} entries</p>
            )}
          </div>
        </div>

        <div className="flex flex-col sm:flex-row gap-2 sm:gap-3">
          <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-purple-50 flex items-center justify-center shrink-0 border border-purple-100">
            <Building className="w-4 h-4 sm:w-5 sm:h-5 text-purple-600" />
          </div>
          <div className="min-w-0">
            <p className="text-[11px] sm:text-xs text-slate-500 mb-0.5">Current Company</p>
            <p className="text-xs sm:text-sm font-semibold text-purple-800 leading-snug break-words">
              {jobTitle !== "N/A" ? `${jobTitle} at ${currentCompany}` : currentCompany}
            </p>
          </div>
        </div>
      </div>

      <hr className="border-gray-100 mb-5" />

      {/* Footer */}
      <div className="flex items-center justify-between">
        <button 
          onClick={() => onViewProfile && onViewProfile(candidate.id)}
          className="px-4 py-2 sm:px-6 sm:py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-xs sm:text-sm font-semibold shadow-sm transition-colors cursor-pointer"
        >
          View Profile
        </button>
        <div className="flex items-center gap-1.5 text-slate-500 shrink-0 pl-2">
          <Calendar className="w-3 h-3 sm:w-4 sm:h-4" />
          <span className="text-[11px] sm:text-sm">Added {addedDate}</span>
        </div>
      </div>
    </div>
  );
}
