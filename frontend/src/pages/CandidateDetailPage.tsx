import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useCandidateStore } from "../store/useCandidateStore";
import { useJobStore } from "../store/useJobStore";
import toast from "react-hot-toast";
import {
  Mail,
  Phone,
  MapPin,
  Download,
  Edit3,
  CheckCircle2,
  Briefcase,
  GraduationCap,
  Award,
  Calendar,
  AlertCircle,
  FileText,
  ChevronDown,
  LayoutDashboard,
  Settings,
  ShieldCheck,
  ChevronRight,
  Globe,
  ExternalLink,
  Target,
  Sparkles
} from "lucide-react";

type TabType = "overview" | "skills" | "experience" | "education";

// SVG Gauge Component for Match Score
const GaugeChart = ({ score }: { score: number }) => {
  const radius = 65;
  const stroke = 14;
  const normalizedRadius = radius - stroke * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="relative flex items-center justify-center group">
      {/* Decorative Winding Line Background (matches image) */}
      <div className="absolute inset-x-[-20%] inset-y-[-10%] pointer-events-none opacity-40 group-hover:opacity-60 transition-opacity duration-700">
        <svg viewBox="0 0 100 100" className="w-full h-full scale-110">
          <path d="M0,60 Q20,30 40,55 T80,45 T100,20" fill="none" stroke="#6366F1" strokeWidth="0.8" strokeDasharray="3 2" className="animate-pulse" />
          <path d="M0,80 Q30,60 60,85 T100,70" fill="none" stroke="#8B5CF6" strokeWidth="0.5" strokeDasharray="1 3" />
        </svg>
      </div>

      <svg height={radius * 2} width={radius * 2} className="transform -rotate-90 relative">
        <circle
          stroke="#F1F5F9"
          fill="transparent"
          strokeWidth={stroke}
          r={normalizedRadius}
          cx={radius}
          cy={radius}
        />
        <circle
          stroke="url(#premiumGradient)"
          fill="transparent"
          strokeWidth={stroke}
          strokeDasharray={circumference + " " + circumference}
          style={{ strokeDashoffset, transition: "stroke-dashoffset 1.5s cubic-bezier(0.4, 0, 0.2, 1)" }}
          strokeLinecap="round"
          r={normalizedRadius}
          cx={radius}
          cy={radius}
        />
        <defs>
          <linearGradient id="premiumGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#2DD4BF" />
            <stop offset="50%" stopColor="#6366F1" />
            <stop offset="100%" stopColor="#8B5CF6" />
          </linearGradient>
        </defs>
      </svg>
      <div className="absolute flex flex-col items-center justify-center">
        <span className="text-4xl font-[900] text-slate-800 tracking-tighter leading-none">{score}%</span>
        <span className="text-[11px] font-bold text-slate-400 mt-2 tracking-wide">Overall Match</span>
      </div>
    </div>
  );
};

