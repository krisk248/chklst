<template>
  <div class="space-y-4">
    <div class="page-header">
      <div>
        <h1 class="page-title text-xl">Export Data</h1>
        <p class="text-gray-400 text-sm">Export deployment data in various formats</p>
      </div>
    </div>

    <!-- Export Options Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <!-- Excel Export -->
      <Card title="Excel Export (.xlsx)">
        <div class="space-y-3">
          <p class="text-gray-400 text-sm">Export deployment data to Excel spreadsheet</p>

          <div class="space-y-2">
            <Button
              variant="secondary"
              size="sm"
              class="w-full justify-start"
              @click="exportExcel('all')"
            >
              <FileSpreadsheet class="w-4 h-4" />
              All Deployments
            </Button>

            <div class="flex gap-2">
              <Select
                v-model="excelProject"
                :options="['All Projects', ...projectNames]"
                label=""
                class="flex-1"
              />
              <Button
                variant="secondary"
                size="sm"
                @click="exportExcel('project')"
                :disabled="excelProject === 'All Projects'"
              >
                <Download class="w-4 h-4" />
              </Button>
            </div>

            <div class="flex gap-2">
              <Select
                v-model="excelMonth"
                :options="monthOptions"
                label=""
                class="flex-1"
              />
              <Select
                v-model="excelYear"
                :options="yearOptions"
                label=""
                class="w-24"
              />
              <Button
                variant="secondary"
                size="sm"
                @click="exportExcel('month')"
              >
                <Download class="w-4 h-4" />
              </Button>
            </div>

            <div class="flex gap-2">
              <Select
                v-model="excelProjectMonth"
                :options="['Select Project', ...projectNames]"
                label=""
                class="flex-1"
              />
              <Button
                variant="secondary"
                size="sm"
                @click="exportExcel('project-month')"
                :disabled="excelProjectMonth === 'Select Project'"
              >
                <Download class="w-4 h-4" />
                Month
              </Button>
            </div>
          </div>
        </div>
      </Card>

      <!-- PDF Export -->
      <Card title="PDF Export (.pdf)">
        <div class="space-y-3">
          <p class="text-gray-400 text-sm">Export deployment reports as PDF documents</p>

          <div class="space-y-2">
            <Button
              variant="secondary"
              size="sm"
              class="w-full justify-start"
              @click="exportPDF('all')"
            >
              <FileText class="w-4 h-4" />
              All Deployments Report
            </Button>

            <div class="flex gap-2">
              <Select
                v-model="pdfProject"
                :options="['All Projects', ...projectNames]"
                label=""
                class="flex-1"
              />
              <Button
                variant="secondary"
                size="sm"
                @click="exportPDF('project')"
                :disabled="pdfProject === 'All Projects'"
              >
                <Download class="w-4 h-4" />
              </Button>
            </div>

            <div class="flex gap-2">
              <Select
                v-model="pdfMonth"
                :options="monthOptions"
                label=""
                class="flex-1"
              />
              <Select
                v-model="pdfYear"
                :options="yearOptions"
                label=""
                class="w-24"
              />
              <Button
                variant="secondary"
                size="sm"
                @click="exportPDF('month')"
              >
                <Download class="w-4 h-4" />
              </Button>
            </div>

            <Button
              variant="secondary"
              size="sm"
              class="w-full justify-start"
              @click="exportPDF('summary')"
            >
              <BarChart3 class="w-4 h-4" />
              Monthly Summary Report
            </Button>
          </div>
        </div>
      </Card>

      <!-- CSV Export -->
      <Card title="CSV Export (.csv)">
        <div class="space-y-3">
          <p class="text-gray-400 text-sm">Export raw data as CSV for analysis</p>

          <div class="space-y-2">
            <Button
              variant="secondary"
              size="sm"
              class="w-full justify-start"
              @click="exportCSV('all')"
            >
              <FileDown class="w-4 h-4" />
              All Deployments
            </Button>

            <div class="flex gap-2">
              <Select
                v-model="csvProject"
                :options="['All Projects', ...projectNames]"
                label=""
                class="flex-1"
              />
              <Button
                variant="secondary"
                size="sm"
                @click="exportCSV('project')"
                :disabled="csvProject === 'All Projects'"
              >
                <Download class="w-4 h-4" />
              </Button>
            </div>

            <div class="flex gap-2">
              <Select
                v-model="csvMonth"
                :options="monthOptions"
                label=""
                class="flex-1"
              />
              <Select
                v-model="csvYear"
                :options="yearOptions"
                label=""
                class="w-24"
              />
              <Button
                variant="secondary"
                size="sm"
                @click="exportCSV('month')"
              >
                <Download class="w-4 h-4" />
              </Button>
            </div>

            <Button
              variant="secondary"
              size="sm"
              class="w-full justify-start"
              @click="exportCSV('failed')"
            >
              <AlertTriangle class="w-4 h-4" />
              Failed Deployments Only
            </Button>
          </div>
        </div>
      </Card>
    </div>

    <!-- Quick Stats -->
    <Card title="Data Summary">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-center">
        <div class="p-3 bg-[#353535] rounded">
          <p class="text-gray-400 text-xs">Total Records</p>
          <p class="text-2xl font-bold text-[#4a9eff]">{{ deploymentsStore.deployments.length }}</p>
        </div>
        <div class="p-3 bg-[#353535] rounded">
          <p class="text-gray-400 text-xs">Projects</p>
          <p class="text-2xl font-bold text-green-400">{{ projectsStore.projects.length }}</p>
        </div>
        <div class="p-3 bg-[#353535] rounded">
          <p class="text-gray-400 text-xs">This Month</p>
          <p class="text-2xl font-bold text-purple-400">{{ thisMonthCount }}</p>
        </div>
        <div class="p-3 bg-[#353535] rounded">
          <p class="text-gray-400 text-xs">Success Rate</p>
          <p class="text-2xl font-bold text-blue-400">{{ successRate }}%</p>
        </div>
      </div>
    </Card>

    <!-- Recent Exports Log -->
    <Card title="Export History">
      <div v-if="exportHistory.length > 0" class="space-y-2">
        <div
          v-for="(exp, idx) in exportHistory"
          :key="idx"
          class="flex items-center justify-between p-2 bg-[#353535] rounded text-sm"
        >
          <div class="flex items-center gap-2">
            <component :is="getExportIcon(exp.format)" class="w-4 h-4 text-gray-400" />
            <span class="text-white">{{ exp.filename }}</span>
          </div>
          <div class="flex items-center gap-3">
            <span class="text-gray-400 text-xs">{{ exp.records }} records</span>
            <span class="text-gray-500 text-xs">{{ exp.time }}</span>
          </div>
        </div>
      </div>
      <div v-else class="text-center py-4 text-gray-400">
        <p>No exports yet. Select an export option above.</p>
      </div>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import Card from '../components/ui/Card.vue'
