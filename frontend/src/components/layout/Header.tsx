import { useLocation } from 'react-router-dom'
import {
  ChevronDown,
  Bell,
  Search,
  User,
  Menu,
  LayoutDashboard,
  CloudUpload,
  Users,
  BarChart2,
  ClipboardCheck,
  Database
} from 'lucide-react'
import { useAuthStore } from '../../store/authStore'

const pageTitles: Record<string, { title: string; icon: any; color: string }> = {
  '/': {
    title: 'Overview',
    icon: LayoutDashboard,
    color: 'bg-violet-100 text-violet-600 border-violet-200'
  },
  '/upload': {
    title: 'Upload Resume',
    icon: CloudUpload,
    color: 'bg-blue-100 text-blue-600 border-blue-200'
  },
  '/candidates': {
    title: 'Candidates',
    icon: Users,
    color: 'bg-teal-100 text-teal-600 border-teal-200'
  },
  '/accuracy': {
    title: 'Accuracy',
    icon: BarChart2,
    color: 'bg-indigo-100 text-indigo-600 border-indigo-200'
  },
  '/corrections': {
    title: 'Corrections',
    icon: ClipboardCheck,
    color: 'bg-rose-100 text-rose-600 border-rose-200'
  },
  '/taxonomy': {
    title: 'Taxonomy',
    icon: Database,
    color: 'bg-amber-100 text-amber-600 border-amber-200'
  },
}

interface HeaderProps {
  onMenuClick?: () => void
}

export default function Header({ onMenuClick }: HeaderProps) {
  const location = useLocation()
  const { user } = useAuthStore()

  // Find the best matching path
  const matchedPath = Object.keys(pageTitles)
    .filter((p) => location.pathname === p || location.pathname.startsWith(p + '/'))
    .sort((a, b) => b.length - a.length)[0] ?? '/'

  const pageInfo = pageTitles[matchedPath] ?? pageTitles['/']

  // Define role-based styles based on the user's reference image
  const roleConfig: Record<string, { label: string; boxClass: string; iconClass: string }> = {
    admin: {
      label: 'Admin',
      boxClass: 'bg-violet-600 shadow-md shadow-violet-200',
      iconClass: 'text-white'
    },
    reviewer: {
      label: 'Reviewer',
      boxClass: 'bg-indigo-50 border border-slate-100',
      iconClass: 'text-violet-600'
    },
    recruiter: {
      label: 'Recruiter',
      boxClass: 'bg-indigo-50 border border-slate-100',
      iconClass: 'text-violet-600'
    }
  }

  const currentRole = user?.role?.toLowerCase() || 'admin'
  const config = roleConfig[currentRole] || roleConfig.admin

  return (
    <div className="flex items-center justify-between px-4 md:px-8 py-4 border-b border-slate-100 bg-white sticky top-0 z-30">
      {/* Left Area: Menu + Title */}
      <div className="flex items-center gap-4 animate-in fade-in slide-in-from-left-4 duration-500">
        <button
          onClick={onMenuClick}
          className="lg:hidden rounded-xl p-2 text-slate-500 hover:bg-slate-50 hover:text-slate-800 transition-all border border-slate-100 shadow-sm"
        >
          <Menu className="h-5 w-5" />
        </button>

        <div className="flex items-center gap-3.5 min-w-0">
          <div className={`flex h-10 w-10 items-center justify-center rounded-xl border shadow-sm transition-all duration-300 ${pageInfo.color}`}>
            <pageInfo.icon className="h-5 w-5" />
          </div>
          <h1 className="text-xl md:text-2xl font-black text-slate-800 tracking-tight truncate leading-none">
            {pageInfo.title}
          </h1>
        </div>
      </div>

      {/* Right Area: Tools + Profile */}
      <div className="flex items-center gap-3 md:gap-6 animate-in fade-in slide-in-from-right-4 duration-500">
        {/* Quick Search - Desktop Only */}
        <div className="hidden xl:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-100 text-slate-400 cursor-pointer hover:bg-slate-100 transition-all">
          <Search className="h-4 w-4" />
          <span className="text-xs font-medium pr-8">Search...</span>
          <span className="text-[10px] font-black opacity-30 px-1.5 py-0.5 rounded border border-slate-200 bg-white">Ctrl + K</span>
        </div>

        {/* Notifications */}
        <button className="relative p-2 rounded-xl text-slate-400 hover:bg-slate-50 transition-all group">
          <Bell className="h-5 w-5 hover:scale-110 transition-transform" />
          <span className="absolute top-2 right-2 h-2 w-2 rounded-full bg-red-500 border-2 border-white" />
        </button>

        {/* Divider */}
        <div className="h-8 w-px bg-slate-100 hidden sm:block" />

        {/* User Profile */}
        <div className="flex items-center gap-2 md:gap-3 cursor-pointer group p-1 rounded-2xl hover:bg-indigo-50 transition-all duration-300">
          <div className={`flex h-9 w-9 items-center justify-center rounded-[12px] transition-all group-hover:shadow-md ${config.boxClass}`}>
            <User className={`h-4 w-4 ${config.iconClass}`} />
          </div>

          <div className="hidden sm:block">
            <h4 className="text-[14px] font-extrabold text-[#475569] leading-none transition-colors group-hover:text-violet-700">
              {config.label}
            </h4>
          </div>

          <ChevronDown className="h-4 w-4 text-slate-300 group-hover:text-violet-400 group-hover:translate-y-0.5 transition-all" />
        </div>
      </div>
    </div>
  )
}
