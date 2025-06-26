<template>
  <div class="container mx-auto px-4 py-6">
    <h1 class="text-2xl font-semibold mb-4">Search Bookmarks</h1>
    <form @submit.prevent="handleSearch" class="mb-6 flex gap-2">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search by title, description, or tag..."
        class="w-full px-3 py-2 border border-gray-300 rounded shadow-sm focus:outline-none focus:ring focus:border-blue-500  "
      />
      <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Search</button>
    </form>

    <!-- Filters -->
    <div class="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div class="border-b border-gray-200  overflow-hidden">
        <nav class="-mb-px flex space-x-4 sm:space-x-6 overflow-x-auto pb-px" aria-label="Sort Tabs">
          <button
            v-for="tab in sortTabs"
            :key="tab.id"
            @click="setSort(tab.id)"
            :class=" [
              currentSort === tab.id
                ? 'border-indigo-500 text-indigo-600  '
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300   ',
              'whitespace-nowrap py-3 px-1 sm:px-2 border-b-2 font-medium text-sm focus:outline-none transition-colors duration-150 ease-in-out'
            ]"
          >
            {{ tab.name }}
          </button>
        </nav>
      </div>
      <div class="flex flex-wrap gap-2 w-full sm:w-auto items-center">
        <div class="flex items-center gap-1 flex-shrink-0 py-1 px-1 rounded-md bg-gray-50  w-full sm:w-auto">
          <span class="text-sm font-medium text-gray-600  hidden sm:inline pl-2">Filter:</span>
          <OrientationFilter />
        </div>
      </div>
    </div>

    <!-- Use BookmarkGrid for results, pagination, and loading -->
    <BookmarkGrid
      :fetchBookmarks="fetchSearchBookmarks"
      :filters="bookmarkFilters"
      :showPagination="true"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { searchBookmarks } from '@/api/index.js'
import { useOrientationStore } from '@/stores/orientation.js'
import OrientationFilter from '@/components/OrientationFilter.vue'
import BookmarkGrid from '@/components/BookmarkGrid.vue'

const route = useRoute()
const router = useRouter()
const orientationStore = useOrientationStore()

const searchQuery = ref(route.query.q || '')
const currentSort = ref(route.query.sort || 'all')
const currentPage = ref(Number(route.query.page) || 1)
const itemsPerPage = 25

const sortTabs = [
  { id: 'all', name: 'All' },
  { id: 'popular', name: 'Popular' },
  { id: 'random', name: 'Random' },
]

function setSort(sort) {
  currentSort.value = sort
  currentPage.value = 1
}

// Sync filters and pagination with URL query
watch(
  [currentPage, currentSort, () => orientationStore.selectedOrientation, searchQuery],
  ([page, sort, orientation, q]) => {
    router.replace({
      query: {
        ...route.query,
        page,
        sort,
        orientation,
        q,
      },
    })
  }
)

// Watch for route changes (browser navigation)
watch(
  () => route.query,
  (query) => {
    if (query.page) currentPage.value = Number(query.page)
    if (query.sort) currentSort.value = query.sort
    if (query.orientation && orientationStore.selectedOrientation !== query.orientation) {
      orientationStore.setOrientation(query.orientation)
    }
    if (query.q !== undefined) searchQuery.value = query.q
  }
)

const bookmarkFilters = computed(() => {
  const filters = {
    q: searchQuery.value,
    sort: currentSort.value,
    page: currentPage.value,
    page_size: itemsPerPage,
  }
  if (orientationStore.selectedOrientation !== 'all') {
    filters.orientation = orientationStore.selectedOrientation
  }
  return filters
})

const fetchSearchBookmarks = async (params = {}) => {
  // params will include q, sort, page, page_size, orientation
  return await searchBookmarks(searchQuery.value, params)
}

const handleSearch = () => {
  currentPage.value = 1
}
</script>

<style scoped>
.aspect-video {
  aspect-ratio: 16 / 9;
}
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
@media (min-width: 640px) {
  .grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
@media (min-width: 768px) {
  .grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}
@media (min-width: 1280px) {
  .grid {
    grid-template-columns: repeat(6, minmax(0, 1fr));
  }
}
</style>