import Select from '../components/ui/Select.vue'
import Button from '../components/ui/Button.vue'
import { useDeploymentsStore, type Deployment } from '../stores/deployments'
import { useProjectsStore } from '../stores/projects'
import { useToast } from '../composables/useToast'
import {
  FileSpreadsheet,
  FileText,
  FileDown,
  Download,
  BarChart3,
  AlertTriangle
} from 'lucide-vue-next'

const deploymentsStore = useDeploymentsStore()
const projectsStore = useProjectsStore()
const { success, error } = useToast()

// Export selections
const excelProject = ref('All Projects')
const excelMonth = ref(new Date().toLocaleString('default', { month: 'long' }))
const excelYear = ref(new Date().getFullYear().toString())
const excelProjectMonth = ref('Select Project')

const pdfProject = ref('All Projects')
const pdfMonth = ref(new Date().toLocaleString('default', { month: 'long' }))
const pdfYear = ref(new Date().getFullYear().toString())

const csvProject = ref('All Projects')
const csvMonth = ref(new Date().toLocaleString('default', { month: 'long' }))
const csvYear = ref(new Date().getFullYear().toString())

// Export history
const exportHistory = ref<Array<{
  format: string
  filename: string
  records: number
  time: string
}>>([])

const monthOptions = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
]

const yearOptions = computed(() => {
  const currentYear = new Date().getFullYear()
  return Array.from({ length: 5 }, (_, i) => (currentYear - i).toString())
})

const projectNames = computed(() =>
  projectsStore.projects.map(p => p.name || `Project ${p.id}`)
)

const thisMonthCount = computed(() => {
  const now = new Date()
  return deploymentsStore.deployments.filter(d => {
    const date = new Date(d.timestamp)
    return date.getMonth() === now.getMonth() && date.getFullYear() === now.getFullYear()
  }).length
})

