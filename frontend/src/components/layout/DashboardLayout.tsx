import { useState, useRef, useEffect } from "react";
import { Outlet, useNavigate, useLocation } from "react-router-dom";
import { useAuthStore } from "../../store/useAuthStore";
import {
  LayoutDashboard, Users, UploadCloud, BarChart3,
  ClipboardCheck, Database, Menu, Bell, Search,
  ChevronDown, LogOut, FileText, Settings, X
} from "lucide-react";

interface NavItem {
  name: string;
  href: string;
  icon: React.ReactNode;
}

export default function DashboardLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setUserMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const navigation: NavItem[] = [
    { name: "Overview", href: "/dashboard", icon: <LayoutDashboard size={20} /> },
    { name: "Upload Resume", href: "/upload", icon: <UploadCloud size={20} /> },
    { name: "Candidates", href: "/candidates", icon: <Users size={20} /> },
    { name: "Accuracy", href: "/accuracy", icon: <BarChart3 size={20} /> },
    { name: "Corrections", href: "/corrections", icon: <ClipboardCheck size={20} /> },
    { name: "Taxonomy", href: "/taxonomy", icon: <Database size={20} /> },
  ];

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const isActive = (href: string) => location.pathname === href || location.pathname.startsWith(`${href}/`);
  const currentPage = navigation.find((n) => isActive(n.href))?.name || "Overview";

  return (
    <div className="flex h-screen overflow-hidden bg-[#F8FAFC] font-sans antialiased text-slate-900">

      {/* Mobile Menu Overlay */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/50 backdrop-blur-sm lg:hidden transition-opacity"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed inset-y-0 left-0 z-50 flex w-64 flex-col bg-[#F5F8FF] border-r border-indigo-50/50 transition-transform duration-300 ease-in-out lg:static lg:translate-x-0
        ${mobileMenuOpen ? "translate-x-0" : "-translate-x-full"}
      `}>

        {/* Logo Section */}
        <div className="flex h-16 shrink-0 items-center px-6 mt-4 mb-6">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-[#6366F1] to-[#4F46E5] text-white shadow-lg shadow-indigo-100">
              <FileText size={20} className="stroke-[2.5]" />
            </div>
            <div className="flex flex-col">
              <span className="text-xl font-extrabold tracking-tight text-[#1E293B] leading-none">Resume</span>
              <span className="text-[10px] font-bold uppercase tracking-widest text-slate-400 mt-1 uppercase">ADMIN CONSOLE</span>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto px-4 space-y-2">
          {navigation.map((item) => {
            const active = isActive(item.href);
            return (
              <button
                key={item.name}
                onClick={() => {
                  navigate(item.href);
                  setMobileMenuOpen(false);
                }}
                className={`
                  group flex w-full items-center gap-4 rounded-xl px-2.5 py-2.5 text-base font-bold transition-all duration-300 relative overflow-hidden
                  ${active
                    ? "bg-gradient-to-r from-[#7C3AED] to-[#2DD4BF] text-white shadow-xl shadow-indigo-200"
                    : "text-[#475569] hover:bg-white hover:text-indigo-600 hover:shadow-sm"}
                `}
              >
                {/* Hover indicator for inactive items */}
                {!active && (
                  <div className="absolute left-0 w-1 h-0 bg-indigo-500 rounded-full transition-all duration-300 group-hover:h-6" />
                )}

                <div className={`${active ? "text-white" : "text-slate-400 group-hover:text-indigo-600 transition-colors"}`}>
                  {item.icon}
                </div>
                <span className="tracking-tight">{item.name}</span>

                {/* Colorful Sparkle on hover for inactive items */}
                {!active && (
                  <div className="absolute -right-2 top-1/2 -translate-y-1/2 w-8 h-8 bg-indigo-500/5 rounded-full blur-xl group-hover:bg-indigo-500/10 transition-colors" />
                )}
              </button>
            );
          })}
        </nav>

        {/* Sidebar Footer - Logout */}
        <div className="p-6 border-t border-slate-50 mt-auto">
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 w-full rounded-2xl p-4 text-sm font-bold text-slate-500 hover:text-rose-600 hover:bg-rose-50/50 transition-all duration-300 group border border-transparent hover:border-rose-100"
          >
            <div className="w-10 h-10 rounded-xl bg-rose-50 flex items-center justify-center text-rose-500 group-hover:bg-rose-100 group-hover:scale-110 shadow-sm transition-all">
              <LogOut size={20} />
            </div>
            <span className="font-bold">Logout</span>
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex flex-1 flex-col overflow-hidden min-w-0">

        {/* Header */}
        <header className="flex h-16 shrink-0 items-center justify-between px-8 bg-white border-b border-slate-50 z-30">

          <div className="flex items-center gap-4">
            <button
              className="text-slate-400 lg:hidden p-2 hover:bg-slate-50 rounded-xl"
              onClick={() => setMobileMenuOpen(true)}
            >
              <Menu size={24} />
            </button>

            <div className="flex items-center gap-3">
               <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600 border border-indigo-100 shadow-sm shadow-indigo-100/30">
                  {navigation.find(n => isActive(n.href))?.icon || <LayoutDashboard size={20} />}
               </div>
               <h1 className="text-lg font-black text-slate-800 tracking-tight">{currentPage}</h1>
            </div>
          </div>

          {/* Search Bar - Center */}
          <div className="hidden lg:flex flex-1 max-w-lg mx-8 relative items-center group">
            <div className="absolute inset-y-0 left-0 flex items-center pl-5 pointer-events-none">
              <Search size={18} className="text-slate-300 group-focus-within:text-indigo-500 transition-colors" />
            </div>
            <input
              type="text"
              placeholder="SEARCH INTELLIGENCE"
              className="h-12 w-full rounded-2xl border border-slate-100 bg-[#F8FAFC] pl-12 pr-16 text-xs font-bold tracking-widest uppercase outline-none transition-all focus:bg-white focus:border-indigo-400 focus:shadow-xl focus:shadow-indigo-500/5 placeholder:text-slate-300"
            />
            <div className="absolute right-4 text-[10px] font-black text-slate-400 uppercase tracking-widest bg-white px-2 py-1.5 rounded-lg border border-slate-100 shadow-sm">
              CTRL + K
            </div>
          </div>

          <div className="flex items-center gap-6">
            <button className="text-slate-400 hover:text-indigo-600 hover:bg-slate-50 p-2.5 rounded-xl transition-all relative">
              <Bell size={20} />
              <span className="absolute top-2.5 right-2.5 w-2 h-2 bg-rose-500 border-2 border-white rounded-full"></span>
            </button>

            {/* User Menu */}
            <div className="relative" ref={userMenuRef}>
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="flex items-center gap-3 p-1 rounded-xl transition-all"
              >
                <div className="h-10 w-10 flex items-center justify-center rounded-xl bg-[#6366F1] text-white font-black text-sm shadow-md shadow-indigo-100 shrink-0">
                  <Users size={18} />
                </div>
                <div className="hidden sm:flex items-center gap-2">
                  <p className="text-xs font-black text-slate-800 tracking-widest uppercase">ADMIN</p>
                  <ChevronDown size={14} className="text-slate-400" />
                </div>
              </button>

              {userMenuOpen && (
                <div className="absolute right-0 top-[calc(100%+12px)] w-56 bg-white rounded-2xl border border-slate-100 shadow-2xl z-50 overflow-hidden py-2 animate-in fade-in slide-in-from-top-4">
                  <div className="px-4 py-3 mb-2 bg-slate-50/50">
                    <p className="text-[12px] font-black text-slate-900">{user?.name || "Admin User"}</p>
                    <p className="text-[10px] font-bold text-slate-400 truncate mt-0.5">{user?.email || "admin@example.com"}</p>
                  </div>
                  <button className="w-full text-left px-4 py-2.5 text-xs font-bold text-slate-600 hover:bg-indigo-50 hover:text-indigo-700 flex items-center gap-3 transition-colors">
                    <Settings size={14} />
                    Account Settings
                  </button>
                  <div className="my-2 border-t border-slate-100"></div>
                  <button
                    onClick={handleLogout}
                    className="w-full text-left px-4 py-2.5 text-xs font-bold text-rose-600 hover:bg-rose-50 flex items-center gap-3 transition-colors"
                  >
                    <LogOut size={14} />
                    Sign Out
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Content Render Area */}
        <main className="flex-1 overflow-y-auto bg-slate-50/50 relative">
          <div className="max-w-[1500px] mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}

