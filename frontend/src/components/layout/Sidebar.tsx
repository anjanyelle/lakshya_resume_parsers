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
  X,
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
  open: boolean
  onClose?: () => void
}

export default function Sidebar({ open, onClose }: SidebarProps) {
  const navigate = useNavigate()
  const { accessToken, clearTokens } = useAuthStore()

  const handleAuthClick = () => {
    if (accessToken) {
      clearTokens()
      toast.success('Logout successfully')
    }
    navigate('/auth')
    onClose?.()
  }

  return (
    <aside
      className={`fixed inset-y-0 left-0 z-50 flex w-64 flex-col bg-white transition-transform duration-300 ease-in-out lg:static lg:w-64 lg:translate-x-0 ${open ? 'translate-x-0' : '-translate-x-full'
        }`}
      style={{
        background: 'linear-gradient(160deg, #f5f3ff 0%, #ede9fe 30%, #e0f2fe 70%, #f0fdfa 100%)',
      }}
    >
      <div className="flex flex-col h-full px-4 py-6">
        {/* Logo & Close Button */}
        <div className="mb-10 flex items-center justify-between px-2">
          <div className="flex items-center gap-4">
            <div
              className="relative flex h-11 w-11 items-center justify-center rounded-xl text-white shadow-2xl shadow-blue-500/20 flex-shrink-0 ring-1 ring-white/10"
              style={{ background: 'linear-gradient(135deg, #2563eb 0%, #4f46e5 100%)' }}
            >
              <div className="absolute inset-0 rounded-xl bg-white/5 backdrop-blur-[1px]"></div>
              <FileText className="relative h-6 w-6" />
            </div>
            <div className="flex flex-col">
              <p className="text-[15px] font-extrabold text-slate-800 tracking-tight leading-[1.2]">Resume Parser</p>
              <p className="text-[9px] font-bold text-slate-400 uppercase tracking-[0.12em] leading-none mt-1">ADMIN CONSOLE</p>
            </div>
          </div>

          {/* Mobile Close Button */}
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-white/50 hover:text-slate-600 lg:hidden"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1.5">
          {navLinks.map((item) => {
            const Icon = item.icon
            return (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === '/'}
                onClick={onClose}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-semibold transition-all duration-200 ${isActive
                    ? 'text-white shadow-lg shadow-violet-200'
                    : 'text-slate-600 hover:bg-white/60 hover:text-slate-900'
                  }`
                }
                style={({ isActive }) =>
                  isActive
                    ? { background: 'linear-gradient(135deg, #7c3aed 0%, #14b8a6 100%)' }
                    : {}
                }
              >
                <Icon className="h-5 w-5 flex-shrink-0" />
                <span>{item.label}</span>
              </NavLink>
            )
          })}
        </nav>

        <div className="mt-auto border-t border-slate-100 pt-6">
          <button
            onClick={handleAuthClick}
            className="flex w-full items-center gap-4 rounded-xl p-2.5 transition-all hover:bg-slate-50 active:scale-95 group"
          >
            <div className={`flex h-10 w-10 items-center justify-center rounded-xl shadow-sm border ${accessToken
              ? 'bg-rose-50 border-rose-100 text-rose-500'
              : 'bg-violet-50 border-violet-100 text-violet-500'
              }`}>
              {accessToken ? <LogOut className="h-5 w-5" /> : <Users className="h-5 w-5" />}
            </div>
            <span className="font-bold text-slate-800 transition-colors">
              {accessToken ? 'Logout' : 'Login'}
            </span>
          </button>
        </div>
      </div>
    </aside>
  )
}
