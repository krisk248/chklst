<template>
  <div class="space-y-6">
    <div class="page-header">
      <div>
        <h1 class="page-title">Library</h1>
        <p class="text-gray-400 mt-2">Manage library presets and defaults</p>
      </div>
    </div>

    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <Card title="Developers">
        <div class="text-center text-3xl font-bold text-[#4a9eff]">
          {{ libraryStore.presets.developers.length }}
        </div>
      </Card>
      <Card title="Build Servers">
        <div class="text-center text-3xl font-bold text-blue-400">
          {{ libraryStore.presets.build_servers.length }}
        </div>
      </Card>
      <Card title="Deploy Servers">
        <div class="text-center text-3xl font-bold text-green-400">
          {{ libraryStore.presets.deploy_servers.length }}
        </div>
      </Card>
      <Card title="Environments">
        <div class="text-center text-3xl font-bold text-yellow-400">
          {{ libraryStore.presets.environments.length }}
        </div>
      </Card>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Developers -->
      <Card title="Developers">
        <div class="space-y-2">
          <div
            v-for="(dev, idx) in libraryStore.presets.developers"
            :key="`dev-${idx}`"
            class="flex items-center justify-between bg-[#404040] p-3 rounded-lg border border-[#555555]"
          >
            <span class="text-white">{{ dev }}</span>
            <Button
              variant="danger"
              size="sm"
              @click="libraryStore.removeDeveloper(dev)"
            >
              <Trash2 class="w-4 h-4" />
            </Button>
          </div>
          <div v-if="libraryStore.presets.developers.length === 0" class="text-center py-8 text-gray-400">
            <p>No developers in library</p>
          </div>
        </div>
        <div class="mt-4 pt-4 border-t border-[#555555]">
          <form @submit.prevent="addDeveloper" class="flex gap-2">
            <Input
              v-model="newDeveloper"
              placeholder="Add developer"
              size="sm"
            />
            <Button type="submit" variant="success">
              <Plus class="w-4 h-4" />
            </Button>
          </form>
        </div>
      </Card>

      <!-- Build Servers -->
      <Card title="Build Servers">
        <div class="space-y-2">
          <div
            v-for="(server, idx) in libraryStore.presets.build_servers"
            :key="`build-${idx}`"
            class="flex items-center justify-between bg-[#404040] p-3 rounded-lg border border-[#555555]"
          >
            <span class="text-white">{{ server }}</span>
            <Button
              variant="danger"
              size="sm"
              @click="libraryStore.removeBuildServer(server)"
            >
              <Trash2 class="w-4 h-4" />
            </Button>
          </div>
          <div v-if="libraryStore.presets.build_servers.length === 0" class="text-center py-8 text-gray-400">
            <p>No build servers in library</p>
          </div>
        </div>
        <div class="mt-4 pt-4 border-t border-[#555555]">
          <form @submit.prevent="addBuildServer" class="flex gap-2">
            <Input
              v-model="newBuildServer"
              placeholder="Add build server"
              size="sm"
            />
            <Button type="submit" variant="success">
              <Plus class="w-4 h-4" />
            </Button>
          </form>
        </div>
      </Card>

      <!-- Deploy Servers -->
      <Card title="Deploy Servers">
        <div class="space-y-2">
          <div
            v-for="(server, idx) in libraryStore.presets.deploy_servers"
            :key="`deploy-${idx}`"
            class="flex items-center justify-between bg-[#404040] p-3 rounded-lg border border-[#555555]"
          >
            <span class="text-white">{{ server }}</span>
            <Button
              variant="danger"
              size="sm"
              @click="libraryStore.removeDeployServer(server)"
            >
              <Trash2 class="w-4 h-4" />
            </Button>
          </div>
          <div v-if="libraryStore.presets.deploy_servers.length === 0" class="text-center py-8 text-gray-400">
            <p>No deploy servers in library</p>
          </div>
        </div>
        <div class="mt-4 pt-4 border-t border-[#555555]">
          <form @submit.prevent="addDeployServer" class="flex gap-2">
            <Input
              v-model="newDeployServer"
              placeholder="Add deploy server"
              size="sm"
            />
            <Button type="submit" variant="success">
              <Plus class="w-4 h-4" />
            </Button>
          </form>
        </div>
      </Card>

      <!-- Environments -->
      <Card title="Environments">
        <div class="space-y-2">
          <div
            v-for="(env, idx) in libraryStore.presets.environments"
            :key="`env-${idx}`"
            class="flex items-center justify-between bg-[#404040] p-3 rounded-lg border border-[#555555]"
          >
            <span class="text-white">{{ env }}</span>
            <Button
              variant="danger"
              size="sm"
              @click="libraryStore.removeEnvironment(env)"
            >
              <Trash2 class="w-4 h-4" />
            </Button>
          </div>
          <div v-if="libraryStore.presets.environments.length === 0" class="text-center py-8 text-gray-400">
            <p>No environments in library</p>
          </div>
        </div>
        <div class="mt-4 pt-4 border-t border-[#555555]">
          <form @submit.prevent="addEnvironment" class="flex gap-2">
            <Input
              v-model="newEnvironment"
              placeholder="Add environment"
              size="sm"
            />
            <Button type="submit" variant="success">
              <Plus class="w-4 h-4" />
            </Button>
          </form>
        </div>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Card from '../components/ui/Card.vue'
import Input from '../components/ui/Input.vue'
import Button from '../components/ui/Button.vue'
import { useLibraryStore } from '../stores/library'
import { useToast } from '../composables/useToast'
import { Trash2, Plus } from 'lucide-vue-next'

const libraryStore = useLibraryStore()
const { success } = useToast()

const newDeveloper = ref('')
const newBuildServer = ref('')
const newDeployServer = ref('')
const newEnvironment = ref('')

const addDeveloper = async () => {
  if (newDeveloper.value.trim()) {
    await libraryStore.addDeveloper(newDeveloper.value.trim())
    success('Developer added!')
    newDeveloper.value = ''
  }
}

const addBuildServer = async () => {
  if (newBuildServer.value.trim()) {
    await libraryStore.addBuildServer(newBuildServer.value.trim())
    success('Build server added!')
    newBuildServer.value = ''
  }
}

const addDeployServer = async () => {
  if (newDeployServer.value.trim()) {
    await libraryStore.addDeployServer(newDeployServer.value.trim())
    success('Deploy server added!')
    newDeployServer.value = ''
  }
}

const addEnvironment = async () => {
  if (newEnvironment.value.trim()) {
    await libraryStore.addEnvironment(newEnvironment.value.trim())
    success('Environment added!')
    newEnvironment.value = ''
  }
}

onMounted(async () => {
  if (libraryStore.presets.developers.length === 0) {
    await libraryStore.fetchPresets()
  }
})
</script>
