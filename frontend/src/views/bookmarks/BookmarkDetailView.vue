<template>
  <!-- Skeleton Loader -->
  <div v-if="loading" class="animate-pulse">
    <div class="rounded-2xl bg-white/80 dark:bg-gray-900/80 shadow-xl border border-gray-200/60 dark:border-gray-800/60 p-6">
      <div class="mb-4 bg-gray-300 dark:bg-gray-700 rounded-lg aspect-video"></div>
      <div class="h-8 bg-gray-300 dark:bg-gray-700 rounded w-3/4 mb-3"></div>
      <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-6 gap-y-3">
        <div class="flex flex-wrap items-center gap-x-4 gap-y-1">
          <div class="h-5 bg-gray-300 dark:bg-gray-700 rounded w-16"></div>
          <div class="h-5 bg-gray-300 dark:bg-gray-700 rounded w-24"></div>
        </div>
        <div class="flex items-center flex-wrap gap-2">
          <div class="h-7 bg-gray-300 dark:bg-gray-700 rounded w-16"></div>
        </div>
      </div>
      <div class="bg-gray-200 dark:bg-gray-700 p-4 rounded-lg mb-6">
        <div class="h-5 bg-gray-300 dark:bg-gray-600 rounded w-32 mb-3"></div>
        <div class="space-y-2">
          <div class="h-4 bg-gray-300 dark:bg-gray-600 rounded"></div>
          <div class="h-4 bg-gray-300 dark:bg-gray-600 rounded w-5/6"></div>
        </div>
      </div>
    </div>
  </div>

  <!-- Error State -->
  <div v-else-if="error" class="rounded-2xl bg-white/80 dark:bg-gray-900/80 shadow-xl border border-gray-200/60 dark:border-gray-800/60 p-8 text-center">
    <p class="font-medium text-red-600 dark:text-red-400">Error Loading Bookmark</p>
    <p class="text-sm text-gray-600 dark:text-gray-400">{{ error.message || 'Failed to load bookmark details. It might have been deleted or the link is incorrect.' }}</p>
    <router-link :to="{ name: 'home' }" class="mt-4 inline-block px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
      Go back home
    </router-link>
  </div>

  <!-- Bookmark Content -->
  <div v-else-if="bookmark">
    <!-- User & Channel -->
    <div class="flex items-center gap-3 mb-6 relative">
      <img
        :src="bookmark.user?.avatar_url || '/media/default.jpg'"
        alt="User Avatar"
        class="w-10 h-10 rounded-full object-cover border border-blue-100 dark:border-blue-900/40"
      >
      <div>
        <div class="flex items-center gap-2">
          <router-link
            v-if="bookmark.user?.username"
            :to="{ name: 'user-profile', params: { username: bookmark.user.username } }"
            class="font-semibold text-gray-900 dark:text-white text-base hover:underline"
          >
            {{ bookmark.user.username }}
          </router-link>
          <span v-else class="font-semibold text-gray-900 dark:text-white text-base">Unknown User</span>
        </div>
        <p v-if="bookmark.user?.bio" class="text-gray-600 dark:text-gray-400 text-xs mt-0.5">{{ bookmark.user.bio }}</p>
      </div>
      <!-- Collect Button (top right of user row) -->
      <button
        class="ml-auto px-4 py-2 bg-indigo-600 text-white rounded shadow hover:bg-indigo-700 transition font-semibold text-sm flex items-center"
        style="position: absolute; right: 0; top: 50%; transform: translateY(-50%);"
        @click="showCollectModal = true"
      >
        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
        </svg>
        Collect
      </button>
    </div>

    <!-- Video Player/Thumbnail -->
    <div class="mb-4 bg-black rounded-lg overflow-hidden shadow-lg">
      <div v-if="bookmark.video && bookmark.video.embed_url" class="relative w-full aspect-video">
        <iframe
          :src="bookmark.video.embed_url"
          frameborder="0"
          allow="autoplay; fullscreen; picture-in-picture"
          allowfullscreen
          class="absolute top-0 left-0 w-full h-full"
          title="Video Player"
        ></iframe>
      </div>
      <div v-else-if="bookmark.video && bookmark.video.thumbnail_url" class="relative w-full aspect-video">
        <img
          :src="bookmark.video.thumbnail_url"
          alt="Video Thumbnail"
          class="absolute top-0 left-0 w-full h-full object-contain bg-gray-800"
        >
      </div>
      <div v-else class="relative w-full bg-gray-700 flex items-center justify-center aspect-video">
        <div class="absolute top-0 left-0 w-full h-full flex items-center justify-center text-gray-400">
          No Video Preview Available
        </div>
      </div>
    </div>

    <!-- Title -->
    <h1 class="text-xl md:text-2xl font-bold text-gray-900 dark:text-white mb-2 break-words">{{ bookmark.title }}</h1>

    <!-- Metadata -->
    <div class="flex flex-wrap items-center text-xs text-gray-600 dark:text-gray-400 gap-x-3 gap-y-1 mb-4">
      <span v-if="bookmark.video" class="whitespace-nowrap">
        {{ bookmark.video.likes_count ?? 0 }} likes
      </span>
      <span v-if="bookmark.video" class="font-bold text-gray-400 dark:text-gray-600">&middot;</span>
      <span class="whitespace-nowrap" :title="formatDate(bookmark.created_at)">
        Bookmarked {{ formatDistanceToNow(bookmark.created_at) }} ago
      </span>
      <template v-if="videoHost && bookmark.video?.source_url">
        <span class="font-bold text-gray-400 dark:text-gray-600 hidden sm:inline">&middot;</span>
        <a
          :href="bookmark.video.source_url"
          target="_blank"
          rel="noopener noreferrer"
          class="whitespace-nowrap hover:underline"
          :title="`Visit video source on ${videoHost}`"
        >
          Host: <strong class="text-gray-700 dark:text-gray-300">{{ videoHost }}</strong>
        </a>
      </template>
    </div>

    <!-- Description -->
    <div class="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg mb-6 shadow-sm">
      <h3 class="text-base font-semibold text-gray-800 dark:text-gray-200 mb-1">Description</h3>
      <p v-if="bookmark.description" class="text-gray-700 dark:text-gray-300 whitespace-pre-wrap text-sm">{{ bookmark.description }}</p>
      <p v-else class="text-gray-500 dark:text-gray-400 italic text-sm">No description provided.</p>
    </div>

    <!-- Tags -->
    <div class="mb-2">
      <h3 class="text-base font-semibold text-gray-800 dark:text-gray-200 mb-1">Tags</h3>
      <div v-if="bookmark.tags && bookmark.tags.length > 0" class="flex flex-wrap gap-2">
        <span
          v-for="(tag, idx) in bookmark.tags"
          :key="tag.id || tag.name || tag || idx"
          class="bg-indigo-100 dark:bg-indigo-700 text-indigo-800 dark:text-indigo-100 px-3 py-1 rounded-full text-xs font-medium"
        >
          {{ tag.name || tag }}
        </span>
      </div>
      <p v-else class="text-gray-500 dark:text-gray-400 italic text-xs">No tags for this bookmark.</p>
    </div>
  </div>

  <!-- Collect Modal -->
  <BaseModal v-model="showCollectModal">
    <h2 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Add to Collection</h2>
    <form @submit.prevent="handleCollect">
      <div class="mb-4">
        <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">Collection</label>
        <select v-model="selectedCollection" class="w-full px-3 py-2 border rounded dark:bg-gray-800 dark:text-white">
          <option disabled value="">Select a collection</option>
          <option v-for="col in collections" :key="col.id" :value="col.id">{{ col.name }}</option>
        </select>
      </div>
      <div class="mb-4">
        <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">Channel</label>
        <select v-model="selectedChannel" class="w-full px-3 py-2 border rounded dark:bg-gray-800 dark:text-white" :disabled="!channels.length">
          <option disabled value="">Select a channel</option>
          <option v-for="chan in channels" :key="chan.id" :value="chan.id">{{ chan.name }}</option>
        </select>
      </div>
      <div v-if="collectError" class="text-red-600 text-sm mb-2">{{ collectError }}</div>
      <button
        type="submit"
        class="w-full px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 transition"
        :disabled="collectLoading"
      >
        <span v-if="collectLoading">Adding...</span>
        <span v-else>Add</span>
      </button>
    </form>
  </BaseModal>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { fetchBookmarkDetail } from '@/api/index.js'
