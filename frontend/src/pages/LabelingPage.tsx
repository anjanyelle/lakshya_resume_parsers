import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { Tag, SkipForward, CheckCircle, ChevronRight, Cpu, X } from "lucide-react";

interface Candidate {
  id: string; full_name: string; email: string; phone?: string; location?: string;
  linkedin_url?: string; summary?: string; raw_resume_text?: string;
  skills?: string[]; companies?: string[]; job_titles?: string[];
  education_degrees?: string[]; universities?: string[];
  parsing_status?: { status: string; confidence_score?: number; error_message?: string };
  created_at: string;
}

interface LabelingProgress { labeled: number; total: number; accuracy_estimate: number; }

interface FormData {
  name: string; email: string; phone: string;
  skills: string[]; companies: string[]; job_titles: string[];
  education_degrees: string[]; universities: string[];
}

const TAG_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  skills: { bg: "bg-brand-50", text: "text-brand-700", border: "border-brand-200" },
  companies: { bg: "bg-violet-50", text: "text-violet-700", border: "border-violet-200" },
  job_titles: { bg: "bg-purple-50", text: "text-purple-700", border: "border-purple-200" },
  education_degrees: { bg: "bg-amber-50", text: "text-amber-700", border: "border-amber-200" },
  universities: { bg: "bg-purple-50", text: "text-purple-700", border: "border-purple-200" },
};

