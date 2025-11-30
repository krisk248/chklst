import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useApi } from '../composables/useApi'

export interface WebSocketMessage {
  type: 'deployment_created' | 'deployment_updated' | 'project_updated' | 'library_updated'
  data: any
}

export interface Component {
  id?: number
  name: string
  developer?: string
  vcs_type?: 'git' | 'svn'
  vcs_url?: string
  build_command?: string
  component_url?: string
  enabled?: boolean
  description?: string
  created_at?: string
  updated_at?: string
}

export interface Project {
  id?: number
  name: string
  build_server?: string
  deploy_server?: string
  database_name?: string
  environment?: string
  backup_location?: string
  description?: string
  components: Component[]
  created_at?: string
  updated_at?: string
}

export const useProjectsStore = defineStore('projects', () => {
  const projects = ref<Project[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const { get, post, put, delete: deleteApi } = useApi()

  const fetchProjects = async () => {
    isLoading.value = true
    error.value = null
    try {
      const response = await get<Project[]>('/projects')
      // Sort projects alphabetically by name (ascending)
      const sortedProjects = (response.data || []).sort((a, b) =>
        (a.name || '').localeCompare(b.name || '')
      )
      projects.value = sortedProjects
    } catch (err) {
      error.value = 'Failed to fetch projects'
      console.error(err)
    } finally {
      isLoading.value = false
    }
  }

  const createProject = async (project: Project): Promise<Project | null> => {
    isLoading.value = true
    error.value = null
    try {
      const response = await post<Project>('/projects', project)
      const newProject = response.data
      if (newProject.id) {
        projects.value.push(newProject)
      }
      return newProject
    } catch (err) {
      error.value = 'Failed to create project'
      console.error(err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  const updateProject = async (id: number, project: Partial<Project>) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await put<Project>(`/projects/${id}`, project)
      const idx = projects.value.findIndex(p => p.id === id)
      if (idx > -1) {
        projects.value[idx] = response.data
      }
      return response.data
    } catch (err) {
      error.value = 'Failed to update project'
      console.error(err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  const deleteProject = async (id: number) => {
    isLoading.value = true
    error.value = null
    try {
      await deleteApi(`/projects/${id}`)
      projects.value = projects.value.filter(p => p.id !== id)
    } catch (err) {
      error.value = 'Failed to delete project'
      console.error(err)
    } finally {
      isLoading.value = false
    }
  }

  const addComponent = async (projectId: number, component: Component) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await post<Component>(
        `/projects/${projectId}/components`,
        component
      )
      const project = projects.value.find(p => p.id === projectId)
      if (project) {
        project.components.push(response.data)
      }
      return response.data
    } catch (err) {
      error.value = 'Failed to add component'
      console.error(err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  const updateComponent = async (
    projectId: number,
    componentId: number,
    component: Partial<Component>
  ) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await put<Component>(
        `/projects/${projectId}/components/${componentId}`,
        component
      )
      const project = projects.value.find(p => p.id === projectId)
      if (project) {
        const idx = project.components.findIndex(c => c.id === componentId)
        if (idx > -1) {
          project.components[idx] = response.data
        }
      }
      return response.data
    } catch (err) {
      error.value = 'Failed to update component'
      console.error(err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  const deleteComponent = async (projectId: number, componentId: number) => {
    isLoading.value = true
    error.value = null
    try {
      await deleteApi(`/projects/${projectId}/components/${componentId}`)
      const project = projects.value.find(p => p.id === projectId)
      if (project) {
        project.components = project.components.filter(c => c.id !== componentId)
      }
    } catch (err) {
      error.value = 'Failed to delete component'
      console.error(err)
    } finally {
      isLoading.value = false
    }
  }

  const getProjectByName = (name: string) => {
    return projects.value.find(p => p.name === name)
  }

  const getComponentsByProject = (projectId: number) => {
    const project = projects.value.find(p => p.id === projectId)
    return project?.components || []
  }

  // WebSocket listener setup
  const setupWebSocketListener = () => {
    if (typeof window !== 'undefined') {
      window.addEventListener('ws-message', (event: Event) => {
        const customEvent = event as CustomEvent
        const message: WebSocketMessage = customEvent.detail

        if (message.type === 'project_updated') {
          // Update existing project
          const index = projects.value.findIndex(p => p.id === message.data.id)
          if (index !== -1) {
            projects.value[index] = message.data
          }
        }
      })
    }
  }

  // Initialize WebSocket listener when store is created
  setupWebSocketListener()

  return {
    projects,
    isLoading,
    error,
    fetchProjects,
    createProject,
    updateProject,
    deleteProject,
    addComponent,
    updateComponent,
    deleteComponent,
    getProjectByName,
    getComponentsByProject,
    setupWebSocketListener,
  }
})
