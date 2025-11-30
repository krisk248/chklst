import { ref } from 'vue'

export interface DeploymentData {
  patchId?: string
  project?: string
  component?: string
  environment?: string
  componentUrl?: string
  buildServer?: string
  buildStatus?: string
  vcsUrl?: string
  deployServer?: string
  buildBackup?: string
  databaseName?: string
  deployStatus?: string
  databaseScript?: string
  developer?: string
  deployedBy?: string
  timestamp?: string
  notes?: string
}

export function useClipboard() {
  const isCopied = ref(false)

  const copyToClipboard = async (text: string): Promise<boolean> => {
    try {
      await navigator.clipboard.writeText(text)
      isCopied.value = true
      setTimeout(() => {
        isCopied.value = false
      }, 2000)
      return true
    } catch (err) {
      console.error('Failed to copy to clipboard:', err)
      return false
    }
  }

  // Format timestamp like "30-Nov-2025 4:47PM"
  const formatTimestamp = (timestamp: string): string => {
    if (!timestamp) return ''
    const date = new Date(timestamp)
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    const day = date.getDate()
    const month = months[date.getMonth()]
    const year = date.getFullYear()
    let hours = date.getHours()
    const minutes = date.getMinutes().toString().padStart(2, '0')
    const ampm = hours >= 12 ? 'PM' : 'AM'
    hours = hours % 12
    hours = hours ? hours : 12
    return `${day}-${month}-${year} ${hours}:${minutes}${ampm}`
  }

  const formatForJira = (data: DeploymentData): string => {
    const lines: string[] = []
    const buildIcon = data.buildStatus === 'success' ? '(/)(/)' : '(x)'
    const deployIcon = data.deployStatus === 'success' ? '(/)(/)' : '(x)'

    lines.push(`h3. 🎫 PATCH: ${data.patchId || 'N/A'} | ${data.project} - Deployment Complete`)
    lines.push('')
    lines.push(`||Field||Value||`)
    lines.push(`|*Project*|${data.project} - ${data.component}|`)
    if (data.environment) lines.push(`|*Environment*|${data.environment}|`)
    if (data.componentUrl) lines.push(`|*URL*|${data.componentUrl}|`)
    if (data.buildServer) lines.push(`|*Build Server*|${data.buildServer}|`)
    lines.push(`|*Build*|${buildIcon} ${data.buildStatus?.toUpperCase()}|`)
    if (data.vcsUrl) lines.push(`|*Git URL*|${data.vcsUrl}|`)
    if (data.deployServer) lines.push(`|*Deploy Server*|${data.deployServer}|`)
    if (data.buildBackup) lines.push(`|*Build Backup*|${data.buildBackup}|`)
    if (data.databaseName) lines.push(`|*Database*|${data.databaseName}|`)
    if (data.databaseScript) lines.push(`|*DB Script*|${data.databaseScript}|`)
    lines.push(`|*Deployment*|${deployIcon} ${data.deployStatus?.toUpperCase()}|`)
    if (data.developer) lines.push(`|*Developer*|${data.developer}|`)
    lines.push(`|*Deployed By*|${data.deployedBy}|`)
    lines.push(`|*Timestamp*|${formatTimestamp(data.timestamp || '')}|`)
    if (data.notes) lines.push(`|*Notes*|${data.notes}|`)

    return lines.join('\n')
  }

  const formatForTeams = (data: DeploymentData): string => {
    const lines: string[] = []
    const buildIcon = data.buildStatus === 'success' ? '✅ PASS' : '❌ FAIL'
    const deployIcon = data.deployStatus === 'success' ? '✅ PASS' : '❌ FAIL'

    lines.push(`🎫 PATCH: ${data.patchId || 'N/A'} | ${data.project} - Deployment Complete`)
    lines.push('')
    lines.push(`• Project: ${data.project} - ${data.component}`)
    if (data.environment) lines.push(`• Environment: ${data.environment}`)
    if (data.componentUrl) lines.push(`• URL: ${data.componentUrl}`)
    if (data.buildServer) lines.push(`• Build Server: ${data.buildServer}`)
    lines.push(`• Build: ${buildIcon}`)
    if (data.vcsUrl) lines.push(`• Git URL: ${data.vcsUrl}`)
    if (data.deployServer) lines.push(`• Deploy Server: ${data.deployServer}`)
    if (data.buildBackup) lines.push(`• Build Backup: ${data.buildBackup}`)
    if (data.databaseName) lines.push(`• Database: ${data.databaseName}`)
    if (data.databaseScript) lines.push(`• DB Script: ${data.databaseScript}`)
    lines.push(`• Deployment: ${deployIcon}`)
    if (data.developer) lines.push(`• Developer: ${data.developer}`)
    lines.push(`• Deployed By: ${data.deployedBy}`)
    lines.push(`• Timestamp: ${formatTimestamp(data.timestamp || '')}`)
    if (data.notes) lines.push(`• Notes: ${data.notes}`)

    return lines.join('\n')
  }

  return {
    isCopied,
    copyToClipboard,
    formatForJira,
    formatForTeams,
  }
}