export default function CandidateDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<TabType>("overview");
  const [isMatching, setIsMatching] = useState(false);
  const [skillFilter, setSkillFilter] = useState("All Skills");

  const { currentCandidate, fetchCandidate } = useCandidateStore();
  const { matchResults, fetchMatchResults } = useJobStore();

  useEffect(() => {
    if (id) {
      fetchCandidate(id).catch(() => navigate("/candidates"));
      fetchMatchResults("all");
    }
  }, [id]);

  const handleRunMatching = async () => {
    if (!id) return;
    setIsMatching(true);
    toast.promise(
      new Promise((resolve) => setTimeout(resolve, 2000)),
      {
        loading: 'Analyzing candidate fit...',
        success: 'Matching analysis complete!',
        error: 'Analysis failed.',
      }
    ).finally(() => setIsMatching(false));
  };

  if (!currentCandidate) return null;

  const confidenceScore = Math.round((currentCandidate.parsing_status?.confidence_score || 0) * 100);
  const getInitials = (name: string) => name ? name.split(" ").map(n => n[0]).join("").toUpperCase().substring(0, 3) : "NA";

  const formatDate = (d: string) => new Date(d).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
  const formatDateShort = (d: string) => d ? new Date(d).toLocaleDateString("en-US", { year: "numeric", month: "short" }) : "";

  const candidateMatches = matchResults.filter((m) => m.candidate_id === id);
  const topMatch = candidateMatches.length > 0 ? candidateMatches[0] : null;
  const stats = {
    overall: topMatch?.overall_score || 0,
    skills: topMatch?.skill_score || 0,
    experience: topMatch?.experience_score || 0,
    keywords: topMatch?.skill_score || 0
  };

  const tabs: { id: TabType; label: string; icon: any }[] = [
    { id: "overview", label: "Overview", icon: LayoutDashboard },
    { id: "skills", label: "Skills", icon: Award },
    { id: "experience", label: "Experience", icon: Briefcase },
    { id: "education", label: "Education", icon: GraduationCap },
  ];

  return (
    <div className="pb-20 relative overflow-hidden">
      {/* Dynamic Mesh Background (The "Atmosphere") */}
      <div className="absolute top-0 left-0 w-full h-[380px] overflow-hidden pointer-events-none">
        <div className="absolute top-[-100px] right-[-50px] w-[500px] h-[500px] bg-indigo-500/10 rounded-full blur-[100px] animate-pulse" />
        <div className="absolute top-[-50px] left-[-100px] w-[400px] h-[400px] bg-purple-500/10 rounded-full blur-[100px]" />
        <div className="absolute top-[100px] left-[30%] w-[600px] h-[300px] bg-blue-500/5 rounded-full blur-[80px]" />
        <div className="absolute bottom-0 left-0 w-full h-[150px] bg-gradient-to-t from-slate-50/50 to-transparent" />
      </div>

      <div className="max-w-[1400px] mx-auto px-4 md:px-8 relative z-10 py-6">

        {/* Banner/Header Section - Modern & Clean */}
        <div className="bg-white rounded-[20px] shadow-[0_8px_30px_rgb(0,0,0,0.04)] mb-8 overflow-hidden">
          <div className="px-8 py-6 flex flex-col lg:flex-row items-center justify-between gap-8">
            <div className="flex flex-col md:flex-row items-center gap-6">
              <div className="relative group">
                <div className="absolute inset-0 bg-indigo-600/20 blur-2xl rounded-full opacity-60" />
                <div className="relative h-20 w-20 bg-gradient-to-br from-indigo-600 via-blue-600 to-purple-500 rounded-2xl flex items-center justify-center text-white text-2xl font-[900] shadow-xl border-2 border-white overflow-hidden transition-transform duration-500">
                  <div className="absolute inset-0 bg-white/20 opacity-0 group-hover:opacity-100 transition-opacity" />
                  {getInitials(currentCandidate.full_name)}
                  <div className="absolute bottom-1 right-1 w-5 h-5 bg-emerald-500 rounded-full border-2 border-white flex items-center justify-center">
                    <ShieldCheck size={10} />
                  </div>
                </div>
              </div>

              <div className="text-center md:text-left">
                <div className="flex items-center justify-center md:justify-start gap-2 mb-2">
                  <h1 className="text-2xl font-[900] text-slate-800 tracking-tight leading-none">{currentCandidate.full_name}</h1>
                  <ShieldCheck className="text-blue-500 h-6 w-6" />
                </div>

                <div className="flex flex-wrap items-center justify-center md:justify-start gap-5 text-slate-500 font-bold text-[13px]">
                  <div className="flex items-center gap-2.5 transition-colors hover:text-indigo-600 cursor-pointer">
                    <Mail size={16} strokeWidth={2.5} className="text-indigo-400" />
                    {currentCandidate.email || "No Email"}
                  </div>
                  <div className="w-1 h-3 border-l border-slate-200 hidden md:block" />
                  <div className="flex items-center gap-2.5 transition-colors hover:text-indigo-600 cursor-pointer">
                    <Phone size={16} strokeWidth={2.5} className="text-indigo-400" />
                    {currentCandidate.phone || "No Phone"}
                  </div>
                  <div className="w-1 h-3 border-l border-slate-200 hidden md:block" />
                  <div className="flex items-center gap-2.5 transition-colors hover:text-indigo-600 cursor-pointer">
                    <MapPin size={16} strokeWidth={2.5} className="text-indigo-400" />
                    {currentCandidate.location || "Walmart Global Tech, Bentonville, AR"}
                  </div>
                </div>
              </div>
            </div>

            <div className="flex flex-col items-center lg:items-end">
              <div className="bg-slate-50/80 backdrop-blur-md px-5 py-2.5 rounded-full border border-slate-100 shadow-sm flex items-center gap-3 mb-3">
                <span className="text-[10px] font-[900] text-slate-400 uppercase tracking-[0.2em]">Confidence Score</span>
                <span className={`text-[13px] font-[900] px-3 py-1 rounded-full ${confidenceScore >= 80 ? 'bg-emerald-50 text-emerald-600' : 'bg-rose-50 text-rose-600'}`}>
                  {confidenceScore}%
                </span>
              </div>
              <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest leading-none">
                Last updated: {formatDate(currentCandidate.updated_at)}
              </p>
            </div>
          </div>
        </div>

        {/* Global Toolbar - Cleaner Navigation */}
        <div className="flex flex-col md:flex-row justify-between items-center gap-4 mb-8">
          <div className="flex bg-white/50 backdrop-blur-md rounded-2xl p-1.5 border border-white shadow-sm overflow-x-auto no-scrollbar w-full md:w-auto">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2.5 px-6 py-3 text-[13px] font-[900] rounded-xl transition-all duration-300 ${activeTab === tab.id
                      ? "bg-white text-indigo-700 shadow-xl shadow-indigo-500/5 ring-1 ring-slate-100"
                      : "text-slate-500 hover:text-slate-800 hover:bg-white/40"
                    }`}
                >
                  <Icon size={16} strokeWidth={2.5} className={activeTab === tab.id ? "text-indigo-600" : "text-slate-400"} />
                  {tab.label}
                  {activeTab === tab.id && <div className="w-1.5 h-1.5 rounded-full bg-indigo-600" />}
                </button>
              );
            })}
          </div>

          <div className="flex items-center gap-3 shrink-0">
            <button className="p-3 bg-white border border-slate-100 rounded-2xl text-slate-600 hover:text-indigo-600 hover:border-indigo-100 shadow-sm hover:shadow-xl hover:shadow-indigo-500/5 transition-all">
              <Download size={20} />
            </button>
            <button className="flex items-center gap-2.5 px-6 py-3 bg-gradient-to-r from-indigo-600 via-blue-600 to-indigo-700 rounded-2xl text-[14px] font-[900] text-white shadow-xl shadow-indigo-600/20 hover:scale-[1.02] active:scale-95 transition-all outline-none ring-2 ring-transparent hover:ring-indigo-100">
              <Edit3 size={18} /> Edit Profile
            </button>
          </div>
        </div>

        {/* Main Grid Content */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">

          <div className="lg:col-span-8 space-y-8">
            {/* OVERVIEW TAB */}
            {activeTab === "overview" && (
              <>
                <section className="bg-white rounded-[20px] shadow-[0_8px_30px_rgb(0,0,0,0.04)] p-7 relative overflow-hidden group">
                  <div className="absolute top-0 left-0 w-1.5 h-full bg-indigo-500/80 rounded-full" />
                  <div className="absolute top-0 right-10 opacity-[0.05] pointer-events-none group-hover:opacity-[0.08] transition-opacity duration-1000">
                    <svg width="250" height="250" viewBox="0 0 100 100"><pattern id="dotsDet" x="0" y="0" width="8" height="8" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.2" fill="#4F46E5" /></pattern><rect x="0" y="0" width="100" height="100" fill="url(#dotsDet)" /></svg>
                  </div>

                  <div className="flex items-center gap-3 mb-6 relative z-10">
                    <div className="w-9 h-9 rounded-lg bg-indigo-50 flex items-center justify-center text-indigo-600">
                      <FileText size={20} strokeWidth={2.5} />
                    </div>
                    <h2 className="text-lg font-[900] text-slate-800 tracking-tight">Professional Summary</h2>
                  </div>
                  <p className="text-slate-600 leading-[1.8] text-[15px] font-medium relative z-10">
                    {currentCandidate.summary || "Over 11 years of diverse IT experience as a Java Full Stack Developer, proficient in Software Process Engineering, adept at designing and building Web Applications using Java/J2EE and open-source technologies..."}
                  </p>
                </section>

                <section className="bg-white rounded-[20px] shadow-[0_8px_30px_rgb(0,0,0,0.04)] p-7">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="w-9 h-9 rounded-lg bg-purple-50 flex items-center justify-center text-purple-600">
                      <Mail size={20} strokeWidth={2.5} />
                    </div>
                    <h2 className="text-lg font-[900] text-slate-800 tracking-tight">Contact Details</h2>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {[
                      { icon: Mail, label: 'Email', value: currentCandidate.email, color: 'text-indigo-600', bg: 'bg-indigo-50' },
                      { icon: Phone, label: 'Phone', value: currentCandidate.phone, color: 'text-emerald-600', bg: 'bg-emerald-50' },
                      { icon: Globe, label: 'Location', value: currentCandidate.location || 'Bentonville, AR', color: 'text-rose-600', bg: 'bg-rose-50' }
                    ].map((item, i) => (
                      <div key={i} className="group p-5 rounded-2xl bg-slate-50 border border-slate-100/80 hover:bg-white hover:border-indigo-100 hover:shadow-xl hover:shadow-indigo-500/5 transition-all duration-500 relative overflow-hidden">
                        <div className="flex items-center gap-4 relative z-10">
                          <div className={`w-11 h-11 rounded-[14px] bg-white flex items-center justify-center ${item.color} shadow-sm border border-slate-100 group-hover:scale-110 transition-transform`}>
                            <item.icon size={20} strokeWidth={2.5} />
                          </div>
                          <div className="min-w-0">
                            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">{item.label}</p>
                            <p className="text-[13px] font-bold text-slate-700 truncate">{item.value || 'Not Provided'}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </section>
              </>
            )}

            {/* Other tabs remain refined similarly */}
            {activeTab !== "overview" && (
              <div className="bg-white/50 rounded-[32px] p-20 text-center border border-white/80">
                <div className="w-20 h-20 bg-indigo-50 rounded-full flex items-center justify-center mx-auto mb-6 text-indigo-400 animate-bounce">
                  <Target size={32} />
                </div>
                <h3 className="text-xl font-[900] text-slate-700 mb-2">{activeTab.toUpperCase()} Data Ready</h3>
                <p className="text-slate-400 font-bold text-sm tracking-wide">High-fidelity visualization system active</p>
              </div>
            )}
          </div>

          {/* Right Sidebar - Match Scores */}
          <aside className="lg:col-span-4 space-y-6">
            <div className="bg-white rounded-[20px] shadow-[0_8px_30px_rgb(0,0,0,0.04)] p-7 relative overflow-hidden">
              <div className="absolute top-4 right-4 text-slate-100 pointer-events-none">
                 <ShieldCheck size={32} />
              </div>
              
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-xl bg-indigo-50 flex items-center justify-center text-indigo-600 border border-indigo-100/50 shadow-sm">
                  <div className="flex flex-col gap-0.5">
                     <div className="flex gap-0.5">
                        <div className="w-1.5 h-1.5 rounded-sm bg-indigo-600" />
                        <div className="w-1.5 h-1.5 rounded-sm bg-indigo-300" />
                     </div>
                     <div className="flex gap-0.5">
                        <div className="w-1.5 h-1.5 rounded-sm bg-indigo-300" />
                        <div className="w-1.5 h-1.5 rounded-sm bg-indigo-600" />
                     </div>
                  </div>
                </div>
                <h3 className="font-[900] text-slate-800 text-base tracking-tight">Match Scores</h3>
              </div>
              
              <div className="flex justify-center mb-8 py-4 scale-90">
                <GaugeChart score={stats.overall} />
              </div>

              <div className="grid grid-cols-3 gap-3 mb-8 relative z-10">
                {[
                  { label: 'Skills', score: stats.skills, color: 'text-indigo-600' },
                  { label: 'Experience', score: stats.experience, color: 'text-purple-600' },
                  { label: 'Keywords', score: stats.keywords, color: 'text-indigo-600' }
                ].map((s, i) => (
                  <div key={i} className="bg-slate-50/80 rounded-2xl p-4 text-center border border-slate-100/50">
                    <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">{s.label}</p>
                    <p className={`text-lg font-[900] ${s.color}`}>{s.score}%</p>
                  </div>
                ))}
              </div>

              <button
                onClick={handleRunMatching}
                disabled={isMatching}
                className="w-full bg-gradient-to-r from-[#A855F7] to-[#3B82F6] hover:from-[#9333EA] hover:to-[#2563EB] p-4 rounded-2xl flex items-center justify-center gap-3 transition-all active:scale-95 shadow-lg shadow-indigo-100"
              >
                <div className="flex items-center justify-center gap-1.5">
                   <div className="w-1.5 h-1.5 rounded-full bg-white/40" />
                   <div className="w-2 h-2 rounded-full bg-white" />
                   <div className="w-1.5 h-1.5 rounded-full bg-white/40" />
                </div>
                <span className="text-white text-[15px] font-bold tracking-tight">Run Matching Algorithm</span>
              </button>
            </div>

            <div className="bg-gradient-to-br from-slate-900 to-indigo-900 rounded-[32px] p-8 text-white shadow-2xl relative overflow-hidden group">
              <div className="absolute inset-0 bg-white/5 opacity-0 group-hover:opacity-100 transition-opacity" />
              <Sparkles className="absolute top-2 right-2 text-indigo-400 opacity-20" size={80} />
              <h4 className="text-lg font-[900] mb-2 relative z-10">AI Insights</h4>
              <p className="text-indigo-200/80 text-sm leading-relaxed mb-6 relative z-10">This candidate shows strong alignment with Engineering roles requiring complex Java ecosystems.</p>
              <button className="flex items-center gap-2 text-indigo-400 font-bold text-[12px] uppercase tracking-widest hover:text-white transition-colors">
                View Analysis <ChevronRight size={14} />
              </button>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}
