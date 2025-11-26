<template>
  <div class="space-y-4">
    <div class="page-header">
      <div>
        <h1 class="page-title text-xl">Reports</h1>
        <p class="text-gray-400 text-sm">Deployment statistics and reports</p>
      </div>
    </div>

    <!-- Month/Year Selection -->
    <Card>
      <form @submit.prevent="loadMonthData" class="flex gap-3 items-end">
        <Select
          v-model="selectedMonth"
          :options="monthOptions"
          label="Month"
        />
        <Select
          v-model="selectedYear"
          :options="yearOptions"
          label="Year"
        />
        <Button type="submit" size="sm">
          <BarChart3 class="w-4 h-4" />
          Load Data
        </Button>
      </form>
    </Card>

    <!-- Statistics Summary -->
    <div v-if="monthDeployments.length > 0" class="grid grid-cols-2 md:grid-cols-4 gap-3">
      <Card>
        <div class="text-center">
          <p class="text-gray-400 text-xs">Total</p>
          <p class="text-2xl font-bold text-[#4a9eff] mt-1">{{ monthDeployments.length }}</p>
        </div>
      </Card>
      <Card>
        <div class="text-center">
          <p class="text-gray-400 text-xs">Success</p>
          <p class="text-2xl font-bold text-green-400 mt-1">{{ successCount }}</p>
        </div>
      </Card>
      <Card>
        <div class="text-center">
          <p class="text-gray-400 text-xs">Failed</p>
          <p class="text-2xl font-bold text-red-400 mt-1">{{ failedCount }}</p>
        </div>
      </Card>
      <Card>
        <div class="text-center">
          <p class="text-gray-400 text-xs">Success Rate</p>
          <p class="text-2xl font-bold text-blue-400 mt-1">{{ successRate }}%</p>
        </div>
      </Card>
    </div>

    <!-- Breakdown by Project and Environment -->
    <div v-if="monthDeployments.length > 0" class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <Card title="Deployments by Project">
        <div class="space-y-1 text-sm max-h-48 overflow-y-auto">
          <div
            v-for="(count, project) in deploymentsByProject"
            :key="project"
            class="flex items-center justify-between py-1 border-b border-[#444444]"
          >
            <span class="text-white">{{ project }}</span>
            <span class="text-[#4a9eff] font-bold">{{ count }}</span>
          </div>
          <div v-if="Object.keys(deploymentsByProject).length === 0" class="text-gray-400">
            No data
          </div>
        </div>
      </Card>

      <Card title="Deployments by Environment">
        <div class="space-y-1 text-sm max-h-48 overflow-y-auto">
          <div
            v-for="(count, env) in deploymentsByEnvironment"
            :key="env"
            class="flex items-center justify-between py-1 border-b border-[#444444]"
          >
            <span class="text-white">{{ env }}</span>
            <span class="text-[#4a9eff] font-bold">{{ count }}</span>
          </div>
          <div v-if="Object.keys(deploymentsByEnvironment).length === 0" class="text-gray-400">
            No data
          </div>
        </div>
      </Card>
    </div>

    <!-- Deployments Table -->
    <Card v-if="monthDeployments.length > 0" title="Deployments for Selected Month">
      <div class="flex gap-2 mb-3">
        <Select
          v-model="sortBy"
          :options="sortOptions"
          label=""
          class="w-40"
        />
        <Select
          v-model="sortOrder"
          :options="['Descending', 'Ascending']"
          label=""
          class="w-32"
        />
      </div>
      <Table
        :data="sortedDeployments"
        :columns="columns"
      >
        <template #actions="{ row }">
          <Button
            variant="secondary"
            size="sm"
            @click="viewDeployment(row)"
          >
            View
          </Button>
        </template>
      </Table>
    </Card>

    <Card v-else title="No Data">
      <div class="text-center py-8 text-gray-400">
        <p>Select a month and year to view deployment statistics</p>
      </div>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import Card from '../components/ui/Card.vue'
import Select from '../components/ui/Select.vue'
import Table from '../components/ui/Table.vue'
import Button from '../components/ui/Button.vue'
import { useDeploymentsStore } from '../stores/deployments'
import { useProjectsStore } from '../stores/projects'
import { useToast } from '../composables/useToast'
import { BarChart3 } from 'lucide-vue-next'

const deploymentsStore = useDeploymentsStore()
const projectsStore = useProjectsStore()
const { success, error } = useToast()

const monthOptions = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
]

