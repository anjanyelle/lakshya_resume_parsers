import type { ReactNode } from 'react'
import Sidebar from './Sidebar'
import Header from './Header'

interface MainLayoutProps {
  children: ReactNode
}

export default function MainLayout({ children }: MainLayoutProps) {
  return (
    <div
      className="flex min-h-screen"
      style={{
        background: 'linear-gradient(160deg, #f5f3ff 0%, #ede9fe 20%, #e0f7fa 60%, #f0fdfa 100%)',
      }}
    >
      {/* Fixed Sidebar */}
      <Sidebar open={true} />

      {/* Main Content Area */}
      <div className="flex flex-1 flex-col min-w-0">
        {/* Top gradient band (teal accent on right) */}
        <div
          className="absolute top-0 right-0 w-1/3 h-48 pointer-events-none z-0"
          style={{
            background:
              'linear-gradient(135deg, rgba(204,251,241,0.6) 0%, rgba(153,246,228,0.4) 50%, transparent 100%)',
            borderRadius: '0 0 0 80px',
          }}
        />

        {/* Page content wrapper */}
        <div className="relative z-10 flex flex-1 flex-col min-h-screen bg-white/70 rounded-tl-2xl shadow-sm ml-0">
          {/* Header */}
          <Header />

          {/* Page Body */}
          <main className="flex-1 overflow-auto p-6">
            {children}
          </main>
        </div>
      </div>
    </div>
  )
}
