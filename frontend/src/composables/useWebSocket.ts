import { ref, onMounted, onUnmounted } from 'vue'

export interface WebSocketMessage {
  type: 'deployment_created' | 'deployment_updated' | 'project_updated' | 'library_updated'
  data: any
}

export function useWebSocket() {
  const isConnected = ref(false)
  const lastMessage = ref<WebSocketMessage | null>(null)
  let ws: WebSocket | null = null
  let reconnectTimeout: ReturnType<typeof setTimeout> | null = null

  const connect = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/ws`

    ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      isConnected.value = true
      console.log('WebSocket connected')
    }

    ws.onclose = () => {
      isConnected.value = false
      console.log('WebSocket disconnected, reconnecting...')
      // Auto-reconnect after 3 seconds
      reconnectTimeout = setTimeout(connect, 3000)
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data)
        lastMessage.value = message
        handleMessage(message)
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e)
      }
    }
  }

  const handleMessage = (message: WebSocketMessage) => {
    // Emit custom events that stores can listen to
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('ws-message', { detail: message }))
    }
  }

  const disconnect = () => {
    if (reconnectTimeout) {
      clearTimeout(reconnectTimeout)
    }
    if (ws) {
      ws.close()
      ws = null
    }
  }

  onMounted(() => {
    connect()
  })

  onUnmounted(() => {
    disconnect()
  })

  return {
    isConnected,
    lastMessage,
    connect,
    disconnect
  }
}
