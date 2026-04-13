import { useEffect, useState } from "react";
import { useCandidateStore } from "../store/useCandidateStore";
import { useJobStore } from "../store/useJobStore";
import { 
  Users, FileText, CheckCircle2, 
  TrendingUp, BarChart3, Clock, ArrowUpRight, 
  Search, Filter, Download, MoreVertical,
  Briefcase, Sparkles, Star, MessageSquare, Send, ChevronRight
} from "lucide-react";
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, ResponsiveContainer, AreaChart, Area,
  PieChart, Pie, Cell, Legend
} from 'recharts';
import { useNavigate } from "react-router-dom";

const monthlyData = [
  { name: "Nov", count: 0.5 },
  { name: "Dec", count: 0.5 },
  { name: "Jan", count: 0.5 },
  { name: "Feb", count: 0.5 },
  { name: "Mar", count: 1 },
  { name: "Apr", count: 5 },
];

const skillsData = [
  { name: 'SQL', value: 4, color: '#8B5CF6' },
  { name: 'Testing', value: 4, color: '#2DD4BF' },
  { name: 'Python', value: 3, color: '#6366F1' },
  { name: 'AWS', value: 3, color: '#F97316' },
  { name: 'GCP', value: 3, color: '#EF4444' },
  { name: 'Azure', value: 3, color: '#EAB308' },
];

const scoreData = [
  { name: '0-20', count: 0 },
  { name: '21-40', count: 0 },
  { name: '41-60', count: 1 },
  { name: '61-80', count: 4 },
  { name: '81-100', count: 0 },
];

