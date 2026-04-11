import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export type NotificationType = 'success' | 'error' | 'info' | 'warning'

export interface AppNotification {
  id: string
  type: NotificationType
  title: string
  message: string
  timestamp: number
  read: boolean
  link?: string
}

interface NotificationState {
  notifications: AppNotification[]
  unreadCount: number
  addNotification: (notification: Omit<AppNotification, 'id' | 'timestamp' | 'read'>) => void
  markAsRead: (id: string) => void
  markAllAsRead: () => void
  removeNotification: (id: string) => void
  clearAll: () => void
}

export const useNotificationStore = create<NotificationState>()(
  persist(
    (set) => ({
      notifications: [],
      unreadCount: 0,
      addNotification: (n) =>
        set((state) => {
          const newNotification: AppNotification = {
            ...n,
            id: Math.random().toString(36).substring(7),
            timestamp: Date.now(),
            read: false,
          }
          const nextNotifications = [newNotification, ...state.notifications].slice(0, 50)
          return {
            notifications: nextNotifications,
            unreadCount: nextNotifications.filter((notif) => !notif.read).length,
          }
        }),
      markAsRead: (id) =>
        set((state) => {
          const next = state.notifications.map((n) =>
            n.id === id ? { ...n, read: true } : n
          )
          return {
            notifications: next,
            unreadCount: next.filter((n) => !n.read).length,
          }
        }),
      markAllAsRead: () =>
        set((state) => ({
          notifications: state.notifications.map((n) => ({ ...n, read: true })),
          unreadCount: 0,
        })),
      removeNotification: (id) =>
        set((state) => {
          const next = state.notifications.filter((n) => n.id !== id)
          return {
            notifications: next,
            unreadCount: next.filter((n) => !n.read).length,
          }
        }),
      clearAll: () => set({ notifications: [], unreadCount: 0 }),
    }),
    {
      name: 'resume-parser-notifications',
    }
  )
)
