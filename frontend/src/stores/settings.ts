import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useApi } from '../composables/useApi'

export interface AppSettings {
  default_deployed_by: string
  excel_export_path: string
}

export const useSettingsStore = defineStore('settings', () => {
  const settings = ref<AppSettings>({
    default_deployed_by: 'Kannan',
    excel_export_path: '/reports',
  })
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const { get, post } = useApi()

  const fetchSettings = async () => {
    isLoading.value = true
    error.value = null
    try {
      const response = await get<AppSettings>('/settings')
      settings.value = response.data || settings.value
    } catch (err) {
      error.value = 'Failed to fetch settings'
      console.error(err)
    } finally {
      isLoading.value = false
    }
  }

  const saveSettings = async (newSettings: Partial<AppSettings>) => {
    isLoading.value = true
    error.value = null
    try {
      const updated = { ...settings.value, ...newSettings }
      const response = await post<AppSettings>('/settings', updated)
      settings.value = response.data || updated
      return true
    } catch (err) {
      error.value = 'Failed to save settings'
      console.error(err)
      return false
    } finally {
      isLoading.value = false
    }
  }

  const setDefaultDeployedBy = (name: string) => {
    settings.value.default_deployed_by = name
  }

  const setExcelExportPath = (path: string) => {
    settings.value.excel_export_path = path
  }

  return {
    settings,
    isLoading,
    error,
    fetchSettings,
    saveSettings,
    setDefaultDeployedBy,
    setExcelExportPath,
  }
})
