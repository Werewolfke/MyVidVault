<template>
  <div>
    <!-- Search Box -->
    <form v-if="showSearch" @submit.prevent="onSearch" class="mb-4 flex gap-2">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search by title, description, or tag..."
        class="w-full px-3 py-2 border border-gray-300 rounded shadow-sm focus:outline-none focus:ring focus:border-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200 dark:placeholder-gray-500"
      />
      <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600">Search</button>
    </form>

    <!-- Loading skeleton -->
    <div v-if="loading" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-6 gap-4 animate-fade-in">
      <div
        v-for="n in skeletonCount"
        :key="n"
        class="rounded-lg bg-gradient-to-br from-gray-200/80 via-gray-100/80 to-gray-300/80 shadow border border-gray-200 dark:border-gray-700 dark:from-gray-700 dark:via-gray-800 dark:to-gray-900 flex flex-col overflow-hidden"
      >
        <div class="aspect-video bg-gradient-to-r from-indigo-100 via-indigo-200 to-indigo-300 animate-pulse dark:from-indigo-900 dark:via-indigo-800 dark:to-indigo-700"></div>
        <div class="p-2">
          <div class="h-3 w-2/3 bg-gray-300 rounded animate-pulse dark:bg-gray-700 mb-1"></div>
          <div class="h-3 w-1/2 bg-gray-300 rounded animate-pulse dark:bg-gray-700"></div>
        </div>
      </div>
    </div>

    <!-- Compact Video Card Grid -->
    <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-6 gap-4">
      <router-link
        v-for="(bookmark, index) in bookmarks"
        :key="bookmark.id"
        :to="{ name: 'bookmark-detail', params: { id: bookmark.id } }"
        class="group rounded-lg bg-white/90 shadow border border-gray-200 dark:bg-gray-800 dark:border-gray-700 flex flex-col transition hover:shadow-lg overflow-hidden relative animate-fade-in-up"
        :style="{ animationDelay: `${index * 50}ms` }"
      >
        <!-- Video Thumbnail -->
        <div class="relative aspect-video bg-gray-200 dark:bg-gray-700">
          <LazyImage
            :src="bookmark.thumbnail_url"
            :alt="bookmark.title"
            class="object-cover w-full h-full transition-transform duration-200 group-hover:scale-105"
          />
          <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition bg-black/40">
            <svg class="w-12 h-12 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z"/>
            </svg>
          </div>
        </div>
        <div class="p-2 flex-1 flex flex-col">
          <h2 class="font-semibold text-xs mb-1 line-clamp-2 text-gray-800 dark:text-gray-200">{{ bookmark.title }}</h2>
          <div class="flex items-center gap-2 mt-auto">
            <span class="text-xs truncate max-w-[80px] text-gray-600 dark:text-gray-400">{{ bookmark.user_username }}</span>
          </div>
        </div>
      </router-link>
    </div>

    <!-- Pagination -->
    <div v-if="showPagination" class="mt-8 flex flex-row flex-wrap justify-center items-center gap-2">
      <button
        class="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-md shadow-sm text-sm font-medium hover:bg-gray-50 dark:bg-gray-800 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
        :disabled="currentPage === 1"
        @click="goToPreviousPage"
      >
        Previous
      </button>
      <span class="text-sm text-gray-600 px-1 dark:text-gray-400">Page {{ currentPage }} of {{ totalPages }}</span>
      <button
        class="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-md shadow-sm text-sm font-medium hover:bg-gray-50 dark:bg-gray-800 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
        :disabled="currentPage === totalPages"
        @click="goToNextPage"
      >
        Next
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import LazyImage from './LazyImage.vue'

const props = defineProps({
  fetchBookmarks: { type: Function, required: true },
  showPagination: { type: Boolean, default: true },
  filters: { type: Object, default: () => ({}) },
  showSearch: { type: Boolean, default: false },
  currentPage: { type: Number, default: 1 }, // NEW
})

