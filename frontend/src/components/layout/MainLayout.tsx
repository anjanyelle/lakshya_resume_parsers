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
      className="flex h-screen relative overflow-hidden bg-slate-100"
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


        {/* Page content wrapper */}
        <div className="relative z-10 flex flex-1 flex-col h-full overflow-hidden bg-slate-100/30 shadow-sm ml-0">
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
