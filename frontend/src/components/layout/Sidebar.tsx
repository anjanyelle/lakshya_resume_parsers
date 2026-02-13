import { NavLink } from 'react-router-dom'
import {
  BarChart3,
  ClipboardCheck,
  Database,
  FileText,
  LayoutDashboard,
  UploadCloud,
  Users,
} from 'lucide-react'

const links = [
  { label: 'Overview', path: '/', icon: LayoutDashboard },
  { label: 'Upload Resume', path: '/upload', icon: UploadCloud },
  { label: 'Candidates', path: '/candidates', icon: Users },
  { label: 'Accuracy', path: '/accuracy', icon: BarChart3 },
  { label: 'Corrections', path: '/corrections', icon: ClipboardCheck },
  { label: 'Taxonomy', path: '/taxonomy', icon: Database },
]

export default function Sidebar() {
  return (
    <aside className="hidden w-64 flex-shrink-0 border-r border-slate-200 bg-white px-4 py-6 lg:block">
      <div className="mb-8 flex items-center gap-3 rounded-xl bg-slate-50 px-4 py-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-600 text-white">
          <FileText className="h-4 w-4" />
        </div>
        <div>
          <p className="text-sm font-semibold text-slate-900">Resume Parser</p>
          <p className="text-xs text-slate-500">Admin Console</p>
        </div>
      </div>

      <nav className="space-y-1 text-sm font-medium">
        {links.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2 transition ${
                  isActive
                    ? 'bg-brand-50 text-brand-700'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                }`
              }
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </NavLink>
          )
        })}
      </nav>
    </aside>
  )
}
