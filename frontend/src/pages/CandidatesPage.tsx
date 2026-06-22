import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useCandidateStore } from "../store/useCandidateStore";
import { useFilterStore } from "../store/filterStore";
import toast from "react-hot-toast";
import { Users, Search, RefreshCw, User, Award, X } from "lucide-react";
import CandidateCard from "../components/candidates/CandidateCard";

type FilterType = "all" | "high-confidence" | "needs-review";
type SortType = "date-added" | "name" | "confidence-score" | "match-score";

export default function CandidatesPage() {
  const [filter, setFilter] = useState<FilterType>("all");
  const [sort, setSort] = useState<SortType>("date-added");
  const [currentPage, setCurrentPage] = useState(1);
  
  const { candidates, pagination, isLoading, fetchCandidates } = useCandidateStore();
  const { searchTerm, company, jobTitle, certification, salaryMin, salaryMax, setSearchTerm, setCompany, setJobTitle, setCertification, resetFilters } = useFilterStore();
  const navigate = useNavigate();

  // Local input state — holds raw typed values before debounce commits them
  const [inputSearchTerm, setInputSearchTerm] = useState(searchTerm || "");
  const [inputCompany, setInputCompany] = useState(company || "");
  const [inputJobTitle, setInputJobTitle] = useState(jobTitle || "");
  const [inputCertification, setInputCertification] = useState(certification || "");

  const debounceTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const isInitialMount = useRef(true);

  const itemsPerPage = 20;

  // Validation helpers
  const validateNameEmailSkill = (val: string) => {
    if (val.length === 0) return null;
    const trimmed = val.trim();
    if (trimmed.length === 0) return "Please enter a valid Name, Email, or Skill.";
    if (trimmed.length > 100) return "Please enter a valid Name, Email, or Skill.";
    if (/^[^a-zA-Z]+$/.test(trimmed)) return "Please enter a valid Name, Email, or Skill.";
    if (!/^[a-zA-Z0-9\s._\-@+]+$/.test(trimmed)) return "Please enter a valid Name, Email, or Skill.";
    return null;
  };

  const validateCompany = (val: string) => {
    if (val.length === 0) return null;
    const trimmed = val.trim();
    if (trimmed.length === 0) return "Please enter a valid Company Name.";
    if (trimmed.length > 100) return "Please enter a valid Company Name.";
    if (/^[^a-zA-Z]+$/.test(trimmed)) return "Please enter a valid Company Name.";
    if (!/^[a-zA-Z0-9\s.,&'-]+$/.test(trimmed)) return "Please enter a valid Company Name.";
    return null;
  };

  const validateJobTitle = (val: string) => {
    if (val.length === 0) return null;
    const trimmed = val.trim();
    if (trimmed.length === 0) return "Please enter a valid Job Title.";
    if (trimmed.length > 100) return "Please enter a valid Job Title.";
    if (/^[^a-zA-Z]+$/.test(trimmed)) return "Please enter a valid Job Title.";
    if (!/^[a-zA-Z0-9\s.\-/+&()]+$/.test(trimmed)) return "Please enter a valid Job Title.";
    return null;
  };

  const validateCertification = (val: string) => {
    if (val.length === 0) return null;
    const trimmed = val.trim();
    if (trimmed.length === 0) return "Please enter a valid Certification Name.";
    if (trimmed.length > 100) return "Please enter a valid Certification Name.";
    if (/^[^a-zA-Z]+$/.test(trimmed)) return "Please enter a valid Certification Name.";
    if (!/^[a-zA-Z0-9\s.\-&/]+$/.test(trimmed)) return "Please enter a valid Certification Name.";
    return null;
  };

  const searchError = validateNameEmailSkill(inputSearchTerm);
  const companyError = validateCompany(inputCompany);
  const jobTitleError = validateJobTitle(inputJobTitle);
  const certError = validateCertification(inputCertification);

  // Debounce: commit local inputs to the filter store 400 ms after the user stops typing
  useEffect(() => {
    if (isInitialMount.current) {
      isInitialMount.current = false;
      return;
    }

    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }

    debounceTimer.current = setTimeout(() => {
      // Only apply filters that are valid
      if (!searchError) setSearchTerm(inputSearchTerm);
      if (!companyError) setCompany(inputCompany);
      if (!jobTitleError) setJobTitle(inputJobTitle);
      if (!certError) setCertification(inputCertification);
      setCurrentPage(1);
    }, 1500);

    return () => {
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current);
      }
    };
  }, [inputSearchTerm, inputCompany, inputJobTitle, inputCertification, searchError, companyError, jobTitleError, certError]);

  // Fetch candidates when committed filter store values or page changes
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

  // Clear all search inputs and filters
  const handleClear = () => {
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }
    setInputSearchTerm("");
    setInputCompany("");
    setInputJobTitle("");
    setInputCertification("");
    resetFilters();
    setCurrentPage(1);
  };

  const hasActiveFilters =
    inputSearchTerm || inputCompany || inputJobTitle || inputCertification;

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

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-purple-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-purple-700 rounded-2xl shadow-lg p-8 mb-6">
          <div className="flex items-center gap-3 mb-2">
            <Users className="w-8 h-8 text-white" />
            <h1 className="text-3xl font-bold text-white">Candidates</h1>
          </div>
          <p className="text-purple-100">
            Manage and review candidate profiles with AI-powered resume parsing insights
          </p>
        </div>

        {/* Search and Filters */}
        <div className="bg-white rounded-2xl shadow-md p-6 mb-6 border border-purple-100">
          <div className="flex flex-col gap-4">
            {/* Search Fields */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Name Search */}
              <div className="relative">
                <div className="relative">
                  <input
                    type="text"
                    placeholder="Search by name, email, or skill..."
                    value={inputSearchTerm}
                    onChange={(e) => setInputSearchTerm(e.target.value)}
                    className={`w-full pl-10 pr-4 py-3 border ${searchError ? 'border-red-500' : 'border-purple-200'} rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 resize-none bg-purple-50/50 focus:bg-white transition-all`}
                  />
                  <Search className="absolute left-3 top-3 h-5 w-5 text-purple-400" />
                </div>
                {searchError && <p className="text-red-500 text-xs mt-1 absolute -bottom-5">{searchError}</p>}
              </div>

              {/* Company Search */}
              <div className="relative">
                <div className="relative">
                  <input
                    type="text"
                    placeholder="Search by company..."
                    value={inputCompany}
                    onChange={(e) => setInputCompany(e.target.value)}
                    className={`w-full pl-10 pr-4 py-3 border ${companyError ? 'border-red-500' : 'border-purple-200'} rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 resize-none bg-purple-50/50 focus:bg-white transition-all`}
                  />
                  <Users className="absolute left-3 top-3 h-5 w-5 text-purple-400" />
                </div>
                {companyError && <p className="text-red-500 text-xs mt-1 absolute -bottom-5">{companyError}</p>}
              </div>

              {/* Job Title Search */}
              <div className="relative">
                <div className="relative">
                  <input
                    type="text"
                    placeholder="Search by job title..."
                    value={inputJobTitle}
                    onChange={(e) => setInputJobTitle(e.target.value)}
                    className={`w-full pl-10 pr-4 py-3 border ${jobTitleError ? 'border-red-500' : 'border-purple-200'} rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 resize-none bg-purple-50/50 focus:bg-white transition-all`}
                  />
                  <User className="absolute left-3 top-3 h-5 w-5 text-purple-400" />
                </div>
                {jobTitleError && <p className="text-red-500 text-xs mt-1 absolute -bottom-5">{jobTitleError}</p>}
              </div>

              {/* Certification Search */}
              <div className="relative mb-2">
                <div className="relative">
                  <input
                    type="text"
                    placeholder="Search by certification..."
                    value={inputCertification}
                    onChange={(e) => setInputCertification(e.target.value)}
                    className={`w-full pl-10 pr-4 py-3 border ${certError ? 'border-red-500' : 'border-purple-200'} rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 resize-none bg-purple-50/50 focus:bg-white transition-all`}
                  />
                  <Award className="absolute left-3 top-3 h-5 w-5 text-purple-400" />
                </div>
                {certError && <p className="text-red-500 text-xs mt-1 absolute -bottom-5">{certError}</p>}
              </div>
            </div>

            {/* Filter Buttons and Sort */}
            <div className="flex flex-col lg:flex-row gap-4">
              {/* Filter Buttons */}
              <div className="flex gap-2">
                <button
                  onClick={() => setFilter("all")}
                  className={`px-6 py-2.5 rounded-xl font-medium transition-all ${filter === "all"
                      ? "bg-gradient-to-r from-purple-600 to-purple-700 text-white shadow-lg hover:shadow-xl"
                      : "bg-purple-50 text-purple-700 hover:bg-purple-100 border border-purple-200"
                    }`}
                >
                  All ({pagination?.total_items || candidates.length})
                </button>
                <button
                  onClick={() => setFilter("high-confidence")}
                  className={`px-6 py-2.5 rounded-xl font-medium transition-all ${filter === "high-confidence"
                      ? "bg-gradient-to-r from-purple-600 to-purple-700 text-white shadow-lg hover:shadow-xl"
                      : "bg-purple-50 text-purple-700 hover:bg-purple-100 border border-purple-200"
                    }`}
                >
                  High Confidence
                </button>
                <button
                  onClick={() => setFilter("needs-review")}
                  className={`px-6 py-2.5 rounded-xl font-medium transition-all ${filter === "needs-review"
                      ? "bg-gradient-to-r from-purple-600 to-purple-700 text-white shadow-lg hover:shadow-xl"
                      : "bg-purple-50 text-purple-700 hover:bg-purple-100 border border-purple-200"
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
                className="px-4 py-3 border border-purple-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 bg-purple-50/50 focus:bg-white transition-all"
              >
                <option value="date-added">Date Added</option>
                <option value="name">Name</option>
                <option value="confidence-score">Confidence Score</option>
                <option value="match-score">Match Score</option>
              </select>
            </div>

            {/* Clear Button */}
            {hasActiveFilters && (
              <div className="flex justify-end">
                <button
                  onClick={handleClear}
                  className="flex items-center gap-2 px-4 py-2 text-sm text-purple-700 bg-purple-50 hover:bg-purple-100 rounded-xl transition-all border border-purple-200"
                >
                  <X className="w-4 h-4" />
                  Clear Filters
                </button>
              </div>
            )}
          </div>
        </div>


        {/* Results Count */}
        <div className="mb-6 flex items-center justify-between">
          <p className="text-sm text-purple-700 font-medium">
            Showing {paginatedCandidates.length} of {pagination?.total_items || filteredCandidates.length}{" "}
            candidates
            {pagination && ` (Page ${pagination.current_page} of ${pagination.total_pages})`}
          </p>
          <button
            onClick={loadCandidates}
            disabled={isLoading}
            className="text-sm text-purple-600 hover:text-purple-700 disabled:opacity-50 flex items-center gap-2 font-medium px-4 py-2 rounded-lg hover:bg-purple-50 transition-all"
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
              <CandidateCard
                key={candidate.id}
                candidate={candidate as any}
                onViewProfile={(id) => navigate(`/candidates/${id}`)}
              />
            ))}
          </div>
        ) : (
          <div className="bg-gradient-to-br from-purple-50 to-white rounded-2xl shadow-md p-12 text-center border border-purple-100">
            <Users className="mx-auto h-12 w-12 text-purple-400" />
            <h3 className="mt-2 text-sm font-medium text-purple-900">
              No candidates found
            </h3>
            <p className="mt-1 text-sm text-purple-600">
              {searchTerm
                ? "Try adjusting your search terms"
                : "Get started by uploading some resumes"}
            </p>
          </div>
        )}

        {/* Pagination */}
        {pagination && pagination.total_pages > 1 && (
          <div className="flex items-center justify-between mt-6 bg-white rounded-2xl shadow-md p-4 border border-purple-100">
            <div className="text-sm text-purple-700 font-medium">
              Page {pagination.current_page} of {pagination.total_pages}
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
                disabled={!pagination.has_prev_page}
                className="px-4 py-2 text-sm border border-purple-200 text-purple-700 rounded-xl hover:bg-purple-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
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
                    className={`px-4 py-2 text-sm rounded-xl transition-all ${pageNum === pagination.current_page
                        ? "bg-gradient-to-r from-purple-600 to-purple-700 text-white shadow-md hover:shadow-lg"
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
                className="px-4 py-2 text-sm border border-purple-200 text-purple-700 rounded-xl hover:bg-purple-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
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