const recentResumes = [
  { id: 1, name: 'Java', date: '4/11/2026', score: 70, status: 'completed', avatar: 'J', color: 'bg-orange-500' },
  { id: 2, name: 'Elias Thorne', date: '4/11/2026', score: 76, status: 'completed', avatar: 'ET', color: 'bg-pink-500' },
  { id: 3, name: 'Professional Summary', date: '4/11/2026', score: 56, status: 'completed', avatar: 'PS', color: 'bg-orange-500' },
];
export default function DashboardPage() {
  const navigate = useNavigate();
  const { candidates, fetchCandidates } = useCandidateStore();
  const { jobs, fetchJobs, matchResults } = useJobStore();

  useEffect(() => {
    fetchCandidates();
    fetchJobs();
  }, [fetchCandidates, fetchJobs]);

  const stats = [
    { label: "Total Resumes", value: "5", icon: <FileText size={22} strokeWidth={2.5} />, trend: "+12.5%", color: "text-white", bg: "bg-indigo-600", trendColor: "text-emerald-500", shadow: "shadow-indigo-500/20", line: "bg-indigo-500" },
    { label: "Analyzed Candidates", value: "5", icon: <Users size={22} strokeWidth={2.5} />, trend: "+8.2%", color: "text-white", bg: "bg-emerald-500", trendColor: "text-emerald-500", shadow: "shadow-emerald-500/20", line: "bg-emerald-500" },
    { label: "Avg. Match Score", value: "69%", icon: <Star size={22} strokeWidth={2.5} />, trend: "+5.4%", color: "text-white", bg: "bg-orange-500", trendColor: "text-emerald-500", shadow: "shadow-orange-500/20", line: "bg-orange-500" },
    { label: "Avg. Processing Time", value: "0 days", icon: <Clock size={22} strokeWidth={2.5} />, trend: "-2.1%", color: "text-white", bg: "bg-blue-500", trendColor: "text-rose-500", shadow: "shadow-blue-500/20", line: "bg-blue-500" },
  ];

  return (
    <div className="relative min-h-[calc(100vh-140px)] animate-in fade-in duration-700 py-6 px-6 max-w-[1400px] mx-auto overflow-hidden">
      
      {/* Dynamic Mesh Gradient Background Blobs (Slightly dimmed for better contrast) */}
      <div className="absolute inset-0 -z-10 pointer-events-none overflow-hidden opacity-80">
         <div className="absolute top-[-10%] right-[20%] w-[500px] h-[500px] bg-indigo-500/10 rounded-full blur-[120px] animate-pulse duration-[8s]" />
         <div className="absolute bottom-[10%] left-[5%] w-[600px] h-[600px] bg-teal-400/10 rounded-full blur-[140px] animate-pulse duration-[10s] delay-1000" />
         <div className="absolute top-[40%] right-[-10%] w-[400px] h-[400px] bg-purple-500/10 rounded-full blur-[100px] animate-pulse duration-[12s] delay-2000" />
      </div>

      
      {/* Stats Grid - More Compact & High Contrast */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-6 relative z-10">
        {stats.map((stat, i) => (
          <div key={i} className="group p-5 bg-white/95 backdrop-blur-3xl rounded-[24px] border border-white/80 shadow-2xl shadow-indigo-900/5 hover:border-indigo-100 transition-all duration-500 relative overflow-hidden">
            {/* Animated Bottom Line - Touch/Hover Reveal */}
            <div className={`absolute bottom-0 left-0 h-[3px] w-0 transition-all duration-500 group-hover:w-full ${stat.line}`} />
            
            <div className="absolute top-0 right-0 w-24 h-24 bg-indigo-500/5 rounded-full blur-2xl group-hover:bg-indigo-500/10 transition-colors duration-700" />
            
            <div className="flex justify-between items-center mb-6 relative z-10">
              <div className={`w-12 h-12 rounded-[18px] ${stat.bg} ${stat.color} flex items-center justify-center shadow-xl ${stat.shadow} border-2 border-white/20 relative overflow-hidden group-hover:scale-110 transition-transform duration-500`}>
                <div className="absolute inset-0 bg-white/20 opacity-0 group-hover:opacity-100 transition-opacity" />
                <span className="relative z-10 drop-shadow-sm">{stat.icon}</span>
              </div>
              <div className={`flex items-center gap-1 text-[9px] font-bold ${stat.trendColor} bg-slate-50/80 backdrop-blur-md px-2.5 py-1 rounded-full border border-slate-100 shadow-sm`}>
                <ArrowUpRight size={10} />
                {stat.trend}
              </div>
            </div>
            <div className="relative z-10">
               <h3 className="text-3xl font-bold text-slate-700 tracking-tighter mb-0.5 leading-none transition-transform duration-500 group-hover:translate-x-1 origin-left">{stat.value}</h3>
               <p className="text-[9px] font-bold uppercase tracking-[0.25em] text-slate-400 opacity-90">{stat.label}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-8 relative z-10">
        
        {/* Monthly Applications Chart - More Compact */}
        <div className="lg:col-span-8 bg-white/90 backdrop-blur-3xl p-6 rounded-[32px] border border-white/60 shadow-2xl shadow-indigo-900/5 group/chart">
           <div className="flex items-center justify-between mb-8">
              <div>
                 <h3 className="text-[11px] font-bold text-slate-700 uppercase tracking-[0.25em] leading-none mb-1.5">MONTHLY APPLICATIONS</h3>
                 <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest opacity-80 leading-none">Submission velocity over time</p>
              </div>
              <div className="w-9 h-9 rounded-lg bg-slate-50 flex items-center justify-center text-slate-300 border border-slate-100 group-hover/chart:border-indigo-200 transition-colors duration-500">
                 <BarChart3 size={16} />
              </div>
           </div>
           
           <div className="h-[240px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={monthlyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366F1" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#6366F1" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" opacity={0.5} />
                  <XAxis 
                    dataKey="name" 
                    axisLine={false} 
                    tickLine={false} 
                    tick={{ fill: '#94A3B8', fontSize: 9, fontWeight: 800 }}
                    dy={10}
                  />
                  <YAxis 
                    axisLine={false} 
                    tickLine={false} 
                    tick={{ fill: '#94A3B8', fontSize: 9, fontWeight: 800 }}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'rgba(255, 255, 255, 0.95)', 
                      backdropFilter: 'blur(20px)',
                      borderRadius: '20px', 
                      border: '1px solid rgba(255, 255, 255, 0.4)', 
                      boxShadow: '0 20px 40px rgba(0,0,0,0.1)', 
                      fontSize: '10px',
                      fontWeight: 800,
                      padding: '12px'
                    }}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="count" 
                    stroke="#6366F1" 
                    strokeWidth={4}
                    fillOpacity={1} 
                    fill="url(#colorCount)" 
                    animationDuration={2000}
                  />
                </AreaChart>
              </ResponsiveContainer>
           </div>
        </div>

        {/* Top Skills Detected Chart - Compact */}
        <div className="lg:col-span-4 bg-white/90 backdrop-blur-3xl p-6 rounded-[32px] border border-white/60 shadow-2xl shadow-indigo-900/5 group/skills">
           <div className="flex items-center justify-between mb-6">
              <div>
                 <h3 className="text-[11px] font-bold text-slate-700 uppercase tracking-[0.25em] leading-none mb-1.5">TOP SKILLS</h3>
                 <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest opacity-80 leading-none">Core candidate expertise</p>
              </div>
              <Sparkles size={16} className="text-indigo-500 animate-pulse" />
           </div>
           
           <div className="h-[260px] w-full flex flex-col items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={skillsData}
                    cx="50%"
                    cy="45%"
                    innerRadius={55}
                    outerRadius={80}
                    paddingAngle={6}
                    dataKey="value"
                    strokeWidth={0}
                  >
                    {skillsData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'white', 
                      borderRadius: '16px', 
                      border: 'none', 
                      boxShadow: '0 10px 30px rgba(0,0,0,0.05)',
                      fontSize: '10px'
                    }}
                  />
                  <Legend 
                    verticalAlign="bottom" 
                    align="center"
                    iconType="circle"
                    formatter={(value, entry: any) => (
                      <span className="text-[8px] font-bold text-slate-500 uppercase tracking-[0.2em] px-2">
                        {value} ({entry.payload.value})
                      </span>
                    )}
                  />
                </PieChart>
              </ResponsiveContainer>
           </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-5 relative z-10">
         
         {/* Processing Queue - More Compact */}
         <div className="bg-white/90 backdrop-blur-3xl p-6 rounded-[32px] border border-white/60 shadow-2xl shadow-indigo-900/5 flex flex-col">
            <div className="flex items-center justify-between mb-6">
               <div>
                  <h3 className="text-[11px] font-bold text-slate-700 uppercase tracking-[0.25em] leading-none mb-1.5">Processing Queue</h3>
                  <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest opacity-80 leading-none">Active extraction tasks</p>
               </div>
               <div className="px-3 py-1 bg-indigo-50 rounded-full text-indigo-600 font-bold text-[9px] border border-indigo-100">
                  0 ACTIVE
               </div>
            </div>
            <div className="flex-1 flex flex-col items-center justify-center py-6 opacity-60">
               <div className="w-16 h-16 bg-slate-50 rounded-[22px] flex items-center justify-center mb-4 shadow-inner border border-white/60">
                  <Clock size={28} className="text-slate-300" />
               </div>
               <p className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em]">Queue is currently clear</p>
            </div>
         </div>

         {/* Recent Resumes - More Compact */}
         <div className="bg-white/90 backdrop-blur-3xl p-6 rounded-[32px] border border-white/60 shadow-2xl shadow-indigo-900/5">
            <div className="flex items-center justify-between mb-8">
               <div>
                  <h3 className="text-[11px] font-bold text-slate-700 uppercase tracking-[0.25em] leading-none mb-1.5">Recent Resumes</h3>
                  <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest opacity-80 leading-none">Latest submissions</p>
               </div>
               <button onClick={() => navigate('/candidates')} className="group flex items-center gap-2 px-4 py-2.5 bg-indigo-50 text-indigo-600 text-[9px] font-bold uppercase tracking-widest rounded-xl hover:bg-indigo-600 hover:text-white transition-all duration-500 border border-indigo-100">
                  View All
                  <ChevronRight size={12} className="group-hover:translate-x-1 transition-transform" />
               </button>
            </div>
            <div className="space-y-4">
               {recentResumes.map((resume) => (
                 <div key={resume.id} className="group flex items-center justify-between p-3.5 bg-white/40 hover:bg-white/80 rounded-2xl border border-transparent hover:border-white/60 hover:shadow-xl hover:shadow-indigo-500/5 transition-all duration-500">
                    <div className="flex items-center gap-4">
                       <div className={`w-11 h-11 rounded-xl ${resume.color} flex items-center justify-center text-white text-[10px] font-bold shadow-lg shadow-inner relative overflow-hidden`}>
                          <div className="absolute inset-0 bg-white/10 group-hover:translate-x-full transition-transform duration-700" />
                          <span className="relative z-10">{resume.avatar}</span>
                       </div>
                       <div>
                          <p className="text-sm font-bold text-slate-700 tracking-tight group-hover:text-indigo-600 transition-colors duration-300">{resume.name}</p>
                          <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest">{resume.date}</p>
                       </div>
                    </div>
                    <div className="flex items-center gap-6 pr-2">
                       <div className="text-right">
                          <p className="text-[8px] font-bold text-slate-400 mb-0.5 leading-none uppercase">SCORE</p>
                          <span className="text-lg font-bold text-indigo-600 tracking-tighter">{resume.score}%</span>
                       </div>
                       <div className="flex items-center gap-1.5">
                          <button className="w-8 h-8 rounded-lg bg-slate-50 flex items-center justify-center text-slate-400 hover:bg-indigo-50 hover:text-indigo-500 transition-all border border-slate-100"><FileText size={14} /></button>
                          <button className="w-8 h-8 rounded-lg bg-slate-50 flex items-center justify-center text-slate-400 hover:bg-indigo-50 hover:text-indigo-500 transition-all border border-slate-100"><Download size={14} /></button>
                       </div>
                    </div>
                 </div>
               ))}
            </div>
         </div>
      </div>

      {/* Score Distribution Chart - Compact Profile */}
      <div className="bg-white/90 backdrop-blur-3xl p-8 rounded-[40px] border border-white/60 shadow-2xl shadow-indigo-900/5 relative z-10 group/score">
         <div className="flex items-center justify-between mb-8">
            <div>
               <h3 className="text-[11px] font-bold text-slate-700 uppercase tracking-[0.25em] leading-none mb-2">SCORE DISTRIBUTION</h3>
               <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest opacity-80 leading-none">Global candidate quality mapping</p>
            </div>
            <div className="w-10 h-10 rounded-xl bg-indigo-50 flex items-center justify-center text-indigo-500 border border-indigo-100 group-hover/score:rotate-12 transition-transform duration-500">
               <TrendingUp size={20} />
            </div>
         </div>
         <div className="h-[200px] w-full">
            <ResponsiveContainer width="100%" height="100%">
               <BarChart data={scoreData} margin={{ top: 0, right: 30, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#6366F1" />
                      <stop offset="100%" stopColor="#2DD4BF" />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" opacity={0.5} />
                  <XAxis 
                    dataKey="name" 
                    axisLine={false} 
                    tickLine={false} 
                    tick={{ fill: '#94A3B8', fontSize: 9, fontWeight: 800 }}
                  />
                  <YAxis 
                    axisLine={false} 
                    tickLine={false} 
                    tick={{ fill: '#94A3B8', fontSize: 9, fontWeight: 800 }}
                  />
                  <Tooltip 
                    cursor={{ fill: 'rgba(99, 102, 241, 0.05)', radius: [10, 10, 0, 0] }}
                    contentStyle={{ 
                       borderRadius: '16px', 
                       border: '1px solid rgba(255, 255, 255, 0.4)', 
                       backgroundColor: 'white', 
                       boxShadow: '0 20px 40px rgba(0,0,0,0.05)', 
                       fontSize: '10px',
                       fontWeight: 800
                    }}
                  />
                  <Bar 
                    dataKey="count" 
                    fill="url(#barGradient)" 
                    radius={[10, 10, 10, 10]}
                    barSize={80}
                    animationDuration={2500}
                  />
               </BarChart>
            </ResponsiveContainer>
         </div>
      </div>

    </div>
  );
}

function Plus({ size }: { size: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 5v14M5 12h14" />
    </svg>
  );
}