const emit = defineEmits(['update:search', 'update:page']) // NEW

const loading = ref(false)
const bookmarks = ref([])
const itemsPerPage = ref(25)
const totalCount = ref(0)
const searchQuery = ref(props.filters.q || '')

const totalPages = computed(() =>
  Math.max(1, Math.ceil(totalCount.value / itemsPerPage.value))
)

// Responsive skeleton count based on viewport
const skeletonCount = computed(() => {
  // Show different number of skeletons based on expected grid layout
  if (typeof window !== 'undefined') {
    const width = window.innerWidth
    if (width < 640) return 6 // sm: 2 cols × 3 rows
    if (width < 768) return 9 // md: 3 cols × 3 rows
    if (width < 1280) return 12 // lg: 4 cols × 3 rows
    return 18 // xl: 6 cols × 3 rows
  }
  return 12 // fallback
})

const loadBookmarks = async () => {
  if (loading.value) return // Prevent multiple simultaneous requests
  
  loading.value = true
  try {
    const params = {
      page: props.currentPage,
      page_size: itemsPerPage.value,
      ...props.filters,
      ...(searchQuery.value ? { q: searchQuery.value } : {})
    }
    const response = await props.fetchBookmarks(params)
    bookmarks.value = response.results
    totalCount.value = response.count
    
    // Preload next page images in the background
    preloadNextPageImages()
  } catch (e) {
    console.error('Failed to load bookmarks:', e)
    bookmarks.value = []
    totalCount.value = 0
  } finally {
    loading.value = false
  }
}

// Preload thumbnails for the next page to improve perceived performance
const preloadNextPageImages = async () => {
  if (props.currentPage >= totalPages.value) return
  
  try {
    const nextPageParams = {
      page: props.currentPage + 1,
      page_size: itemsPerPage.value,
      ...props.filters,
      ...(searchQuery.value ? { q: searchQuery.value } : {})
    }
    const response = await props.fetchBookmarks(nextPageParams)
    
    // Preload the first few images from next page
    response.results.slice(0, 6).forEach(bookmark => {
      if (bookmark.thumbnail_url) {
        const img = new Image()
        img.src = bookmark.thumbnail_url
      }
    })
  } catch (e) {
    // Silently fail for preloading
    console.debug('Preload failed:', e)
  }
}

function onSearch() {
  emit('update:search', searchQuery.value)
  emit('update:page', 1) // Reset to page 1 on search
}

function goToPreviousPage() {
  if (props.currentPage > 1) emit('update:page', props.currentPage - 1)
}
function goToNextPage() {
  if (props.currentPage < totalPages.value) {
    emit('update:page', props.currentPage + 1); // Emit the next page number
  }
}

onMounted(loadBookmarks)
watch(() => [props.currentPage, props.filters], loadBookmarks, { deep: true });
</script>

<style scoped>
.aspect-video {
  aspect-ratio: 16 / 9; /* Ensures 16:9 aspect ratio */
  overflow: hidden; /* Prevents content from overflowing */
  position: relative; /* Ensures child elements are positioned correctly */
}

img {
  object-fit: cover; /* Ensures the image fills the container while maintaining aspect ratio */
  width: 100%; /* Ensures the image spans the full width of the container */
  height: 100%; /* Ensures the image spans the full height of the container */
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Animation for grid items */
@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.animate-fade-in-up {
  animation: fade-in-up 0.5s ease-out forwards;
  opacity: 0;
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}

/* Performance optimization: Use GPU acceleration */
.group {
  transform: translateZ(0);
  backface-visibility: hidden;
}

/* Reduce motion for users who prefer it */
@media (prefers-reduced-motion: reduce) {
  .animate-fade-in-up,
  .animate-fade-in {
    animation: none;
    opacity: 1;
    transform: none;
  }
  
  .transition {
    transition: none;
  }
}
</style>