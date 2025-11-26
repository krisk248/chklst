import { useAppStore } from '../stores'

export function useToast() {
  const appStore = useAppStore()

  const showToast = (
    message: string,
    type: 'info' | 'success' | 'error' | 'warning' = 'info',
    duration = 3000
  ) => {
    appStore.showNotification(message, type)
    if (duration > 0) {
      setTimeout(() => {
        appStore.hideNotification()
      }, duration)
    }
  }

  const success = (message: string, duration = 3000) => {
    showToast(message, 'success', duration)
  }

  const error = (message: string, duration = 3000) => {
    showToast(message, 'error', duration)
  }

  const info = (message: string, duration = 3000) => {
    showToast(message, 'info', duration)
  }

  const warning = (message: string, duration = 3000) => {
    showToast(message, 'warning', duration)
  }

  return {
    showToast,
    success,
    error,
    info,
    warning,
  }
}
