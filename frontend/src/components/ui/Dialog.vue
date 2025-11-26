<template>
  <Teleport to="body">
    <transition
      enter-active-class="ease-out duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="ease-in duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="isOpen"
        class="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4"
        @click="handleBackdropClick"
      >
        <transition
          enter-active-class="ease-out duration-200"
          enter-from-class="opacity-0 scale-95"
          enter-to-class="opacity-100 scale-100"
          leave-active-class="ease-in duration-200"
          leave-from-class="opacity-100 scale-100"
          leave-to-class="opacity-0 scale-95"
        >
          <div
            v-if="isOpen"
            class="bg-[#2b2b2b] rounded-lg border border-[#555555] max-w-md w-full shadow-xl"
            @click.stop
          >
            <div class="flex items-center justify-between border-b border-[#555555] p-6">
              <h2 class="text-xl font-bold text-white">{{ title }}</h2>
              <button
                @click="emit('close')"
                class="text-gray-400 hover:text-white transition-colors"
              >
                <X class="w-5 h-5" />
              </button>
            </div>
            <div class="p-6">
              <slot />
            </div>
            <div v-if="$slots.footer" class="border-t border-[#555555] p-6 flex gap-3 justify-end">
              <slot name="footer" />
            </div>
          </div>
        </transition>
      </div>
    </transition>
  </Teleport>
</template>

<script setup lang="ts">
import { X } from 'lucide-vue-next'

interface Props {
  isOpen: boolean
  title: string
  closeOnBackdrop?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  closeOnBackdrop: true,
})

const emit = defineEmits<{
  close: []
}>()

const handleBackdropClick = () => {
  if (props.closeOnBackdrop) {
    emit('close')
  }
}
</script>
