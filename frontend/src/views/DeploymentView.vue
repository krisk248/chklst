<template>
  <div class="space-y-4">
    <div class="page-header">
      <div>
        <h1 class="page-title text-xl">Create Deployment</h1>
        <p class="text-gray-400 text-sm">Record a new deployment</p>
      </div>
    </div>

    <Card title="Deployment Information">
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <!-- Project and Component Selection -->
        <div class="grid grid-cols-2 gap-3">
          <Select
            v-model="form.project_id"
            :options="projectNames"
            label="Project"
            required
            @update:model-value="handleProjectChange"
          />
          <Select
            v-model="form.component_id"
            :options="componentNames"
            label="Component"
            required
            :disabled="!form.project_id"
          />
        </div>

        <!-- Auto-filled Section (Compact) -->
        <div v-if="selectedComponent" class="p-3 bg-[#353535] rounded-lg border border-[#444444] text-xs">
          <h3 class="text-xs font-medium text-gray-500 mb-2">Auto-filled (Read-only)</h3>
          <div class="grid grid-cols-3 gap-2">
            <div>
              <span class="text-gray-500">Component:</span>
              <span class="text-gray-300 ml-1">{{ autoFilled.component_name }}</span>
            </div>
            <div>
              <span class="text-gray-500">Developer:</span>
              <span class="text-gray-300 ml-1">{{ autoFilled.developer }}</span>
            </div>
            <div>
              <span class="text-gray-500">Environment:</span>
              <span class="text-gray-300 ml-1">{{ autoFilled.environment }}</span>
            </div>
            <div>
              <span class="text-gray-500">Build Server:</span>
              <span class="text-gray-300 ml-1">{{ autoFilled.build_server }}</span>
            </div>
            <div>
              <span class="text-gray-500">Deploy Server:</span>
              <span class="text-gray-300 ml-1">{{ autoFilled.deploy_server }}</span>
            </div>
            <div>
              <span class="text-gray-500">Database:</span>
              <span class="text-gray-300 ml-1">{{ autoFilled.database_name }}</span>
            </div>
          </div>
          <div class="mt-2">
            <span class="text-gray-500">VCS:</span>
            <span class="text-gray-300 ml-1 break-all">{{ autoFilled.vcs_url }}</span>
          </div>
        </div>

        <!-- Deployment Details -->
        <div class="space-y-3 p-3 bg-[#404040] rounded-lg border border-[#555555]">
          <div class="grid grid-cols-2 gap-3">
            <Input
              v-model="form.jira_id"
              label="Patch ID"
              placeholder="e.g., PAT-123 (optional)"
            />
            <div class="flex gap-2 items-end">
              <Input
                v-model="form.timestamp"
                label="Timestamp"
                type="datetime-local"
                required
                class="flex-1"
              />
              <Button type="button" @click="setCurrentTimestamp" variant="secondary" size="sm">
                <Clock class="w-3 h-3" />
                Now
              </Button>
            </div>
          </div>

          <!-- Radio Buttons Row -->
          <div class="grid grid-cols-3 gap-4">
            <!-- Database Script -->
            <div>
              <label class="text-xs font-medium text-gray-300 block mb-1">DB Script</label>
              <div class="flex items-center gap-3">
                <label class="flex items-center gap-1 cursor-pointer text-sm">
                  <input v-model="form.database_script" type="radio" :value="false" class="w-3 h-3" />
                  <span>No</span>
                </label>
                <label class="flex items-center gap-1 cursor-pointer text-sm">
                  <input v-model="form.database_script" type="radio" :value="true" class="w-3 h-3" />
                  <span>Yes</span>
                </label>
              </div>
            </div>

            <!-- Build Status -->
            <div>
              <label class="text-xs font-medium text-gray-300 block mb-1">Build Status</label>
              <div class="flex items-center gap-3">
                <label class="flex items-center gap-1 cursor-pointer text-sm">
                  <input v-model="form.build_status" type="radio" value="success" class="w-3 h-3" />
                  <span class="text-green-400">Success</span>
                </label>
                <label class="flex items-center gap-1 cursor-pointer text-sm">
                  <input v-model="form.build_status" type="radio" value="failed" class="w-3 h-3" />
                  <span class="text-red-400">Failed</span>
                </label>
              </div>
            </div>

            <!-- Deploy Status -->
            <div>
              <label class="text-xs font-medium text-gray-300 block mb-1">Deploy Status</label>
              <div class="flex items-center gap-3">
                <label class="flex items-center gap-1 cursor-pointer text-sm">
                  <input v-model="form.deploy_status" type="radio" value="success" class="w-3 h-3" />
                  <span class="text-green-400">Success</span>
                </label>
                <label class="flex items-center gap-1 cursor-pointer text-sm">
                  <input v-model="form.deploy_status" type="radio" value="failed" class="w-3 h-3" />
                  <span class="text-red-400">Failed</span>
                </label>
              </div>
            </div>
          </div>

          <!-- DB Script Name (conditional) -->
          <Input
            v-if="form.database_script"
            v-model="form.database_script_name"
            label="Script Name"
            placeholder="e.g., migration_001.sql"
          />

          <!-- Notes -->
          <Textarea
            v-model="form.notes"
            label="Notes"
            placeholder="Additional notes..."
            :rows="2"
          />

          <!-- Deployed By (read-only from settings) -->
          <div class="flex items-center gap-2">
            <span class="text-xs text-gray-400">Deployed By:</span>
            <span class="text-sm font-medium text-white">{{ form.deployed_by || settingsStore.settings?.default_deployed_by || 'Kannan' }}</span>
            <span class="text-xs text-gray-500">(from Settings)</span>
          </div>
        </div>

        <!-- Saved State Banner -->
        <div v-if="savedDeployment" class="p-3 bg-green-900/30 border border-green-600 rounded-lg">
          <div class="flex items-center gap-2 text-green-400 mb-2">
            <CheckCircle class="w-5 h-5" />
            <span class="font-medium">Deployment Saved Successfully!</span>
          </div>
          <p class="text-sm text-gray-300">Use the buttons below to copy deployment info, then click Clear to start a new deployment.</p>
        </div>

        <!-- Actions (Centered, Bigger) -->
        <div class="flex gap-4 justify-center pt-3 border-t border-[#555555]">
          <!-- Show Copy buttons after save OR when form is valid -->
          <Button
            type="button"
            variant="secondary"
            size="lg"
            @click="handleCopyToJira"
            :disabled="!isFormValid && !savedDeployment"
          >
            <Copy class="w-5 h-5" />
            Copy to JIRA
          </Button>
          <Button
            type="button"
            variant="secondary"
            size="lg"
            @click="handleCopyToTeams"
            :disabled="!isFormValid && !savedDeployment"
          >
            <Copy class="w-5 h-5" />
            Copy to Teams
          </Button>

          <!-- Clear button - shown after save -->
          <Button
            v-if="savedDeployment"
            type="button"
            variant="danger"
            size="lg"
            @click="resetForm"
          >
            <Eraser class="w-5 h-5" />
            Clear
          </Button>

          <!-- Save button - hidden after save -->
          <Button
            v-else
            variant="success"
            size="lg"
            @click="handleSubmit"
            :disabled="!isFormValid || isSubmitting"
          >
            <Save class="w-5 h-5" />
            {{ isSubmitting ? 'Saving...' : 'Save Deployment' }}
          </Button>
        </div>
      </form>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import Card from '../components/ui/Card.vue'
