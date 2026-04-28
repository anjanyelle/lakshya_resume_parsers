import { useState, useCallback, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useDropzone } from "react-dropzone";
import { useCandidateStore } from "../store/useCandidateStore";
import { useAuthStore } from "../store/useAuthStore";
import {
  connectSocket,
  subscribeToParsingProgress,
  subscribeToParsingComplete,
  subscribeToParsingFailed,
} from "../services/socket";
import { FileUp, Search, Layers, Zap, Info, ChevronDown } from "lucide-react";
import toast from "react-hot-toast";
import axios from "axios";
import ParsedDataDebugView from "../components/upload/ParsedDataDebugView";
import SpeedGauge from "../components/upload/SpeedGauge";
import ParsedResultCard from "../components/upload/ParsedResultCard";
import ModelResultsView from "../components/upload/ModelResultsView";

interface LLMModel {
  id: string;
  name: string;
  badge: string;
  inputPrice: string;
  outputPrice: string;
}

interface UploadFile {
  file: File;
  id: string;
  status: "pending" | "uploading" | "parsing" | "completed" | "error";
  progress: number;
  message: string;
  candidateId?: string;
  result?: any;
  error?: string;
  sections?: SectionData;
}

interface SectionData {
  experience?: {
    text: string;
    char_count: number;
  };
  education?: {
    text: string;
    char_count: number;
  };
}

interface ParsedSectionsResponse {
  status: string;
  work_experience: Array<any>;
  education: Array<any>;
  processing_time_ms: number;
  message: string;
}

const LLM_MODELS: LLMModel[] = [
  {
    id: "own-model",
    name: "Our Own Model",
    badge: "Default",
    inputPrice: "Free",
    outputPrice: "Free",
  },
  {
    id: "gemini-2.0-flash-lite",
    name: "Gemini 2.0 Flash-Lite",
    badge: "Cheapest",
    inputPrice: "$0.075",
    outputPrice: "$0.30",
  },
  {
    id: "deepseek-v3",
    name: "DeepSeek V3.2",
    badge: "Best value",
    inputPrice: "$0.14",
    outputPrice: "$0.28",
  },
  {
    id: "claude-haiku-4-5",
    name: "Claude Haiku 4.5",
    badge: "Reliable",
    inputPrice: "$1.00",
    outputPrice: "$5.00",
  },
  {
    id: "gpt-4o-mini",
    name: "GPT-4o Mini",
    badge: "Fallback",
    inputPrice: "$0.15",
    outputPrice: "$0.60",
  },
];