export default function LabelingPage() {
  const [currentCandidate, setCurrentCandidate] = useState<Candidate | null>(null);
  const [progress, setProgress] = useState<LabelingProgress>({ labeled: 0, total: 0, accuracy_estimate: 0 });
  const [isLoading, setIsLoading] = useState(false);
  const [currentSkill, setCurrentSkill] = useState("");
  const [currentCompany, setCurrentCompany] = useState("");
  const [currentJobTitle, setCurrentJobTitle] = useState("");
  const [currentDegree, setCurrentDegree] = useState("");
  const [currentUniversity, setCurrentUniversity] = useState("");
  const navigate = useNavigate();

  const [formData, setFormData] = useState<FormData>({
    name: "", email: "", phone: "", skills: [], companies: [], job_titles: [], education_degrees: [], universities: [],
  });

  useEffect(() => { loadProgress(); loadNextCandidate(); }, []);

  const loadProgress = async () => {
    try {
      const res = await fetch("/api/labeling/progress");
      const data = await res.json();
      if (res.ok) setProgress(data);
    } catch { console.error("Failed to load progress"); }
  };

  const loadNextCandidate = async () => {
    setIsLoading(true);
    try {
      const res = await fetch("/api/labeling/next");
      const data = await res.json();
      if (res.ok && data) {
        setCurrentCandidate(data);
        setFormData({
          name: data.full_name || "", email: data.email || "", phone: data.phone || "",
          skills: data.skills || [], companies: data.companies || [], job_titles: data.job_titles || [],
          education_degrees: data.education_degrees || [], universities: data.universities || []
        });
      } else { setCurrentCandidate(null); toast.success("All candidates have been labeled!"); }
    } catch { toast.error("Failed to load next candidate"); }
    finally { setIsLoading(false); }
  };

  const addTag = (type: keyof FormData, value: string) => {
    if (!value.trim()) return;
    const arr = formData[type] as string[];
    if (!arr.includes(value.trim())) setFormData((p) => ({ ...p, [type]: [...arr, value.trim()] }));
  };

  const removeTag = (type: keyof FormData, val: string) =>
    setFormData((p) => ({ ...p, [type]: (p[type] as string[]).filter((i) => i !== val) }));

  const handleCorrectAndNext = async () => {
    if (!currentCandidate) return;
    try {
      const res = await fetch("/api/labeling/save", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ candidate_id: currentCandidate.id, corrected_fields: formData, action: "corrected" })
      });
      if (res.ok) { toast.success("Corrections saved!"); loadProgress(); loadNextCandidate(); }
      else toast.error("Failed to save corrections");
    } catch { toast.error("Failed to save corrections"); }
  };

  const handleSkip = async () => {
    if (!currentCandidate) return;
    try {
      const res = await fetch("/api/labeling/save", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ candidate_id: currentCandidate.id, action: "skipped" })
      });
      if (res.ok) { toast("Candidate skipped", { icon: "⏭️" }); loadProgress(); loadNextCandidate(); }
      else toast.error("Failed to skip candidate");
    } catch { toast.error("Failed to skip candidate"); }
  };

  const handleApprove = async () => {
    if (!currentCandidate) return;
    try {
      const res = await fetch("/api/labeling/save", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ candidate_id: currentCandidate.id, corrected_fields: formData, action: "approved" })
      });
      if (res.ok) { toast.success("Candidate approved for training!"); loadProgress(); loadNextCandidate(); }
      else toast.error("Failed to approve candidate");
    } catch { toast.error("Failed to approve candidate"); }
  };

  const getConfidenceBadge = (c: number) => {
    if (c >= 0.9) return "bg-emerald-50 text-emerald-700 border-emerald-200";
    if (c >= 0.7) return "bg-amber-50 text-amber-700 border-amber-200";
    return "bg-red-50 text-red-700 border-red-200";
  };

  const progressPct = progress.total > 0 ? (progress.labeled / progress.total) * 100 : 0;

  const TagInput = ({ label, type, value, onChange, onAdd }: {
    label: string; type: keyof FormData; value: string;
    onChange: (v: string) => void; onAdd: () => void;
  }) => {
    const colors = TAG_COLORS[type as string] || TAG_COLORS.skills;
    return (
      <div>
        <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">{label}</label>
        <div className="flex gap-2 mb-2">
          <input type="text" value={value} onChange={(e) => onChange(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && (e.preventDefault(), onAdd(), onChange(""))}
            className="flex-1 px-3 py-2 border border-slate-200 rounded-xl text-xs focus:ring-2 focus:ring-brand-500 focus:border-transparent outline-none"
            placeholder={`Add ${label.toLowerCase()}...`} />
          <button type="button" onClick={() => { onAdd(); onChange(""); }}
            className="px-3 py-2 text-white text-xs font-bold rounded-xl transition-colors"
            style={{ background: '#7C3AED' }}>
            Add
          </button>
        </div>
        {(formData[type] as string[]).length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {(formData[type] as string[]).map((item, i) => (
              <span key={i} className={`flex items-center gap-1 px-2.5 py-1 text-xs font-semibold rounded-lg border ${colors.bg} ${colors.text} ${colors.border}`}>
                {item}
                <button type="button" onClick={() => removeTag(type, item)} className="opacity-60 hover:opacity-100 transition-opacity ml-0.5">
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}
          </div>
        )}
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-[3px] border-purple-100 mx-auto mb-3" style={{ borderTopColor: '#7C3AED' }} />
          <p className="text-sm font-medium text-slate-400">Loading candidate...</p>
        </div>
      </div>
    );
  }

  if (!currentCandidate) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
        <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-12 text-center max-w-md w-full">
          <div className="h-16 w-16 bg-emerald-50 rounded-2xl flex items-center justify-center mx-auto mb-5">
            <CheckCircle className="w-8 h-8 text-emerald-500" />
          </div>
          <h2 className="text-xl font-bold text-slate-800 mb-2">All Caught Up!</h2>
          <p className="text-sm text-slate-500 mb-6">All candidates have been labeled. Great work!</p>
          <div className="bg-slate-50 rounded-xl p-4 mb-6">
            <div className="text-3xl font-black mb-1" style={{ color: '#7C3AED' }}>{progress.labeled} / {progress.total}</div>
            <p className="text-xs text-slate-500">candidates labeled</p>
            <div className="mt-3 w-full bg-slate-200 rounded-full h-2 overflow-hidden">
              <div className="h-2 rounded-full" style={{ background: 'linear-gradient(to right, #7C3AED, #9333EA)', width: `${progressPct}%` }} />
            </div>
            <p className="text-xs text-slate-500 mt-2">Estimated accuracy: {Math.round(progress.accuracy_estimate * 100)}%</p>
          </div>
          <button onClick={() => navigate("/dashboard")}
            className="w-full px-5 py-2.5 text-white text-sm font-bold rounded-xl transition-colors"
            style={{ background: '#7C3AED' }}>
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="p-6 sm:p-8 max-w-7xl mx-auto space-y-5">

        {/* Header */}
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-4">
            <div className="p-2.5 rounded-xl shadow-sm text-white flex-shrink-0" style={{ background: 'linear-gradient(135deg, #7C3AED 0%, #9333EA 100%)' }}>
              <Tag className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-800">Resume Labeling</h1>
              <p className="text-slate-500 text-sm font-medium">Manually correct and approve AI-parsed resume data</p>
            </div>
          </div>
          {/* Progress */}
          <div className="hidden sm:flex flex-col items-end bg-white border border-slate-100 rounded-xl px-5 py-3 shadow-sm">
            <div className="text-xl font-black text-slate-800">{progress.labeled}<span className="text-slate-300 text-sm font-semibold"> / {progress.total}</span></div>
            <div className="w-24 bg-slate-100 rounded-full h-1.5 mt-1.5 mb-1 overflow-hidden">
              <div className="h-1.5 rounded-full transition-all" style={{ background: '#7C3AED', width: `${progressPct}%` }} />
            </div>
            <p className="text-slate-400 text-[10px] font-bold uppercase tracking-wider">{Math.round(progressPct)}% COMPLETE</p>
          </div>
        </div>

        {/* Candidate Info Strip */}
        <div className="bg-white rounded-2xl border border-slate-100 shadow-sm px-5 py-3.5 flex items-center gap-4">
          <div className="h-10 w-10 bg-gradient-to-br from-brand-100 to-brand-200 rounded-xl flex items-center justify-center flex-shrink-0">
            <span className="text-sm font-black text-brand-700">{currentCandidate.full_name?.charAt(0)?.toUpperCase()}</span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-bold text-slate-800 truncate">{currentCandidate.full_name}</p>
            <p className="text-xs text-slate-400 truncate">{currentCandidate.email}</p>
          </div>
          {currentCandidate.parsing_status?.confidence_score && (
            <span className={`flex-shrink-0 px-2.5 py-1 text-xs font-bold rounded-full border ${getConfidenceBadge(currentCandidate.parsing_status.confidence_score)}`}>
              AI: {Math.round(currentCandidate.parsing_status.confidence_score * 100)}%
            </span>
          )}
          <div className="flex items-center gap-1.5 text-xs text-slate-400 flex-shrink-0">
            <Cpu className="w-3.5 h-3.5" />
            <span>Reviewing</span>
          </div>
        </div>

        {/* Main 2-col Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {/* Left: Raw Text */}
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden flex flex-col">
            <div className="px-5 py-4 border-b border-slate-50 flex items-center gap-2">
              <div className="h-6 w-6 bg-brand-50 rounded-lg flex items-center justify-center">
                <Tag className="w-3 h-3 text-brand-600" />
              </div>
              <h2 className="text-sm font-bold text-slate-800">Raw Resume Text</h2>
            </div>
            <div className="flex-1 p-4">
              <div className="h-[480px] overflow-y-auto bg-slate-50 rounded-xl p-4 border border-slate-100">
                <pre className="text-xs text-slate-600 whitespace-pre-wrap font-mono leading-relaxed">
                  {currentCandidate.raw_resume_text || "No raw text available"}
                </pre>
              </div>
            </div>
          </div>

          {/* Right: Edit Form */}
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden flex flex-col">
            <div className="px-5 py-4 border-b border-slate-50 flex items-center gap-2">
              <div className="h-6 w-6 bg-brand-50 rounded-lg flex items-center justify-center">
                <CheckCircle className="w-3 h-3 text-brand-600" />
              </div>
              <h2 className="text-sm font-bold text-slate-800">Corrected Data</h2>
            </div>
            <div className="flex-1 p-5 overflow-y-auto max-h-[480px]">
              <div className="space-y-4">
                {/* Basic fields */}
                {[
                  { label: "Full Name", key: "name" as keyof FormData, type: "text", placeholder: "Full name" },
                  { label: "Email", key: "email" as keyof FormData, type: "email", placeholder: "Email address" },
                  { label: "Phone", key: "phone" as keyof FormData, type: "tel", placeholder: "Phone number" },
                ].map(({ label, key, type, placeholder }) => (
                  <div key={key}>
                    <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">{label}</label>
                    <input type={type} value={formData[key] as string}
                      onChange={(e) => setFormData((p) => ({ ...p, [key]: e.target.value }))}
                      className="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-brand-500 focus:border-transparent outline-none"
                      placeholder={placeholder} />
                  </div>
                ))}

                <TagInput label="Skills" type="skills" value={currentSkill} onChange={setCurrentSkill} onAdd={() => addTag("skills", currentSkill)} />
                <TagInput label="Companies" type="companies" value={currentCompany} onChange={setCurrentCompany} onAdd={() => addTag("companies", currentCompany)} />
                <TagInput label="Job Titles" type="job_titles" value={currentJobTitle} onChange={setCurrentJobTitle} onAdd={() => addTag("job_titles", currentJobTitle)} />
                <TagInput label="Education Degrees" type="education_degrees" value={currentDegree} onChange={setCurrentDegree} onAdd={() => addTag("education_degrees", currentDegree)} />
                <TagInput label="Universities" type="universities" value={currentUniversity} onChange={setCurrentUniversity} onAdd={() => addTag("universities", currentUniversity)} />
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-4 flex items-center justify-between gap-3">
          <button onClick={handleSkip}
            className="flex items-center gap-2 px-5 py-2.5 border border-slate-200 text-slate-600 hover:bg-slate-50 text-sm font-semibold rounded-xl transition-colors">
            <SkipForward className="w-4 h-4" /> Skip
          </button>
          <div className="flex items-center gap-3">
            <button onClick={handleCorrectAndNext}
              className="flex items-center gap-2 px-6 py-2.5 text-white text-sm font-bold rounded-xl transition-colors shadow-sm"
              style={{ background: '#7C3AED' }}>
              Correct & Next <ChevronRight className="w-4 h-4" />
            </button>
            <button onClick={handleApprove}
              className="flex items-center gap-2 px-6 py-2.5 text-white text-sm font-bold rounded-xl transition-colors shadow-sm"
              style={{ background: '#059669' }}>
              <CheckCircle className="w-4 h-4" /> Approve
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
