<template>
  <div class="space-y-4">
    <div class="page-header">
      <div>
        <h1 class="page-title text-xl">Deployment Analysis</h1>
        <p class="text-gray-400 text-sm">Insights and trends from your deployment data</p>
      </div>
      <div class="flex items-center gap-2">
        <Select
          v-model="selectedMonth"
          :options="monthOptions"
          label=""
          class="w-32"
        />
        <Select
          v-model="selectedYear"
          :options="yearOptions"
          label=""
          class="w-24"
        />
      </div>
    </div>

    <!-- Overview Stats -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
      <Card class="!p-3">
        <div class="flex items-center gap-3">
          <div class="p-2 bg-blue-500/20 rounded">
            <Activity class="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <p class="text-gray-400 text-xs">Total Deployments</p>
            <p class="text-xl font-bold text-white">{{ totalDeployments }}</p>
          </div>
        </div>
      </Card>
      <Card class="!p-3">
        <div class="flex items-center gap-3">
          <div class="p-2 bg-green-500/20 rounded">
            <CheckCircle class="w-5 h-5 text-green-400" />
          </div>
          <div>
            <p class="text-gray-400 text-xs">Success Rate</p>
            <p class="text-xl font-bold text-green-400">{{ successRate }}%</p>
          </div>
        </div>
      </Card>
      <Card class="!p-3">
        <div class="flex items-center gap-3">
          <div class="p-2 bg-purple-500/20 rounded">
            <Users class="w-5 h-5 text-purple-400" />
          </div>
          <div>
            <p class="text-gray-400 text-xs">Active Developers</p>
            <p class="text-xl font-bold text-purple-400">{{ activeDevelopers }}</p>
          </div>
        </div>
      </Card>
      <Card class="!p-3">
        <div class="flex items-center gap-3">
          <div class="p-2 bg-orange-500/20 rounded">
            <Folder class="w-5 h-5 text-orange-400" />
          </div>
          <div>
            <p class="text-gray-400 text-xs">Active Projects</p>
            <p class="text-xl font-bold text-orange-400">{{ activeProjects }}</p>
          </div>
        </div>
      </Card>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <!-- Top Deployers -->
      <Card title="Top Deployers">
        <div class="space-y-2">
          <div
            v-for="(dev, idx) in topDeployers"
            :key="dev.name"
            class="flex items-center justify-between p-2 bg-[#353535] rounded"
          >
            <div class="flex items-center gap-2">
              <span class="w-6 h-6 rounded-full bg-[#4a9eff] flex items-center justify-center text-xs font-bold">
                {{ idx + 1 }}
              </span>
              <span class="text-white text-sm">{{ dev.name }}</span>
            </div>
            <div class="flex items-center gap-3">
              <div class="w-24 bg-gray-700 rounded-full h-2">
                <div
                  class="bg-[#4a9eff] h-2 rounded-full"
                  :style="{ width: `${(dev.count / maxDeployerCount) * 100}%` }"
                ></div>
              </div>
              <span class="text-gray-400 text-sm w-8 text-right">{{ dev.count }}</span>
            </div>
          </div>
          <p v-if="topDeployers.length === 0" class="text-gray-400 text-center py-2">No data</p>
        </div>
      </Card>

      <!-- Most Deployed Projects -->
      <Card title="Most Deployed Projects">
        <div class="space-y-2">
          <div
            v-for="(proj, idx) in topProjects"
            :key="proj.name"
            class="flex items-center justify-between p-2 bg-[#353535] rounded"
          >
            <div class="flex items-center gap-2">
              <span class="w-6 h-6 rounded-full bg-green-500 flex items-center justify-center text-xs font-bold">
                {{ idx + 1 }}
              </span>
              <span class="text-white text-sm">{{ proj.name }}</span>
            </div>
            <div class="flex items-center gap-3">
              <div class="w-24 bg-gray-700 rounded-full h-2">
                <div
                  class="bg-green-500 h-2 rounded-full"
                  :style="{ width: `${(proj.count / maxProjectCount) * 100}%` }"
                ></div>
              </div>
              <span class="text-gray-400 text-sm w-8 text-right">{{ proj.count }}</span>
            </div>
          </div>
          <p v-if="topProjects.length === 0" class="text-gray-400 text-center py-2">No data</p>
        </div>
      </Card>

      <!-- Deployments by Environment -->
      <Card title="Deployments by Environment">
        <div class="space-y-2">
          <div
            v-for="env in environmentStats"
            :key="env.name"
            class="flex items-center justify-between p-2 bg-[#353535] rounded"
          >
            <div class="flex items-center gap-2">
              <Server class="w-4 h-4 text-gray-400" />
              <span class="text-white text-sm">{{ env.name }}</span>
            </div>
            <div class="flex items-center gap-3">
              <div class="w-24 bg-gray-700 rounded-full h-2">
                <div
                  class="bg-purple-500 h-2 rounded-full"
                  :style="{ width: `${(env.count / maxEnvCount) * 100}%` }"
                ></div>
              </div>
              <span class="text-gray-400 text-sm w-8 text-right">{{ env.count }}</span>
            </div>
          </div>
          <p v-if="environmentStats.length === 0" class="text-gray-400 text-center py-2">No environment data</p>
        </div>
      </Card>

      <!-- JIRA Compliance -->
      <Card title="JIRA ID Compliance">
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-gray-400 text-sm">With JIRA ID</span>
            <span class="text-green-400 font-bold">{{ jiraCompliance.with }} ({{ jiraComplianceRate }}%)</span>
          </div>
          <div class="w-full bg-gray-700 rounded-full h-3">
            <div
              class="bg-green-500 h-3 rounded-full"
              :style="{ width: `${jiraComplianceRate}%` }"
            ></div>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-gray-400 text-sm">Without JIRA ID</span>
            <span class="text-red-400 font-bold">{{ jiraCompliance.without }}</span>
          </div>
          <div class="mt-3 p-2 bg-[#353535] rounded text-xs text-gray-400">
            Deployments with valid JIRA IDs help maintain traceability and audit compliance.
          </div>
        </div>
      </Card>

      <!-- Peak Deployment Times -->
      <Card title="Peak Deployment Hours">
        <div class="space-y-2">
          <div
            v-for="hour in peakHours"
            :key="hour.hour"
            class="flex items-center justify-between p-2 bg-[#353535] rounded"
          >
            <div class="flex items-center gap-2">
              <Clock class="w-4 h-4 text-gray-400" />
              <span class="text-white text-sm">{{ hour.label }}</span>
            </div>
            <div class="flex items-center gap-3">
              <div class="w-24 bg-gray-700 rounded-full h-2">
                <div
                  class="bg-orange-500 h-2 rounded-full"
                  :style="{ width: `${(hour.count / maxHourCount) * 100}%` }"
                ></div>
              </div>
              <span class="text-gray-400 text-sm w-8 text-right">{{ hour.count }}</span>
            </div>
          </div>
        </div>
      </Card>

      <!-- Daily Distribution -->
      <Card title="Deployments by Day of Week">
        <div class="space-y-2">
          <div
            v-for="day in dailyStats"
            :key="day.name"
            class="flex items-center justify-between p-2 bg-[#353535] rounded"
          >
            <span class="text-white text-sm w-20">{{ day.name }}</span>
            <div class="flex items-center gap-3 flex-1 ml-2">
              <div class="flex-1 bg-gray-700 rounded-full h-2">
                <div
                  class="bg-cyan-500 h-2 rounded-full"
                  :style="{ width: `${(day.count / maxDayCount) * 100}%` }"
                ></div>
              </div>
              <span class="text-gray-400 text-sm w-8 text-right">{{ day.count }}</span>
            </div>
          </div>
        </div>
      </Card>
    </div>

    <!-- Failed Deployments Analysis -->
    <Card title="Failed Deployments Analysis">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="p-3 bg-[#353535] rounded">
          <div class="flex items-center gap-2 mb-2">
            <XCircle class="w-4 h-4 text-red-400" />
            <span class="text-gray-400 text-sm">Build Failures</span>
          </div>
          <p class="text-2xl font-bold text-red-400">{{ failedStats.buildFailed }}</p>
          <p class="text-xs text-gray-500">{{ failedStats.buildFailedRate }}% of all deployments</p>
        </div>
        <div class="p-3 bg-[#353535] rounded">
          <div class="flex items-center gap-2 mb-2">
            <AlertTriangle class="w-4 h-4 text-orange-400" />
            <span class="text-gray-400 text-sm">Deploy Failures</span>
          </div>
          <p class="text-2xl font-bold text-orange-400">{{ failedStats.deployFailed }}</p>
          <p class="text-xs text-gray-500">{{ failedStats.deployFailedRate }}% of all deployments</p>
        </div>
        <div class="p-3 bg-[#353535] rounded">
          <div class="flex items-center gap-2 mb-2">
            <TrendingUp class="w-4 h-4 text-green-400" />
            <span class="text-gray-400 text-sm">Overall Success</span>
          </div>
          <p class="text-2xl font-bold text-green-400">{{ failedStats.successCount }}</p>
          <p class="text-xs text-gray-500">{{ successRate }}% success rate</p>
        </div>
      </div>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import Card from '../components/ui/Card.vue'
