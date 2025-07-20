<template>
  <div>
    <!-- Search Box -->
    <div v-if="showSearch" class="mb-4">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search by title, description, or tag..."
        class="w-full px-3 py-2 border border-gray-600 rounded shadow-sm focus:outline-none focus:ring focus:border-primary bg-surface text-text-main placeholder-text-secondary"
      />
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4 animate-fade-in">
      <div
        v-for="n in 8"
        :key="n"
        class="rounded-lg bg-surface shadow border border-gray-700 flex flex-col overflow-hidden min-h-[180px]"
      >
        <div class="aspect-video bg-background animate-pulse"></div>
        <div class="h-4 w-2/3 bg-background rounded animate-pulse mt-2 mx-4"></div>
      </div>
    </div>

    <!-- Compact Video Card Grid -->
    <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-6 gap-4">
      <router-link
        v-for="bookmark in bookmarks"
        :key="bookmark.id"
        :to="{ name: 'bookmark-detail', params: { id: bookmark.id } }"
        class="group rounded-lg bg-surface shadow border border-gray-700 flex flex-col transition hover:shadow-lg overflow-hidden relative"
      >
        <!-- Video Thumbnail -->
        <div class="relative aspect-video bg-background">
          <img
            v-intersect="bookmark"
            :alt="bookmark.title"
            @error="onImageError"
            class="object-cover w-full h-full transition-transform duration-200 group-hover:scale-105"
          />
          <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition bg-black/40">
            <svg class="w-12 h-12 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z"/>
            </svg>
          </div>
        </div>
        <div class="p-2 flex-1 flex flex-col">
          <h2 class="font-semibold text-xs mb-1 line-clamp-2 text-text-main">{{ bookmark.title }}</h2>
          <!-- Tags -->
          <div v-if="bookmark.tags && bookmark.tags.length" class="flex flex-wrap gap-1 my-1">
            <button
              v-for="tag in bookmark.tags.slice(0, 2)"
              :key="tag"
              @click.prevent="searchByTag(tag)"
              class="px-1.5 py-0.5 bg-primary/10 text-primary/80 rounded-full text-[10px] font-semibold hover:bg-primary/20 transition"
            >
              {{ tag }}
            </button>
          </div>
          <div class="flex items-center gap-2 mt-auto">
            <span class="text-xs truncate max-w-[80px] text-text-secondary">{{ bookmark.user_username }}</span>
          </div>
        </div>
      </router-link>
    </div>

    <!-- Pagination -->
    <div v-if="showPagination && totalPages > 1" class="fixed bottom-0 left-0 right-0 p-4 flex justify-center items-center z-50">
      <div class="flex items-center gap-2 bg-surface/80 backdrop-blur-md border border-gray-700 rounded-full shadow-lg px-4 py-2">
        <button
          class="px-4 py-2 bg-surface border border-gray-600 text-text-main rounded-full text-sm font-medium hover:bg-background disabled:opacity-50 transition"
          :disabled="currentPage === 1"
          @click="goToPreviousPage"
        >
          Previous
        </button>
        <span class="text-sm text-text-secondary px-2 font-medium">Page {{ currentPage }} of {{ totalPages }}</span>
        <button
          class="px-4 py-2 bg-surface border border-gray-600 text-text-main rounded-full text-sm font-medium hover:bg-background disabled:opacity-50 transition"
          :disabled="currentPage === totalPages"
          @click="goToNextPage"
        >
          Next
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'

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
let debounceTimeout = null

const totalPages = computed(() =>
  Math.max(1, Math.ceil(totalCount.value / itemsPerPage.value))
)

const loadBookmarks = async () => {
  loading.value = true
  try {
    const params = {
      page: props.currentPage, // CHANGED
      page_size: itemsPerPage.value,
      ...props.filters,
      ...(searchQuery.value ? { q: searchQuery.value } : {})
    }
    const response = await props.fetchBookmarks(params)
    bookmarks.value = response.results.map(bookmark => ({
      ...bookmark,
      thumbnail: null, // Initialize thumbnail to null
    }));
    totalCount.value = response.count
  } catch (e) {
    bookmarks.value = []
    totalCount.value = 0
  }
  loading.value = false
}

function onSearch() {
  emit('update:search', searchQuery.value)
  emit('update:page', 1) // Reset to page 1 on search
}

function searchByTag(tag) {
  searchQuery.value = tag;
}

// Watch for changes in the search query and apply a debounce
watch(searchQuery, () => {
  clearTimeout(debounceTimeout);
  debounceTimeout = setTimeout(() => {
    onSearch();
  }, 300); // Wait for 300ms after the user stops typing
});

function goToPreviousPage() {
  if (props.currentPage > 1) emit('update:page', props.currentPage - 1)
}
function goToNextPage() {
  if (props.currentPage < totalPages.value) {
    emit('update:page', props.currentPage + 1); // Emit the next page number
  }
}

onMounted(loadBookmarks)

const vIntersect = {
  mounted: (el, binding) => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const bookmark = binding.value;
            // Directly set the 'src' attribute on the DOM element
            if (bookmark && bookmark.thumbnail_url) {
              el.src = bookmark.thumbnail_url;
            } else {
              // If there's no thumbnail URL, use the placeholder immediately
              el.src = '/media/default.jpg';
            }
            // Stop observing the element
            observer.unobserve(el);
          }
        });
      },
      {
        rootMargin: '0px 0px 200px 0px', // Start loading images 200px before they enter the viewport
      }
    );
    observer.observe(el);
  },
};

watch(() => [props.currentPage, props.filters], loadBookmarks, { deep: true });

const onImageError = (event) => {
  // Replace broken image with a default placeholder
  event.target.src = '/media/default.jpg';
};
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
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
