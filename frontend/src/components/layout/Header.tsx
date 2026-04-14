import { useLocation } from 'react-router-dom'
import { useState, useEffect, useRef } from 'react'
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
import { useNotificationStore } from '../../store/notificationStore'
import { useCandidateStore } from '../../store/candidateStore'
import GlobalSearch from './GlobalSearch'
import NotificationDropdown from './NotificationDropdown'

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
  const { candidates } = useCandidateStore()
  const { addNotification, unreadCount } = useNotificationStore()

  const [isSearchOpen, setIsSearchOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false)
  const [isProfileOpen, setIsProfileOpen] = useState(false)

  const searchRef = useRef<HTMLDivElement>(null)
  const notificationRef = useRef<HTMLDivElement>(null)
  const profileRef = useRef<HTMLDivElement>(null)

  // System Notification Watcher
  // Monitors candidate status changes to alert the user
  const prevCandidatesRef = useRef(candidates)
  useEffect(() => {
    candidates.forEach((current) => {
      const stored = prevCandidatesRef.current.find((c) => c.id === current.id)
      if (stored && stored.status !== current.status) {
        if (current.status === 'success') {
          addNotification({
            type: 'success',
            title: 'Analysis Complete',
            message: `Resume for ${current.full_name || 'Candidate'} successfully processed with ${Math.round((current.parsing_jobs?.[0]?.confidence_score || 0) * 100)}% accuracy.`,
            link: `/candidates/${current.id}`
          })
        } else if (current.status === 'failed') {
          addNotification({
            type: 'error',
            title: 'Extraction Failed',
            message: `Critical error encountered while parsing ${current.full_name || 'candidate resume'}. Please review in corrections.`,
            link: `/corrections`
          })
        }
      }
    })
    prevCandidatesRef.current = candidates
  }, [candidates, addNotification])

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(e.target as Node)) setIsSearchOpen(false)
      if (notificationRef.current && !notificationRef.current.contains(e.target as Node)) setIsNotificationsOpen(false)
      if (profileRef.current && !profileRef.current.contains(e.target as Node)) setIsProfileOpen(false)
    }

    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        const input = document.getElementById('header-search-input')
        input?.focus()
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    window.addEventListener('keydown', handleKeyDown)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
      window.removeEventListener('keydown', handleKeyDown)
    }
  }, [])

  // Find the best matching path
  const matchedPath = Object.keys(pageTitles)
    .filter((p) => location.pathname === p || location.pathname.startsWith(p + '/'))
    .sort((a, b) => b.length - a.length)[0] ?? '/'

  const pageInfo = pageTitles[matchedPath] ?? pageTitles['/']

  // Define role-based styles based on the user's reference image
  const roleConfig: Record<string, { label: string; boxClass: string; iconClass: string }> = {
    admin: {
      label: 'Admin',
      boxClass: 'bg-violet-600 shadow-xl shadow-violet-200/50',
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
    <div className="flex items-center justify-between px-4 md:px-8 py-4 border-b border-slate-100 bg-white sticky top-0 z-30 h-20">
      {/* Left Area: Menu + Title */}
      <div className="flex items-center gap-4">
        <button
          onClick={onMenuClick}
          className="lg:hidden rounded-xl p-2 text-slate-500 hover:bg-slate-50 transition-all"
        >
          <Menu className="h-5 w-5" />
        </button>

        <div className="flex items-center gap-4 min-w-0">
          <div className={`flex h-11 w-11 items-center justify-center rounded-2xl border shadow-sm transition-all duration-300 ${pageInfo.color}`}>
            <pageInfo.icon className="h-5.5 w-5.5" />
          </div>
          <h1 className="text-xl md:text-2xl font-bold text-slate-600 tracking-tight truncate leading-none">
            {pageInfo.title}
          </h1>
        </div>
      </div>

      {/* Right Area: Tools + Profile */}
      <div className="flex items-center gap-8 md:gap-12 ml-auto">
        {/* Search Intelligence Dropdown */}
        <div className="relative hidden xl:block" ref={searchRef}>
          <div
            className={`flex items-center gap-4 pl-6 pr-2 py-3 rounded-2xl transition-all duration-700 border backdrop-blur-xl ${isSearchOpen ? 'bg-white/90 border-violet-300 shadow-2xl shadow-violet-200/30 w-[480px]' : 'bg-slate-50/50 border-slate-100 w-80 hover:border-slate-200 hover:bg-white hover:shadow-lg hover:shadow-slate-200/40'
              } group cursor-pointer`}
          >
            <Search className={`h-5 w-5 transition-colors duration-500 ${isSearchOpen ? 'text-violet-500' : 'text-slate-400 group-hover:text-slate-600'}`} />
            <input
              type="text"
              placeholder="SEARCH..."
              className="flex-1 bg-transparent border-none text-[11px] font-bold text-slate-700 focus:outline-none placeholder:text-slate-400/50 placeholder:font-bold placeholder:tracking-[0.2em] uppercase"
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value)
                setIsSearchOpen(true)
              }}
              onFocus={() => setIsSearchOpen(true)}
              id="header-search-input"
            />
            <div className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl bg-white border border-slate-100 shadow-sm transition-all duration-500 ${isSearchOpen ? 'opacity-0 scale-75 translate-x-6' : 'opacity-60 group-hover:opacity-100 group-hover:border-slate-200'}`}>
              <span className="text-[10px] font-black text-slate-400 uppercase tracking-tighter">CTRL</span>
              <span className="text-[10px] font-black text-slate-200">+</span>
              <span className="text-[10px] font-bold text-slate-400">K</span>
            </div>
          </div>

          {/* Results Center Dropdown */}
          <div className="absolute left-0 w-full pt-1.5">
            <GlobalSearch
              isOpen={isSearchOpen}
              onClose={() => setIsSearchOpen(false)}
              query={searchQuery}
            />
          </div>
        </div>

        <div className="flex items-center gap-4">
          {/* Notifications */}
          <div className="relative" ref={notificationRef}>
            <button
              onClick={() => setIsNotificationsOpen(!isNotificationsOpen)}
              className={`relative p-2.5 rounded-xl transition-all duration-300 group ${isNotificationsOpen ? 'bg-violet-50 text-violet-600 shadow-inner' : 'text-slate-400 hover:bg-slate-50'
                }`}
            >
              <Bell className={`h-5 w-5 transition-transform duration-300 ${isNotificationsOpen ? 'scale-110' : 'group-hover:scale-110'}`} />
              {unreadCount > 0 && (
                <span className="absolute top-2 right-2 flex h-4 w-4 items-center justify-center rounded-full border-2 border-white bg-red-500 text-[8px] font-black text-white shadow-sm animate-in zoom-in">
                  {unreadCount}
                </span>
              )}
            </button>
            {isNotificationsOpen && <NotificationDropdown onClose={() => setIsNotificationsOpen(false)} />}
          </div>

          {/* User Profile */}
          <div className="relative" ref={profileRef}>
            <div
              onClick={() => setIsProfileOpen(!isProfileOpen)}
              className={`flex items-center gap-2 md:gap-3 cursor-pointer group p-1.5 rounded-2xl transition-all duration-500 border border-transparent ${isProfileOpen ? 'bg-slate-50 border-slate-100 shadow-inner' : 'hover:bg-slate-50'
                }`}
            >
              <div className={`relative flex h-10 w-10 items-center justify-center rounded-xl transition-all duration-500 group-hover:scale-110 group-hover:-rotate-3 ${config.boxClass}`}>
                <User className={`h-5 w-5 ${config.iconClass}`} />
                {/* Status Indicator */}
                <div className="absolute -top-0.5 -right-0.5 h-3 w-3 rounded-full border-2 border-white bg-emerald-500 shadow-sm shadow-emerald-200" />
              </div>
              <div className="hidden sm:flex flex-col min-w-[70px]">
                <h4 className="text-[13px] font-bold text-slate-700 leading-none uppercase tracking-tight">
                  {config.label}
                </h4>
                <span className="text-[9px] font-bold text-slate-400 mt-1 uppercase tracking-widest opacity-0 group-hover:opacity-100 transition-all duration-500 translate-y-2 group-hover:translate-y-0">
                  Settings
                </span>
              </div>
              <ChevronDown className={`h-4 w-4 text-slate-400 transition-all duration-300 ml-1 ${isProfileOpen ? 'rotate-180 text-violet-500' : 'group-hover:translate-y-0.5'}`} />
            </div>

            {isProfileOpen && (
              <div className="absolute right-0 mt-3 w-48 overflow-hidden rounded-2xl bg-white p-1.5 shadow-2xl ring-1 ring-slate-100 animate-in fade-in zoom-in-95 slide-in-from-top-2">
                <button className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-xs font-bold text-slate-600 hover:bg-slate-50 hover:text-slate-900 transition-all uppercase tracking-widest">
                  <User className="h-4 w-4" /> My Profile
                </button>
                <div className="h-px bg-slate-50 my-1" />
                <button className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-xs font-black text-rose-600 hover:bg-rose-50 transition-all uppercase tracking-widest">
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

    </div>
  )
}
