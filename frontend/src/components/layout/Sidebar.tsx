import { NavLink, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import { toast } from 'react-hot-toast'
import {
  BarChart2,
  ClipboardCheck,
  CloudUpload,
  Database,
  FileText,
  LayoutDashboard,
  LogOut,
  Users,
} from 'lucide-react'

const navLinks = [
  { label: 'Overview', path: '/', icon: LayoutDashboard },
  { label: 'Upload Resume', path: '/upload', icon: CloudUpload },
  { label: 'Candidates', path: '/candidates', icon: Users },
  { label: 'Accuracy', path: '/accuracy', icon: BarChart2 },
  { label: 'Corrections', path: '/corrections', icon: ClipboardCheck },
  { label: 'Taxonomy', path: '/taxonomy', icon: Database },
]

type SidebarProps = {
  open?: boolean
}

export default function Sidebar({ open = true }: SidebarProps) {
  const navigate = useNavigate()
  const { accessToken, clearTokens } = useAuthStore()

  const handleAuthClick = () => {
    if (accessToken) {
      clearTokens()
      toast.success('Logout successfully')
    }
    navigate('/auth')
  }

  return (
    <aside
      className={`hidden flex-shrink-0 overflow-hidden transition-all duration-300 ease-in-out lg:flex lg:flex-col ${
        open ? 'w-56' : 'w-0'
      }`}
      style={{
        background: 'linear-gradient(160deg, #f5f3ff 0%, #ede9fe 30%, #e0f2fe 70%, #f0fdfa 100%)',
        minHeight: '100vh',
      }}
    >
      <div className="flex w-56 flex-col h-full px-3 py-4">
        {/* Logo */}
        <div className="mb-6 flex items-center gap-3 px-2 py-3">
          <div
            className="flex h-9 w-9 items-center justify-center rounded-xl text-white shadow-md flex-shrink-0"
            style={{ background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)' }}
          >
            <FileText className="h-4 w-4" />
          </div>
          <div>
            <p className="text-sm font-bold text-slate-800">Resume Parser</p>
            <p className="text-[10px] text-slate-500 leading-tight">Admin Console</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="space-y-0.5">
          {navLinks.map((item) => {
            const Icon = item.icon
            return (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === '/'}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200 ${
                    isActive
                      ? 'text-white shadow-md'
                      : 'text-slate-600 hover:bg-white/60 hover:text-slate-900'
                  }`
                }
                style={({ isActive }) =>
                  isActive
                    ? { background: 'linear-gradient(135deg, #7c3aed 0%, #14b8a6 100%)' }
                    : {}
                }
              >
                <Icon className="h-4 w-4 flex-shrink-0" />
                <span>{item.label}</span>
              </NavLink>
            )
          })}

          {/* Auth Toggle */}
          <button
            onClick={handleAuthClick}
            className="group flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-slate-600 transition-all duration-200 hover:bg-white/60 hover:text-slate-900"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-50 text-slate-400 transition-colors group-hover:bg-violet-600 group-hover:text-white">
              {accessToken ? <LogOut className="h-4 w-4" /> : <Users className="h-4 w-4" />}
            </div>
            <span>{accessToken ? 'Logout' : 'Login'}</span>
          </button>
        </nav>
      </div>
    </aside>
  )
}