import Input from '../components/ui/Input.vue'
import Select from '../components/ui/Select.vue'
import Textarea from '../components/ui/Textarea.vue'
import Button from '../components/ui/Button.vue'
import { useProjectsStore, type Component } from '../stores/projects'
import { useDeploymentsStore } from '../stores/deployments'
import { useSettingsStore } from '../stores/settings'
import { useLibraryStore } from '../stores/library'
import { useClipboard, type DeploymentData } from '../composables/useClipboard'
import { useToast } from '../composables/useToast'
import { Clock, Copy, Save, Eraser, CheckCircle } from 'lucide-vue-next'

const projectsStore = useProjectsStore()
const deploymentsStore = useDeploymentsStore()
const settingsStore = useSettingsStore()
const libraryStore = useLibraryStore()
const { copyToClipboard, formatForJira, formatForTeams } = useClipboard()
const { success, error } = useToast()

// Helper to get local datetime in format required by datetime-local input
const getLocalDateTimeString = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day}T${hours}:${minutes}`
}

const form = ref({
  project_id: '',
  component_id: '',
  jira_id: '',
  timestamp: getLocalDateTimeString(),
  database_script: false,
  database_script_name: '',
  build_status: 'success' as 'success' | 'failed',
  deploy_status: 'success' as 'success' | 'failed',
  notes: '',
  deployed_by: settingsStore.settings?.default_deployed_by || 'Kannan',
})

const autoFilled = ref({
  component_name: '',
  developer: '',
  environment: '',
  build_server: '',
  deploy_server: '',
  database_name: '',
  vcs_url: '',
})

const selectedComponent = ref<Component | null>(null)
const isSubmitting = ref(false)
const savedDeployment = ref<DeploymentData | null>(null)  // Stores last saved deployment for copy operations

const projectNames = computed(() =>
  projectsStore.projects.map(p => p.name || `Project ${p.id}`)
)

const componentNames = computed(() => {
  if (!form.value.project_id) return []
  const project = projectsStore.projects.find(
    p => (p.name || `Project ${p.id}`) === form.value.project_id
  )
  return project?.components.map(c => c.name) || []
})

const isFormValid = computed(() => {
  return (
    form.value.project_id &&
    form.value.component_id &&
    form.value.timestamp &&
    form.value.deployed_by
  )
})

const handleProjectChange = () => {
  form.value.component_id = ''
  selectedComponent.value = null
  Object.keys(autoFilled.value).forEach(key => {
    autoFilled.value[key as keyof typeof autoFilled.value] = ''
  })
}

const handleComponentChange = () => {
  const project = projectsStore.projects.find(
    p => (p.name || `Project ${p.id}`) === form.value.project_id
  )
  const component = project?.components.find(c => c.name === form.value.component_id)

  if (component && project) {
    selectedComponent.value = component
    autoFilled.value = {
      component_name: component.name,
      developer: component.developer,
      environment: project.environment,
      build_server: project.build_server,
      deploy_server: project.deploy_server,
      database_name: project.database_name,
      vcs_url: component.vcs_url,
    }
  }
}

const setCurrentTimestamp = () => {
  form.value.timestamp = getLocalDateTimeString()
}

// Build deployment data for copy operations
const buildDeploymentData = (): DeploymentData => {
  const project = projectsStore.projects.find(
    p => (p.name || `Project ${p.id}`) === form.value.project_id
  )
  return {
    patchId: form.value.jira_id || undefined,
    project: form.value.project_id,
    component: form.value.component_id,
    environment: autoFilled.value.environment || project?.environment,
    componentUrl: selectedComponent.value?.component_url,
    buildServer: autoFilled.value.build_server || project?.build_server,
    buildStatus: form.value.build_status,
    vcsUrl: autoFilled.value.vcs_url || selectedComponent.value?.vcs_url,
    deployServer: autoFilled.value.deploy_server || project?.deploy_server,
    buildBackup: project?.backup_location,
    databaseName: autoFilled.value.database_name || project?.database_name,
    deployStatus: form.value.deploy_status,
    databaseScript: form.value.database_script ? form.value.database_script_name : undefined,
    developer: autoFilled.value.developer || selectedComponent.value?.developer,
    deployedBy: form.value.deployed_by,
    timestamp: form.value.timestamp,
    notes: form.value.notes || undefined,
  }
}

const handleCopyToJira = async () => {
  if (!isFormValid.value && !savedDeployment.value) return

  // Use saved data if available, otherwise build from current form
  const data = savedDeployment.value || buildDeploymentData()

  const text = formatForJira(data)
  if (await copyToClipboard(text)) {
    success('Copied to clipboard for JIRA!')
  } else {
    error('Failed to copy to clipboard')
  }
}

const handleCopyToTeams = async () => {
  if (!isFormValid.value && !savedDeployment.value) return

  // Use saved data if available, otherwise build from current form
  const data = savedDeployment.value || buildDeploymentData()

  const text = formatForTeams(data)
  if (await copyToClipboard(text)) {
    success('Copied to clipboard for Teams!')
  } else {
    error('Failed to copy to clipboard')
  }
}

const handleSubmit = async () => {
  // Prevent double-clicks
  if (isSubmitting.value) return
  if (!isFormValid.value) return

  if (!form.value.jira_id || form.value.jira_id.trim() === '') {
    const confirmed = window.confirm(
      'No Patch ID entered. Continue saving without a Patch ID?'
    )
    if (!confirmed) return
  }

  isSubmitting.value = true

  const project = projectsStore.projects.find(
    p => (p.name || `Project ${p.id}`) === form.value.project_id
  )

  const deployment = {
    jira_id: form.value.jira_id?.trim() || null,
    project_id: parseInt(project?.id?.toString() || '0'),
    component_id: selectedComponent.value?.id ? parseInt(selectedComponent.value.id.toString()) : undefined,
    timestamp: form.value.timestamp,
    environment: autoFilled.value.environment,
    vcs_url: autoFilled.value.vcs_url,
    developer_name: autoFilled.value.developer,
    build_server: autoFilled.value.build_server,
    deploy_server: autoFilled.value.deploy_server,
    database_name: autoFilled.value.database_name,
    database_script: form.value.database_script ? form.value.database_script_name : undefined,
    build_status: form.value.build_status,
    deploy_status: form.value.deploy_status,
    notes: form.value.notes,
    deployed_by: form.value.deployed_by,
  }

  try {
    const result = await deploymentsStore.createDeployment(deployment)
    if (result) {
      success('Deployment saved! Use Copy buttons or Clear to start new.')
      // Store saved data for copy operations
      savedDeployment.value = buildDeploymentData()
      // Don't reset form - let user copy first
    } else {
      error('Failed to save deployment')
      savedDeployment.value = null
    }
  } finally {
    isSubmitting.value = false
  }
}

const resetForm = () => {
  form.value = {
    project_id: '',
    component_id: '',
    jira_id: '',
    timestamp: getLocalDateTimeString(),
    database_script: false,
    database_script_name: '',
    build_status: 'success',
    deploy_status: 'success',
    notes: '',
    deployed_by: settingsStore.settings?.default_deployed_by || 'Kannan',
  }
  selectedComponent.value = null
  savedDeployment.value = null  // Clear saved state
  Object.keys(autoFilled.value).forEach(key => {
    autoFilled.value[key as keyof typeof autoFilled.value] = ''
  })
}

watch(() => form.value.component_id, () => {
  handleComponentChange()
})

onMounted(async () => {
  if (projectsStore.projects.length === 0) {
    await projectsStore.fetchProjects()
  }
  if (libraryStore.presets.developers.length === 0) {
    await libraryStore.fetchPresets()
  }
  await settingsStore.fetchSettings()
  form.value.deployed_by = settingsStore.settings?.default_deployed_by || 'Kannan'
})
</script>
