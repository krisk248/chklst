import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useApi } from '../composables/useApi'

export interface WebSocketMessage {
  type: 'deployment_created' | 'deployment_updated' | 'project_updated' | 'library_updated'
  data: any
}

export interface LibraryPresets {
  id?: number
  developers: string[]
  build_servers: string[]
  deploy_servers: string[]
  environments: string[]
  created_at?: string
  updated_at?: string
}

export const useLibraryStore = defineStore('library', () => {
  const presets = ref<LibraryPresets>({
    developers: [],
    build_servers: [],
    deploy_servers: [],
    environments: [],
  })
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const { get, put, delete: deleteApi } = useApi()

  const fetchPresets = async () => {
    isLoading.value = true
    error.value = null
    try {
      const response = await get<LibraryPresets>('/library')
      presets.value = response.data || {
        developers: [],
        build_servers: [],
        deploy_servers: [],
        environments: [],
      }
    } catch (err) {
      error.value = 'Failed to fetch library presets'
      console.error(err)
    } finally {
      isLoading.value = false
    }
  }

  const addDeveloper = async (name: string) => {
    if (!presets.value.developers.includes(name)) {
      presets.value.developers.push(name)
      await savePresets()
    }
  }

  const removeDeveloper = async (name: string) => {
    presets.value.developers = presets.value.developers.filter(d => d !== name)
    await savePresets()
  }

  const addBuildServer = async (server: string) => {
    if (!presets.value.build_servers.includes(server)) {
      presets.value.build_servers.push(server)
      await savePresets()
    }
  }

  const removeBuildServer = async (server: string) => {
    presets.value.build_servers = presets.value.build_servers.filter(s => s !== server)
    await savePresets()
  }

  const addDeployServer = async (server: string) => {
    if (!presets.value.deploy_servers.includes(server)) {
      presets.value.deploy_servers.push(server)
      await savePresets()
    }
  }

  const removeDeployServer = async (server: string) => {
    presets.value.deploy_servers = presets.value.deploy_servers.filter(s => s !== server)
    await savePresets()
  }

  const addEnvironment = async (env: string) => {
    if (!presets.value.environments.includes(env)) {
      presets.value.environments.push(env)
      await savePresets()
    }
  }

  const removeEnvironment = async (env: string) => {
    presets.value.environments = presets.value.environments.filter(e => e !== env)
    await savePresets()
  }

  const savePresets = async () => {
    isLoading.value = true
    error.value = null
    try {
      await put('/library', presets.value)
    } catch (err) {
      error.value = 'Failed to save presets'
      console.error(err)
    } finally {
      isLoading.value = false
    }
  }

  // WebSocket listener setup
  const setupWebSocketListener = () => {
    if (typeof window !== 'undefined') {
      window.addEventListener('ws-message', (event: Event) => {
        const customEvent = event as CustomEvent
        const message: WebSocketMessage = customEvent.detail

        if (message.type === 'library_updated') {
          // Refetch library presets when library is updated
          fetchPresets()
        }
      })
    }
  }

  // Initialize WebSocket listener when store is created
  setupWebSocketListener()

  return {
    presets,
    isLoading,
    error,
    fetchPresets,
    addDeveloper,
    removeDeveloper,
    addBuildServer,
    removeBuildServer,
    addDeployServer,
    removeDeployServer,
    addEnvironment,
    removeEnvironment,
    savePresets,
    setupWebSocketListener,
  }
})
