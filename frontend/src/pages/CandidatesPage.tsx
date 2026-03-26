import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useCandidateStore } from "../store/useCandidateStore";
import toast from "react-hot-toast";

type FilterType = "all" | "high-confidence" | "needs-review";
type SortType = "date-added" | "name" | "confidence-score";

export default function CandidatesPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [filter, setFilter] = useState<FilterType>("all");
  const [sort, setSort] = useState<SortType>("date-added");
  const [currentPage, setCurrentPage] = useState(1);

  const { candidates, pagination, isLoading, fetchCandidates } = useCandidateStore();
  const navigate = useNavigate();

  const itemsPerPage = 20;

  useEffect(() => {
    loadCandidates();
  }, [currentPage, searchTerm]);

  const loadCandidates = async () => {
    try {
      await fetchCandidates(currentPage, itemsPerPage, searchTerm);
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
    if (confidence >= 0.8) return "bg-green-100 text-green-800";
    if (confidence >= 0.6) return "bg-yellow-100 text-yellow-800";
    return "bg-red-100 text-red-800";
  };

  const getInitials = (name: string) => {
    if (!name) return "?";
    return name
      .split(" ")
      .map((part) => part.charAt(0).toUpperCase())
      .slice(0, 2)
      .join("");
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
    <div className="p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Candidates</h1>
        <p className="text-gray-600">Manage and review candidate profiles</p>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Search Bar */}
          <div className="flex-1">
            <div className="relative">
              <input
                type="text"
                placeholder="Search by name, email, or skill..."
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                  setCurrentPage(1);
                }}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
              <svg
                className="absolute left-3 top-2.5 h-5 w-5 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </div>
          </div>

          {/* Filter Buttons */}
          <div className="flex gap-2">
            <button
              onClick={() => setFilter("all")}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filter === "all"
                  ? "bg-indigo-600 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              All ({pagination?.total_items || candidates.length})
            </button>
            <button
              onClick={() => setFilter("high-confidence")}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filter === "high-confidence"
                  ? "bg-indigo-600 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              High Confidence
            </button>
            <button
              onClick={() => setFilter("needs-review")}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filter === "needs-review"
                  ? "bg-indigo-600 text-white"
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
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          >
            <option value="date-added">Date Added</option>
            <option value="name">Name</option>
            <option value="confidence-score">Confidence Score</option>
          </select>
        </div>
      </div>

      {/* Debug Info - TEMPORARY */}
      {pagination && (
        <div className="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-xs font-mono">
            <strong>DEBUG:</strong> Pagination = {JSON.stringify(pagination)}
          </p>
        </div>
      )}
      {!pagination && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-xs font-mono">
            <strong>DEBUG:</strong> Pagination is NULL or undefined
          </p>
        </div>
      )}

      {/* Results Count */}
      <div className="mb-4 flex items-center justify-between">
        <p className="text-sm text-gray-600">
          Showing {paginatedCandidates.length} of {pagination?.total_items || filteredCandidates.length}{" "}
          candidates
          {pagination && ` (Page ${pagination.current_page} of ${pagination.total_pages})`}
        </p>
        <button
          onClick={loadCandidates}
          disabled={isLoading}
          className="text-sm text-indigo-600 hover:text-indigo-700 disabled:opacity-50"
        >
          {isLoading ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      {/* Candidates Grid */}
      {isLoading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>
      ) : paginatedCandidates.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
          {paginatedCandidates.map((candidate) => (
            <div
              key={candidate.id}
              className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow p-6"
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center">
                  <div className="h-12 w-12 bg-indigo-100 rounded-full flex items-center justify-center">
                    <span className="text-indigo-600 font-semibold">
                      {getInitials(candidate.full_name)}
                    </span>
                  </div>
                  <div className="ml-3">
                    <h3 className="font-semibold text-gray-900">
                      {candidate.full_name}
                    </h3>
                    <p className="text-sm text-gray-600">{candidate.email}</p>
                  </div>
                </div>

                {/* Confidence Badge */}
                <span
                  className={`px-2 py-1 text-xs font-medium rounded-full ${getConfidenceColor(candidate.parsing_status?.confidence_score || 0)}`}
                >
                  {Math.round(
                    (candidate.parsing_status?.confidence_score || 0) * 100,
                  )}
                  %
                </span>
              </div>

              {/* Skills */}
              {candidate.skills && candidate.skills.length > 0 && (
                <div className="mb-4">
                  <p className="text-sm text-gray-600 mb-2">Top Skills</p>
                  <div className="flex flex-wrap gap-1">
                    {candidate.skills.slice(0, 3).map((skill, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded"
                      >
                        {skill.skill_name}
                      </span>
                    ))}
                    {candidate.skills.length > 3 && (
                      <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs font-medium rounded">
                        +{candidate.skills.length - 3} more
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
                  className="flex-1 mr-2 px-3 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors"
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
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
            />
          </svg>
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
              className="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>

            {/* Page Numbers */}
            <div className="flex items-center space-x-1">
              {Array.from({ length: Math.min(5, pagination.total_pages) }, (_, i) => {
                let pageNum;
                if (pagination.total_pages <= 5) {
                  pageNum = i + 1;
                } else if (pagination.current_page <= 3) {
                  pageNum = i + 1;
                } else if (pagination.current_page >= pagination.total_pages - 2) {
                  pageNum = pagination.total_pages - 4 + i;
                } else {
                  pageNum = pagination.current_page - 2 + i;
                }

                return (
                  <button
                    key={pageNum}
                    onClick={() => setCurrentPage(pageNum)}
                    className={`px-3 py-1 text-sm border rounded-md ${
                      pagination.current_page === pageNum
                        ? "bg-indigo-600 text-white border-indigo-600"
                        : "border-gray-300 hover:bg-gray-50"
                    }`}
                  >
                    {pageNum}
                  </button>
                );
              })}
            </div>

            <button
              onClick={() =>
                setCurrentPage((prev) => Math.min(pagination.total_pages, prev + 1))
              }
              disabled={!pagination.has_next_page}
              className="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
