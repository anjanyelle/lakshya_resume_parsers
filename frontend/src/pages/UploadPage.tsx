import { useState, useCallback, useEffect, useRef } from "react";
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
import ModelResultsView from "../components/upload/ModelResultsView";
import { 
  UploadCloud, 
  FileText, 
  Sparkles, 
  Info, 
  Eye, 
  Trash2,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Plus,
  ChevronDown,
  Layers,
  ArrowRight
} from "lucide-react";

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
  const [showModelDropdown, setShowModelDropdown] = useState(false);
  
  const dropdownRef = useRef<HTMLDivElement>(null);
  const { uploadResume } = useCandidateStore();
  const navigate = useNavigate();

  // Close dropdown on click outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowModelDropdown(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Socket.io connection
  useEffect(() => {
    connectSocket();

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

    return () => {};
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
        handleBulkUploadInternal(newFiles);
      } else {
        const file = newFiles[0];
        setUploadFiles([file]);
        handleUpload(file);
      }
    },
    [isBulkMode, selectedLLM],
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
      "text/plain": [".txt"],
    },
    maxSize: 10 * 1024 * 1024,
    multiple: isBulkMode,
  });

  const handleUpload = async (uploadFile: UploadFile) => {
    try {
      setCurrentUpload({
        ...uploadFile,
        status: "uploading",
        message: "Uploading...",
        progress: 0,
      });

      const llmProvider = selectedLLM === "own-model" ? "" : selectedLLM;
      const candidate = await uploadResume(uploadFile.file, llmProvider);

      if (!candidate || !candidate.id) {
        throw new Error("Invalid response from server");
      }

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

      setCurrentUpload((prev) =>
        prev ? { ...prev, candidateId: candidate.id, status: "parsing", message: "Extracting text...", progress: 25 } : null
      );
    } catch (error: any) {
      const errorMessage = error.message || "Upload failed";
      setCurrentUpload((prev) => prev ? { ...prev, status: "error", message: "Failed", error: errorMessage } : null);
      toast.error(errorMessage);
    }
  };

  const handleBulkUploadInternal = async (files: UploadFile[]) => {
    for (const file of files) {
      await handleUpload(file);
      await new Promise((resolve) => setTimeout(resolve, 500));
    }
  };

  const resetUpload = () => {
    setCurrentUpload(null);
  };

  const clearAll = () => {
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

  const removeFile = (id: string) => {
    setUploadFiles(prev => prev.filter(f => f.id !== id));
  };

  const currentModel = LLM_MODELS.find(m => m.id === selectedLLM) || LLM_MODELS[0];

  return (
    <div className="relative min-h-[calc(100vh-140px)] animate-in fade-in duration-700 pb-10 px-6 max-w-[1400px] mx-auto overflow-hidden">
      
      {/* Dynamic Mesh Gradient Background Blobs */}
      <div className="absolute inset-0 -z-10 pointer-events-none overflow-hidden">
         <div className="absolute top-[-10%] left-[30%] w-[500px] h-[500px] bg-indigo-500/10 rounded-full blur-[120px] animate-pulse duration-[8s]" />
         <div className="absolute bottom-[10%] right-[0%] w-[600px] h-[600px] bg-teal-400/10 rounded-full blur-[140px] animate-pulse duration-[10s] delay-1000" />
         <div className="absolute top-[40%] left-[-10%] w-[400px] h-[400px] bg-purple-500/10 rounded-full blur-[100px] animate-pulse duration-[12s] delay-2000" />
      </div>

      {/* Compact Header Area */}
      <div className="flex items-center justify-between mb-8 mt-2 relative z-10">
        <div>
          <h1 className="text-2xl font-black tracking-tight leading-none mb-2">
             <span className="bg-gradient-to-r from-indigo-600 via-purple-600 to-teal-500 bg-clip-text text-transparent">Resume Intelligence</span>
          </h1>
          <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest leading-none opacity-90 italic">Enterprise Extraction & AI Analysis Engine</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 mb-10 relative z-20">
        
        {/* Left Section: Upload Box (60%) */}
        <div className="lg:col-span-7">
           <div className={`h-full bg-white/70 backdrop-blur-2xl rounded-[40px] border border-white/40 transition-all duration-500 shadow-2xl shadow-indigo-500/5 flex flex-col items-center justify-center p-8 min-h-[380px] relative overflow-hidden group/container
              ${isDragActive ? 'border-indigo-400 bg-indigo-50/20 scale-[0.99]' : 'hover:border-indigo-200/50'}
           `}>
              {/* Inner subtle glow for the container */}
              <div className="absolute inset-0 bg-gradient-to-br from-white/20 to-transparent pointer-events-none" />
              
              {/* Ready State */}
              {!currentUpload && (
                <div {...getRootProps()} className="w-full text-center cursor-pointer group flex flex-col items-center relative z-10">
                  <input {...getInputProps()} />
                  
                  {/* Dashed Border Visual Layer */}
                  <div className="absolute inset-4 border-2 border-dashed border-slate-100 group-hover:border-indigo-200/50 rounded-[32px] transition-colors duration-500" />
                  
                  <div className="w-20 h-20 bg-gradient-to-tr from-indigo-600 to-teal-400 rounded-[28px] flex items-center justify-center shadow-2xl shadow-indigo-200 mb-8 group-hover:scale-110 group-hover:rotate-3 transition-all duration-500 relative">
                    <UploadCloud size={38} className="text-white relative z-10" />
                    <div className="absolute inset-0 bg-white/20 rounded-[28px] scale-0 group-hover:scale-100 transition-transform duration-500" />
                  </div>
                  
                  <h3 className="text-2xl font-bold text-slate-700 mb-2 tracking-tighter">Drop Resume Here</h3>
                  <p className="text-[11px] font-bold text-slate-400 max-w-xs mx-auto mb-8 uppercase tracking-[0.2em] leading-relaxed opacity-80">
                    Automatic parsing • scoring • mapping
                  </p>
                  
                  <button className="relative px-10 py-4 bg-slate-800 overflow-hidden text-white text-[11px] font-bold uppercase tracking-[0.25em] rounded-2xl hover:shadow-2xl hover:shadow-indigo-500/20 transition-all duration-500 group/btn">
                    <span className="relative z-10">Select File</span>
                    <div className="absolute inset-0 bg-indigo-600 translate-y-full group-hover/btn:translate-y-0 transition-transform duration-500" />
                  </button>
                </div>
              )}

              {/* Processing State (Attractive Design Refinement) */}
              {currentUpload && (
                 <div className="w-full text-center animate-in zoom-in duration-500 relative z-10">
                    <div className="relative mx-auto w-48 h-48 mb-10">
                       {/* Background Track with soft glow */}
                       <div className="absolute inset-0 rounded-full border-[8px] border-slate-50 shadow-inner"></div>
                       
                       <svg className="absolute inset-0 w-full h-full -rotate-90 drop-shadow-xl">
                          <circle
                             cx="96"
                             cy="96"
                             r="88"
                             fill="transparent"
                             stroke="url(#attractiveProgressGradient)"
                             strokeWidth="16"
                             strokeDasharray="553"
                             strokeDashoffset={553 - (553 * currentUpload.progress) / 100}
                             className="transition-all duration-1000 ease-out"
                             strokeLinecap="round"
                          />
                          <defs>
                             <linearGradient id="attractiveProgressGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                <stop offset="0%" stopColor="#2DD4BF" />
                                <stop offset="50%" stopColor="#6366F1" />
                                <stop offset="100%" stopColor="#8B5CF6" />
                             </linearGradient>
                          </defs>
                       </svg>
                       
                       <div className="absolute inset-0 flex flex-col items-center justify-center">
                          <span className="text-5xl font-black text-slate-700 tracking-tighter leading-none mb-1">{currentUpload.progress}%</span>
                          <span className="text-[10px] font-black text-indigo-500 uppercase tracking-[0.2em]">STATUS</span>
                       </div>
                    </div>
                    
                    <div className="space-y-3 mb-10">
                       <h3 className="text-2xl font-bold text-slate-700 tracking-tight leading-none">{currentUpload.message}</h3>
                       <div className="flex items-center justify-center gap-2">
                          <FileText size={18} className="text-slate-300" />
                          <p className="text-[11px] font-bold text-slate-400 uppercase tracking-widest">{currentUpload.file.name}</p>
                       </div>
                    </div>
                    
                    <div className="flex items-center justify-center gap-4">
                       {currentUpload.status === 'completed' && (
                          <button onClick={resetUpload} className="px-12 py-4 bg-gradient-to-r from-emerald-500 to-teal-500 text-white text-[11px] font-bold uppercase tracking-[0.2em] rounded-2xl shadow-xl shadow-emerald-100 hover:scale-105 transition-all">
                             Process Next
                          </button>
                       )}
                       {currentUpload.status === 'error' && (
                          <div className="space-y-6">
                             <div className="flex items-center justify-center gap-2 px-6 py-3 bg-rose-50 rounded-xl border border-rose-100">
                                <AlertCircle size={16} className="text-rose-500" />
                                <p className="text-rose-600 text-[10px] font-bold uppercase tracking-wider">{currentUpload.error}</p>
                             </div>
                             <button onClick={resetUpload} className="px-12 py-4 bg-rose-500 text-white text-[11px] font-bold uppercase tracking-[0.2em] rounded-2xl hover:bg-rose-600 shadow-xl shadow-rose-100 transition-all">
                                Try Again
                             </button>
                          </div>
                       )}
                    </div>
                 </div>
              )}
           </div>
        </div>

        {/* Right Section: Compact Settings (40%) */}
        <div className="lg:col-span-5 flex flex-col gap-8">
           
           {/* Mode Toggle Area (Transparent Glass) */}
           <div className="bg-white/70 backdrop-blur-2xl p-8 rounded-[40px] border border-white/40 shadow-2xl shadow-indigo-500/5 flex items-center justify-between group/mode">
              <div className="flex items-center gap-5">
                 <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-50 to-white flex items-center justify-center text-indigo-600 shadow-inner border border-white/60 group-hover/mode:scale-105 transition-transform duration-500">
                    {isBulkMode ? <Layers size={22}/> : <Plus size={22}/>}
                 </div>
                 <div>
                    <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.25em] mb-1.5 leading-none">PROCESS MODE</h4>
                    <p className="text-xl font-bold text-slate-700 tracking-tight leading-none">{isBulkMode ? 'Bulk Queue' : 'Direct Analysis'}</p>
                 </div>
              </div>
              <div className="bg-slate-100/50 backdrop-blur-md p-1.5 rounded-[22px] flex items-center border border-white/20">
                 <button onClick={() => setIsBulkMode(false)} className={`px-6 py-3 text-[10px] font-black uppercase tracking-[0.15em] rounded-xl transition-all duration-500 ${!isBulkMode ? 'bg-white text-indigo-600 shadow-xl shadow-indigo-100/30' : 'text-slate-400 hover:text-slate-600'}`}>Single</button>
                 <button onClick={() => setIsBulkMode(true)} className={`px-6 py-3 text-[10px] font-black uppercase tracking-[0.15em] rounded-xl transition-all duration-500 ${isBulkMode ? 'bg-white text-indigo-600 shadow-xl shadow-indigo-100/30' : 'text-slate-400 hover:text-slate-600'}`}>Bulk</button>
              </div>
           </div>

           {/* Custom Model Dropdown selection (Vibrant Design) */}
           <div className="bg-white/70 backdrop-blur-2xl p-8 rounded-[40px] border border-white/40 shadow-2xl shadow-indigo-500/5 flex flex-col flex-1 relative z-20 group/model">
              {/* Decorative accent for the dropdown card */}
              <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/5 rounded-full blur-3xl group-hover/model:bg-indigo-500/10 transition-colors duration-700" />
              
              <div className="flex items-center justify-between mb-8 relative z-10">
                 <h3 className="text-[11px] font-black text-slate-700 uppercase tracking-[0.2em] flex items-center gap-2">
                    Extraction Engine
                    <Sparkles size={14} className="text-indigo-500 animate-pulse" />
                 </h3>
                 <div className="w-8 h-8 rounded-full bg-slate-50 flex items-center justify-center text-slate-400 border border-white/60">
                    <Info size={14} />
                 </div>
              </div>

              <div className="relative z-20" ref={dropdownRef}>
                 <button 
                  onClick={() => setShowModelDropdown(!showModelDropdown)}
                  className={`w-full group flex items-center justify-between p-5 rounded-[24px] border-2 transition-all duration-500 
                    ${showModelDropdown ? 'border-indigo-500 bg-white shadow-2xl shadow-indigo-200/50' : 'border-slate-50 bg-white hover:border-slate-200 hover:shadow-xl hover:shadow-indigo-500/5'}
                  `}
                 >
                    <div className="flex items-center gap-5">
                       <div className={`w-10 h-10 rounded-2xl flex items-center justify-center text-white font-black text-xs shadow-xl transition-all duration-500 group-hover:rotate-12
                          ${currentModel.id === 'own-model' ? 'bg-gradient-to-br from-emerald-400 to-emerald-600 shadow-emerald-100' : 'bg-gradient-to-br from-indigo-500 to-indigo-700 shadow-indigo-100'}`}>
                          {currentModel.name.charAt(0)}
                       </div>
                       <div className="text-left">
                          <p className={`text-[13px] font-bold tracking-tight leading-none mb-2 transition-colors duration-300 ${showModelDropdown ? 'text-indigo-600' : 'text-slate-700'}`}>{currentModel.name}</p>
                          <span className={`text-[9px] font-black uppercase tracking-[0.15em] px-2 py-0.5 rounded-lg border
                             ${currentModel.id === 'own-model' ? 'bg-emerald-50 text-emerald-600 border-emerald-100' : 'bg-indigo-50 text-indigo-500 border-indigo-100'}`}>
                             {currentModel.badge}
                          </span>
                       </div>
                    </div>
                    <ChevronDown size={18} className={`text-slate-300 transition-transform duration-500 ${showModelDropdown ? 'rotate-180 text-indigo-500' : ''}`} />
                 </button>

                 {/* Dropdown Menu (Refined alignment) */}
                 {showModelDropdown && (
                    <div className="absolute top-[calc(100%+10px)] left-0 right-0 bg-white border border-slate-100 rounded-[28px] shadow-2xl shadow-indigo-900/10 z-50 overflow-hidden p-2 animate-in fade-in slide-in-from-top-2 duration-300">
                       <div className="space-y-1">
                          {LLM_MODELS.map((model) => (
                             <button
                                key={model.id}
                                onClick={() => {
                                  setSelectedLLM(model.id);
                                  setShowModelDropdown(false);
                                }}
                                className={`w-full flex items-center justify-between p-3.5 rounded-2xl transition-all duration-300
                                   ${selectedLLM === model.id ? 'bg-indigo-50/50' : 'hover:bg-slate-50'}
                                `}
                             >
                                <div className="flex items-center gap-4">
                                   <div className={`w-7 h-7 rounded-lg flex items-center justify-center text-white font-bold text-[9px] shadow-sm
                                      ${model.id === 'own-model' ? 'bg-emerald-400' : 'bg-indigo-400'}`}>
                                      {model.name.charAt(0)}
                                   </div>
                                   <div className="text-left">
                                      <p className={`text-[11px] font-bold leading-none mb-1.5 ${selectedLLM === model.id ? 'text-indigo-600' : 'text-slate-600'}`}>{model.name}</p>
                                      <div className="flex items-center gap-2">
                                         <p className="text-[8px] font-medium text-slate-400 uppercase tracking-widest">Pricing: {model.inputPrice} / {model.outputPrice}</p>
                                      </div>
                                   </div>
                                </div>
                                {selectedLLM === model.id && (
                                   <div className="w-5 h-5 rounded-full bg-indigo-500 flex items-center justify-center">
                                      <CheckCircle2 size={10} className="text-white" />
                                   </div>
                                )}
                             </button>
                          ))}
                       </div>
                    </div>
                 )}
              </div>
              
              <div className="mt-auto pt-8 flex items-center justify-between opacity-80 relative z-10">
                 <div className="flex items-center gap-3">
                    <div className="px-3 py-1 bg-amber-50 text-amber-600 text-[10px] font-black rounded-lg border border-amber-100">
                       SECURE PARSING
                    </div>
                 </div>
                 <p className="text-[9px] font-bold text-slate-400 italic">v2.4.1 Active</p>
              </div>
           </div>
        </div>
      </div>

      {/* Results Section (Glass Panel) */}
      <div className="bg-white/70 backdrop-blur-2xl rounded-[48px] border border-white/40 shadow-2xl shadow-indigo-500/5 p-10 relative z-10 group/history">
         {/* Decorative flare for history */}
         <div className="absolute bottom-[-10%] left-[20%] w-64 h-64 bg-teal-400/5 rounded-full blur-[80px]" />
         
         <div className="flex items-center justify-between mb-10 relative z-10">
            <div>
               <h3 className="text-2xl font-bold text-slate-700 tracking-tighter leading-none mb-2">Analysis History</h3>
               <p className="text-[11px] font-black text-slate-400 uppercase tracking-[0.2em] opacity-80 leading-none">Complete candidate data extraction history</p>
            </div>
            <div className="flex items-center gap-8">
               <div className="flex flex-col items-end">
                  <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1.5">QUEUE SIZE</span>
                  <div className="px-4 py-1 bg-indigo-50 rounded-lg text-indigo-600 font-black text-sm border border-indigo-100">
                     {uploadFiles.length}
                  </div>
               </div>
               <button onClick={clearAll} className="group flex items-center gap-2 px-8 py-4 bg-rose-50 text-rose-600 text-[11px] font-black uppercase tracking-widest rounded-[22px] hover:bg-rose-500 hover:text-white hover:shadow-2xl hover:shadow-rose-300 transition-all duration-500 outline-none">
                  <Trash2 size={16} />
                  Clear List
               </button>
            </div>
         </div>

         <div className="space-y-4 relative z-10">
            {uploadFiles.length === 0 ? (
               <div className="flex flex-col items-center justify-center py-20 border-2 border-dashed border-slate-100/50 rounded-[40px] group/empty hover:border-indigo-100/50 transition-colors duration-700">
                  <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center mb-6 shadow-xl shadow-slate-100 group-hover/empty:scale-110 group-hover/empty:rotate-3 transition-transform duration-500">
                     <FileText size={28} className="text-slate-300 group-hover/empty:text-indigo-400 transition-colors" />
                  </div>
                  <p className="text-[12px] font-black text-slate-400 uppercase tracking-[0.2em] group-hover/empty:text-indigo-600 transition-colors duration-500">Queue is currently empty</p>
               </div>
            ) : (
               <div className="grid grid-cols-1 gap-4">
                  {uploadFiles.map((file, index) => (
                     <div 
                        key={file.id} 
                        className="group flex items-center justify-between p-5 bg-white border border-slate-50 rounded-[30px] hover:border-indigo-200 hover:shadow-2xl hover:shadow-indigo-500/10 transition-all duration-500 translate-y-0 hover:-translate-y-1"
                        style={{ animationDelay: `${index * 50}ms` }}
                     >
                        <div className="flex items-center gap-6">
                           <div className={`w-14 h-14 rounded-[22px] flex items-center justify-center text-white text-lg font-black shadow-lg shadow-indigo-100 relative overflow-hidden transition-all duration-500 group-hover:px-6
                              ${file.status === 'completed' ? 'bg-gradient-to-br from-indigo-500 to-indigo-700' : 
                                file.status === 'error' ? 'bg-gradient-to-br from-rose-500 to-rose-700' : 
                                'bg-gradient-to-br from-amber-500 to-amber-700'}
                           `}>
                              {file.status === 'parsing' ? <Loader2 size={24} className="animate-spin" /> : file.file.name.charAt(0).toUpperCase()}
                              <div className="absolute inset-0 bg-white/20 translate-x-[-100%] group-hover:translate-x-full transition-transform duration-700" />
                           </div>
                           <div>
                              <p className="text-base font-bold text-slate-700 tracking-tight leading-none mb-2.5 group-hover:text-indigo-600 transition-colors duration-300 truncate max-w-[200px]">{file.file.name}</p>
                              <div className="flex items-center gap-4">
                                 <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{formatFileSize(file.file.size)}</span>
                                 <div className="w-1 h-1 bg-slate-100 rounded-full"></div>
                                 <span className={`text-[9px] font-black uppercase tracking-[0.1em] px-3 py-1 rounded-lg border
                                    ${file.status === 'completed' ? 'bg-emerald-50 text-emerald-600 border-emerald-100' : 
                                      file.status === 'error' ? 'bg-rose-50 text-rose-600 border-rose-100' : 
                                      'bg-amber-50 text-amber-600 border-amber-100'}`}>
                                    {file.status}
                                 </span>
                              </div>
                           </div>
                        </div>
                        
                        <div className="flex items-center gap-10">
                           {file.status === 'completed' && (
                              <div className="flex items-center gap-4 pr-10 border-r border-slate-50">
                                 <div className="text-right">
                                    <p className="text-[9px] font-black text-slate-400 mb-1 leading-none">MATCH SCORE</p>
                                    <p className="text-sm font-black text-slate-700 leading-none">Highly Qualified</p>
                                 </div>
                                 <div className="w-14 h-14 rounded-2xl bg-slate-50 border border-slate-100 flex items-center justify-center text-slate-700 font-black text-sm shadow-inner group-hover:bg-indigo-50 group-hover:text-indigo-600 group-hover:border-indigo-100 transition-all duration-300">
                                    92%
                                 </div>
                              </div>
                           )}
                           
                           <div className="flex items-center gap-3">
                              <button 
                                 onClick={() => file.candidateId && navigate(`/candidates/${file.candidateId}`)}
                                 disabled={file.status !== 'completed'}
                                 className="w-12 h-12 rounded-[18px] bg-white border border-slate-100 flex items-center justify-center text-slate-300 hover:text-indigo-600 hover:border-indigo-100 hover:shadow-xl hover:shadow-indigo-100 transition-all duration-500 disabled:opacity-20 group/btn"
                                 title="View Analysis"
                              >
                                 <Eye size={20} className="group-hover/btn:scale-110 group-hover/btn:rotate-6 transition-transform" />
                              </button>
                              <button 
                                 onClick={() => removeFile(file.id)}
                                 className="w-12 h-12 rounded-[18px] bg-white border border-slate-100 flex items-center justify-center text-slate-300 hover:text-rose-600 hover:border-rose-100 hover:shadow-xl hover:shadow-rose-100 transition-all duration-500 group/btn"
                                 title="Remove from History"
                              >
                                 <Trash2 size={20} className="group-hover/btn:scale-110 group-hover/btn:-rotate-6 transition-transform" />
                              </button>
                           </div>
                        </div>
                     </div>
                  ))}
               </div>
            )}
         </div>
      </div>
    </div>
  );
}
