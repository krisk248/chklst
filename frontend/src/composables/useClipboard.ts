import { ref } from 'vue'

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

  const formatForJira = (data: Record<string, any>): string => {
    const lines: string[] = []
    for (const [key, value] of Object.entries(data)) {
      if (value !== null && value !== undefined && value !== '') {
        const formattedKey = key
          .replace(/_/g, ' ')
          .replace(/\b\w/g, l => l.toUpperCase())
        lines.push(`${formattedKey}: ${value}`)
      }
    }
    return lines.join('\n')
  }

  const formatForTeams = (data: Record<string, any>): string => {
    const lines: string[] = ['**Deployment Information:**', '']
    for (const [key, value] of Object.entries(data)) {
      if (value !== null && value !== undefined && value !== '') {
        const formattedKey = key
          .replace(/_/g, ' ')
          .replace(/\b\w/g, l => l.toUpperCase())
        lines.push(`**${formattedKey}:** ${value}`)
      }
    }
    return lines.join('\n')
  }

  return {
    isCopied,
    copyToClipboard,
    formatForJira,
    formatForTeams,
  }
}