import axios from 'axios'
import BaseModal from '@/components/BaseModal.vue'

const route = useRoute()
const loading = ref(true)
const error = ref(null)
const bookmark = ref(null)

const id = computed(() => route.params.id)

async function fetchBookmark() {
  loading.value = true
  error.value = null
  try {
    bookmark.value = await fetchBookmarkDetail(id.value)
  } catch (err) {
    error.value = err?.response?.data || { message: 'Failed to load bookmark details.' }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchBookmark()
})

const showCollectModal = ref(false)
const collections = ref([])
const channels = ref([])
const selectedCollection = ref('')
const selectedChannel = ref('')
const collectLoading = ref(false)
const collectError = ref('')

// Get JWT token from localStorage
function getAuthHeaders() {
  const access = localStorage.getItem('access')
  return access ? { Authorization: `Bearer ${access}` } : {}
}

watch(showCollectModal, async (open) => {
  if (open) {
    collectError.value = ''
    selectedCollection.value = ''
    selectedChannel.value = ''
    channels.value = []
    try {
      const res = await axios.get('/api/collections/', {
        headers: getAuthHeaders()
      })
      collections.value = res.data
    } catch {
      collections.value = []
    }
  }
})

watch(selectedCollection, async (collectionId) => {
  selectedChannel.value = ''
  channels.value = []
  if (collectionId) {
    try {
      const res = await axios.get(`/api/collections/${collectionId}/channels/`, {
        headers: getAuthHeaders()
      })
      channels.value = res.data
    } catch {
      channels.value = []
    }
  }
})

