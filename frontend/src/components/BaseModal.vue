<template>
  <transition name="glass-fade">
    <div
      v-if="modelValue"
      class="fixed inset-0 z-50 flex items-center justify-center"
      style="backdrop-filter: blur(12px) saturate(160%) brightness(1.1); background: rgba(255,255,255,0.12);"
      @click.self="close"
    >
      <div
        class="bg-white/70 rounded-lg shadow-lg p-6 w-full max-w-md relative border border-white/30 dark:bg-gray-800/70 dark:border-gray-600"
        style="backdrop-filter: blur(24px) saturate(180%) brightness(1.1);"
      >
        <button
          class="absolute top-2 right-2 text-gray-400 hover:text-gray-700 dark:text-gray-300 dark:hover:text-gray-500"
          @click="close"
          aria-label="Close"
        >
          &times;
        </button>
        <slot />
      </div>
    </div>
  </transition>
</template>

<script setup>
const props = defineProps({
  modelValue: { type: Boolean, required: true }
})
const emit = defineEmits(['update:modelValue'])
function close() {
  emit('update:modelValue', false)
}
</script>

<style>
.glass-fade-enter-active, .glass-fade-leave-active {
  transition: opacity 0.3s cubic-bezier(.4,0,.2,1), transform 0.3s cubic-bezier(.4,0,.2,1);
}
.glass-fade-enter-from, .glass-fade-leave-to {
  opacity: 0;
  transform: scale(0.96) translateY(16px);
}
.glass-fade-enter-to, .glass-fade-leave-from {
  opacity: 1;
  transform: scale(1) translateY(0);
}
</style>