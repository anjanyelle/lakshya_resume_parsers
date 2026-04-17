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
  Target,
  BarChart2,
  ClipboardCheck,
  Database,
  Sun,
  Moon,
  Plus,
  Settings as SettingsIcon
} from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import { useNotificationStore } from '../../store/notificationStore'
import { useCandidateStore } from '../../store/candidateStore'
import { useTheme } from '../../contexts/ThemeContext'
import { useNavigate } from 'react-router-dom'
import GlobalSearch from './GlobalSearch'
import NotificationDropdown from './NotificationDropdown'

interface HeaderProps {
  onMenuClick: () => void
}

const pageTitles: Record<string, { title: string; icon: any; color: string }> = {
  '/': { title: 'OVERVIEW', icon: LayoutDashboard, color: 'bg-brand-50 text-brand-600 border-brand-100' },
  '/upload': { title: 'UPLOAD', icon: CloudUpload, color: 'bg-brand-50 text-brand-600 border-brand-100' },
  '/candidates': { title: 'CANDIDATES', icon: Users, color: 'bg-brand-50 text-brand-600 border-brand-100' },
  '/accuracy': { title: 'ACCURACY', icon: Target, color: 'bg-brand-50 text-brand-600 border-brand-100' },
  '/quality': { title: 'QUALITY', icon: BarChart2, color: 'bg-brand-50 text-brand-600 border-brand-100' },
  '/corrections': { title: 'CORRECTIONS', icon: ClipboardCheck, color: 'bg-brand-50 text-brand-600 border-brand-100' },
  '/taxonomy': { title: 'TAXONOMY', icon: Database, color: 'bg-brand-50 text-brand-600 border-brand-100' },
  '/settings': { title: 'SETTINGS', icon: SettingsIcon, color: 'bg-brand-50 text-brand-600 border-brand-100' },
}

const roleConfig: Record<string, { label: string; iconClass: string; boxClass: string }> = {
  admin: { label: 'Admin', iconClass: 'text-brand-600', boxClass: 'bg-brand-50 dark:bg-brand-900/30' },
  recruiter: { label: 'Recruiter', iconClass: 'text-brand-500', boxClass: 'bg-brand-50/50 dark:bg-brand-900/20' },
  default: { label: 'User', iconClass: 'text-brand-400', boxClass: 'bg-brand-50/30 dark:bg-brand-900/10' },
}