async function handleCollect() {
  collectError.value = ''
  if (!selectedCollection.value) {
    collectError.value = 'Please select a collection.'
    return
  }
  collectLoading.value = true
  try {
    await axios.post('/api/bookmarks/create/', {
      video: bookmark.value.video.id,
      collection: selectedCollection.value,
      channel: selectedChannel.value || null,
      title: bookmark.value.title,
      description: bookmark.value.description,
      tags: bookmark.value.tags?.map(t => t.name || t) || [],
    }, {
      headers: getAuthHeaders()
    })
    showCollectModal.value = false
  } catch (e) {
    collectError.value = e?.response?.data?.detail || 'Failed to add bookmark.'
  } finally {
    collectLoading.value = false
  }
}

const videoHost = computed(() => {
  try {
    return new URL(bookmark.value?.video?.source_url || '').hostname.replace('www.', '')
  } catch {
    return null
  }
})

function formatDate(dateStr) {
  const date = new Date(dateStr)
  return date.toLocaleString()
}
function formatDistanceToNow(dateStr) {
  const now = Date.now()
  const then = new Date(dateStr).getTime()
  const diff = Math.floor((now - then) / 1000)
  if (diff < 60) return `${diff} seconds`
  if (diff < 3600) return `${Math.floor(diff / 60)} minutes`
  if (diff < 86400) return `${Math.floor(diff / 3600)} hours`
  return `${Math.floor(diff / 86400)} days`
}

function orientationClass(orientation) {
  if (orientation === 'landscape') return 'bg-green-100 text-green-800 dark:bg-green-700 dark:text-green-100'
  if (orientation === 'portrait') return 'bg-blue-100 text-blue-800 dark:bg-blue-700 dark:text-blue-100'
  return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-100'
}
function getOrientationLabel(orientation) {
  if (orientation === 'landscape') return 'Landscape'
  if (orientation === 'portrait') return 'Portrait'
  return 'Unknown'
}
</script>

<style scoped>
/* Tailwind handles most styles, keep custom styles minimal */
.whitespace-pre-wrap {
  white-space: pre-wrap;
}

/* Hide scrollbars for carousels */
.hide-scrollbar::-webkit-scrollbar {
  display: none;
}
.hide-scrollbar {
  scrollbar-width: none;
  -ms-overflow-style: none;
}

</style>