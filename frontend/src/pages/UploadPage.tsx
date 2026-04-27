import { useState, useCallback, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useDropzone } from "react-dropzone";
import { useCandidateStore } from "../store/useCandidateStore";
import {
  connectSocket,
  subscribeToParsingProgress,
  subscribeToParsingComplete,
  subscribeToParsingFailed,
} from "../services/socket";
import toast from "react-hot-toast";
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

  const { uploadResume } = useCandidateStore();
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

      // Start upload with selected LLM (send empty string for own-model)
      const llmProvider = selectedLLM === "own-model" ? "" : selectedLLM;
      const candidate = await uploadResume(uploadFile.file, llmProvider);

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

  const resetUpload = () => {
    setUploadFiles([]);
    setCurrentUpload(null);
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
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-teal-50 to-cyan-50 relative overflow-hidden">
      {/* Decorative blur circles */}
      <div className="absolute top-10 right-10 w-[600px] h-[600px] bg-gradient-to-br from-teal-300/30 to-cyan-300/30 rounded-full blur-3xl pointer-events-none"></div>
      <div className="absolute bottom-10 left-10 w-[500px] h-[500px] bg-gradient-to-br from-purple-300/25 to-teal-300/25 rounded-full blur-3xl pointer-events-none"></div>
      <div className="absolute top-1/3 right-1/3 w-[400px] h-[400px] bg-gradient-to-br from-cyan-200/20 to-blue-200/20 rounded-full blur-3xl pointer-events-none"></div>
      
      <div className="relative p-8 max-w-5xl mx-auto">
        <div className="mb-10">
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-2xl font-semibold text-slate-800">Resume Analyzer</h1>
          </div>
          <p className="text-sm text-slate-600">
            Upload and analyze resumes with AI-powered insights
          </p>
        </div>

        {/* Mode Toggle */}
        <div className="mb-6">
          <div className="inline-flex items-center bg-white rounded-xl p-1 shadow-sm border border-slate-200">
            <button
              onClick={() => setIsBulkMode(false)}
              className={`px-6 py-2.5 rounded-lg font-medium transition-all duration-200 ${
                !isBulkMode
                  ? "bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-sm shadow-purple-500/20"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              Single Upload
            </button>
            <button
              onClick={() => setIsBulkMode(true)}
              className={`px-6 py-2.5 rounded-lg font-medium transition-all duration-200 ${
                isBulkMode
                  ? "bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-sm shadow-purple-500/20"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              Bulk Upload
            </button>
          </div>
        </div>

        {/* LLM Model Selector */}
        <div className="mb-6 bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select AI Model for Experience Extraction
        </label>
        <div className="relative">
          <button
            onClick={() => setShowLLMDropdown(!showLLMDropdown)}
            className="w-full flex items-center justify-between px-4 py-3 bg-white border border-gray-300 rounded-lg hover:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors"
          >
            <div className="flex items-center space-x-3">
              <div className="flex-1 text-left">
                <div className="flex items-center space-x-2">
                  <span className="font-medium text-gray-900">
                    {LLM_MODELS.find((m) => m.id === selectedLLM)?.name}
                  </span>
                  <span className={`px-2 py-0.5 text-xs font-semibold rounded-full ${
                    selectedLLM === "own-model" ? "bg-gray-100 text-gray-800" : "bg-indigo-100 text-indigo-800"
                  }`}>
                    {LLM_MODELS.find((m) => m.id === selectedLLM)?.badge}
                  </span>
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {LLM_MODELS.find((m) => m.id === selectedLLM)?.inputPrice} input / {LLM_MODELS.find((m) => m.id === selectedLLM)?.outputPrice} output per 1M tokens
                </div>
              </div>
            </div>
            <svg
              className={`w-5 h-5 text-gray-400 transition-transform ${
                showLLMDropdown ? "rotate-180" : ""
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </button>

          {showLLMDropdown && (
            <div className="absolute z-10 w-full mt-2 bg-white border border-gray-200 rounded-lg shadow-lg">
              {LLM_MODELS.map((model) => (
                <button
                  key={model.id}
                  onClick={() => {
                    setSelectedLLM(model.id);
                    setShowLLMDropdown(false);
                  }}
                  className={`w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors first:rounded-t-lg last:rounded-b-lg ${
                    selectedLLM === model.id ? "bg-indigo-50" : ""
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <span className="font-medium text-gray-900">
                          {model.name}
                        </span>
                        <span className={`px-2 py-0.5 text-xs font-semibold rounded-full ${
                          model.id === "own-model" ? "bg-gray-100 text-gray-800" : "bg-indigo-100 text-indigo-800"
                        }`}>
                          {model.badge}
                        </span>
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {model.inputPrice} input / {model.outputPrice} output per 1M tokens
                      </div>
                    </div>
                    {selectedLLM === model.id && (
                      <svg
                        className="w-5 h-5 text-indigo-600"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                          clipRule="evenodd"
                        />
                      </svg>
                    )}
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
        {selectedLLM === "own-model" && (
          <p className="mt-2 text-sm text-gray-600">
            Using built-in rule-based + BERT NER pipeline — no API call made
          </p>
        )}
      </div>

        {/* Upload Area */}
        {!currentUpload && uploadFiles.length === 0 && (
          <div className="bg-white/60 backdrop-blur-md rounded-3xl border-2 border-dashed border-purple-200 p-20 hover:border-purple-400 hover:bg-white/70 transition-all duration-300 shadow-xl shadow-purple-100/50">
            <div
              {...getRootProps()}
              className={`text-center cursor-pointer transition-all duration-300 ${
                isDragActive
                  ? "scale-105"
                  : "hover:scale-[1.02]"
              }`}
            >
              <input {...getInputProps()} />
              <div className="mx-auto w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg shadow-purple-500/30 mb-8">
                <svg
                  className="h-8 w-8 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                  />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-slate-800 mb-3">
                Upload Resume Files
              </h3>
              <p className="text-sm text-slate-600 mb-6">
                Drag & drop your resume files here, or click to browse
              </p>
              <p className="text-xs text-slate-500 mb-6">
                Supports PDF, DOC, and DOCX files • Max 10MB per file
              </p>
              <button className="px-6 py-2.5 bg-gradient-to-r from-purple-600 to-purple-700 text-white text-sm font-medium rounded-xl hover:shadow-lg hover:shadow-purple-500/40 transition-all duration-200">
                Choose Files
              </button>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!currentUpload && uploadFiles.length === 0 && (
          <div className="mt-16 text-center">
            <div className="mx-auto w-14 h-14 bg-purple-100 rounded-full flex items-center justify-center mb-4">
              <svg className="w-7 h-7 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-base font-medium text-slate-800 mb-1">No Resumes Uploaded</h3>
            <p className="text-sm text-slate-500">Upload your first resume to get started with AI-powered analysis.</p>
          </div>
        )}

        {/* Single File Pending State */}
        {!isBulkMode && uploadFiles.length > 0 && !currentUpload && (
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-medium text-gray-900">
                Ready to upload
              </h3>
              <p className="text-sm text-gray-500">
                {uploadFiles[0].file.name} (
                {formatFileSize(uploadFiles[0].file.size)})
              </p>
            </div>
            <div className="space-x-3">
              <button
                onClick={() => handleUpload(uploadFiles[0])}
                className="px-6 py-2.5 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-xl hover:shadow-lg hover:shadow-purple-500/20 transition-all duration-200 font-medium"
              >
                Upload Resume
              </button>
              <button
                onClick={resetUpload}
                className="px-6 py-2.5 bg-slate-100 text-slate-700 rounded-xl hover:bg-slate-200 transition-colors font-medium"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Single Upload Progress */}
      {currentUpload && !isBulkMode && (
        <>
          {/* Show progress UI only during upload/parsing */}
          {(currentUpload.status === "uploading" || currentUpload.status === "parsing" || currentUpload.status === "error") && (
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
              <div className="mb-4">
                <h3 className="text-lg font-medium text-gray-900">
                  Uploading: {currentUpload.file.name}
                </h3>
                <p className="text-sm text-gray-500">
                  Size: {formatFileSize(currentUpload.file.size)}
                </p>
              </div>

              {/* Progress Bar */}
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">
                    {currentUpload.message}
                  </span>
                  <span className="text-sm text-gray-500">
                    {currentUpload.progress}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${currentUpload.progress}%` }}
                  />
                </div>
              </div>

              {/* Speed Gauge - Show during parsing */}
              {currentUpload.status === "parsing" && (
                <div className="mb-4 bg-gray-50 rounded-lg p-4">
                  <SpeedGauge value={currentUpload.progress} label="Parsing Progress" />
                </div>
              )}

              {/* Error State */}
              {currentUpload.status === "error" && (
                <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-red-800 text-sm">{currentUpload.error}</p>
                </div>
              )}
            </div>
          )}

          {/* Completed State - No wrapper */}
          {currentUpload.status === "completed" && currentUpload.result && (
            <>
              {console.log("📊 Upload result:", currentUpload.result)}
              {console.log("🔍 model_results field:", currentUpload.result.model_results)}
              
              <ParsedResultCard
                result={currentUpload.result}
                candidateId={currentUpload.candidateId}
                onUploadAnother={resetUpload}
              />
              
              {/* Model Results View - Raw DeBERTa Extraction */}
              {currentUpload.result.model_results ? (
                <div className="mt-6">
                  <ModelResultsView modelResults={currentUpload.result.model_results} />
                </div>
              ) : (
                <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <p className="text-yellow-800 text-sm">
                    ⚠️ No model_results found in API response. Check backend logs.
                  </p>
                </div>
              )}
              
              {/* Debug View - Full Parsed JSON */}
              <div className="mt-6">
                <ParsedDataDebugView 
                  data={currentUpload.result} 
                  candidateId={currentUpload.candidateId}
                />
              </div>
            </>
          )}
        </>
      )}

        {/* Bulk Upload */}
        {isBulkMode && uploadFiles.length > 0 && (
          <div className="space-y-4">
            {/* Upload Controls */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">
                {uploadFiles.length} file{uploadFiles.length !== 1 ? "s" : ""}{" "}
                selected
              </h3>
              <div className="space-x-3">
                <button
                  onClick={handleBulkUpload}
                  disabled={uploadFiles.some(
                    (f) => f.status === "uploading" || f.status === "parsing",
                  )}
                  className="px-6 py-2.5 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-xl hover:shadow-lg hover:shadow-purple-500/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 font-medium"
                >
                  Upload All
                </button>
                <button
                  onClick={resetUpload}
                  className="px-6 py-2.5 bg-slate-100 text-slate-700 rounded-xl hover:bg-slate-200 transition-colors font-medium"
                >
                  Clear All
                </button>
              </div>
            </div>
          </div>

            {/* File List */}
            {uploadFiles.map((uploadFile) => (
              <div
                key={uploadFile.id}
                className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6"
              >
              <div className="flex items-center justify-between mb-2">
                <div>
                  <h4 className="font-medium text-gray-900">
                    {uploadFile.file.name}
                  </h4>
                  <p className="text-sm text-gray-500">
                    {formatFileSize(uploadFile.file.size)}
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  {uploadFile.status === "pending" && (
                    <button
                      onClick={() => handleUpload(uploadFile)}
                      className="px-4 py-1.5 bg-gradient-to-r from-purple-600 to-blue-600 text-white text-sm rounded-lg hover:shadow-md transition-all font-medium"
                    >
                      Upload
                    </button>
                  )}
                  <span
                    className={`px-3 py-1 text-xs font-semibold rounded-full ${
                      uploadFile.status === "completed"
                        ? "bg-gradient-to-r from-teal-500 to-teal-600 text-white"
                        : uploadFile.status === "error"
                          ? "bg-gradient-to-r from-red-500 to-pink-500 text-white"
                          : uploadFile.status === "parsing"
                            ? "bg-gradient-to-r from-purple-500 to-blue-500 text-white"
                            : "bg-slate-100 text-slate-700"
                    }`}
                  >
                    {uploadFile.status}
                  </span>
                </div>
              </div>

              {/* Progress */}
              {uploadFile.status !== "pending" && (
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm text-gray-600">
                      {uploadFile.message}
                    </span>
                    <span className="text-sm text-gray-500">
                      {uploadFile.progress}%
                    </span>
                  </div>
                  <div className="w-full bg-slate-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all duration-300 ${
                        uploadFile.status === "error"
                          ? "bg-gradient-to-r from-red-500 to-pink-500"
                          : "bg-gradient-to-r from-purple-600 to-blue-600"
                      }`}
                      style={{ width: `${uploadFile.progress}%` }}
                    />
                  </div>
                </div>
              )}

              {/* Error */}
              {uploadFile.error && (
                <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded-xl text-red-800 text-sm">
                  {uploadFile.error}
                </div>
              )}
            </div>
          ))}

          {/* Summary */}
          {uploadFiles.length > 0 &&
            uploadFiles.every(
              (f) => f.status === "completed" || f.status === "error",
            ) && (
              <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  Upload Summary
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-green-600">
                      {
                        uploadFiles.filter((f) => f.status === "completed")
                          .length
                      }
                    </p>
                    <p className="text-sm text-gray-600">Successful</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-red-600">
                      {uploadFiles.filter((f) => f.status === "error").length}
                    </p>
                    <p className="text-sm text-gray-600">Failed</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-gray-600">
                      {uploadFiles.length}
                    </p>
                    <p className="text-sm text-gray-600">Total</p>
                  </div>
                </div>
                <button
                  onClick={resetUpload}
                  className="mt-4 w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-xl hover:shadow-lg hover:shadow-purple-500/20 transition-all duration-200 font-medium"
                >
                  Upload More Files
                </button>
              </div>
            )}
        </div>
      )}
      </div>
    </div>
  );
}
