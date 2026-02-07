import type { ReactNode } from 'react'
import Header from './Header'
import Sidebar from './Sidebar'

interface MainLayoutProps {
  children: ReactNode
}

export default function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="min-h-screen bg-slate-50">
      <Header />
      <div className="mx-auto flex max-w-6xl gap-6 px-6 py-8">
        <Sidebar />
        <main className="flex-1">
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-subtle">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