import Select from '../components/ui/Select.vue'
import { useDeploymentsStore } from '../stores/deployments'
import { useProjectsStore } from '../stores/projects'
import {
  Activity,
  CheckCircle,
  Users,
  Folder,
  Server,
  Clock,
  XCircle,
  AlertTriangle,
  TrendingUp
} from 'lucide-vue-next'

const deploymentsStore = useDeploymentsStore()
const projectsStore = useProjectsStore()

const selectedMonth = ref('All')
const selectedYear = ref(new Date().getFullYear().toString())

const monthOptions = ['All', 'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December']

const yearOptions = computed(() => {
  const currentYear = new Date().getFullYear()
  return Array.from({ length: 5 }, (_, i) => (currentYear - i).toString())
})

const filteredDeployments = computed(() => {
  let data = [...deploymentsStore.deployments]

  if (selectedMonth.value !== 'All') {
    const monthIndex = monthOptions.indexOf(selectedMonth.value) - 1
    data = data.filter(d => {
      const date = new Date(d.timestamp)
      return date.getMonth() === monthIndex
    })
  }

  data = data.filter(d => {
    const date = new Date(d.timestamp)
    return date.getFullYear() === parseInt(selectedYear.value)
  })

  return data
})

const totalDeployments = computed(() => filteredDeployments.value.length)

