<template>
  <div class="space-y-6">
    <div class="page-header">
      <div>
        <h1 class="page-title">Settings</h1>
        <p class="text-gray-400 mt-2">Manage application settings and preferences</p>
      </div>
    </div>

    <form @submit.prevent="handleSaveSettings">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Settings Navigation -->
        <div class="lg:col-span-1">
          <Card title="Settings">
            <nav class="space-y-2">
              <button
                v-for="item in settingsSections"
                :key="item.id"
                type="button"
                @click="activeSection = item.id"
                :class="[
                  'w-full text-left px-4 py-3 rounded-lg transition-all',
                  activeSection === item.id
                    ? 'bg-[#4a9eff] text-white'
                    : 'bg-[#404040] text-gray-300 hover:bg-[#555555]',
                ]"
              >
                {{ item.label }}
              </button>
            </nav>
          </Card>
        </div>

        <!-- Settings Content -->
        <div class="lg:col-span-2">
          <!-- User Defaults Section -->
          <Card v-if="activeSection === 'user'" title="User Defaults">
            <div class="space-y-4">
              <Select
                v-model="settingsForm.default_deployed_by"
                :options="developerOptions"
                label="Default Deployed By"
                required
              />
              <p class="text-sm text-gray-400 mt-4">
                This user will be pre-selected in the deployment form.
              </p>
            </div>
          </Card>

          <!-- Export Settings Section -->
          <Card v-if="activeSection === 'export'" title="Export Settings">
            <div class="space-y-4">
              <Input
                v-model="settingsForm.excel_export_path"
                label="Excel Export Path"
                placeholder="/reports/exports"
                required
              />
              <p class="text-sm text-gray-400 mt-4">
                Specify the default directory for exported Excel files.
              </p>
            </div>
          </Card>

          <!-- Display Settings Section -->
          <Card v-if="activeSection === 'display'" title="Display Settings">
            <div class="space-y-4">
              <div class="space-y-2">
                <label class="text-sm font-medium text-gray-300">Theme</label>
                <Select
                  v-model="displaySettings.theme"
                  :options="['Dark', 'Light']"
                />
              </div>
              <div class="space-y-2">
                <label class="text-sm font-medium text-gray-300">Items Per Page</label>
                <Select
                  v-model="displaySettings.itemsPerPage"
                  :options="['10', '25', '50', '100']"
                />
              </div>
            </div>
          </Card>

          <!-- Advanced Settings Section -->
          <Card v-if="activeSection === 'advanced'" title="Advanced Settings">
            <div class="space-y-4">
              <div class="space-y-2">
                <label class="flex items-center gap-2 cursor-pointer">
                  <input
                    v-model="advancedSettings.enableNotifications"
                    type="checkbox"
                    class="w-4 h-4"
                  />
                  <span class="text-white">Enable Browser Notifications</span>
                </label>
              </div>
              <div class="space-y-2">
                <label class="flex items-center gap-2 cursor-pointer">
                  <input
                    v-model="advancedSettings.enableAutoRefresh"
                    type="checkbox"
                    class="w-4 h-4"
                  />
                  <span class="text-white">Enable Auto-refresh</span>
                </label>
              </div>
              <div class="space-y-2">
                <label class="text-sm font-medium text-gray-300">Auto-refresh Interval (seconds)</label>
                <Input
                  v-model.number="advancedSettings.refreshInterval"
                  type="number"
                  min="5"
                  max="300"
                />
              </div>
            </div>
          </Card>

          <!-- Save Button -->
          <div class="mt-6">
            <Button variant="success" type="submit">
              <Save class="w-4 h-4" />
              Save Settings
            </Button>
          </div>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import Card from '../components/ui/Card.vue'
import Input from '../components/ui/Input.vue'
import Select from '../components/ui/Select.vue'
import Button from '../components/ui/Button.vue'
import { useSettingsStore } from '../stores/settings'
import { useLibraryStore } from '../stores/library'
import { useToast } from '../composables/useToast'
import { Save } from 'lucide-vue-next'

const settingsStore = useSettingsStore()
const libraryStore = useLibraryStore()
const { success, error } = useToast()

const activeSection = ref('user')

const settingsSections = [
  { id: 'user', label: 'User Defaults' },
  { id: 'export', label: 'Export Settings' },
  { id: 'display', label: 'Display' },
  { id: 'advanced', label: 'Advanced' },
]

const settingsForm = ref({
  default_deployed_by: settingsStore.settings.default_deployed_by,
  excel_export_path: settingsStore.settings.excel_export_path,
})

const displaySettings = ref({
  theme: 'Dark',
  itemsPerPage: '25',
})

const advancedSettings = ref({
  enableNotifications: true,
  enableAutoRefresh: false,
  refreshInterval: 30,
})

const developerOptions = computed(() => libraryStore.presets.developers)

const handleSaveSettings = async () => {
  const result = await settingsStore.saveSettings({
    default_deployed_by: settingsForm.value.default_deployed_by,
    excel_export_path: settingsForm.value.excel_export_path,
  })

  if (result) {
    success('Settings saved successfully!')
  } else {
    error('Failed to save settings')
  }
}

onMounted(async () => {
  if (libraryStore.presets.developers.length === 0) {
    await libraryStore.fetchPresets()
  }
  await settingsStore.fetchSettings()
  settingsForm.value = {
    default_deployed_by: settingsStore.settings.default_deployed_by,
    excel_export_path: settingsStore.settings.excel_export_path,
  }
})
</script>
