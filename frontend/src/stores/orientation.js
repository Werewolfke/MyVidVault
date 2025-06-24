import { defineStore } from 'pinia'
import { ref } from 'vue'

const ORIENTATION_KEY = 'orientationFilter'

export const useOrientationStore = defineStore('orientation', () => {
  const orientationFilters = [
    { id: 'all', name: 'All' },
    { id: 'straight', name: 'Straight' },
    { id: 'gay', name: 'Gay' },
    { id: 'bi', name: 'Bi' },
    { id: 'trans', name: 'Trans' },
    { id: 'sfw', name: 'SFW' },
  ]

  const selectedOrientation = ref(
    localStorage.getItem(ORIENTATION_KEY) || 'all'
  )

  function setOrientation(id) {
    selectedOrientation.value = id
    localStorage.setItem(ORIENTATION_KEY, id)
  }

  return { orientationFilters, selectedOrientation, setOrientation }
})