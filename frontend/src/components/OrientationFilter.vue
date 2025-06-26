<template>
  <div class="flex flex-row flex-wrap gap-1">
    <button
      v-for="filter in orientationStore.orientationFilters"
      :key="filter.id"
      @click="orientationStore.setOrientation(filter.id)"
      :class="[
        orientationStore.selectedOrientation === filter.id
          ? 'bg-indigo-100 text-indigo-700 shadow-sm dark:bg-indigo-900 dark:text-indigo-300'
          : 'bg-white text-gray-600 hover:bg-gray-100 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700',
        'px-3 py-1.5 rounded-md text-xs sm:text-sm font-medium focus:outline-none transition-all'
      ]"
    >
      {{ filter.name }}
    </button>
  </div>
</template>

<script setup>
import { useOrientationStore } from '@/stores/orientation.js'
const orientationStore = useOrientationStore()
</script>