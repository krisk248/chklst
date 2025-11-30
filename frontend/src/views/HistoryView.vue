<template>
  <div class="space-y-4">
    <div class="page-header">
      <div>
        <h1 class="page-title text-xl">Deployment History</h1>
        <p class="text-gray-400 text-sm">View and analyze deployments</p>
      </div>
      <Button variant="secondary" size="sm" @click="handleRefresh">
        <RefreshCw class="w-4 h-4" />
        Refresh
      </Button>
    </div>

    <!-- Summary Stats - Deployed By and Success Rate -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
      <Card>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-400 text-xs">Deployed By</p>
            <p class="text-xl font-bold text-white mt-1">{{ currentDeployedBy }}</p>
          </div>
          <div class="text-right">
            <p class="text-gray-400 text-xs">Success Rate</p>
            <p class="text-xl font-bold mt-1">
              <span class="text-green-400">{{ successCount }}</span>
              <span class="text-gray-400">/</span>
              <span class="text-white">{{ filteredDeployments.length }}</span>
            </p>
          </div>
        </div>
      </Card>
      <div class="grid grid-cols-4 gap-2">
        <Card class="!p-2">
          <div class="flex flex-col items-center justify-center h-full">
            <p class="text-gray-400 text-xs">7 Days</p>
            <p class="text-base font-semibold text-[#4a9eff] mt-1">{{ deploymentsLast7Days }}</p>
          </div>
        </Card>
        <Card class="!p-2">
          <div class="flex flex-col items-center justify-center h-full">
            <p class="text-gray-400 text-xs">30 Days</p>
            <p class="text-base font-semibold text-blue-400 mt-1">{{ deploymentsLast30Days }}</p>
          </div>
        </Card>
        <Card class="!p-2">
          <div class="flex flex-col items-center justify-center h-full">
            <p class="text-gray-400 text-xs">Month</p>
            <p class="text-base font-semibold text-purple-400 mt-1">{{ deploymentsThisMonth }}</p>
          </div>
        </Card>
        <Card class="!p-2">
          <div class="flex flex-col items-center justify-center h-full">
            <p class="text-gray-400 text-xs">Total</p>
            <p class="text-base font-semibold text-green-400 mt-1">{{ deploymentsStore.deployments.length }}</p>
          </div>
        </Card>
      </div>
    </div>

    <!-- Filter Tabs and Project Dropdown -->
    <div class="flex flex-wrap items-center gap-2">
      <Button
        v-for="tab in filterTabs"
        :key="tab.value"
        :variant="activeFilters.includes(tab.value) ? 'primary' : 'secondary'"
        size="sm"
        @click="toggleFilter(tab.value)"
      >
        {{ tab.label }}
      </Button>

      <!-- Project Dropdown -->
      <div class="relative ml-2">
        <select
          v-model="selectedProject"
          class="bg-[#2a2a2a] border border-gray-600 rounded px-3 py-1.5 text-sm text-white focus:outline-none focus:border-[#4a9eff]"
        >
          <option value="">All Projects</option>
          <option v-for="project in projectsStore.projects" :key="project.id" :value="project.id">
            {{ project.name }}
          </option>
        </select>
      </div>

      <!-- Sort Options -->
      <div class="relative ml-2">
        <select
          v-model="sortOption"
          class="bg-[#2a2a2a] border border-gray-600 rounded px-3 py-1.5 text-sm text-white focus:outline-none focus:border-[#4a9eff]"
        >
          <option value="date-desc">Newest First</option>
          <option value="date-asc">Oldest First</option>
          <option value="null-first">NULL Patch IDs First</option>
          <option value="project">By Project</option>
        </select>
      </div>
    </div>

    <!-- Deployment History Table -->
    <Card title="Deployments">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-gray-700">
              <th class="text-left py-2 px-3 text-gray-400 font-medium">Patch ID</th>
              <th class="text-left py-2 px-3 text-gray-400 font-medium">Timestamp</th>
              <th class="text-left py-2 px-3 text-gray-400 font-medium">Project</th>
              <th class="text-left py-2 px-3 text-gray-400 font-medium">Component</th>
              <th class="text-left py-2 px-3 text-gray-400 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="deployment in filteredDeployments"
              :key="deployment.id"
              class="border-b border-gray-800 hover:bg-[#353535]"
            >
              <td class="py-2 px-3">
                <span :class="deployment.jira_id ? 'text-white' : 'text-orange-400 italic'">
                  {{ deployment.jira_id || 'NULL' }}
                </span>
              </td>
              <td class="py-2 px-3 text-gray-300">{{ formatDate(deployment.timestamp) }}</td>
              <td class="py-2 px-3 text-white">{{ getProjectName(deployment.project_id) }}</td>
              <td class="py-2 px-3 text-gray-300">{{ getComponentName(deployment.component_id) }}</td>
              <td class="py-2 px-3">
                <div class="flex gap-1">
                  <button
                    @click="viewDeployment(deployment)"
                    class="px-2 py-1 text-xs bg-blue-600 hover:bg-blue-700 text-white rounded"
                  >
                    View
                  </button>
                  <button
                    @click="editDeployment(deployment)"
                    class="px-2 py-1 text-xs bg-yellow-600 hover:bg-yellow-700 text-white rounded"
                  >
                    Edit
                  </button>
                  <button
                    @click="confirmDelete(deployment)"
                    class="px-2 py-1 text-xs bg-red-600 hover:bg-red-700 text-white rounded"
                  >
                    Delete
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="filteredDeployments.length === 0">
              <td colspan="5" class="py-8 text-center text-gray-400">
                {{ deploymentsStore.isLoading ? 'Loading...' : 'No deployments found' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </Card>

    <!-- View Modal -->
    <div v-if="viewModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="viewModal = null">
      <Card class="w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-bold text-white">Deployment Details</h3>
          <Button variant="secondary" size="sm" @click="viewModal = null">
            <X class="w-4 h-4" />
          </Button>
        </div>

        <div class="space-y-4">
          <!-- Status Banner -->
          <div :class="viewModal.deploy_status === 'success' ? 'bg-green-900/30 border-green-600' : 'bg-red-900/30 border-red-600'" class="p-3 rounded border">
            <div class="flex justify-between items-center">
              <span class="text-gray-400">Status</span>
              <span :class="viewModal.deploy_status === 'success' ? 'text-green-400' : 'text-red-400'" class="font-bold text-lg">
                {{ viewModal.deploy_status.toUpperCase() }}
              </span>
            </div>
          </div>

          <!-- Details Grid -->
          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-3">
              <div class="p-2 bg-[#353535] rounded">
                <p class="text-gray-400 text-xs">Patch ID</p>
                <p class="text-white font-medium">{{ viewModal.jira_id || 'NULL' }}</p>
              </div>
              <div class="p-2 bg-[#353535] rounded">
                <p class="text-gray-400 text-xs">Project</p>
                <p class="text-white font-medium">{{ getProjectName(viewModal.project_id) }}</p>
              </div>
              <div class="p-2 bg-[#353535] rounded">
                <p class="text-gray-400 text-xs">Component</p>
                <p class="text-white font-medium">{{ getComponentName(viewModal.component_id) }}</p>
              </div>
              <div class="p-2 bg-[#353535] rounded">
                <p class="text-gray-400 text-xs">Environment</p>
                <p class="text-white font-medium">{{ viewModal.environment || 'N/A' }}</p>
              </div>
              <div class="p-2 bg-[#353535] rounded">
                <p class="text-gray-400 text-xs">Developer</p>
                <p class="text-white font-medium">{{ viewModal.developer_name || 'N/A' }}</p>
              </div>
            </div>
            <div class="space-y-3">
              <div class="p-2 bg-[#353535] rounded">
                <p class="text-gray-400 text-xs">Timestamp</p>
                <p class="text-white font-medium">{{ formatDate(viewModal.timestamp) }}</p>
              </div>
              <div class="p-2 bg-[#353535] rounded">
                <p class="text-gray-400 text-xs">Deployed By</p>
                <p class="text-white font-medium">{{ viewModal.deployed_by || 'N/A' }}</p>
              </div>
              <div class="p-2 bg-[#353535] rounded">
                <p class="text-gray-400 text-xs">Build Status</p>
                <p :class="viewModal.build_status === 'success' ? 'text-green-400' : 'text-red-400'" class="font-medium">
                  {{ viewModal.build_status }}
                </p>
              </div>
              <div class="p-2 bg-[#353535] rounded">
                <p class="text-gray-400 text-xs">DB Script</p>
                <p class="text-white font-medium">{{ viewModal.database_script || 'No' }}</p>
              </div>
              <div class="p-2 bg-[#353535] rounded">
                <p class="text-gray-400 text-xs">VCS URL</p>
                <p class="text-white font-medium text-xs break-all">{{ viewModal.vcs_url || 'N/A' }}</p>
              </div>
            </div>
          </div>

          <!-- Notes -->
          <div v-if="viewModal.notes" class="p-3 bg-[#353535] rounded">
            <p class="text-gray-400 text-xs mb-1">Notes</p>
            <p class="text-white">{{ viewModal.notes }}</p>
          </div>

          <!-- Server Info -->
          <div class="grid grid-cols-2 gap-3">
            <div class="p-2 bg-[#353535] rounded">
              <p class="text-gray-400 text-xs">Build Server</p>
              <p class="text-white text-sm">{{ viewModal.build_server || 'N/A' }}</p>
            </div>
            <div class="p-2 bg-[#353535] rounded">
              <p class="text-gray-400 text-xs">Deploy Server</p>
              <p class="text-white text-sm">{{ viewModal.deploy_server || 'N/A' }}</p>
            </div>
          </div>
        </div>

        <div class="flex gap-2 mt-4 justify-end">
          <Button variant="secondary" size="sm" @click="handleCopyToJira(viewModal)">
            <Copy class="w-4 h-4" />
            Copy to JIRA
          </Button>
          <Button variant="secondary" size="sm" @click="handleCopyToTeams(viewModal)">
            <Copy class="w-4 h-4" />
            Copy to Teams
          </Button>
        </div>
      </Card>
    </div>

    <!-- Edit Modal -->
    <div v-if="editModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="editModal = null">
      <Card class="w-full max-w-xl mx-4 max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-bold text-white">Edit Deployment</h3>
          <Button variant="secondary" size="sm" @click="editModal = null">
            <X class="w-4 h-4" />
          </Button>
        </div>

        <div class="space-y-3">
          <div>
            <label class="text-gray-400 text-xs block mb-1">Patch ID</label>
            <input
              v-model="editForm.jira_id"
              type="text"
              class="w-full bg-[#2a2a2a] border border-gray-600 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-[#4a9eff]"
              placeholder="e.g., PAT-123"
            />
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-gray-400 text-xs block mb-1">Project</label>
              <select
                v-model="editForm.project_id"
                class="w-full bg-[#2a2a2a] border border-gray-600 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-[#4a9eff]"
              >
                <option v-for="project in projectsStore.projects" :key="project.id" :value="project.id">
                  {{ project.name }}
                </option>
              </select>
            </div>
            <div>
              <label class="text-gray-400 text-xs block mb-1">Component</label>
              <select
                v-model="editForm.component_id"
                class="w-full bg-[#2a2a2a] border border-gray-600 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-[#4a9eff]"
              >
                <option v-for="comp in selectedProjectComponents" :key="comp.id" :value="comp.id">
                  {{ comp.name }}
                </option>
              </select>
            </div>
          </div>

          <div>
            <label class="text-gray-400 text-xs block mb-1">Developer Name</label>
            <input
              v-model="editForm.developer_name"
              type="text"
              class="w-full bg-[#2a2a2a] border border-gray-600 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-[#4a9eff]"
            />
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-gray-400 text-xs block mb-1">Build Status</label>
              <div class="flex gap-3 mt-1">
                <label class="flex items-center gap-1 cursor-pointer">
                  <input v-model="editForm.build_status" type="radio" value="success" class="w-3 h-3" />
                  <span class="text-green-400 text-sm">Success</span>
                </label>
                <label class="flex items-center gap-1 cursor-pointer">
                  <input v-model="editForm.build_status" type="radio" value="failed" class="w-3 h-3" />
                  <span class="text-red-400 text-sm">Failed</span>
                </label>
              </div>
            </div>
            <div>
              <label class="text-gray-400 text-xs block mb-1">Deploy Status</label>
              <div class="flex gap-3 mt-1">
                <label class="flex items-center gap-1 cursor-pointer">
                  <input v-model="editForm.deploy_status" type="radio" value="success" class="w-3 h-3" />
                  <span class="text-green-400 text-sm">Success</span>
                </label>
                <label class="flex items-center gap-1 cursor-pointer">
                  <input v-model="editForm.deploy_status" type="radio" value="failed" class="w-3 h-3" />
                  <span class="text-red-400 text-sm">Failed</span>
                </label>
              </div>
            </div>
          </div>

          <div>
            <label class="text-gray-400 text-xs block mb-1">Notes</label>
            <textarea
              v-model="editForm.notes"
              rows="2"
              class="w-full bg-[#2a2a2a] border border-gray-600 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-[#4a9eff]"
            ></textarea>
          </div>
        </div>

        <div class="flex gap-2 mt-4 justify-end">
          <Button variant="secondary" @click="editModal = null">Cancel</Button>
          <Button variant="primary" @click="saveEdit" :disabled="isSaving">
            <Save class="w-4 h-4" />
            {{ isSaving ? 'Saving...' : 'Save Changes' }}
          </Button>
        </div>
      </Card>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="deleteModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="deleteModal = null">
      <Card class="w-full max-w-md mx-4">
        <div class="text-center">
          <AlertTriangle class="w-12 h-12 text-red-400 mx-auto mb-3" />
          <h3 class="text-lg font-bold text-white mb-2">Delete Deployment?</h3>
          <p class="text-gray-400 text-sm mb-4">
            Are you sure you want to delete this deployment?<br />
            <span class="text-white">{{ deleteModal.jira_id || 'NULL' }}</span> -
            <span class="text-gray-300">{{ getProjectName(deleteModal.project_id) }}</span>
          </p>
          <p class="text-red-400 text-xs mb-4">This action cannot be undone.</p>
          <div class="flex gap-2 justify-center">
            <Button variant="secondary" @click="deleteModal = null">Cancel</Button>
            <Button variant="primary" class="!bg-red-600 hover:!bg-red-700" @click="performDelete" :disabled="isDeleting">
              <Trash2 class="w-4 h-4" />
              {{ isDeleting ? 'Deleting...' : 'Delete' }}
            </Button>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import Card from '../components/ui/Card.vue'
import Button from '../components/ui/Button.vue'
import { useDeploymentsStore, type Deployment } from '../stores/deployments'
import { useProjectsStore } from '../stores/projects'
import { useSettingsStore } from '../stores/settings'
import { useClipboard, type DeploymentData } from '../composables/useClipboard'
import { useToast } from '../composables/useToast'
import { RefreshCw, Copy, X, Save, Trash2, AlertTriangle } from 'lucide-vue-next'

const deploymentsStore = useDeploymentsStore()
const projectsStore = useProjectsStore()
const settingsStore = useSettingsStore()
const { copyToClipboard, formatForJira, formatForTeams } = useClipboard()
const { success, error } = useToast()

// Modals
const viewModal = ref<Deployment | null>(null)
const editModal = ref<Deployment | null>(null)
const deleteModal = ref<Deployment | null>(null)

// Edit form
const editForm = ref({
  jira_id: '',
  project_id: 0,
  component_id: 0,
  developer_name: '',
  build_status: 'success',
  deploy_status: 'success',
  notes: '',
})

// State
const isSaving = ref(false)
const isDeleting = ref(false)
const activeFilters = ref<string[]>(['all'])
const selectedProject = ref<number | ''>('')
const sortOption = ref('date-desc')

const filterTabs = [
  { label: 'All', value: 'all' },
  { label: 'This Week', value: 'week' },
  { label: 'This Month', value: 'month' },
]

// Toggle filter (multi-select for week/month, single for all)
const toggleFilter = (value: string) => {
  if (value === 'all') {
    activeFilters.value = ['all']
  } else {
    // Remove 'all' if selecting week/month
    activeFilters.value = activeFilters.value.filter(f => f !== 'all')

    if (activeFilters.value.includes(value)) {
      activeFilters.value = activeFilters.value.filter(f => f !== value)
      if (activeFilters.value.length === 0) {
        activeFilters.value = ['all']
      }
    } else {
      activeFilters.value.push(value)
    }
  }
}

const getProjectName = (projectId: number) => {
  const project = projectsStore.projects.find(p => p.id === projectId)
  return project?.name || `Project ${projectId}`
}

const getComponentName = (componentId?: number) => {
  if (!componentId) return 'N/A'
  for (const project of projectsStore.projects) {
    const component = project.components?.find(c => c.id === componentId)
    if (component) return component.name
  }
  return `Component ${componentId}`
}

const selectedProjectComponents = computed(() => {
  if (!editForm.value.project_id) return []
  const project = projectsStore.projects.find(p => p.id === editForm.value.project_id)
  return project?.components || []
})

const currentDeployedBy = computed(() => {
  return settingsStore.settings?.default_deployed_by || 'Kannan'
})

const successCount = computed(() => {
  return filteredDeployments.value.filter(d => d.deploy_status === 'success').length
})

const filteredDeployments = computed(() => {
  const now = new Date()
  let filtered = [...deploymentsStore.deployments]

  // Apply time filters
  if (!activeFilters.value.includes('all')) {
    if (activeFilters.value.includes('week')) {
      const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
      filtered = filtered.filter(d => new Date(d.timestamp) >= weekAgo)
    }
    if (activeFilters.value.includes('month')) {
      filtered = filtered.filter(d => {
        const date = new Date(d.timestamp)
        return date.getMonth() === now.getMonth() && date.getFullYear() === now.getFullYear()
      })
    }
  }

  // Apply project filter
  if (selectedProject.value) {
    filtered = filtered.filter(d => d.project_id === selectedProject.value)
  }

  // Apply sorting
  switch (sortOption.value) {
    case 'date-desc':
      filtered.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
      break
    case 'date-asc':
      filtered.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
      break
    case 'null-first':
      filtered.sort((a, b) => {
        if (!a.jira_id && b.jira_id) return -1
        if (a.jira_id && !b.jira_id) return 1
        return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
      })
      break
    case 'project':
      filtered.sort((a, b) => getProjectName(a.project_id).localeCompare(getProjectName(b.project_id)))
      break
  }

  return filtered
})

const deploymentsLast7Days = computed(() => {
  const now = new Date()
  const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
  return deploymentsStore.deployments.filter(d => new Date(d.timestamp) >= sevenDaysAgo).length
})

const deploymentsLast30Days = computed(() => {
  const now = new Date()
  const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
  return deploymentsStore.deployments.filter(d => new Date(d.timestamp) >= thirtyDaysAgo).length
})

const deploymentsThisMonth = computed(() => {
  const now = new Date()
  return deploymentsStore.deployments.filter(d => {
    const date = new Date(d.timestamp)
    return date.getMonth() === now.getMonth() && date.getFullYear() === now.getFullYear()
  }).length
})

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  const day = date.getDate().toString().padStart(2, '0')
  const month = (date.getMonth() + 1).toString().padStart(2, '0')
  const year = date.getFullYear()
  let hours = date.getHours()
  const minutes = date.getMinutes().toString().padStart(2, '0')
  const ampm = hours >= 12 ? 'PM' : 'AM'
  hours = hours % 12
  hours = hours ? hours : 12 // 0 should be 12
  return `${day}/${month}/${year} ${hours}:${minutes} ${ampm}`
}

// Modal actions
const viewDeployment = (deployment: Deployment) => {
  viewModal.value = deployment
}

const editDeployment = (deployment: Deployment) => {
  editForm.value = {
    jira_id: deployment.jira_id || '',
    project_id: deployment.project_id,
    component_id: deployment.component_id || 0,
    developer_name: deployment.developer_name || '',
    build_status: deployment.build_status || 'success',
    deploy_status: deployment.deploy_status || 'success',
    notes: deployment.notes || '',
  }
  editModal.value = deployment
}

const confirmDelete = (deployment: Deployment) => {
  deleteModal.value = deployment
}

const saveEdit = async () => {
  if (!editModal.value?.id) return

  isSaving.value = true
  try {
    await deploymentsStore.updateDeployment(editModal.value.id, {
      jira_id: editForm.value.jira_id || undefined,
      project_id: editForm.value.project_id,
      component_id: editForm.value.component_id || undefined,
      developer_name: editForm.value.developer_name || undefined,
      build_status: editForm.value.build_status,
      deploy_status: editForm.value.deploy_status,
      notes: editForm.value.notes || undefined,
    })
    success('Deployment updated successfully!')
    editModal.value = null
    await deploymentsStore.fetchDeployments()
  } catch (err) {
    error('Failed to update deployment')
  } finally {
    isSaving.value = false
  }
}

const performDelete = async () => {
  if (!deleteModal.value?.id) return

  isDeleting.value = true
  try {
    await deploymentsStore.deleteDeployment(deleteModal.value.id)
    success('Deployment deleted successfully!')
    deleteModal.value = null
  } catch (err) {
    error('Failed to delete deployment')
  } finally {
    isDeleting.value = false
  }
}

// Build deployment data for copy operations
const buildDeploymentDataFromHistory = (deployment: Deployment): DeploymentData => {
  const project = projectsStore.projects.find(p => p.id === deployment.project_id)
  let component = null
  if (deployment.component_id) {
    for (const proj of projectsStore.projects) {
      component = proj.components?.find(c => c.id === deployment.component_id)
      if (component) break
    }
  }

  return {
    patchId: deployment.jira_id || undefined,
    project: project?.name || `Project ${deployment.project_id}`,
    component: component?.name || getComponentName(deployment.component_id),
    environment: deployment.environment || project?.environment,
    componentUrl: component?.component_url,
    buildServer: deployment.build_server || project?.build_server,
    buildStatus: deployment.build_status,
    vcsUrl: deployment.vcs_url || component?.vcs_url,
    deployServer: deployment.deploy_server || project?.deploy_server,
    buildBackup: project?.backup_location,
    databaseName: deployment.database_name || project?.database_name,
    deployStatus: deployment.deploy_status,
    databaseScript: deployment.database_script || undefined,
    developer: deployment.developer_name || component?.developer,
    deployedBy: deployment.deployed_by,
    timestamp: deployment.timestamp,
    notes: deployment.notes || undefined,
  }
}

const handleCopyToJira = async (deployment: Deployment) => {
  const data = buildDeploymentDataFromHistory(deployment)

  const text = formatForJira(data)
  if (await copyToClipboard(text)) {
    success('Copied to clipboard for JIRA!')
  } else {
    error('Failed to copy')
  }
}

const handleCopyToTeams = async (deployment: Deployment) => {
  const data = buildDeploymentDataFromHistory(deployment)

  const text = formatForTeams(data)
  if (await copyToClipboard(text)) {
    success('Copied to clipboard for Teams!')
  } else {
    error('Failed to copy')
  }
}

const handleRefresh = async () => {
  await deploymentsStore.fetchDeployments()
  success('Deployments refreshed!')
}

onMounted(async () => {
  if (projectsStore.projects.length === 0) {
    await projectsStore.fetchProjects()
  }
  if (deploymentsStore.deployments.length === 0) {
    await deploymentsStore.fetchDeployments()
  }
  if (!settingsStore.settings) {
    await settingsStore.fetchSettings()
  }
})
</script>
