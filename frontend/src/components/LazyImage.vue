<template>
  <div class="lazy-image-container" ref="container">
    <!-- Placeholder while loading -->
    <div
      v-if="!loaded && !error && !showingDefault"
      class="w-full h-full bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 animate-pulse dark:from-gray-700 dark:via-gray-600 dark:to-gray-700 flex items-center justify-center"
    >
      <svg class="w-8 h-8 text-gray-400 dark:text-gray-500" fill="currentColor" viewBox="0 0 24 24">
        <path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/>
      </svg>
    </div>
    
    <!-- Actual image (only show if not using default placeholder) -->
    <img
      v-if="shouldShowImage && !showingDefault"
      :src="imageSrc"
      :alt="alt"
      :class="[imageClass, { 'opacity-0': !loaded, 'opacity-100': loaded }]"
      class="transition-opacity duration-300"
      @load="onLoad"
      @error="onError"
    />
    
    <!-- Default placeholder for broken/missing images -->
    <div
      v-if="showingDefault && loaded"
      class="w-full h-full bg-gradient-to-br from-slate-100 to-slate-200 dark:from-slate-800 dark:to-slate-900 flex items-center justify-center relative"
    >
      <!-- Video icon background -->
      <div class="absolute inset-0 flex items-center justify-center">
        <svg class="w-16 h-16 text-slate-300 dark:text-slate-600" fill="currentColor" viewBox="0 0 24 24">
          <path d="M17,10.5V7A1,1 0 0,0 16,6H4A1,1 0 0,0 3,7V17A1,1 0 0,0 4,18H16A1,1 0 0,0 17,17V13.5L21,17.5V6.5L17,10.5Z"/>
        </svg>
      </div>
      <!-- Play button overlay -->
      <div class="absolute inset-0 flex items-center justify-center">
        <div class="bg-black/30 rounded-full p-3">
          <svg class="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
            <path d="M8 5v14l11-7z"/>
          </svg>
        </div>
      </div>
      <!-- Label -->
      <div class="absolute bottom-2 left-2 right-2">
        <div class="bg-black/50 rounded px-2 py-1">
          <p class="text-xs text-white font-medium truncate">{{ alt || 'Video Thumbnail' }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'

const props = defineProps({
  src: {
    type: String,
    required: true
  },
  alt: {
    type: String,
    default: ''
  },
  class: {
    type: String,
    default: ''
  }
})

const container = ref(null)
const loaded = ref(false)
const error = ref(false)
const imageSrc = ref('')
const imageClass = ref(props.class)
const inView = ref(false)
const showingDefault = ref(false)

let observer = null

const shouldShowImage = computed(() => inView.value && imageSrc.value)

const onLoad = () => {
  loaded.value = true
  error.value = false
  showingDefault.value = false
}

const onError = () => {
  // Show default placeholder when image fails to load
  error.value = true
  loaded.value = true // Consider it "loaded" to show the default
  showingDefault.value = true
}

const loadImage = () => {
  if (props.src && !imageSrc.value) {
    imageSrc.value = props.src
    showingDefault.value = false
    error.value = false
  }
}

const setupIntersectionObserver = () => {
  if (!container.value) return

  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          inView.value = true
          loadImage()
          // Once we start loading, we can disconnect the observer
          if (observer) {
            observer.disconnect()
            observer = null
          }
        }
      })
    },
    {
      rootMargin: '100px', // Start loading when the image is 100px away from viewport
      threshold: 0.1 // Trigger when 10% of the element is visible
    }
  )

  observer.observe(container.value)
}

// Watch for changes in src prop
watch(() => props.src, (newSrc) => {
  if (newSrc !== imageSrc.value) {
    // Reset state when src changes
    loaded.value = false
    error.value = false
    imageSrc.value = ''
    showingDefault.value = false
    
    if (inView.value) {
      loadImage()
    }
  }
})

onMounted(() => {
  // Check if IntersectionObserver is supported
  if ('IntersectionObserver' in window) {
    setupIntersectionObserver()
  } else {
    // Fallback for browsers that don't support IntersectionObserver
    inView.value = true
    loadImage()
  }
})

onUnmounted(() => {
  if (observer) {
    observer.disconnect()
  }
})
</script>

<style scoped>
.lazy-image-container {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
}
</style>
