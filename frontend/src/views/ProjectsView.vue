<template>
  <div class="space-y-6">
    <div class="page-header">
      <div>
        <h1 class="page-title">Projects</h1>
        <p class="text-gray-400 mt-2">Manage projects and their components</p>
      </div>
      <Button variant="success" @click="showAddProjectDialog = true">
        <Plus class="w-4 h-4" />
        Add Project
      </Button>
    </div>

    <div class="grid grid-cols-3 gap-6">
      <!-- Projects List -->
      <div class="col-span-1">
        <Card title="Projects">
          <div class="space-y-2">
            <button
              v-for="project in projectsStore.projects"
              :key="project.id"
              @click="selectedProjectId = project.id"
              :class="[
                'w-full text-left px-4 py-3 rounded-lg border transition-all',
                selectedProjectId === project.id
                  ? 'bg-[#4a9eff] border-[#4a9eff] text-white'
                  : 'bg-[#404040] border-[#555555] text-gray-300 hover:border-[#4a9eff]',
              ]"
            >
              {{ project.name }}
            </button>
            <div v-if="projectsStore.projects.length === 0" class="text-center py-8 text-gray-400">
              <p>No projects yet</p>
            </div>
          </div>
          <div class="flex gap-2 mt-4 pt-4 border-t border-[#555555]">
            <Button
              variant="danger"
              size="sm"
              @click="handleDeleteProject"
              :disabled="!selectedProjectId"
              class="flex-1"
            >
              <Trash2 class="w-4 h-4" />
              Delete
            </Button>
            <Button
              variant="secondary"
              size="sm"
              @click="handleCopyProject"
              :disabled="!selectedProjectId"
              class="flex-1"
            >
              <Copy class="w-4 h-4" />
              Copy
            </Button>
          </div>
        </Card>
      </div>

      <!-- Project Details -->
      <div class="col-span-2">
        <Card v-if="selectedProject" title="Project Details">
          <form @submit.prevent="handleSaveProject" class="space-y-4">
            <Input
              v-model="selectedProject.name"
              label="Project Name"
              required
            />
            <Select
              v-model="selectedProject.build_server"
              :options="libraryStore.presets.build_servers"
              label="Build Server"
              required
            />
            <Select
              v-model="selectedProject.deploy_server"
              :options="libraryStore.presets.deploy_servers"
              label="Deploy Server"
              required
            />
            <Input
              v-model="selectedProject.database_name"
              label="Database"
              required
            />
            <Select
              v-model="selectedProject.environment"
              :options="libraryStore.presets.environments"
              label="Environment"
              required
            />
            <Input
              v-model="selectedProject.backup_location"
              label="Backup Location"
              placeholder="/backups/project"
            />

            <!-- Components Section -->
            <div class="border-t border-[#555555] pt-6">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-bold text-white">Components</h3>
                <Button
                  type="button"
                  variant="success"
                  size="sm"
                  @click="showAddComponentDialog = true"
                >
                  <Plus class="w-4 h-4" />
                  Add
                </Button>
              </div>

              <div class="space-y-2">
                <div
                  v-for="component in selectedProject.components"
                  :key="component.id"
                  class="flex items-center justify-between bg-[#404040] p-3 rounded-lg border border-[#555555]"
                >
                  <div>
                    <p class="font-medium text-white">{{ component.name }}</p>
                    <p class="text-sm text-gray-400">{{ component.developer }}</p>
                  </div>
                  <div class="flex gap-2">
                    <Button
                      type="button"
                      variant="secondary"
                      size="sm"
                      @click="editComponent(component)"
                    >
                      Edit
                    </Button>
                    <Button
                      type="button"
                      variant="danger"
                      size="sm"
                      @click="handleDeleteComponent(component.id!)"
                    >
                      Delete
                    </Button>
                  </div>
                </div>
                <div v-if="selectedProject.components.length === 0" class="text-center py-8 text-gray-400">
                  <p>No components yet</p>
                </div>
              </div>
            </div>

            <div class="flex gap-3 justify-end pt-4 border-t border-[#555555]">
              <Button variant="secondary" type="button" @click="selectedProjectId = null">
                Cancel
              </Button>
              <Button variant="success" type="submit">
                <Save class="w-4 h-4" />
                Save Project
              </Button>
            </div>
          </form>
        </Card>
        <Card v-else title="Project Details">
          <div class="text-center py-12 text-gray-400">
            <p>Select a project to view details</p>
          </div>
        </Card>
      </div>
    </div>

    <!-- Add/Edit Project Dialog -->
    <Dialog
      :is-open="showAddProjectDialog"
      title="Add New Project"
      @close="showAddProjectDialog = false"
    >
      <div class="space-y-4">
        <Input
          v-model="newProject.name"
          label="Project Name"
          placeholder="e.g., BRHUB"
          required
        />
        <Select
          v-model="newProject.build_server"
          :options="libraryStore.presets.build_servers"
          label="Build Server"
          required
        />
        <Select
          v-model="newProject.deploy_server"
          :options="libraryStore.presets.deploy_servers"
          label="Deploy Server"
          required
        />
        <Input
          v-model="newProject.database_name"
          label="Database"
          required
        />
        <Select
          v-model="newProject.environment"
          :options="libraryStore.presets.environments"
          label="Environment"
          required
        />
        <Input
          v-model="newProject.backup_location"
          label="Backup Location"
          placeholder="/backups/project"
        />
      </div>

      <template #footer>
        <Button variant="secondary" @click="showAddProjectDialog = false">
          Cancel
        </Button>
        <Button variant="success" @click="handleAddProject">
          Create Project
        </Button>
      </template>
    </Dialog>

    <!-- Add/Edit Component Dialog -->
    <Dialog
      :is-open="showAddComponentDialog"
      :title="editingComponent ? 'Edit Component' : 'Add Component'"
      @close="showAddComponentDialog = false"
    >
      <div class="space-y-4">
        <Input
          v-model="newComponent.name"
          label="Component Name"
          required
        />
        <Select
          v-model="newComponent.developer"
          :options="libraryStore.presets.developers"
          label="Developer"
          required
        />
        <Select
          v-model="newComponent.vcs_type"
          :options="['git', 'svn']"
          label="VCS Type"
          required
        />
        <Input
          v-model="newComponent.vcs_url"
          label="VCS URL"
          placeholder="https://..."
          required
        />
        <Input
          v-model="newComponent.build_command"
          label="Build Command"
          placeholder="npm run build"
          required
        />
        <Input
          v-model="newComponent.component_url"
          label="Component URL"
          placeholder="https://..."
          required
        />
      </div>

      <template #footer>
        <Button variant="secondary" @click="showAddComponentDialog = false">
          Cancel
        </Button>
        <Button variant="success" @click="handleAddComponent">
          {{ editingComponent ? 'Update' : 'Add' }} Component
        </Button>
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import Card from '../components/ui/Card.vue'
import Input from '../components/ui/Input.vue'
import Select from '../components/ui/Select.vue'
import Button from '../components/ui/Button.vue'
import Dialog from '../components/ui/Dialog.vue'
import { useProjectsStore, type Project, type Component } from '../stores/projects'
import { useLibraryStore } from '../stores/library'
import { useClipboard } from '../composables/useClipboard'
import { useToast } from '../composables/useToast'
import { Plus, Trash2, Copy, Save } from 'lucide-vue-next'

