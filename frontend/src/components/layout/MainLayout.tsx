import { ReactNode, useState } from 'react'
import Sidebar from './Sidebar'
import Header from './Header'

interface MainLayoutProps {
  children: ReactNode
}

export default function MainLayout({ children }: MainLayoutProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)

  const toggleSidebar = () => setIsSidebarOpen(!isSidebarOpen)
  const closeSidebar = () => setIsSidebarOpen(false)

  return (
    <div
      className="flex min-h-screen relative overflow-x-hidden"
      style={{
        background: 'linear-gradient(160deg, #f5f3ff 0%, #ede9fe 20%, #e0f7fa 60%, #f0fdfa 100%)',
      }}
    >
      {/* Mobile Backdrop */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-slate-900/40 backdrop-blur-sm transition-opacity lg:hidden"
          onClick={closeSidebar}
        />
      )}

      {/* Sidebar */}
      <Sidebar open={isSidebarOpen} onClose={closeSidebar} />

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
        <div className="relative z-10 flex flex-1 flex-col min-h-screen bg-white/70 lg:rounded-tl-2xl shadow-sm ml-0">
          {/* Header */}
          <Header onMenuClick={toggleSidebar} />

          {/* Page Body */}
          <main className="flex-1 overflow-auto p-4 md:p-6 lg:p-8">
            <div className="mx-auto max-w-[1600px]">
              {children}
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}