const successRate = computed(() => {
  if (deploymentsStore.deployments.length === 0) return 0
  const successCount = deploymentsStore.deployments.filter(d => d.deploy_status === 'success').length
  return Math.round((successCount / deploymentsStore.deployments.length) * 100)
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

const getExportIcon = (format: string) => {
  switch (format) {
    case 'xlsx': return FileSpreadsheet
    case 'pdf': return FileText
    case 'csv': return FileDown
    default: return FileDown
  }
}

const filterDeployments = (type: string, project?: string, month?: string, year?: string): Deployment[] => {
  let filtered = [...deploymentsStore.deployments]

  if (type === 'project' && project && project !== 'All Projects') {
    const projectObj = projectsStore.projects.find(p => p.name === project)
    if (projectObj) {
      filtered = filtered.filter(d => d.project_id === projectObj.id)
    }
  }

  if (type === 'month' || type === 'project-month') {
    const monthIndex = monthOptions.indexOf(month || '')
    const yearNum = parseInt(year || new Date().getFullYear().toString())
    filtered = filtered.filter(d => {
      const date = new Date(d.timestamp)
      return date.getMonth() === monthIndex && date.getFullYear() === yearNum
    })
  }

  if (type === 'project-month' && project && project !== 'Select Project') {
    const projectObj = projectsStore.projects.find(p => p.name === project)
    if (projectObj) {
      filtered = filtered.filter(d => d.project_id === projectObj.id)
    }
  }

  if (type === 'failed') {
    filtered = filtered.filter(d => d.deploy_status === 'failed' || d.build_status === 'failed')
  }

  return filtered.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
}

const formatDeploymentForExport = (d: Deployment) => ({
  'Patch ID': d.jira_id || 'N/A',
  'Timestamp': new Date(d.timestamp).toLocaleString(),
  'Project': getProjectName(d.project_id),
  'Component': getComponentName(d.component_id),
  'Environment': d.environment || 'N/A',
  'Developer': d.developer_name || 'N/A',
  'Build Status': d.build_status,
  'Deploy Status': d.deploy_status,
  'Deployed By': d.deployed_by || 'N/A',
  'Notes': d.notes || '',
})

const generateCSV = (data: Deployment[]): string => {
  if (data.length === 0) return ''

  const formatted = data.map(formatDeploymentForExport)
  const headers = Object.keys(formatted[0])
  const rows = formatted.map(row =>
    headers.map(h => {
      const val = row[h as keyof typeof row]
      // Escape quotes and wrap in quotes if contains comma
      const escaped = String(val).replace(/"/g, '""')
      return escaped.includes(',') || escaped.includes('\n') ? `"${escaped}"` : escaped
    }).join(',')
  )

  return [headers.join(','), ...rows].join('\n')
}

const downloadFile = (content: string, filename: string, mimeType: string) => {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

const addToHistory = (format: string, filename: string, records: number) => {
  exportHistory.value.unshift({
    format,
    filename,
    records,
    time: new Date().toLocaleTimeString(),
  })
  // Keep only last 10 exports
  if (exportHistory.value.length > 10) {
    exportHistory.value.pop()
  }
}

// Export functions
const exportExcel = async (type: string) => {
  let data: Deployment[] = []
  let filename = 'deployments'

  switch (type) {
    case 'all':
      data = filterDeployments('all')
      filename = `all_deployments_${new Date().toISOString().split('T')[0]}`
      break
    case 'project':
      data = filterDeployments('project', excelProject.value)
      filename = `${excelProject.value.replace(/\s+/g, '_')}_deployments`
      break
    case 'month':
      data = filterDeployments('month', undefined, excelMonth.value, excelYear.value)
      filename = `deployments_${excelMonth.value}_${excelYear.value}`
      break
    case 'project-month':
      data = filterDeployments('project-month', excelProjectMonth.value, excelMonth.value, excelYear.value)
      filename = `${excelProjectMonth.value.replace(/\s+/g, '_')}_${excelMonth.value}_${excelYear.value}`
      break
  }

  if (data.length === 0) {
    error('No data to export')
    return
  }

  // For Excel, we'll generate CSV (can be opened in Excel)
  // In production, you'd use a library like xlsx
  const csv = generateCSV(data)
  downloadFile(csv, `${filename}.csv`, 'text/csv;charset=utf-8;')
  addToHistory('xlsx', `${filename}.csv`, data.length)
  success(`Exported ${data.length} records to ${filename}.csv`)
}

const exportPDF = async (type: string) => {
  let data: Deployment[] = []
  let filename = 'deployments_report'
  let title = 'Deployment Report'

  switch (type) {
    case 'all':
      data = filterDeployments('all')
      filename = `all_deployments_report_${new Date().toISOString().split('T')[0]}`
      title = 'All Deployments Report'
      break
    case 'project':
      data = filterDeployments('project', pdfProject.value)
      filename = `${pdfProject.value.replace(/\s+/g, '_')}_report`
      title = `${pdfProject.value} - Deployment Report`
      break
    case 'month':
      data = filterDeployments('month', undefined, pdfMonth.value, pdfYear.value)
      filename = `deployments_report_${pdfMonth.value}_${pdfYear.value}`
      title = `Deployment Report - ${pdfMonth.value} ${pdfYear.value}`
      break
    case 'summary':
      data = filterDeployments('month', undefined, pdfMonth.value, pdfYear.value)
      filename = `monthly_summary_${pdfMonth.value}_${pdfYear.value}`
      title = `Monthly Summary - ${pdfMonth.value} ${pdfYear.value}`
      break
  }

  if (data.length === 0) {
    error('No data to export')
    return
  }

  // Generate HTML report for printing as PDF
  const successCount = data.filter(d => d.deploy_status === 'success').length
  const failedCount = data.filter(d => d.deploy_status === 'failed').length
  const rate = Math.round((successCount / data.length) * 100)

  const html = `
    <!DOCTYPE html>
    <html>
    <head>
      <title>${title}</title>
      <style>
        body { font-family: Arial, sans-serif; margin: 20px; color: #333; }
        h1 { color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 10px; }
        .summary { display: flex; gap: 20px; margin: 20px 0; }
        .stat { background: #f3f4f6; padding: 15px; border-radius: 8px; text-align: center; }
        .stat-value { font-size: 24px; font-weight: bold; color: #2563eb; }
        .stat-label { font-size: 12px; color: #666; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 12px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background: #2563eb; color: white; }
        tr:nth-child(even) { background: #f9fafb; }
        .success { color: #22c55e; }
        .failed { color: #ef4444; }
        .footer { margin-top: 20px; text-align: center; color: #666; font-size: 11px; }
      </style>
    </head>
    <body>
      <h1>${title}</h1>
      <p>Generated: ${new Date().toLocaleString()}</p>

      <div class="summary">
        <div class="stat">
          <div class="stat-value">${data.length}</div>
          <div class="stat-label">Total Deployments</div>
        </div>
        <div class="stat">
          <div class="stat-value success">${successCount}</div>
          <div class="stat-label">Successful</div>
        </div>
        <div class="stat">
          <div class="stat-value failed">${failedCount}</div>
          <div class="stat-label">Failed</div>
        </div>
        <div class="stat">
          <div class="stat-value">${rate}%</div>
          <div class="stat-label">Success Rate</div>
        </div>
      </div>

      <table>
        <thead>
          <tr>
            <th>Patch ID</th>
            <th>Date</th>
            <th>Project</th>
            <th>Component</th>
            <th>Build</th>
            <th>Deploy</th>
            <th>Deployed By</th>
          </tr>
        </thead>
        <tbody>
          ${data.map(d => `
            <tr>
              <td>${d.jira_id || 'N/A'}</td>
              <td>${new Date(d.timestamp).toLocaleDateString()}</td>
              <td>${getProjectName(d.project_id)}</td>
              <td>${getComponentName(d.component_id)}</td>
              <td class="${d.build_status}">${d.build_status}</td>
              <td class="${d.deploy_status}">${d.deploy_status}</td>
              <td>${d.deployed_by || 'N/A'}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>

      <div class="footer">
        <p>chklst v3.0.0 - Deployment Tracking System</p>
      </div>
    </body>
    </html>
  `

  // Open in new window for printing
  const printWindow = window.open('', '_blank')
  if (printWindow) {
    printWindow.document.write(html)
    printWindow.document.close()
    printWindow.print()
    addToHistory('pdf', `${filename}.pdf`, data.length)
    success(`Generated PDF report with ${data.length} records`)
  } else {
    error('Please allow popups to generate PDF')
  }
}

const exportCSV = async (type: string) => {
  let data: Deployment[] = []
  let filename = 'deployments'

  switch (type) {
    case 'all':
      data = filterDeployments('all')
      filename = `all_deployments_${new Date().toISOString().split('T')[0]}`
      break
    case 'project':
      data = filterDeployments('project', csvProject.value)
      filename = `${csvProject.value.replace(/\s+/g, '_')}_deployments`
      break
    case 'month':
      data = filterDeployments('month', undefined, csvMonth.value, csvYear.value)
      filename = `deployments_${csvMonth.value}_${csvYear.value}`
      break
    case 'failed':
      data = filterDeployments('failed')
      filename = `failed_deployments_${new Date().toISOString().split('T')[0]}`
      break
  }

  if (data.length === 0) {
    error('No data to export')
    return
  }

  const csv = generateCSV(data)
  downloadFile(csv, `${filename}.csv`, 'text/csv;charset=utf-8;')
  addToHistory('csv', `${filename}.csv`, data.length)
  success(`Exported ${data.length} records to ${filename}.csv`)
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