const selectedMonth = ref(monthOptions[new Date().getMonth()])
const selectedYear = ref(new Date().getFullYear().toString())
const sortBy = ref('Timestamp')
const sortOrder = ref('Descending')

const sortOptions = ['Timestamp', 'Project', 'Component', 'Status']

const yearOptions = computed(() => {
  const currentYear = new Date().getFullYear()
  return Array.from({ length: 5 }, (_, i) => (currentYear - i).toString())
})

const selectedMonthNumber = computed(() => {
  return monthOptions.indexOf(selectedMonth.value) + 1
})

const getProjectName = (projectId: number) => {
  const project = projectsStore.projects.find(p => p.id === projectId)
  return project?.name || `Project ${projectId}`
}

const getComponentName = (componentId?: number) => {
  if (!componentId) return 'N/A'
  for (const project of projectsStore.projects) {
    const component = project.components.find(c => c.id === componentId)
    if (component) return component.name
  }
  return `Component ${componentId}`
}

const columns = [
  { key: 'jira_id', label: 'Patch ID' },
  {
    key: 'project_id',
    label: 'Project',
    format: (value: number) => getProjectName(value),
  },
  {
    key: 'component_id',
    label: 'Component',
    format: (value: number) => getComponentName(value),
  },
  {
    key: 'timestamp',
    label: 'Date',
    format: (value: string) => {
      const date = new Date(value)
      return date.toLocaleDateString()
    },
  },
  {
    key: 'deploy_status',
    label: 'Status',
    format: (value: string) => value.charAt(0).toUpperCase() + value.slice(1),
  },
]

const monthDeployments = computed(() => {
  return deploymentsStore.getDeploymentsByMonth(selectedMonthNumber.value, parseInt(selectedYear.value))
})

const sortedDeployments = computed(() => {
  const sorted = [...monthDeployments.value]
  const ascending = sortOrder.value === 'Ascending'

  sorted.sort((a, b) => {
    let valA: any, valB: any
    switch (sortBy.value) {
      case 'Timestamp':
        valA = new Date(a.timestamp).getTime()
        valB = new Date(b.timestamp).getTime()
        break
      case 'Project':
        valA = getProjectName(a.project_id)
        valB = getProjectName(b.project_id)
        break
      case 'Component':
        valA = getComponentName(a.component_id)
        valB = getComponentName(b.component_id)
        break
      case 'Status':
        valA = a.deploy_status
        valB = b.deploy_status
        break
      default:
        valA = new Date(a.timestamp).getTime()
        valB = new Date(b.timestamp).getTime()
    }

    if (typeof valA === 'string') {
      return ascending ? valA.localeCompare(valB) : valB.localeCompare(valA)
    }
    return ascending ? valA - valB : valB - valA
  })

  return sorted
})

const successCount = computed(() => {
  return monthDeployments.value.filter(d => d.deploy_status === 'success').length
})

const failedCount = computed(() => {
  return monthDeployments.value.filter(d => d.deploy_status === 'failed').length
})

const successRate = computed(() => {
  if (monthDeployments.value.length === 0) return 0
  return Math.round((successCount.value / monthDeployments.value.length) * 100)
})

const deploymentsByProject = computed(() => {
  const result: Record<string, number> = {}
  monthDeployments.value.forEach(d => {
    const projectName = getProjectName(d.project_id)
    result[projectName] = (result[projectName] || 0) + 1
  })
  // Sort by count descending
  return Object.fromEntries(
    Object.entries(result).sort(([, a], [, b]) => b - a)
  )
})

const deploymentsByEnvironment = computed(() => {
  const result: Record<string, number> = {}
  monthDeployments.value.forEach(d => {
    const env = d.environment || 'Unknown'
    result[env] = (result[env] || 0) + 1
  })
  return Object.fromEntries(
    Object.entries(result).sort(([, a], [, b]) => b - a)
  )
})

const loadMonthData = () => {
  if (monthDeployments.value.length > 0) {
    success(`Loaded ${monthDeployments.value.length} deployments`)
  } else {
    error('No deployments found for selected month')
  }
}

const viewDeployment = (deployment: any) => {
  console.log('Viewing deployment:', deployment)
}

onMounted(async () => {
  if (projectsStore.projects.length === 0) {
    await projectsStore.fetchProjects()
  }
  if (deploymentsStore.deployments.length === 0) {
    await deploymentsStore.fetchDeployments()
  }
})
</script>
