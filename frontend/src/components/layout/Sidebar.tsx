import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  FileSearch,
  Users,
  Briefcase,
  GitCompare,
  Settings,
  Sparkles,
  LogOut,
  ChevronRight,
} from "lucide-react";

const links = [
  { label: "Dashboard", path: "/", icon: LayoutDashboard },
  { label: "Resume Analyzer", path: "/upload", icon: FileSearch },
  { label: "Candidates", path: "/candidates", icon: Users },
  { label: "Jobs", path: "/jobs", icon: Briefcase },
  { label: "Matching", path: "/matching", icon: GitCompare },
  { label: "Settings", path: "/settings", icon: Settings },
];

type SidebarProps = {
  open?: boolean;
};

export default function Sidebar({ open = true }: SidebarProps) {
  return (
    <aside
      className={`hidden flex-shrink-0 overflow-hidden border-r border-slate-200/60 bg-white/80 backdrop-blur-3xl transition-all duration-300 ease-in-out lg:flex lg:flex-col ${
        open ? "w-64" : "w-0"
      }`}
    >
      <div className="flex flex-col h-full w-64 px-5 py-8">
        {/* Logo Section - Modern & Premium */}
        <div className="mb-10 flex items-center gap-4 px-2 translate-y-[-4px]">
          <div className="group relative">
            <div className="absolute inset-0 bg-indigo-500/20 blur-xl rounded-full scale-110 group-hover:scale-125 transition-transform duration-500 opacity-60" />
            <div className="relative flex h-11 w-11 items-center justify-center rounded-[14px] bg-gradient-to-br from-indigo-600 via-blue-600 to-teal-500 shadow-lg shadow-indigo-600/30 overflow-hidden">
               <div className="absolute inset-0 bg-white/20 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
               <Sparkles className="h-6 w-6 text-white group-hover:rotate-12 transition-transform duration-500" />
            </div>
          </div>
          <div>
            <h2 className="text-lg font-[900] text-slate-700 tracking-tight leading-none mb-1">ATS Hub</h2>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest leading-none opacity-80">AI Recruiter</p>
          </div>
        </div>

        {/* Navigation - High Fidelity */}
        <nav className="flex-1 flex flex-col gap-1.5 list-none">
          {links.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `group relative flex items-center justify-between rounded-2xl px-4 py-3.5 transition-all duration-500 ${
                    isActive
                      ? "bg-gradient-to-r from-teal-400 via-emerald-400 to-indigo-600 text-white shadow-xl shadow-teal-500/20"
                      : "text-slate-400 hover:bg-indigo-50/50 hover:text-slate-700"
                  }`
                }
              >
                <div className="flex items-center gap-3.5 relative z-10">
                  <div className="transition-transform duration-500 group-hover:scale-110">
                     <Icon size={18} strokeWidth={isActive ? 2.5 : 2} />
                  </div>
                  <span className={`text-[13px] font-bold tracking-tight ${isActive ? "opacity-100" : "opacity-80 group-hover:opacity-100 transition-opacity"}`}>
                    {item.label}
                  </span>
                </div>
                
                {isActive && (
                   <div className="absolute inset-0 rounded-2xl bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
                )}
                
                {!isActive && (
                   <ChevronRight size={14} className="opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-500 text-slate-300" />
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* User / Logout Section - Matching Aesthetic */}
        <div className="mt-auto pt-6 border-t border-slate-100/80">
          <button className="group w-full flex items-center justify-between p-3.5 rounded-2xl bg-white border border-slate-100 shadow-sm hover:shadow-xl hover:shadow-indigo-500/5 hover:border-indigo-100 transition-all duration-500">
             <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-orange-50 flex items-center justify-center text-orange-500 group-hover:bg-orange-500 group-hover:text-white transition-all duration-500 overflow-hidden relative">
                   <div className="absolute inset-0 bg-white/20 animate-pulse opacity-0 group-hover:opacity-100" />
                   <LogOut size={18} className="relative z-10" />
                </div>
                <div className="text-left">
                   <p className="text-[13px] font-bold text-slate-700 tracking-tight leading-none mb-1">Logout</p>
                   <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest leading-none">Admin Console</p>
                </div>
             </div>
          </button>
        </div>
      </div>
    </aside>
  );
}