const projectsStore = useProjectsStore()
const libraryStore = useLibraryStore()
const { copyToClipboard } = useClipboard()
const { success, error } = useToast()

const selectedProjectId = ref<number | null>(null)
const showAddProjectDialog = ref(false)
const showAddComponentDialog = ref(false)
const editingComponent = ref<Component | null>(null)

const newProject = ref<Project>({
  name: '',
  build_server: '',
  deploy_server: '',
  database_name: '',
  environment: '',
  backup_location: '',
  components: [],
})

const newComponent = ref<Component>({
  name: '',
  developer: '',
  vcs_type: 'git',
  vcs_url: '',
  build_command: '',
  component_url: '',
})

const selectedProject = computed(() => {
  return projectsStore.projects.find(p => p.id === selectedProjectId.value) || null
})

const handleAddProject = async () => {
  if (!newProject.value.name) {
    error('Project name is required')
    return
  }

  const result = await projectsStore.createProject({
    ...newProject.value,
    components: [],
  })

  if (result) {
    success('Project created successfully!')
    showAddProjectDialog.value = false
    newProject.value = {
      name: '',
      build_server: '',
      deploy_server: '',
      database_name: '',
      environment: '',
      backup_location: '',
      components: [],
    }
    selectedProjectId.value = result.id || null
  } else {
    error('Failed to create project')
  }
}