const successRate = computed(() => {
  if (totalDeployments.value === 0) return 0
  const success = filteredDeployments.value.filter(d => d.deploy_status === 'success').length
  return Math.round((success / totalDeployments.value) * 100)
})

const activeDevelopers = computed(() => {
  const devs = new Set(filteredDeployments.value.map(d => d.developer_name || d.deployed_by).filter(Boolean))
  return devs.size
})

const activeProjects = computed(() => {
  const projs = new Set(filteredDeployments.value.map(d => d.project_id))
  return projs.size
})

const getProjectName = (projectId: number) => {
  const project = projectsStore.projects.find(p => p.id === projectId)
  return project?.name || `Project ${projectId}`
}

// Top Deployers
const topDeployers = computed(() => {
  const counts: Record<string, number> = {}
  filteredDeployments.value.forEach(d => {
    const name = d.deployed_by || d.developer_name || 'Unknown'
    counts[name] = (counts[name] || 0) + 1
  })
  return Object.entries(counts)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 5)
})

const maxDeployerCount = computed(() => Math.max(...topDeployers.value.map(d => d.count), 1))

// Top Projects
const topProjects = computed(() => {
  const counts: Record<number, number> = {}
  filteredDeployments.value.forEach(d => {
    counts[d.project_id] = (counts[d.project_id] || 0) + 1
  })
  return Object.entries(counts)
    .map(([id, count]) => ({ name: getProjectName(parseInt(id)), count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 5)
})

const maxProjectCount = computed(() => Math.max(...topProjects.value.map(p => p.count), 1))

// Environment Stats
const environmentStats = computed(() => {
  const counts: Record<string, number> = {}
  filteredDeployments.value.forEach(d => {
    const env = d.environment || 'Unknown'
    counts[env] = (counts[env] || 0) + 1
  })
  return Object.entries(counts)
    .filter(([name]) => name !== 'Unknown')
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
})

const maxEnvCount = computed(() => Math.max(...environmentStats.value.map(e => e.count), 1))

// JIRA Compliance
const jiraCompliance = computed(() => {
  const withJira = filteredDeployments.value.filter(d => d.jira_id && d.jira_id.trim() !== '').length
  return {
    with: withJira,
    without: totalDeployments.value - withJira
  }
})

const jiraComplianceRate = computed(() => {
  if (totalDeployments.value === 0) return 0
  return Math.round((jiraCompliance.value.with / totalDeployments.value) * 100)
})

// Peak Hours
const peakHours = computed(() => {
  const counts: Record<number, number> = {}
  filteredDeployments.value.forEach(d => {
    const hour = new Date(d.timestamp).getHours()
    counts[hour] = (counts[hour] || 0) + 1
  })
  return Object.entries(counts)
    .map(([hour, count]) => ({
      hour: parseInt(hour),
      label: `${parseInt(hour).toString().padStart(2, '0')}:00 - ${(parseInt(hour) + 1).toString().padStart(2, '0')}:00`,
      count
    }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 5)
})

const maxHourCount = computed(() => Math.max(...peakHours.value.map(h => h.count), 1))

// Daily Stats
const dailyStats = computed(() => {
  const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
  const counts: Record<number, number> = { 0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0 }
  filteredDeployments.value.forEach(d => {
    const day = new Date(d.timestamp).getDay()
    counts[day] = (counts[day] || 0) + 1
  })
  return days.map((name, idx) => ({ name, count: counts[idx] }))
})

const maxDayCount = computed(() => Math.max(...dailyStats.value.map(d => d.count), 1))

// Failed Stats
const failedStats = computed(() => {
  const buildFailed = filteredDeployments.value.filter(d => d.build_status === 'failed').length
  const deployFailed = filteredDeployments.value.filter(d => d.deploy_status === 'failed').length
  const successCount = filteredDeployments.value.filter(d => d.deploy_status === 'success').length

  return {
    buildFailed,
    deployFailed,
    successCount,
    buildFailedRate: totalDeployments.value ? Math.round((buildFailed / totalDeployments.value) * 100) : 0,
    deployFailedRate: totalDeployments.value ? Math.round((deployFailed / totalDeployments.value) * 100) : 0
  }
})

onMounted(async () => {
  if (projectsStore.projects.length === 0) {
    await projectsStore.fetchProjects()
  }
  if (deploymentsStore.deployments.length === 0) {
    await deploymentsStore.fetchDeployments()
  }
})
</script>
