<template>
  <!-- Skeleton Loader -->
  <div v-if="loading" class="animate-pulse">
    <div class="rounded-2xl bg-white/80 shadow-xl border border-gray-200/60 p-6 dark:bg-gray-800 dark:border-gray-700">
      <div class="mb-4 bg-gray-300 rounded-lg aspect-video dark:bg-gray-700"></div>
      <div class="h-8 bg-gray-300 rounded w-3/4 mb-3 dark:bg-gray-700"></div>
      <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-6 gap-y-3">
        <div class="flex flex-wrap items-center gap-x-4 gap-y-1">
          <div class="h-5 bg-gray-300 rounded w-16 dark:bg-gray-700"></div>
          <div class="h-5 bg-gray-300 rounded w-24 dark:bg-gray-700"></div>
        </div>
        <div class="flex items-center flex-wrap gap-2">
          <div class="h-7 bg-gray-300 rounded w-16 dark:bg-gray-700"></div>
        </div>
      </div>
      <div class="bg-gray-200 p-4 rounded-lg mb-6 dark:bg-gray-700">
        <div class="h-5 bg-gray-300 rounded w-32 mb-3 dark:bg-gray-700"></div>
        <div class="space-y-2">
          <div class="h-4 bg-gray-300 rounded dark:bg-gray-700"></div>
          <div class="h-4 bg-gray-300 rounded w-5/6 dark:bg-gray-700"></div>
        </div>
      </div>
    </div>
  </div>

  <!-- Error State -->
  <div v-else-if="error" class="rounded-2xl bg-white/80 shadow-xl border border-gray-200/60 p-8 text-center dark:bg-gray-800 dark:border-gray-700">
    <p class="font-medium text-red-600 dark:text-red-400">Error Loading Bookmark</p>
    <p class="text-sm text-gray-600 dark:text-gray-400">{{ error.message || 'Failed to load bookmark details. It might have been deleted or the link is incorrect.' }}</p>
    <router-link :to="{ name: 'home' }" class="mt-4 inline-block px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 dark:bg-indigo-500 dark:hover:bg-indigo-600">
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
        class="w-10 h-10 rounded-full object-cover border border-blue-100 dark:border-blue-400"
      >
      <div>
        <div class="flex items-center gap-2">
          <router-link
            v-if="bookmark.user?.username"
            :to="{ name: 'user-profile', params: { username: bookmark.user.username } }"
            class="font-semibold text-gray-900 text-base hover:underline dark:text-gray-200"
          >
            {{ bookmark.user.username }}
          </router-link>
          <span v-else class="font-semibold text-gray-900 text-base dark:text-gray-200">Unknown User</span>
        </div>
        <p v-if="bookmark.user?.bio" class="text-gray-600 text-xs mt-0.5 dark:text-gray-400">{{ bookmark.user.bio }}</p>
      </div>
    </div>

    <!-- Video Player/Thumbnail -->
    <div class="relative mb-4 bg-black rounded-lg overflow-hidden shadow-lg">
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

    <!-- Icon Section -->
    <div class="absolute bottom-0 right-0 bg-gray-800 rounded-lg shadow-lg p-2 flex gap-2 justify-end m-2 w-auto">
      <!-- Add Icon -->
      <button
        class="text-white hover:text-indigo-400 transition"
        @click="showCollectModal = true"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
        </svg>
      </button>

      <!-- Like Icon -->
      <button
        class="text-white hover:text-red-400 transition"
        @click="toggleLike"
      >
        <svg
          :class="isLiked ? 'text-red-400' : 'text-white'"
          class="w-5 h-5"
          fill="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            v-if="isLiked"
            d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"
          />
          <path
            v-else
            d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"
          />
        </svg>
      </button>

      <!-- Report Icon -->
      <button
        class="text-white hover:text-yellow-400 transition"
        @click="reportBookmark"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M10.29 3.71a1 1 0 011.42 0l8.58 8.59a1 1 0 010 1.42l-8.58 8.59a1 1 0 01-1.42 0l-8.58-8.59a1 1 0 010-1.42l8.58-8.59z" />
          <line x1="12" y1="8" x2="12" y2="12" stroke-linecap="round" stroke-linejoin="round" />
          <circle cx="12" cy="16" r="0.5" fill="currentColor" />
        </svg>
      </button>

      <!-- View Users Icon -->
      <button
        class="text-white hover:text-blue-400 transition"
        @click="showUsersModal = true"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4a4 4 0 110 8 4 4 0 010-8zm0 10c-4 0-8 2-8 6v2h16v-2c0-4-4-6-8-6z"/>
        </svg>
      </button>
    </div>

    <!-- Title -->
    <h1 class="text-xl md:text-2xl font-bold text-gray-900 mb-2 break-words dark:text-gray-200">{{ bookmark.title }}</h1>

    <!-- Metadata -->
    <div class="flex flex-wrap items-center text-xs text-gray-600 gap-x-3 gap-y-1 mb-4 dark:text-gray-400">
      <span v-if="bookmark.video" class="whitespace-nowrap">
        {{ bookmark.video.likes_count ?? 0 }} likes
      </span>
      <span v-if="bookmark.video" class="font-bold text-gray-400">&middot;</span>
      <span class="whitespace-nowrap" :title="formatDate(bookmark.created_at)">
        Bookmarked {{ formatDistanceToNow(bookmark.created_at) }} ago
      </span>
      <template v-if="videoHost && bookmark.video?.source_url">
        <span class="font-bold text-gray-400 hidden sm:inline">&middot;</span>
        <a
          :href="bookmark.video.source_url"
          target="_blank"
          rel="noopener noreferrer"
          class="whitespace-nowrap hover:underline dark:text-blue-400"
          :title="`Visit video source on ${videoHost}`"
        >
          Host: <strong class="text-gray-700 dark:text-gray-300">{{ videoHost }}</strong>
        </a>
      </template>
    </div>

    <!-- Description -->
    <div class="bg-gray-50 p-4 rounded-lg mb-6 shadow-sm dark:bg-gray-800">
      <h3 class="text-base font-semibold text-gray-800 mb-1 dark:text-gray-200">Description</h3>
      <p v-if="bookmark.description" class="text-gray-700 whitespace-pre-wrap text-sm dark:text-gray-300">{{ bookmark.description }}</p>
      <p v-else class="text-gray-500 italic text-sm dark:text-gray-400">No description provided.</p>
    </div>

    <!-- Tags -->
    <div class="mb-2">
      <h3 class="text-base font-semibold text-gray-800 mb-1 dark:text-gray-200">Tags</h3>
      <div v-if="bookmark.tags && bookmark.tags.length > 0" class="flex flex-wrap gap-2">
        <router-link
          v-for="(tag, idx) in bookmark.tags"
          :key="tag.id || tag.name || tag || idx"
          :to="{ name: 'home', query: { tag: tag.name || tag } }"
          class="bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-xs font-medium hover:bg-indigo-200 transition dark:bg-indigo-900 dark:text-indigo-300 dark:hover:bg-indigo-800"
        >
          {{ tag.name || tag }}
        </router-link>
      </div>
      <p v-else class="text-gray-500 italic text-xs dark:text-gray-400">No tags for this bookmark.</p>
    </div>

  </div>

  <!-- Collect Modal -->
  <BaseModal v-model="showCollectModal">
    <h2 class="text-lg font-semibold mb-4 text-gray-900 ">Add to Collection</h2>
    <form @submit.prevent="handleCollect">
      <div class="mb-4">
        <label class="block mb-1 text-sm font-medium text-gray-700 ">Collection</label>
        <select v-model="selectedCollection" class="w-full px-3 py-2 border rounded  ">
          <option disabled value="">Select a collection</option>
          <option v-for="col in collections" :key="col.id" :value="col.id">{{ col.name }}</option>
        </select>
      </div>
      <div class="mb-4">
        <label class="block mb-1 text-sm font-medium text-gray-700 ">Channel</label>
        <select v-model="selectedChannel" class="w-full px-3 py-2 border rounded  " :disabled="!channels.length">
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

  <!-- Users Modal -->
  <BaseModal v-model="showUsersModal">
    <h2 class="text-lg font-semibold mb-4 text-gray-900">Users Who Bookmarked This Video</h2>
    <div v-if="usersLoading" class="text-center text-gray-500">Loading...</div>
    <div v-else-if="usersError" class="text-center text-red-500">{{ usersError }}</div>
    <ul v-else class="space-y-2">
      <li v-for="user in users" :key="user.id" class="flex items-center gap-3">
        <img :src="user.avatar_url || '/media/default.jpg'" alt="User Avatar" class="w-8 h-8 rounded-full object-cover">
        <router-link :to="{ name: 'user-profile', params: { username: user.username } }" class="text-gray-800 hover:underline">
          {{ user.username }}
        </router-link>
        <button
          v-if="user.id !== currentUserId"
          @click="toggleFollow(user.id)"
          :class="user.is_followed ? 'bg-red-500 hover:bg-red-600' : 'bg-indigo-500 hover:bg-indigo-600'"
          class="px-3 py-1 text-white rounded text-sm transition"
        >
          {{ user.is_followed ? 'Unfollow' : 'Follow' }}
        </button>
      </li>
    </ul>
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
const isLiked = ref(false)
const currentUserId = ref(null)

