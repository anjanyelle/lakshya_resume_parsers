import React from 'react'
import { Check, X, Bell, ExternalLink, Calendar, Trash2 } from 'lucide-react'
import { useNotificationStore, type AppNotification } from '../../store/notificationStore'

interface NotificationDropdownProps {
  onClose: () => void
}

export default function NotificationDropdown({ onClose }: NotificationDropdownProps) {
  const { notifications, unreadCount, markAsRead, markAllAsRead, removeNotification, clearAll } = useNotificationStore()

  const typeStyles: Record<string, { bg: string; icon: any; color: string }> = {
    success: { bg: 'bg-emerald-50 text-emerald-600', icon: Check, color: 'text-emerald-500' },
    error: { bg: 'bg-rose-50 text-rose-600', icon: X, color: 'text-rose-500' },
    info: { bg: 'bg-violet-50 text-violet-600', icon: Bell, color: 'text-violet-500' },
    warning: { bg: 'bg-amber-50 text-amber-600', icon: Bell, color: 'text-amber-500' },
  }

  const formatTime = (ts: number) => {
    const min = Math.floor((Date.now() - ts) / 60000)
    if (min < 1) return 'JUST NOW'
    if (min < 60) return `${min} MIN AGO`
    const hours = Math.floor(min / 60)
    if (hours < 24) return `${hours} HOURS AGO`
    return new Date(ts).toLocaleDateString()
  }

  return (
    <div className="absolute right-0 mt-3 w-80 sm:w-96 overflow-hidden rounded-2xl bg-white/95 backdrop-blur-xl shadow-2xl ring-1 ring-slate-100 z-50 animate-in fade-in zoom-in-95 slide-in-from-top-2 duration-300">
      <div className="flex items-center justify-between border-b border-slate-100 bg-white/50 px-4 py-4">
        <div className="flex flex-col">
           <h3 className="text-sm font-bold text-slate-800 uppercase tracking-tight">System Alerts</h3>
           <p className="text-[10px] font-bold text-slate-400 mt-0.5">{unreadCount} UNREAD NOTIFICATIONS</p>
        </div>
        <div className="flex items-center gap-1">
          <button 
            onClick={markAllAsRead} 
            className="p-2 rounded-lg text-slate-400 hover:text-violet-600 hover:bg-violet-50 transition-all uppercase text-[10px] font-bold tracking-widest"
            title="Mark all as read"
          >
            Mark All
          </button>
          <button 
             onClick={clearAll}
             className="p-2 rounded-lg text-slate-300 hover:text-rose-600 hover:bg-rose-50 transition-all"
             title="Clear Inbox"
          >
             <Trash2 className="h-4 w-4" />
          </button>
        </div>
      </div>

      <div className="max-h-[420px] overflow-y-auto scrollbar-thin">
        {notifications.length === 0 ? (
          <div className="py-16 px-4 text-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-50 text-slate-300 mx-auto mb-3 shadow-inner">
              <Bell className="h-6 w-6" />
            </div>
            <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">Inbox Zero</p>
            <p className="text-[10px] text-slate-300 mt-1 uppercase tracking-tighter italic-placeholder">— All system events cleared —</p>
          </div>
        ) : (
          <div className="divide-y divide-slate-50">
            {notifications.map((notif) => {
              const style = typeStyles[notif.type] || typeStyles.info
              return (
                <div 
                  key={notif.id}
                  onClick={() => markAsRead(notif.id)}
                  className={`group relative flex items-start gap-3 p-4 transition-all duration-300 cursor-pointer ${
                    !notif.read ? 'bg-violet-50/30' : 'hover:bg-slate-50'
                  }`}
                >
                  <div className={`flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl shadow-sm ${style.bg} transition-transform duration-300 group-hover:scale-110`}>
                    <style.icon className="h-5 w-5" />
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                       <p className={`text-xs font-bold tracking-tight ${!notif.read ? 'text-slate-800' : 'text-slate-600'}`}>
                         {notif.title}
                       </p>
                       {!notif.read && (
                         <span className="h-2 w-2 rounded-full bg-violet-500 shadow-sm shadow-violet-200 animate-pulse" />
                       )}
                    </div>
                    <p className="text-[11px] text-slate-400 leading-tight mt-1 truncate-2-lines line-clamp-2">
                       {notif.message}
                    </p>
                    <div className="flex items-center gap-3 mt-2">
                       <span className="flex items-center gap-1.5 text-[9px] font-bold text-slate-300 uppercase tracking-widest leading-none">
                          <Calendar className="h-3 w-3" />
                          {formatTime(notif.timestamp)}
                       </span>
                       {notif.link && (
                          <a 
                            href={notif.link} 
                            onClick={(e) => { e.stopPropagation(); onClose(); }}
                            className="flex items-center gap-1 text-[9px] font-bold text-violet-400 hover:text-violet-600 uppercase tracking-widest"
                          >
                             View <ExternalLink className="h-2.5 w-2.5" />
                          </a>
                       )}
                    </div>
                  </div>
                  <button 
                    onClick={(e) => { e.stopPropagation(); removeNotification(notif.id); }}
                    className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 p-1.5 text-slate-300 hover:text-rose-500 transition-all rounded-lg"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </div>
              )
            })}
          </div>
        )}
      </div>

      <div className="border-t border-slate-100 bg-slate-50/50 px-4 py-3 text-center">
        <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest">
           Resume Center
        </p>
      </div>
    </div>
  )
}