export default function UploadPage() {
  const [uploadFiles, setUploadFiles] = useState<UploadFile[]>([]);
  const [isBulkMode, setIsBulkMode] = useState(false);
  const [currentUpload, setCurrentUpload] = useState<UploadFile | null>(null);
  const [selectedLLM, setSelectedLLM] = useState<string>("own-model");
  const [showLLMDropdown, setShowLLMDropdown] = useState(false);
  const [extractedSections, setExtractedSections] = useState<SectionData | null>(null);
  const [isExtractingSections, setIsExtractingSections] = useState(false);
  const [parsedSections, setParsedSections] = useState<ParsedSectionsResponse | null>(null);
  const [isParsingModel, setIsParsingModel] = useState(false);

  const { uploadResume } = useCandidateStore();
  const { token } = useAuthStore();
  const navigate = useNavigate();

  // Socket.io connection
  useEffect(() => {
    connectSocket();

    // Subscribe to parsing events
    const handleProgress = (data: {
      candidateId: string;
      progress: number;
      message: string;
    }) => {
      setUploadFiles((prev) =>
        prev.map((uploadFile) => {
          if (uploadFile.candidateId === data.candidateId) {
            return {
              ...uploadFile,
              progress: data.progress,
              message: data.message,
              status: data.progress === 100 ? "completed" : "parsing",
            };
          }
          return uploadFile;
        }),
      );

      setCurrentUpload((prev) => {
        if (prev?.candidateId === data.candidateId) {
          return {
            ...prev,
            progress: data.progress,
            message: data.message,
            status: data.progress === 100 ? "completed" : "parsing",
          };
        }
        return prev;
      });
    };

    const handleComplete = (data: { candidateId: string; data: any }) => {
      setUploadFiles((prev) =>
        prev.map((uploadFile) => {
          if (uploadFile.candidateId === data.candidateId) {
            return {
              ...uploadFile,
              status: "completed",
              progress: 100,
              message: "Complete!",
              result: data.data,
            };
          }
          return uploadFile;
        }),
      );

      setCurrentUpload((prev) => {
        if (prev?.candidateId === data.candidateId) {
          return {
            ...prev,
            status: "completed",
            progress: 100,
            message: "Complete!",
            result: data.data,
          };
        }
        return prev;
      });

      toast.success("Resume parsing completed!");
    };

    const handleFailed = (data: { candidateId: string; error: string }) => {
      setUploadFiles((prev) =>
        prev.map((uploadFile) => {
          if (uploadFile.candidateId === data.candidateId) {
            return {
              ...uploadFile,
              status: "error",
              message: "Failed",
              error: data.error,
            };
          }
          return uploadFile;
        }),
      );

      setCurrentUpload((prev) => {
        if (prev?.candidateId === data.candidateId) {
          return {
            ...prev,
            status: "error",
            message: "Failed",
            error: data.error,
          };
        }
        return prev;
      });

      toast.error("Resume parsing failed");
    };

    subscribeToParsingProgress(handleProgress);
    subscribeToParsingComplete(handleComplete);
    subscribeToParsingFailed(handleFailed);

    return () => {
      // Cleanup subscriptions
    };
  }, []);

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      const newFiles: UploadFile[] = acceptedFiles.map((file) => ({
        file,
        id: Math.random().toString(36).substr(2, 9),
        status: "pending" as const,
        progress: 0,
        message: "Ready to upload",
      }));

      if (isBulkMode) {
        setUploadFiles((prev) => [...prev, ...newFiles]);
      } else {
        setUploadFiles(newFiles.slice(0, 1)); // Single file mode
      }
    },
    [isBulkMode],
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        [".docx"],
      "text/plain": [".txt"],
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: isBulkMode,
  });

  const extractSections = async (file: File): Promise<SectionData | null> => {
    try {
      const formData = new FormData();
      formData.append("file", file);

      const baseUrl = import.meta.env.VITE_API_URL || "http://localhost:3001";
      const response = await axios.post(
        `${baseUrl}/api/v1/upload`,
        formData,
        {
          headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "multipart/form-data",
          },
        }
      );

      // Python backend returns different structure
      const sections: SectionData = {};
      if (response.data.jobs?.[0]?.parsed_data?.work_experience) {
        sections.experience = JSON.stringify(response.data.jobs[0].parsed_data.work_experience, null, 2);
      }
      if (response.data.jobs?.[0]?.parsed_data?.education) {
        sections.education = JSON.stringify(response.data.jobs[0].parsed_data.education, null, 2);
      }

      return sections;
    } catch (error) {
      console.error("Error extracting sections:", error);
      return null;
    }
  };

  const handleUpload = async (uploadFile: UploadFile) => {
    try {
      // Update status to uploading
      setUploadFiles((prev) =>
        prev.map((f) =>
          f.id === uploadFile.id
            ? {
              ...f,
              status: "uploading",
              message: "Uploading...",
              progress: 0,
            }
            : f,
        ),
      );

      if (!isBulkMode) {
        setCurrentUpload({
          ...uploadFile,
          status: "uploading",
          message: "Uploading...",
          progress: 0,
        });
      }

      // Extract sections first - STOP HERE, don't upload yet
      setIsExtractingSections(true);
      const sections = await extractSections(uploadFile.file);
      setExtractedSections(sections);
      setIsExtractingSections(false);

      // Check if candidate was returned successfully
      if (!candidate || !candidate.id) {
        throw new Error("Invalid response from server");
      }

      // Update with candidate ID
      setUploadFiles((prev) =>
        prev.map((f) =>
          f.id === uploadFile.id
            ? {
              ...f,
              candidateId: candidate.id,
              status: "parsing",
              message: "Extracting text...",
              progress: 25,
            }
            : f,
        ),
      );

      if (!isBulkMode) {
        setCurrentUpload((prev) =>
          prev
            ? {
              ...prev,
              candidateId: candidate.id,
              status: "parsing",
              message: "Extracting text...",
              progress: 25,
            }
            : null,
        );
      }
    } catch (error: any) {
      const errorMessage = error.message || "Upload failed";

      setUploadFiles((prev) =>
        prev.map((f) =>
          f.id === uploadFile.id
            ? { ...f, status: "error", message: "Failed", error: errorMessage }
            : f,
        ),
      );

      if (!isBulkMode) {
        setCurrentUpload((prev) =>
          prev
            ? {
              ...prev,
              status: "error",
              message: "Failed",
              error: errorMessage,
            }
            : null,
        );
      }

      toast.error(errorMessage);
    }
  };

  const handleBulkUpload = async () => {
    const pendingFiles = uploadFiles.filter((f) => f.status === "pending");

    for (const file of pendingFiles) {
      await handleUpload(file);
      // Add small delay between uploads to avoid overwhelming the server
      await new Promise((resolve) => setTimeout(resolve, 500));
    }
  };

  const parseExtractedSections = async () => {
    if (!extractedSections) {
      toast.error("No sections extracted yet");
      return;
    }

    setIsParsingModel(true);
    setParsedSections(null);

    try {
      const aiServiceUrl = "http://localhost:8000";
      const response = await axios.post<ParsedSectionsResponse>(
        `${aiServiceUrl}/parse-sections`,
        {
          experience_text: extractedSections.experience?.text || "",
          education_text: extractedSections.education?.text || "",
        }
      );

      setParsedSections(response.data);
      toast.success("Sections parsed successfully!");
    } catch (error: any) {
      console.error("Error parsing sections:", error);
      if (error.response?.data?.detail) {
        toast.error(error.response.data.detail);
      } else if (error.code === "ERR_NETWORK") {
        toast.error("Unable to connect to AI service on port 8000");
      } else {
        toast.error("Failed to parse sections");
      }
    } finally {
      setIsParsingModel(false);
    }
  };

  const resetUpload = () => {
    setUploadFiles([]);
    setCurrentUpload(null);
    setExtractedSections(null);
    setParsedSections(null);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return "text-green-600 bg-green-100";
    if (score >= 0.6) return "text-yellow-600 bg-yellow-100";
    return "text-red-600 bg-red-100";
  };

  return (
    <div className="min-h-screen bg-slate-50/50">
      <div className="p-8 max-w-[1400px] mx-auto">
        {/* Page Header */}
        <div className="flex items-center gap-4 mb-10">
          <div className="p-2.5 rounded-xl shadow-sm text-white flex-shrink-0" style={{ background: 'linear-gradient(135deg, #7C3AED 0%, #9333EA 100%)' }}>
            <FileUp className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-800 tracking-tight">Resume Intelligence</h1>
            <p className="text-slate-500 text-sm font-medium">Configure and process resumes with precision</p>
          </div>
        </div>

        {/* Main Grid: Left (Upload) | Right (Settings Stack) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">

          {/* Left Column: Resume Upload Area */}
          <div className="lg:col-span-8">
            {!currentUpload && uploadFiles.length === 0 ? (
              <div className="bg-white rounded-[32px] border-2 border-dashed border-slate-200 p-16 transition-all duration-300 shadow-sm group interactive-box">
                <div
                  {...getRootProps()}
                  className={`text-center cursor-pointer transition-all duration-300 ${isDragActive ? "scale-[1.02]" : "hover:scale-[1.01]"}`}
                >
                  <input {...getInputProps()} />
                  <div className="mx-auto w-20 h-20 shadow-xl shadow-purple-50 flex items-center justify-center rounded-[24px] text-white mb-8 transition-transform group-hover:rotate-6" style={{ background: 'linear-gradient(135deg, #7C3AED, #9333EA)' }}>
                    <FileUp className="h-10 w-10" />
                  </div>
                  <h3 className="text-xl font-bold text-slate-800 mb-2">
                    Upload Resume Files
                  </h3>
                  <p className="text-slate-500 text-sm mb-8 max-w-xs mx-auto">
                    Drag & drop your resumes here, or click to browse. Supports PDF, DOCX, and TXT.
                  </p>
                  <button className="px-8 py-3.5 text-white text-xs font-bold rounded-xl shadow-lg shadow-purple-50 transition-all duration-200 uppercase tracking-wider" style={{ background: 'linear-gradient(135deg, #7C3AED, #9333EA)' }}>
                    Choose Files
                  </button>
                </div>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Single File Actions */}
                {!isBulkMode && uploadFiles.length > 0 && !currentUpload && (
                  <div className="bg-white rounded-3xl shadow-sm border border-slate-100 p-8 flex flex-col md:flex-row items-center justify-between gap-6 hover:border-purple-600 transition-colors">
                    <div className="flex items-center gap-6">
                      <div className="h-14 w-14 bg-slate-50 rounded-2xl flex items-center justify-center border border-slate-100">
                        <FileUp className="w-6 h-6 text-purple-600" />
                      </div>
                      <div>
                        <h3 className="text-lg font-bold text-slate-800 tracking-tight">{uploadFiles[0].file.name}</h3>
                        <p className="text-slate-400 font-medium text-xs uppercase tracking-wider">{formatFileSize(uploadFiles[0].file.size)}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <button
                        onClick={() => handleUpload(uploadFiles[0])}
                        className="px-8 py-3.5 text-white text-xs font-bold rounded-xl shadow-lg shadow-purple-50 transition-all uppercase tracking-wider"
                        style={{ background: 'linear-gradient(135deg, #7C3AED, #9333EA)' }}
                      >
                        Analyze
                      </button>
                      <button
                        onClick={resetUpload}
                        className="px-8 py-3.5 bg-slate-100 text-slate-500 text-xs font-bold rounded-xl hover:bg-slate-200 transition-all uppercase tracking-wider"
                      >
                        Discard
                      </button>
                    </div>
                  </div>
                )}

                {/* Processing State */}
                {currentUpload && !isBulkMode && (
                  <div className="space-y-6">
                    {(currentUpload.status === "uploading" || currentUpload.status === "parsing" || currentUpload.status === "error") && (
                      <div className="bg-white rounded-3xl shadow-sm border border-slate-100 p-8 transition-colors interactive-box">
                        <div className="flex items-center gap-5 mb-8">
                          <div className="h-14 w-14 bg-purple-50 rounded-2xl flex items-center justify-center border border-purple-100">
                            <Layers className="w-6 h-6 text-purple-600" />
                          </div>
                          <div>
                            <h3 className="text-lg font-bold text-slate-800 tracking-tight">Processing Pipeline</h3>
                            <p className="text-slate-400 font-medium text-xs uppercase tracking-wider">{currentUpload.file.name}</p>
                          </div>
                        </div>

                        <div className="mb-8">
                          <div className="flex items-center justify-between mb-3">
                            <span className="text-xs font-bold text-slate-600 uppercase tracking-wider">{currentUpload.message}</span>
                            <span className="text-sm font-bold text-purple-600">{currentUpload.progress}%</span>
                          </div>
                          <div className="w-full bg-slate-100 rounded-full h-3 p-1">
                            <div
                              className="h-1 rounded-full transition-all duration-500"
                              style={{ width: `${currentUpload.progress}%`, background: 'linear-gradient(90deg, #7C3AED, #9333EA)' }}
                            />
                          </div>
                        </div>

                        {currentUpload.status === "error" && (
                          <div className="p-4 bg-red-50 border border-red-100 rounded-xl flex items-center gap-3">
                            <X className="w-5 h-5 text-red-600" />
                            <p className="text-red-900 font-medium text-xs">{currentUpload.error}</p>
                          </div>
                        )}
                      </div>
                    )}

                    {currentUpload.status === "completed" && currentUpload.result && (
                      <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                        <ParsedResultCard result={currentUpload.result} candidateId={currentUpload.candidateId} onUploadAnother={resetUpload} />
                        {currentUpload.result.model_results && <ModelResultsView modelResults={currentUpload.result.model_results} />}
                        <ParsedDataDebugView data={currentUpload.result} candidateId={currentUpload.candidateId} />
                      </div>
                    )}
                  </div>
                )}

                {/* Bulk List */}
                {isBulkMode && uploadFiles.length > 0 && (
                  <div className="space-y-6">
                    <div className="bg-white rounded-3xl shadow-sm border border-slate-100 p-8 flex items-center justify-between hover:border-purple-600 transition-colors">
                      <div className="flex items-center gap-4">
                        <div className="h-12 w-12 bg-purple-50 rounded-xl flex items-center justify-center">
                          <Layers className="w-6 h-6 text-purple-600" />
                        </div>
                        <div>
                          <h3 className="text-lg font-bold text-slate-800 tracking-tight">Bulk Operations</h3>
                          <p className="text-slate-400 font-medium text-xs uppercase tracking-wider">{uploadFiles.length} items in queue</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <button
                          onClick={handleBulkUpload}
                          disabled={uploadFiles.some((f) => f.status === "uploading" || f.status === "parsing")}
                          className="px-8 py-3.5 text-white text-xs font-bold rounded-xl shadow-lg shadow-purple-50 disabled:opacity-50 transition-all uppercase tracking-wider"
                          style={{ background: 'linear-gradient(135deg, #7C3AED, #9333EA)' }}
                        >
                          Start Bulk
                        </button>
                        <button onClick={resetUpload} className="px-8 py-3.5 bg-slate-100 text-slate-500 text-xs font-bold rounded-xl hover:bg-slate-200 transition-all uppercase tracking-wider">
                          Clear
                        </button>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {uploadFiles.map((uploadFile) => (
                        <div key={uploadFile.id} className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 hover:border-purple-500 transition-colors">
                          <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center gap-4">
                              <div className="h-10 w-10 bg-slate-50 rounded-xl flex items-center justify-center border border-slate-100">
                                <FileUp className="w-5 h-5 text-purple-600" />
                              </div>
                              <div className="max-w-[150px] md:max-w-[200px]">
                                <h4 className="font-bold text-slate-800 text-sm truncate">{uploadFile.file.name}</h4>
                                <p className="text-[10px] font-medium text-slate-400 uppercase">{formatFileSize(uploadFile.file.size)}</p>
                              </div>
                            </div>
                            <span className={`px-3 py-1.5 text-[9px] font-bold uppercase tracking-wider rounded-lg ${uploadFile.status === "completed" ? "bg-emerald-100 text-emerald-700" :
                              uploadFile.status === "error" ? "bg-red-100 text-red-700" :
                                uploadFile.status === "parsing" ? "bg-purple-100 text-purple-700" :
                                  "bg-slate-100 text-slate-500"
                              }`}>
                              {uploadFile.status}
                            </span>
                          </div>

                          {uploadFile.status !== "pending" && (
                            <div className="mt-4">
                              <div className="flex items-center justify-between mb-2">
                                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{uploadFile.message}</span>
                                <span className="text-[10px] font-bold text-purple-600">{uploadFile.progress}%</span>
                              </div>
                              <div className="w-full bg-slate-50 rounded-full h-2 overflow-hidden border border-slate-100">
                                <div
                                  className="h-full transition-all duration-300"
                                  style={{
                                    width: `${uploadFile.progress}%`,
                                    background: uploadFile.status === "error" ? '#ef4444' : 'linear-gradient(90deg, #7C3AED, #9333EA)'
                                  }}
                                />
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Right Column: Settings Stack */}
          <div className="lg:col-span-4 space-y-6">

            {/* Box 1: Mode Selection */}
            <div className="bg-white rounded-3xl border border-slate-100 p-8 shadow-sm transition-all interactive-box">
              <div className="flex items-center gap-3 mb-6">
                <div className="h-10 w-10 bg-purple-50 rounded-xl flex items-center justify-center">
                  <Layers className="w-5 h-5 text-purple-600" />
                </div>
                <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider">Processing Mode</h3>
              </div>
              <div className="flex bg-slate-50 rounded-2xl p-1.5 border border-slate-100">
                <button
                  onClick={() => setIsBulkMode(false)}
                  className={`flex-1 px-4 py-2 rounded-xl font-bold text-[10px] transition-all duration-200 ${!isBulkMode ? "bg-white text-purple-600 shadow-sm border border-slate-100" : "text-slate-400 hover:text-slate-600"
                    }`}
                >
                  SINGLE
                </button>
                <button
                  onClick={() => setIsBulkMode(true)}
                  className={`flex-1 px-4 py-2 rounded-xl font-bold text-[10px] transition-all duration-200 ${isBulkMode ? "bg-white text-purple-600 shadow-sm border border-slate-100" : "text-slate-400 hover:text-slate-600"
                    }`}
                >
                  BULK
                </button>
              </div>
            </div>

            {/* Box 2: AI Engine Selection */}
            <div className="bg-white rounded-3xl border border-slate-100 p-8 shadow-sm transition-all interactive-box">
              <div className="flex items-center gap-3 mb-6">
                <div className="h-10 w-10 bg-purple-50 rounded-xl flex items-center justify-center">
                  <Zap className="w-5 h-5 text-purple-600" />
                </div>
                <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider">AI Intelligence</h3>
              </div>
              <div className="relative">
                <button
                  onClick={() => setShowLLMDropdown(!showLLMDropdown)}
                  className="w-full flex items-center justify-between px-5 py-3.5 bg-slate-50 border border-slate-100 rounded-xl hover:border-purple-200 transition-all"
                >
                  <div className="text-left">
                    <p className="text-sm font-bold text-slate-800 leading-tight">
                      {LLM_MODELS.find((m) => m.id === selectedLLM)?.name}
                    </p>
                    <p className="text-[10px] font-medium text-purple-500 uppercase mt-0.5">
                      {LLM_MODELS.find((m) => m.id === selectedLLM)?.badge}
                    </p>
                  </div>
                  <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform ${showLLMDropdown ? "rotate-180" : ""}`} />
                </button>

                {showLLMDropdown && (
                  <div className="absolute z-20 w-full mt-3 bg-white border border-slate-100 rounded-2xl shadow-xl overflow-hidden py-1">
                    {LLM_MODELS.map((model) => (
                      <button
                        key={model.id}
                        onClick={() => {
                          setSelectedLLM(model.id);
                          setShowLLMDropdown(false);
                        }}
                        className={`w-full px-5 py-3.5 text-left hover:bg-slate-50 transition-colors ${selectedLLM === model.id ? "bg-purple-50" : ""
                          }`}
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <p className={`text-xs font-bold ${selectedLLM === model.id ? "text-purple-600" : "text-slate-700"}`}>
                              {model.name}
                            </p>
                            <p className="text-[9px] font-medium text-slate-400 uppercase">{model.badge}</p>
                          </div>
                          {selectedLLM === model.id && <Zap className="w-3.5 h-3.5 text-purple-600" fill="currentColor" />}
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Box 3: Status / Selection Info */}
            <div className="bg-white rounded-3xl border border-slate-100 p-8 shadow-sm transition-all interactive-box">
              <div className="flex items-center gap-3 mb-6">
                <div className="h-10 w-10 bg-purple-50 rounded-xl flex items-center justify-center">
                  <Info className="w-5 h-5 text-purple-600" />
                </div>
                <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider">Queue Info</h3>
              </div>
              <div className="flex items-center justify-between p-4 bg-slate-50 rounded-2xl border border-slate-100">
                <div>
                  <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Items</p>
                  <p className="text-lg font-bold text-slate-800">{uploadFiles.length}</p>
                </div>
                <div className="h-10 w-10 rounded-full border-4 border-purple-100 border-t-purple-600 animate-spin opacity-20" />
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}