export default function Header({ onMenuClick }: HeaderProps) {
  const location = useLocation()
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const { unreadCount } = useNotificationStore()
  const { theme, toggleTheme } = useTheme()

  const [isSearchOpen, setIsSearchOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false)
  const [isProfileOpen, setIsProfileOpen] = useState(false)

  const searchRef = useRef<HTMLDivElement>(null)
  const notificationRef = useRef<HTMLDivElement>(null)
  const profileRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsSearchOpen(false)
      }
      if (notificationRef.current && !notificationRef.current.contains(event.target as Node)) {
        setIsNotificationsOpen(false)
      }
      if (profileRef.current && !profileRef.current.contains(event.target as Node)) {
        setIsProfileOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const currentPath = location.pathname
  const pageInfo = pageTitles[currentPath] || (currentPath.startsWith('/candidates/')
    ? { title: 'CANDIDATE PROFILE', icon: Users, color: 'bg-emerald-50 text-emerald-600 border-emerald-100' }
    : { title: 'RESUME PARSER', icon: LayoutDashboard, color: 'bg-slate-50 text-slate-600 border-slate-100' })

  const config = roleConfig[user?.role || 'default'] || roleConfig.default

  return (
    <div className="flex items-center justify-between px-4 md:px-8 py-4 border-b border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900 sticky top-0 z-30 h-20 transition-colors duration-300">
      {/* Left Area: Menu + Title */}
      <div className="flex items-center gap-4">
        <button
          onClick={onMenuClick}
          className="lg:hidden rounded-xl p-2 text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800 transition-all"
        >
          <Menu className="h-5 w-5" />
        </button>

        <div className="flex items-center gap-4 min-w-0">
          <div className={`flex h-11 w-11 items-center justify-center rounded-2xl border shadow-sm transition-all duration-300 ${pageInfo.color} dark:border-slate-700`}>
            <pageInfo.icon className="h-5.5 w-5.5" />
          </div>
          <p className="text-[15px] font-black text-slate-800 dark:text-slate-500 uppercase tracking-[0.2em] select-none">
            {pageInfo.title}
          </p>
        </div>
      </div>

      {/* Right Area: Tools + Profile */}
      <div className="flex items-center gap-4 md:gap-6 ml-auto">


        {/* Search Intelligence Dropdown */}
        <div className="relative hidden xl:block" ref={searchRef}>
          <div
            className={`flex items-center gap-4 pl-6 pr-2 py-3 rounded-2xl transition-all duration-700 border backdrop-blur-xl ${isSearchOpen ? 'bg-white/90 dark:bg-slate-800/90 border-orange-600 shadow-2xl shadow-orange-200/30 w-[400px]' : 'bg-slate-50/50 dark:bg-slate-800/50 border-slate-100 dark:border-slate-700 w-64 hover:border-orange-200 hover:bg-white dark:hover:bg-slate-800 hover:shadow-lg hover:shadow-orange-100/40'
              } group cursor-pointer`}
          >
            <Search className={`h-5 w-5 transition-colors duration-500 ${isSearchOpen ? 'text-orange-600' : 'text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-300'}`} />
            <input
              type="text"
              placeholder="SEARCH..."
              className="flex-1 bg-transparent border-none text-[11px] font-bold text-slate-800 dark:text-slate-200 focus:outline-none placeholder:text-slate-400/50 placeholder:font-bold placeholder:tracking-[0.2em] uppercase"
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value)
                setIsSearchOpen(true)
              }}
              onFocus={() => setIsSearchOpen(true)}
              id="header-search-input"
            />
          </div>

          <div className="absolute left-0 w-full pt-1.5">
            <GlobalSearch
              isOpen={isSearchOpen}
              onClose={() => setIsSearchOpen(false)}
              query={searchQuery}
            />
          </div>
        </div>

        <div className="flex items-center gap-2 md:gap-4">
          {/* Dark Mode Toggle */}
          <button
            onClick={toggleTheme}
            className="p-2.5 rounded-xl text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 transition-all group"
            title={theme === 'light' ? 'Switch to Dark Mode' : 'Switch to Light Mode'}
          >
            {theme === 'light' ? (
              <Moon className="h-5 w-5 transition-transform group-hover:-rotate-12" />
            ) : (
              <Sun className="h-5 w-5 transition-transform group-hover:rotate-45" />
            )}
          </button>

          {/* Notifications */}
          <div className="relative" ref={notificationRef}>
            <button
              onClick={() => setIsNotificationsOpen(!isNotificationsOpen)}
              className={`relative p-2.5 rounded-xl transition-all duration-300 group ${isNotificationsOpen ? 'bg-orange-50 dark:bg-slate-800 text-orange-600 shadow-inner' : 'text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800'
                }`}
            >
              <Bell className={`h-5 w-5 transition-transform duration-300 ${isNotificationsOpen ? 'scale-110' : 'group-hover:scale-110'}`} />
              {unreadCount > 0 && (
                <span className="absolute top-2 right-2 flex h-4 w-4 items-center justify-center rounded-full border-2 border-white dark:border-slate-900 bg-red-500 text-[8px] font-black text-white shadow-sm animate-in zoom-in">
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
              className={`flex items-center gap-2 md:gap-3 cursor-pointer group p-1.5 rounded-2xl transition-all duration-500 border border-transparent ${isProfileOpen ? 'bg-slate-50 dark:bg-slate-800 border-slate-100 dark:border-slate-700 shadow-inner' : 'hover:bg-slate-50 dark:hover:bg-slate-800'
                }`}
            >
              <div className={`relative flex h-10 w-10 items-center justify-center rounded-xl transition-all duration-500 group-hover:scale-110 group-hover:-rotate-3 ${config.boxClass}`}>
                <User className={`h-5 w-5 ${config.iconClass}`} />
                <div className="absolute -top-0.5 -right-0.5 h-3 w-3 rounded-full border-2 border-white dark:border-slate-800 bg-emerald-500 shadow-sm shadow-emerald-200" />
              </div>
              <div className="hidden sm:flex flex-col min-w-[70px]">
                <h4 className="text-[13px] font-bold text-slate-800 dark:text-slate-200 leading-none uppercase tracking-tight">
                  {config.label}
                </h4>
                <span className="text-[9px] font-bold text-slate-400 mt-1 uppercase tracking-widest opacity-0 group-hover:opacity-100 transition-all duration-500 translate-y-2 group-hover:translate-y-0">
                  Settings
                </span>
              </div>
              <ChevronDown className={`h-4 w-4 text-slate-400 transition-all duration-300 ml-1 ${isProfileOpen ? 'rotate-180 text-orange-500' : 'group-hover:translate-y-0.5'}`} />
            </div>

            {isProfileOpen && (
              <div className="absolute right-0 mt-3 w-48 overflow-hidden rounded-2xl bg-white dark:bg-slate-800 p-1.5 shadow-2xl ring-1 ring-slate-100 dark:ring-slate-700 animate-in fade-in zoom-in-95 slide-in-from-top-2">
                <button className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-xs font-bold text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 hover:text-slate-900 dark:hover:text-white transition-all uppercase tracking-widest">
                  <User className="h-4 w-4" /> My Profile
                </button>
                <div className="h-px bg-slate-50 dark:bg-slate-700 my-1" />
                <button className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-xs font-black text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-900/10 transition-all uppercase tracking-widest">
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
