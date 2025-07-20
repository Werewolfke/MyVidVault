<template>
  <div class="flex flex-row flex-wrap gap-1">
    <button
      v-for="filter in orientationStore.orientationFilters"
      :key="filter.id"
      @click="orientationStore.setOrientation(filter.id)"
      :class="[
        orientationStore.selectedOrientation === filter.id
          ? 'bg-primary/20 text-primary shadow-sm'
          : 'bg-surface text-text-secondary hover:bg-background',
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