const id = computed(() => route.params.id)

async function fetchBookmark() {
  loading.value = true
  error.value = null
  try {
    const data = await fetchBookmarkDetail(id.value)
    bookmark.value = data

    // Fetch "liked" status only if the user is logged in
    const access = localStorage.getItem('access')
    if (access) {
      const response = await axios.get(`/api/videos/${bookmark.value.video.id}/like-status/`, {
        headers: { Authorization: `Bearer ${access}` }
      })
      isLiked.value = response.data.is_liked

      const userRes = await axios.get('/api/profile/me/', {
        headers: { Authorization: `Bearer ${access}` }
      })
      currentUserId.value = userRes.data.id
    }
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

const showUsersModal = ref(false)
const users = ref([])
const usersLoading = ref(false)
const usersError = ref(null)

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

watch(showUsersModal, async (open) => {
  if (open) {
    usersLoading.value = true
    usersError.value = null
    try {
      const response = await axios.get(`/api/videos/${bookmark.value.video.id}/users-bookmarked/`, {
        headers: getAuthHeaders()
      })
      users.value = response.data
    } catch (err) {
      usersError.value = 'Failed to load users.'
    } finally {
      usersLoading.value = false
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
  if (orientation === 'landscape') return 'bg-green-100 text-green-800  '
  if (orientation === 'portrait') return 'bg-blue-100 text-blue-800  '
  return 'bg-gray-100 text-gray-800  '
}
function getOrientationLabel(orientation) {
  if (orientation === 'landscape') return 'Landscape'
  if (orientation === 'portrait') return 'Portrait'
  return 'Unknown'
}

async function toggleLike() {
  try {
    const access = localStorage.getItem('access')
    await axios.post(
      `/api/videos/${bookmark.value.video.id}/like/`,
      {},
      { headers: { Authorization: `Bearer ${access}` } }
    )
    const response = await axios.get(`/api/videos/${bookmark.value.video.id}/like-status/`, {
      headers: getAuthHeaders()
    })
    isLiked.value = response.data.is_liked // Update "liked" status after toggling
  } catch (err) {
    console.error('Failed to toggle like:', err)
  }
}

// Get JWT token from localStorage
function getAuthHeaders() {
  const access = localStorage.getItem('access')
  return access ? { Authorization: `Bearer ${access}` } : {}
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