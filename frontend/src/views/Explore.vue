
<template>
  <div class="container mx-auto px-4 py-6">
    <div class="flex-grow">
      <h1 class="text-2xl font-semibold mb-1 text-gray-800 dark:text-gray-200">Explore Bookmarks</h1>
      <div class="mb-4 text-sm text-gray-600 dark:text-gray-400">
        Page {{ currentPage }} of {{ totalPages }} ({{ totalCount }} results)
      </div>
      <!-- Filter + Sort controls -->
      <div class="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div class="border-b border-gray-200 dark:border-gray-700 overflow-hidden">
          <nav class="-mb-px flex space-x-4 sm:space-x-6 overflow-x-auto pb-px" aria-label="Sort Tabs">
            <button
              v-for="tab in homeSortTabs"
              :key="tab.id"
              @click="currentSort = tab.id"
              :class="[
                currentSort === tab.id
                  ? 'border-indigo-500 text-indigo-600 dark:border-indigo-400 dark:text-indigo-300'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300 dark:hover:border-gray-600',
                'whitespace-nowrap py-3 px-1 sm:px-2 border-b-2 font-medium text-sm focus:outline-none transition-colors duration-150 ease-in-out'
              ]"
            >
              {{ tab.name }}
            </button>
          </nav>
        </div>
        <div class="flex flex-wrap gap-2 w-full sm:w-auto items-center">
          <div class="flex items-center gap-1 flex-shrink-0 py-1 px-1 rounded-md bg-gray-50 dark:bg-gray-800 w-full sm:w-auto">
            <span class="text-sm font-medium text-gray-600 dark:text-gray-400 hidden sm:inline pl-2">Filter:</span>
            <OrientationFilter />
          </div>
        </div>
      </div>

      <!-- BookmarkGrid with search and pagination -->
      <BookmarkGrid
        :fetchBookmarks="fetchVideosWrapper"
        :filters="bookmarkGridFilters"
        :showPagination="true"
        :showSearch="true"
        :currentPage="currentPage"
        @update:search="onSearchUpdate"
        @update:page="val => currentPage = val"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { fetchVideos } from '@/api/index.js';
import { useOrientationStore } from '@/stores/orientation.js';
import OrientationFilter from '@/components/OrientationFilter.vue';
import BookmarkGrid from '@/components/BookmarkGrid.vue';

const route = useRoute();
const router = useRouter();
const orientationStore = useOrientationStore();

const currentPage = ref(Number(route.query.page) || 1);
const currentSort = ref(route.query.sort || 'all');
const search = ref(route.query.q || '');

const homeSortTabs = [
  { id: 'all', name: 'All' },
  { id: 'popular', name: 'Popular' },
  { id: 'random', name: 'Random' },
  { id: 'following', name: 'Following' }, // NEW
];

// Sync orientation with query
if (route.query.orientation && orientationStore.selectedOrientation !== route.query.orientation) {
  orientationStore.setOrientation(route.query.orientation);
}

// Keep URL in sync with state
watch(
  [currentPage, currentSort, () => orientationStore.selectedOrientation, search],
  ([page, sort, orientation, q]) => {
    router.replace({
      query: {
        ...route.query,
        page,
        sort,
        orientation,
        q,
      },
    });
  }
);

// Watch for route changes (e.g., browser navigation)
watch(
  () => route.query,
  (query) => {
    if (query.page) currentPage.value = Number(query.page);
    if (query.sort) currentSort.value = query.sort;
    if (query.orientation && orientationStore.selectedOrientation !== query.orientation) {
      orientationStore.setOrientation(query.orientation);
    }
    if (query.q !== undefined) search.value = query.q;
  }
);

const itemsPerPage = 25;
const totalCount = ref(0);

const totalPages = computed(() =>
  Math.max(1, Math.ceil(totalCount.value / itemsPerPage))
);

const bookmarkGridFilters = computed(() => {
  const filters = {
    page: currentPage.value,
    page_size: itemsPerPage,
    sort: currentSort.value,
  };
  if (orientationStore.selectedOrientation !== 'all') {
    filters.orientation = orientationStore.selectedOrientation;
  }
  if (search.value) {
    filters.q = search.value;
  }
  if (currentSort.value === 'following') {
    filters.following = true;
  }
  return filters;
});

const fetchVideosWrapper = async (params) => {
  const response = await fetchVideos(params);
  totalCount.value = response.count;
  return response;
};

function onSearchUpdate(q) {
  search.value = q;
  currentPage.value = 1;
}

watch(currentSort, () => {
  currentPage.value = 1;
});
watch(() => orientationStore.selectedOrientation, () => {
  currentPage.value = 1;
});
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
@keyframes fade-in {
  from { opacity: 0; transform: translateY(16px);}
  to { opacity: 1; transform: none;}
}
.animate-fade-in {
  animation: fade-in 0.7s cubic-bezier(.4,0,.2,1);
}
</style>
