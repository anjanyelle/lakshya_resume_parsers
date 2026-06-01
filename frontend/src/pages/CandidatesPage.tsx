import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useCandidateStore } from "../store/useCandidateStore";
import { useFilterStore } from "../store/filterStore";
import toast from "react-hot-toast";
import { Users, Search, RefreshCw, User, Award, DollarSign } from "lucide-react";

type FilterType = "all" | "high-confidence" | "needs-review";
type SortType = "date-added" | "name" | "confidence-score" | "match-score";

export default function CandidatesPage() {
  const [filter, setFilter] = useState<FilterType>("all");
  const [sort, setSort] = useState<SortType>("date-added");
  const [currentPage, setCurrentPage] = useState(1);

  const { candidates, pagination, isLoading, fetchCandidates } = useCandidateStore();
  const { searchTerm, company, jobTitle, certification, salaryMin, salaryMax, setSearchTerm, setCompany, setJobTitle, setCertification, setSalaryRange } = useFilterStore();
  const navigate = useNavigate();

  const itemsPerPage = 20;

  useEffect(() => {
    loadCandidates();
  }, [currentPage, searchTerm, company, jobTitle, certification, salaryMin, salaryMax]);

  const loadCandidates = async () => {
    try {
      await fetchCandidates(currentPage, itemsPerPage, searchTerm, company, jobTitle, certification, salaryMin, salaryMax);
    } catch (error) {
      toast.error("Failed to load candidates");
    }
  };

  // Client-side filter and sort (search is handled server-side)
  const filteredCandidates = candidates
    .filter((candidate) => {
      // Status filter (client-side)
      const confidence = candidate.parsing_status?.confidence_score || 0;
      const matchesFilter =
        filter === "all" ||
        (filter === "high-confidence" && confidence >= 0.8) ||
        (filter === "needs-review" && confidence < 0.8);

      return matchesFilter;
    })
    .sort((a, b) => {
      // Sort logic (client-side)
      switch (sort) {
        case "name":
          return (a.full_name || "").localeCompare(b.full_name || "");
        case "confidence-score":
          const aConfidence = a.parsing_status?.confidence_score || 0;
          const bConfidence = b.parsing_status?.confidence_score || 0;
          return bConfidence - aConfidence;
        case "match-score":
          const aMatchScore = a.match_score || 0;
          const bMatchScore = b.match_score || 0;
          return bMatchScore - aMatchScore;
        case "date-added":
        default:
          return (
            new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
          );
      }
    });

  // Use server-side pagination
  const paginatedCandidates = filteredCandidates;
  
  // Debug: Log pagination state
  console.log("🔍 Pagination state:", pagination);
  console.log("🔍 Candidates count:", candidates.length);

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return "bg-purple-100 text-purple-800";
    if (confidence >= 0.6) return "bg-purple-50 text-purple-700";
    return "bg-gray-100 text-gray-600";
  };

  const getMatchScoreColor = (score: number) => {
    if (score >= 0.8) return "bg-green-100 text-green-800";
    if (score >= 0.6) return "bg-blue-100 text-blue-800";
    if (score >= 0.4) return "bg-yellow-100 text-yellow-800";
    return "bg-red-100 text-red-800";
  };

  
  const getExperienceSummary = (workExperience: any[]) => {
    if (!workExperience || workExperience.length === 0) return "No experience";

    const currentJob = workExperience.find((exp) => exp.is_current);
    if (currentJob) {
      return `${currentJob.job_title} at ${currentJob.company_name}`;
    }

    const latestJob = workExperience[0];
    return `Previously ${latestJob.job_title} at ${latestJob.company_name}`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center gap-3 mb-2">
            <Users className="w-6 h-6 text-purple-600" />
            <h1 className="text-2xl font-bold text-gray-900">Candidates</h1>
          </div>
          <p className="text-gray-600">
            Manage and review candidate profiles with AI-powered resume parsing insights
          </p>
        </div>

        {/* Search and Filters */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <div className="flex flex-col gap-4">
          {/* Search Fields */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Name Search */}
            <div className="relative">
              <input
                type="text"
                placeholder="Search by name, email, or skill..."
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                  setCurrentPage(1);
                }}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              />
              <Search className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
            </div>

            {/* Company Search */}
            <div className="relative">
              <input
                type="text"
                placeholder="Search by company..."
                value={company}
                onChange={(e) => {
                  setCompany(e.target.value);
                  setCurrentPage(1);
                }}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              />
              <Users className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
            </div>

            {/* Job Title Search */}
            <div className="relative">
              <input
                type="text"
                placeholder="Search by job title..."
                value={jobTitle}
                onChange={(e) => {
                  setJobTitle(e.target.value);
                  setCurrentPage(1);
                }}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              />
              <User className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
            </div>

            {/* Certification Search */}
            <div className="relative">
              <input
                type="text"
                placeholder="Search by certification..."
                value={certification}
                onChange={(e) => {
                  setCertification(e.target.value);
                  setCurrentPage(1);
                }}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              />
              <Award className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
            </div>

            {/* Salary Min */}
            <div className="relative">
              <input
                type="number"
                placeholder="Min salary..."
                value={salaryMin || ""}
                onChange={(e) => {
                  setSalaryRange(e.target.value ? parseFloat(e.target.value) : null, salaryMax);
                  setCurrentPage(1);
                }}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              />
              <DollarSign className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
            </div>

            {/* Salary Max */}
            <div className="relative">
              <input
                type="number"
                placeholder="Max salary..."
                value={salaryMax || ""}
                onChange={(e) => {
                  setSalaryRange(salaryMin, e.target.value ? parseFloat(e.target.value) : null);
                  setCurrentPage(1);
                }}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              />
              <DollarSign className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
            </div>
          </div>

          {/* Filter Buttons and Sort */}
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Filter Buttons */}
            <div className="flex gap-2">
              <button
                onClick={() => setFilter("all")}
                className={`px-6 py-2.5 rounded-xl font-medium transition-colors ${
                  filter === "all"
                    ? "bg-purple-600 text-white hover:bg-purple-700"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                All ({pagination?.total_items || candidates.length})
              </button>
              <button
                onClick={() => setFilter("high-confidence")}
                className={`px-6 py-2.5 rounded-xl font-medium transition-colors ${
                  filter === "high-confidence"
                    ? "bg-purple-600 text-white hover:bg-purple-700"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                High Confidence
              </button>
              <button
                onClick={() => setFilter("needs-review")}
                className={`px-6 py-2.5 rounded-xl font-medium transition-colors ${
                  filter === "needs-review"
                    ? "bg-purple-600 text-white hover:bg-purple-700"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                Needs Review
              </button>
            </div>

            {/* Sort Options */}
            <select
              value={sort}
              onChange={(e) => {
                setSort(e.target.value as SortType);
                setCurrentPage(1);
              }}
              className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="date-added">Date Added</option>
              <option value="name">Name</option>
              <option value="confidence-score">Confidence Score</option>
            </select>
          </div>
        </div>
      </div>


          {/* Results Count */}
          <div className="mb-6 flex items-center justify-between">
            <p className="text-sm text-gray-600">
              Showing {paginatedCandidates.length} of {pagination?.total_items || filteredCandidates.length}{" "}
              candidates
              {pagination && ` (Page ${pagination.current_page} of ${pagination.total_pages})`}
            </p>
            <button
              onClick={loadCandidates}
              disabled={isLoading}
              className="text-sm text-purple-600 hover:text-purple-700 disabled:opacity-50 flex items-center gap-2"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
              {isLoading ? "Refreshing..." : "Refresh"}
            </button>
          </div>

          {/* Candidates Grid */}
          {isLoading ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
            </div>
          ) : paginatedCandidates.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
          {paginatedCandidates.map((candidate) => (
              <div
                key={candidate.id}
                className="bg-white rounded-lg shadow-sm hover:shadow-lg transition-all duration-200 p-6 border border-gray-100 hover:border-purple-200"
              >
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center">
                    <div className="h-12 w-12 bg-purple-100 rounded-full flex items-center justify-center">
                      <User className="w-6 h-6 text-purple-600" />
                    </div>
                    <div className="ml-3">
                      <h3 className="font-semibold text-gray-900 text-lg">
                        {candidate.full_name}
                      </h3>
                      <p className="text-sm text-gray-600">{candidate.email}</p>
                    </div>
                </div>

                {/* Confidence Badge */}
                <div className="flex flex-col gap-1 items-end">
                  <span
                    className={`px-2 py-1 text-xs font-medium rounded-full ${getConfidenceColor(candidate.parsing_status?.confidence_score || 0)}`}
                  >
                    {Math.round(
                      (candidate.parsing_status?.confidence_score || 0) * 100,
                    )}
                    %
                  </span>
                  {candidate.match_score !== undefined && candidate.match_score !== null && (
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded-full ${getMatchScoreColor(candidate.match_score)}`}
                    >
                      Match: {Math.round(candidate.match_score * 100)}%
                    </span>
                  )}
                </div>
              </div>

              {/* Skills */}
              {candidate.skills && candidate.skills.length > 0 && (
                <div className="mb-4">
                  <p className="text-sm font-medium text-gray-700 mb-2">Top Skills</p>
                  <div className="flex flex-wrap gap-1.5">
                    {candidate.skills.slice(0, 4).map((skill, index) => (
                      <span
                        key={index}
                        className="px-2.5 py-1 bg-purple-100 text-purple-800 text-xs font-medium rounded-lg border border-purple-200"
                      >
                        {skill.skill_name}
                      </span>
                    ))}
                    {candidate.skills.length > 4 && (
                      <span className="px-2.5 py-1 bg-gray-100 text-gray-600 text-xs font-medium rounded-lg border border-gray-200">
                        +{candidate.skills.length - 4} more
                      </span>
                    )}
                  </div>
                </div>
              )}

              {/* Experience Summary */}
              <div className="mb-4">
                <p className="text-sm text-gray-600 mb-1">Experience</p>
                <p className="text-sm text-gray-900">
                  {getExperienceSummary(candidate.work_experience || [])}
                </p>
              </div>

              {/* Actions */}
              <div className="flex items-center justify-between">
                <button
                  onClick={() => navigate(`/candidates/${candidate.id}`)}
                  className="flex-1 mr-2 px-4 py-2.5 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 transition-colors"
                >
                  View Profile
                </button>
                <div className="text-xs text-gray-500">
                  Added {formatDate(candidate.created_at)}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm p-12 text-center">
          <Users className="mx-auto h-12 w-12 text-purple-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">
            No candidates found
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchTerm
              ? "Try adjusting your search terms"
              : "Get started by uploading some resumes"}
          </p>
        </div>
      )}

      {/* Pagination */}
      {pagination && pagination.total_pages > 1 && (
        <div className="flex items-center justify-between mt-6 bg-white rounded-lg shadow-sm p-4">
          <div className="text-sm text-gray-600">
            Page {pagination.current_page} of {pagination.total_pages}
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
              disabled={!pagination.has_prev_page}
              className="px-3 py-1 text-sm border border-purple-200 text-purple-700 rounded-md hover:bg-purple-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>

            {/* Page Numbers */}
            {Array.from({ length: Math.min(5, pagination.total_pages) }).map((_, idx) => {
              let pageNum;
              if (pagination.total_pages <= 5) {
                pageNum = idx + 1;
              } else if (pagination.current_page <= 3) {
                pageNum = idx + 1;
              } else if (pagination.current_page >= pagination.total_pages - 2) {
                pageNum = pagination.total_pages - 4 + idx;
              } else {
                pageNum = pagination.current_page - 2 + idx;
              }

              return (
                <button
                  key={idx}
                  onClick={() => setCurrentPage(pageNum)}
                  className={`px-3 py-1 text-sm rounded-md transition-colors ${
                    pageNum === pagination.current_page
                      ? "bg-purple-600 text-white hover:bg-purple-700"
                      : "border border-purple-200 text-purple-700 hover:bg-purple-50"
                  }`}
                >
                  {pageNum}
                </button>
              );
            })}

            <button
              onClick={() =>
                setCurrentPage((prev) => Math.min(pagination.total_pages, prev + 1))
              }
              disabled={!pagination.has_next_page}
              className="px-3 py-1 text-sm border border-purple-200 text-purple-700 rounded-md hover:bg-purple-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      )}
      </div>
    </div>
  );
}
