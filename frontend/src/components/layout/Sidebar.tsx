import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  FileSearch,
  Users,
  Briefcase,
  GitCompare,
  Settings,
  Sparkles,
  Eye,
  Zap,
} from "lucide-react";

const links = [
  { label: "Dashboard", path: "/", icon: LayoutDashboard },
  { label: "Resume Analyzer", path: "/upload", icon: FileSearch },
  { label: "Section Preview", path: "/section-preview", icon: Eye },
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
      className={`hidden flex-shrink-0 overflow-hidden border-r border-gray-100 bg-white transition-all duration-200 ease-in-out lg:flex lg:flex-col ${open ? "w-64" : "w-0"
        }`}
    >
      <div className="flex flex-col h-full w-64 px-5 py-8">
        {/* Logo */}
        <div className="mb-10 flex items-center gap-4 px-2">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl shadow-lg shadow-purple-200 text-white" style={{ background: 'linear-gradient(135deg, #7C3AED, #9333EA)' }}>
            <Sparkles className="h-6 w-6" />
          </div>
          <div>
            <p className="text-base font-black text-navy-900 tracking-tight leading-tight">
              Lakshya AI
            </p>
            <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mt-0.5">ATS Analyzer</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-2 text-[15px] font-semibold">
          {links.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `group flex items-center gap-3.5 rounded-xl px-4 py-3 transition-all duration-200 ${isActive
                    ? "text-white shadow-md shadow-purple-200"
                    : "text-slate-500 hover:bg-slate-50 hover:text-slate-900"
                  }`
                }
                style={({ isActive }) => isActive ? { background: 'linear-gradient(135deg, #7C3AED, #9333EA)' } : {}}
              >
                <Icon className={`h-5 w-5 transition-colors ${item.path === "/" ? "" : ""}`} />
                {item.label}
              </NavLink>
            );
          })}
        </nav>

        {/* Status Badge */}
        <div className="mt-auto pt-6 border-t border-slate-50">
          <div className="flex items-center gap-3 px-4 py-3 rounded-xl border border-purple-100/50" style={{ background: '#f3e8ff' }}>
            <div className="flex h-7 w-7 items-center justify-center rounded-lg text-white shadow-sm" style={{ background: '#7C3AED' }}>
              <Zap className="h-4 w-4" />
            </div>
            <span className="text-xs font-bold" style={{ color: '#7C3AED' }}>PRO Version</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
