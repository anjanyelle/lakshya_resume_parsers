import { Settings } from 'lucide-react'

export default function SettingsPage() {
  return (
    <div className="space-y-6 animate-fade-in">
      {/* General Settings */}
      <div className="rounded-xl bg-white p-5 shadow-card border border-slate-100">
        <h3 className="mb-4 text-sm font-bold text-slate-800">General</h3>
        <div className="space-y-4">
          {[
            { label: 'Application Name', value: 'ATS Analyzer', type: 'text' },
            { label: 'Default Job Role', value: 'Full Stack Developer', type: 'text' },
            { label: 'Max File Size (MB)', value: '10', type: 'number' },
          ].map((field) => (
            <div key={field.label} className="flex items-center gap-4">
              <label className="w-48 flex-shrink-0 text-sm font-bold text-slate-800">{field.label}</label>
              <input
                type={field.type}
                defaultValue={field.value}
                className="flex-1 rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-violet-300"
              />
            </div>
          ))}
        </div>
      </div>

      {/* Backend Connection */}
      <div className="rounded-xl bg-white p-5 shadow-card border border-slate-100">
        <h3 className="mb-1 text-sm font-bold text-slate-800">Backend Connection</h3>
        <p className="mb-4 text-xs text-slate-400">Configure the Python backend API endpoint</p>
        <div className="space-y-4">
          <div className="flex items-center gap-4">
            <label className="w-48 flex-shrink-0 text-sm font-bold text-slate-800">API URL</label>
            <input
              type="text"
              defaultValue="http://localhost:8000"
              className="flex-1 rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-violet-300"
            />
          </div>
          <div className="flex items-center gap-4">
            <div className="w-48" />
            <div className="flex items-center gap-3">
              <div className="flex h-2.5 w-2.5 rounded-full bg-amber-400" />
              <span className="text-sm text-slate-500">Disconnected — Demo Mode active</span>
              <button
                className="rounded-lg px-3 py-1.5 text-xs font-medium text-white transition-all hover:opacity-90"
                style={{ background: 'linear-gradient(135deg,#7c3aed,#a78bfa)' }}
              >
                Test Connection
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Save */}
      <div className="flex justify-end">
        <button
          className="rounded-xl px-6 py-2.5 text-sm font-semibold text-white shadow-md transition-all hover:opacity-90"
          style={{ background: 'linear-gradient(135deg,#7c3aed,#a78bfa)' }}
        >
          Save Changes
        </button>
      </div>
    </div>
  )
}
