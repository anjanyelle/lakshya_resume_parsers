import { useState } from "react";
import axios from "axios";
import { FileText, Sparkles, AlertCircle, CheckCircle2 } from "lucide-react";

export default function ModelTestPage() {
  const [experienceText, setExperienceText] = useState("");
  const [educationText, setEducationText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);

  const handleTest = async () => {
    if (!experienceText.trim() && !educationText.trim()) {
      setError("Please enter experience or education text to test");
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      // Call AI service directly (runs on port 8000)
      const response = await axios.post(
        "http://localhost:8000/test-ner-postprocessor",
        {
          model: "own-model",
          experience_text: experienceText,
          education_text: educationText
        },
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      setResult(response.data);
    } catch (err: any) {
      console.error("Error testing model:", err);
      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else if (err.code === "ERR_NETWORK") {
        setError("Unable to connect to AI service. Please check if the AI service is running on port 8000.");
      } else {
        setError("Failed to test model. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center gap-3 mb-2">
            <Sparkles className="w-6 h-6 text-purple-600" />
            <h1 className="text-2xl font-bold text-gray-900">NER Post-Processor Test</h1>
          </div>
          <p className="text-gray-600">
            Test the production-grade NER post-processing pipeline with your resume text
          </p>
        </div>

        {/* Input Section */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Work Experience Text
              </label>
              <textarea
                value={experienceText}
                onChange={(e) => setExperienceText(e.target.value)}
                placeholder="Paste work experience text here...&#10;&#10;Example:&#10;Senior Data Engineer&#10;Infosys - Jan 2021 to Mar 2023 - Hyderabad&#10;Google (Client)"
                className="w-full h-48 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none font-mono text-sm"
              />
              <span className="text-sm text-gray-500 mt-1 block">
                {experienceText.length} characters
              </span>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Education Text
              </label>
              <textarea
                value={educationText}
                onChange={(e) => setEducationText(e.target.value)}
                placeholder="Paste education text here...&#10;&#10;Example:&#10;B.Tech Computer Science&#10;JNTU Hyderabad, 2015-2019, Grade 8.2"
                className="w-full h-48 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none font-mono text-sm"
              />
              <span className="text-sm text-gray-500 mt-1 block">
                {educationText.length} characters
              </span>
            </div>
          </div>
          <div className="mt-4 flex justify-end">
            <button
              onClick={handleTest}
              disabled={isLoading || (!experienceText.trim() && !educationText.trim())}
              className="px-6 py-2.5 bg-purple-600 text-white rounded-xl hover:bg-purple-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isLoading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <FileText className="w-4 h-4" />
                  Test NER Post-Processor
                </>
              )}
            </button>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Results Section */}
        {result && (
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center gap-3 mb-4">
              <CheckCircle2 className="w-5 h-5 text-green-600" />
              <h2 className="text-lg font-semibold text-gray-900">NER Post-Processor Results</h2>
            </div>

            {/* Statistics */}
            {result.statistics && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <h3 className="text-sm font-semibold text-blue-800 mb-2">Processing Statistics</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="text-blue-700">Raw Entities:</span>
                    <span className="ml-2 font-semibold text-blue-900">{result.statistics.total_raw_entities}</span>
                  </div>
                  <div>
                    <span className="text-blue-700">Validated:</span>
                    <span className="ml-2 font-semibold text-blue-900">{result.statistics.total_validated_entities}</span>
                  </div>
                  <div>
                    <span className="text-blue-700">Filtering Rate:</span>
                    <span className="ml-2 font-semibold text-blue-900">{result.statistics.filtering_rate?.toFixed(1)}%</span>
                  </div>
                  <div>
                    <span className="text-blue-700">Processing Time:</span>
                    <span className="ml-2 font-semibold text-blue-900">{result.processing_time_ms?.toFixed(0)}ms</span>
                  </div>
                </div>
              </div>
            )}

            {/* Validated Entities */}
            {result.validated_entities && (
              <div className="mb-6">
                <h3 className="text-md font-semibold text-gray-800 mb-3">Validated Entities</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {result.validated_entities.companies && result.validated_entities.companies.length > 0 && (
                    <div className="border border-gray-200 rounded-lg p-3 bg-gray-50">
                      <span className="font-medium text-gray-700 text-sm">Companies:</span>
                      <div className="mt-1 text-sm text-gray-900">
                        {result.validated_entities.companies.join(', ')}
                      </div>
                    </div>
                  )}
                  {result.validated_entities.roles && result.validated_entities.roles.length > 0 && (
                    <div className="border border-gray-200 rounded-lg p-3 bg-gray-50">
                      <span className="font-medium text-gray-700 text-sm">Roles:</span>
                      <div className="mt-1 text-sm text-gray-900">
                        {result.validated_entities.roles.join(', ')}
                      </div>
                    </div>
                  )}
                  {result.validated_entities.clients && result.validated_entities.clients.length > 0 && (
                    <div className="border border-gray-200 rounded-lg p-3 bg-gray-50">
                      <span className="font-medium text-gray-700 text-sm">Clients:</span>
                      <div className="mt-1 text-sm text-gray-900">
                        {result.validated_entities.clients.join(', ')}
                      </div>
                    </div>
                  )}
                  {result.validated_entities.locations && result.validated_entities.locations.length > 0 && (
                    <div className="border border-gray-200 rounded-lg p-3 bg-gray-50">
                      <span className="font-medium text-gray-700 text-sm">Locations:</span>
                      <div className="mt-1 text-sm text-gray-900">
                        {result.validated_entities.locations.join(', ')}
                      </div>
                    </div>
                  )}
                  {result.validated_entities.degrees && result.validated_entities.degrees.length > 0 && (
                    <div className="border border-gray-200 rounded-lg p-3 bg-gray-50">
                      <span className="font-medium text-gray-700 text-sm">Degrees:</span>
                      <div className="mt-1 text-sm text-gray-900">
                        {result.validated_entities.degrees.join(', ')}
                      </div>
                    </div>
                  )}
                  {result.validated_entities.institutions && result.validated_entities.institutions.length > 0 && (
                    <div className="border border-gray-200 rounded-lg p-3 bg-gray-50">
                      <span className="font-medium text-gray-700 text-sm">Institutions:</span>
                      <div className="mt-1 text-sm text-gray-900">
                        {result.validated_entities.institutions.join(', ')}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Work Experience Results */}
            {result.work_experience && result.work_experience.length > 0 && (
              <div className="mb-6">
                <h3 className="text-md font-semibold text-gray-800 mb-3">
                  Structured Work Experience ({result.work_experience.length} entries)
                </h3>
                <div className="space-y-4">
                  {result.work_experience.map((exp: any, idx: number) => (
                    <div key={idx} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                      <div className="grid grid-cols-2 gap-3 text-sm">
                        {exp.job_title && (
                          <div>
                            <span className="font-medium text-gray-700">Job Title:</span>
                            <span className="ml-2 text-gray-900">{exp.job_title}</span>
                          </div>
                        )}
                        {exp.company_name && (
                          <div>
                            <span className="font-medium text-gray-700">Company:</span>
                            <span className="ml-2 text-gray-900">{exp.company_name}</span>
                          </div>
                        )}
                        {exp.client && (
                          <div>
                            <span className="font-medium text-gray-700">Client:</span>
                            <span className="ml-2 text-gray-900">{exp.client}</span>
                          </div>
                        )}
                        {exp.location && (
                          <div>
                            <span className="font-medium text-gray-700">Location:</span>
                            <span className="ml-2 text-gray-900">{exp.location}</span>
                          </div>
                        )}
                        {exp.start_date && (
                          <div>
                            <span className="font-medium text-gray-700">Start Date:</span>
                            <span className="ml-2 text-gray-900">{exp.start_date}</span>
                          </div>
                        )}
                        {exp.end_date && (
                          <div>
                            <span className="font-medium text-gray-700">End Date:</span>
                            <span className="ml-2 text-gray-900">{exp.end_date}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Education Results */}
            {result.education && result.education.length > 0 && (
              <div className="mb-6">
                <h3 className="text-md font-semibold text-gray-800 mb-3">
                  Structured Education ({result.education.length} entries)
                </h3>
                <div className="space-y-4">
                  {result.education.map((edu: any, idx: number) => (
                    <div key={idx} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                      <div className="grid grid-cols-2 gap-3 text-sm">
                        {edu.degree && (
                          <div>
                            <span className="font-medium text-gray-700">Degree:</span>
                            <span className="ml-2 text-gray-900">{edu.degree}</span>
                          </div>
                        )}
                        {edu.institution && (
                          <div>
                            <span className="font-medium text-gray-700">Institution:</span>
                            <span className="ml-2 text-gray-900">{edu.institution}</span>
                          </div>
                        )}
                        {edu.field_of_study && (
                          <div>
                            <span className="font-medium text-gray-700">Field:</span>
                            <span className="ml-2 text-gray-900">{edu.field_of_study}</span>
                          </div>
                        )}
                        {edu.start_year && (
                          <div>
                            <span className="font-medium text-gray-700">Start Year:</span>
                            <span className="ml-2 text-gray-900">{edu.start_year}</span>
                          </div>
                        )}
                        {edu.end_year && (
                          <div>
                            <span className="font-medium text-gray-700">End Year:</span>
                            <span className="ml-2 text-gray-900">{edu.end_year}</span>
                          </div>
                        )}
                        {edu.gpa && (
                          <div>
                            <span className="font-medium text-gray-700">GPA:</span>
                            <span className="ml-2 text-gray-900">{edu.gpa}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Raw Entities (for debugging) */}
            {result.raw_entities && result.raw_entities.raw_predictions && (
              <div className="mb-6">
                <details className="border border-gray-200 rounded-lg">
                  <summary className="px-4 py-3 bg-gray-50 cursor-pointer text-sm font-medium text-gray-700">
                    Show Raw Entities (Debug)
                  </summary>
                  <div className="p-4 bg-gray-100">
                    <pre className="text-xs text-gray-800 overflow-x-auto">
                      {JSON.stringify(result.raw_entities.raw_predictions, null, 2)}
                    </pre>
                  </div>
                </details>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
