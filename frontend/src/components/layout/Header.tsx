import { useLocation } from 'react-router-dom'

const pageTitles: Record<string, { title: string; subtitle: string }> = {
  '/': {
    title: 'ATS Resume Analyzer',
    subtitle: 'AI-powered recruitment insights and candidate analysis.',
  },
  '/upload': {
    title: 'Resume Analyzer',
    subtitle: 'Upload and analyze resumes with AI-powered insights.',
  },
  '/candidates': {
    title: 'Candidate Management',
    subtitle: 'Manage and review analyzed candidates.',
  },
  '/job-postings': {
    title: 'Job Postings',
    subtitle: 'Manage job postings and requirements.',
  },
  '/analytics': {
    title: 'Analytics',
    subtitle: 'Deep insights into your recruitment pipeline.',
  },
  '/settings': {
    title: 'Settings',
    subtitle: 'Configure your ATS preferences.',
  },
}

export default function Header() {
  const location = useLocation()

  // Find the best matching path
  const matchedPath = Object.keys(pageTitles)
    .filter((p) => location.pathname === p || location.pathname.startsWith(p + '/'))
    .sort((a, b) => b.length - a.length)[0] ?? '/'

  const pageInfo = pageTitles[matchedPath] ?? pageTitles['/']

  return (
    <div className="flex items-start justify-between px-6 py-5 border-b border-slate-100 bg-white">
      {/* Left: Title */}
      <div>
        <h1 className="text-2xl font-bold text-slate-800">{pageInfo.title}</h1>
        <p className="mt-0.5 text-sm text-slate-500">{pageInfo.subtitle}</p>
      </div>
    </div>
  )
}
