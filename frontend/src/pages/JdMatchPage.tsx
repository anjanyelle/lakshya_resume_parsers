import { useState, useEffect } from "react";
import { Loader2, Briefcase, CheckCircle2, AlertCircle, XCircle } from "lucide-react";
import { apiRequest } from "../services/api";

export default function JdMatchPage() {
  const [jdText, setJdText] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState("");
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState("");

  const handleParseAndMatch = async () => {
    if (!jdText.trim()) return;
    
    setLoading(true);
    setError("");
    
    // Simulate the sequence of messages requested by the user
    const messages = [
      "Parsing Job Description...",
      "Extracting Requirements...",
      "Searching Candidates...",
      "Ranking Candidates..."
    ];
    
    let messageIndex = 0;
    setLoadingMessage(messages[0]);
    
    const interval = setInterval(() => {
      messageIndex++;
      if (messageIndex < messages.length) {
        setLoadingMessage(messages[messageIndex]);
      }
    }, 1500);

    try {
      const response = await apiRequest.post("/jd/match", { jobDescription: jdText });
      const data = response.data;
      clearInterval(interval);
      
      if (!data.success) {
        throw new Error(data.message || "Failed to parse and match JD.");
      }
      
      setResults(data);
    } catch (err: any) {
      clearInterval(interval);
      setError(err.message || "An unexpected error occurred.");
    } finally {
      setLoading(false);
      setLoadingMessage("");
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-emerald-700 bg-emerald-50 ring-emerald-600/20";
    if (score >= 60) return "text-amber-700 bg-amber-50 ring-amber-600/20";
    return "text-red-700 bg-red-50 ring-red-600/10";
  };

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Briefcase className="h-6 w-6 text-blue-600" />
          Job Description Match
        </h1>
        <p className="mt-2 text-sm text-gray-600">
          Paste a complete Job Description to instantly find, analyze, and rank the best candidates in your database.
        </p>
      </div>

      {!results && !loading && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-6">
            <label htmlFor="jdText" className="block text-sm font-medium text-gray-900 mb-2">
              Job Description
            </label>
            <textarea
              id="jdText"
              className="block w-full rounded-lg border border-gray-300 py-3 px-4 text-gray-900 focus:border-blue-500 focus:ring-blue-500 sm:text-sm transition-colors duration-200"
              style={{ height: "300px" }}
              placeholder="Paste complete Job Description here..."
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
            />
            
            {error && (
              <div className="mt-4 p-4 rounded-lg bg-red-50 text-red-700 flex items-center gap-2">
                <AlertCircle className="h-5 w-5" />
                <p className="text-sm font-medium">{error}</p>
              </div>
            )}

            <div className="mt-6">
              <button
                onClick={handleParseAndMatch}
                disabled={!jdText.trim()}
                className="inline-flex items-center justify-center rounded-lg bg-blue-600 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                Parse JD & Match Candidates
              </button>
            </div>
          </div>
        </div>
      )}

      {loading && (
        <div className="flex flex-col items-center justify-center py-20 bg-white rounded-xl shadow-sm border border-gray-200">
          <Loader2 className="h-12 w-12 text-blue-600 animate-spin mb-6" />
          <h3 className="text-lg font-medium text-gray-900">{loadingMessage}</h3>
          <p className="mt-2 text-sm text-gray-500">This may take a few moments as we run our 8-dimension matching engine.</p>
        </div>
      )}

      {results && !loading && (
        <div className="space-y-6">
          {/* Header Actions */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
                Results for: <span className="text-blue-600">{results.parsedJob?.title || "Unknown Job Role"}</span>
              </h2>
              <div className="mt-1 flex items-center gap-4 text-sm text-gray-500">
                <span className="flex items-center gap-1"><Briefcase className="h-4 w-4"/> {results.parsedJob?.domain || "Any Domain"}</span>
                <span>•</span>
                <span>Experience: {results.parsedJob?.min_experience_years || 0}{results.parsedJob?.max_experience_years ? `-${results.parsedJob?.max_experience_years}` : '+'} years</span>
              </div>
            </div>
            
            <button
              onClick={() => {
                setResults(null);
                setJdText("");
              }}
              className="inline-flex items-center justify-center rounded-lg bg-white px-4 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 transition-all"
            >
              Start New Match
            </button>
          </div>
          
          {/* Filters Bar */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 flex flex-wrap items-center gap-4">
            <span className="text-sm font-medium text-gray-700">Filters applied:</span>
            <span className="inline-flex items-center gap-x-1.5 rounded-md px-2 py-1 text-xs font-medium text-gray-900 ring-1 ring-inset ring-gray-200 bg-gray-50">
              <CheckCircle2 className="h-3.5 w-3.5 text-blue-500" />
              Score &gt; 0%
            </span>
            <span className="inline-flex items-center gap-x-1.5 rounded-md px-2 py-1 text-xs font-medium text-gray-900 ring-1 ring-inset ring-gray-200 bg-gray-50">
              <CheckCircle2 className="h-3.5 w-3.5 text-blue-500" />
              Exp &ge; {results.parsedJob?.min_experience_years || 0} years
            </span>
          </div>

          {/* DataGrid */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">#</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Candidate Name</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Current Job Title</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total Experience</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Match Score</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-64">Matched Skills</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-64">Missing Skills</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Domain</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Action</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {results.matches && results.matches.length > 0 ? (
                    results.matches.map((match: any, index: number) => (
                      <tr key={match.candidate_id} className="hover:bg-slate-50 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {index + 1}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">{match.candidate_name}</div>
                          <div className="text-xs text-gray-500">{match.candidate_email}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {match.candidate_title || "Unknown"}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {match.candidate_experience ? `${match.candidate_experience.toFixed(1)} years` : 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ${getScoreColor(match.overall_score)}`}>
                            {match.overall_score.toFixed(1)}%
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex flex-wrap gap-1">
                            {match.matching_skills?.slice(0, 4).map((skill: string) => (
                              <span key={skill} className="inline-flex items-center rounded-md bg-blue-50 px-1.5 py-0.5 text-xs font-medium text-blue-700 ring-1 ring-inset ring-blue-700/10">
                                {skill}
                              </span>
                            ))}
                            {match.matching_skills?.length > 4 && (
                              <span className="inline-flex items-center rounded-md bg-gray-50 px-1.5 py-0.5 text-xs font-medium text-gray-600 ring-1 ring-inset ring-gray-500/10">
                                +{match.matching_skills.length - 4}
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex flex-wrap gap-1">
                            {match.missing_skills?.slice(0, 4).map((skill: string) => (
                              <span key={skill} className="inline-flex items-center rounded-md bg-red-50 px-1.5 py-0.5 text-xs font-medium text-red-700 ring-1 ring-inset ring-red-600/10">
                                {skill}
                              </span>
                            ))}
                            {match.missing_skills?.length > 4 && (
                              <span className="inline-flex items-center rounded-md bg-gray-50 px-1.5 py-0.5 text-xs font-medium text-gray-600 ring-1 ring-inset ring-gray-500/10">
                                +{match.missing_skills.length - 4}
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {match.candidate_domain || "Any"}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <a 
                            href={`/candidates/${match.candidate_id}`} 
                            target="_blank" 
                            rel="noreferrer"
                            className="inline-flex items-center justify-center rounded bg-white px-2.5 py-1.5 text-xs font-semibold text-blue-600 shadow-sm ring-1 ring-inset ring-blue-300 hover:bg-blue-50"
                          >
                            View Profile
                          </a>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={8} className="px-6 py-12 text-center">
                        <XCircle className="mx-auto h-8 w-8 text-gray-400 mb-3" />
                        <h3 className="text-sm font-medium text-gray-900">No candidates found</h3>
                        <p className="mt-1 text-sm text-gray-500">We couldn't find any candidates matching this job description.</p>
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
