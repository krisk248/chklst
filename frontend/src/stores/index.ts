import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    isLoading: false,
    notification: {
      visible: false,
      message: '',
      type: 'info' as 'info' | 'success' | 'error' | 'warning',
    },
  }),
  getters: {
    hasNotification: (state) => state.notification.visible,
  },
  actions: {
    setLoading(loading: boolean) {
      this.isLoading = loading
    },
    showNotification(
      message: string,
      type: 'info' | 'success' | 'error' | 'warning' = 'info'
    ) {
      this.notification = {
        visible: true,
        message,
        type,
      }
      setTimeout(() => {
        this.notification.visible = false
      }, 3000)
    },
    hideNotification() {
      this.notification.visible = false
    },
  },
})