const handleSaveProject = async () => {
  if (!selectedProject.value || !selectedProject.value.id) return

  const result = await projectsStore.updateProject(selectedProject.value.id, {
    name: selectedProject.value.name,
    build_server: selectedProject.value.build_server,
    deploy_server: selectedProject.value.deploy_server,
    database_name: selectedProject.value.database_name,
    environment: selectedProject.value.environment,
    backup_location: selectedProject.value.backup_location,
  })

  if (result) {
    success('Project saved successfully!')
  } else {
    error('Failed to save project')
  }
}

const handleDeleteProject = async () => {
  if (!selectedProjectId.value) return
  if (confirm('Are you sure you want to delete this project?')) {
    await projectsStore.deleteProject(selectedProjectId.value)
    selectedProjectId.value = null
    success('Project deleted successfully!')
  }
}

const handleCopyProject = async () => {
  if (!selectedProject.value) return
  const text = `Project: ${selectedProject.value.name}
Build Server: ${selectedProject.value.build_server}
Deploy Server: ${selectedProject.value.deploy_server}
Database: ${selectedProject.value.database_name}
Environment: ${selectedProject.value.environment}`

  if (await copyToClipboard(text)) {
    success('Project details copied!')
  } else {
    error('Failed to copy')
  }
}

const handleAddComponent = async () => {
  if (!selectedProject.value || !selectedProject.value.id) return

  if (editingComponent.value && editingComponent.value.id) {
    const result = await projectsStore.updateComponent(
      selectedProject.value.id,
      editingComponent.value.id,
      newComponent.value
    )
    if (result) {
      success('Component updated successfully!')
    } else {
      error('Failed to update component')
    }
  } else {
    const result = await projectsStore.addComponent(
      selectedProject.value.id,
      newComponent.value
    )
    if (result) {
      success('Component added successfully!')
    } else {
      error('Failed to add component')
    }
  }

  showAddComponentDialog.value = false
  resetComponentForm()
}

const handleDeleteComponent = async (componentId: number) => {
  if (!selectedProject.value || !selectedProject.value.id) return
  if (confirm('Are you sure you want to delete this component?')) {
    await projectsStore.deleteComponent(selectedProject.value.id, componentId)
    success('Component deleted successfully!')
  }
}

const editComponent = (component: Component) => {
  editingComponent.value = component
  newComponent.value = { ...component }
  showAddComponentDialog.value = true
}

const resetComponentForm = () => {
  editingComponent.value = null
  newComponent.value = {
    name: '',
    developer: '',
    vcs_type: 'git',
    vcs_url: '',
    build_command: '',
    component_url: '',
  }
}

onMounted(async () => {
  if (projectsStore.projects.length === 0) {
    await projectsStore.fetchProjects()
  }
  if (libraryStore.presets.developers.length === 0) {
    await libraryStore.fetchPresets()
  }
})
</script>
