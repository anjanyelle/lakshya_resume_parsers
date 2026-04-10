import { Briefcase, Plus } from 'lucide-react'

export default function JobPostingsPage() {
  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div />
        <button
          className="flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-semibold text-white shadow-md transition-all hover:opacity-90"
          style={{ background: 'linear-gradient(135deg,#7c3aed,#a78bfa)' }}
        >
          <Plus className="h-4 w-4" />
          New Job Posting
        </button>
      </div>

      <div className="flex flex-col items-center justify-center py-20 text-center">
        <div
          className="flex h-20 w-20 items-center justify-center rounded-3xl mb-5"
          style={{
            background: 'linear-gradient(135deg,rgba(124,58,237,0.1),rgba(20,184,166,0.1))',
          }}
        >
          <Briefcase className="h-10 w-10 text-violet-400" />
        </div>
        <h3 className="text-lg font-semibold text-slate-700">No Job Postings Yet</h3>
        <p className="mt-2 text-sm text-slate-400 max-w-sm">
          Create job postings to match candidates against specific role requirements and
          generate AI-powered fit scores.
        </p>
        <button
          className="mt-6 flex items-center gap-2 rounded-xl px-5 py-2.5 text-sm font-semibold text-white shadow-md transition-all hover:opacity-90"
          style={{ background: 'linear-gradient(135deg,#7c3aed,#a78bfa)' }}
        >
          <Plus className="h-4 w-4" />
          Create First Job Posting
        </button>
      </div>
    </div>
  )
}
