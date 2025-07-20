<template>
  <!-- Skeleton Loader -->
  <div v-if="loading" class="animate-pulse">
    <div class="p-6">
      <div class="mb-4 bg-surface rounded-lg aspect-video"></div>
      <div class="h-8 bg-surface rounded w-3/4 mb-3"></div>
      <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-6 gap-y-3">
        <div class="flex flex-wrap items-center gap-x-4 gap-y-1">
          <div class="h-5 bg-surface rounded w-16"></div>
          <div class="h-5 bg-surface rounded w-24"></div>
        </div>
      </div>
    </div>
  </div>

  <!-- Error State -->
  <div v-else-if="error" class="p-8 text-center">
    <p class="font-medium text-red-400">Error Loading Bookmark</p>
    <p class="text-sm text-text-secondary">{{ error.message || 'Failed to load bookmark details.' }}</p>
    <router-link :to="{ name: 'home' }" class="mt-4 inline-block px-4 py-2 text-sm font-medium rounded-md text-white bg-primary hover:bg-primary/80">
      Go back home
    </router-link>
  </div>

  <!-- Bookmark Content -->
  <div v-else-if="bookmark">
    <!-- User & Channel -->
    <div class="flex items-center gap-3 mb-6 relative">
      <img :src="bookmark.user?.avatar_url || '/media/default.jpg'" alt="User Avatar" class="w-10 h-10 rounded-full object-cover border border-primary/20" />
      <div>
        <div class="flex items-center gap-2">
          <router-link v-if="bookmark.user?.username" :to="{ name: 'user-profile', params: { username: bookmark.user.username } }" class="font-semibold text-text-main text-base hover:underline">
            {{ bookmark.user.username }}
          </router-link>
          <span v-else class="font-semibold text-text-main text-base">Unknown User</span>
        </div>
        <p v-if="bookmark.user?.bio" class="text-text-secondary text-xs mt-0.5">{{ bookmark.user.bio }}</p>
      </div>
    </div>

    <!-- Video Player/Thumbnail -->
    <div class="mb-4">
      <div v-if="bookmark.video && bookmark.video.embed_url" class="flex justify-end mb-2">
        <button @click="useIframe = !useIframe" class="px-2 py-1 text-xs bg-surface hover:bg-background text-text-secondary rounded">
          Switch to {{ useIframe ? 'Direct Player' : 'Iframe Player' }}
        </button>
      </div>
      <div class="relative bg-black rounded-lg overflow-hidden shadow-lg">
        <div v-if="bookmark.video && bookmark.video.embed_url" class="relative w-full aspect-video">
          <video v-if="!useIframe" ref="videoPlayer" controls autoplay muted playsinline class="absolute top-0 left-0 w-full h-full" title="Video Player"></video>
          <iframe v-if="useIframe" :src="bookmark.video.embed_url" frameborder="0" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen class="absolute top-0 left-0 w-full h-full" title="Video Player"></iframe>
        </div>
        <div v-else-if="bookmark.video && bookmark.video.thumbnail_url" class="relative w-full aspect-video">
          <img :src="bookmark.video.thumbnail_url" alt="Video Thumbnail" class="absolute top-0 left-0 w-full h-full object-contain bg-background" />
        </div>
        <div v-else class="relative w-full bg-surface flex items-center justify-center aspect-video">
          <div class="absolute top-0 left-0 w-full h-full flex items-center justify-center text-text-secondary">
            No Video Preview Available
          </div>
        </div>
      </div>
    </div>

    <!-- Title -->
    <h1 class="text-xl md:text-2xl font-bold text-text-main mb-2 break-words">{{ bookmark.title }}</h1>

    <!-- Metadata -->
    <div class="flex flex-wrap items-center text-xs text-text-secondary gap-x-3 gap-y-1 mb-4">
      <span v-if="bookmark.video" class="whitespace-nowrap">{{ bookmark.video.likes_count ?? 0 }} likes</span>
      <span v-if="bookmark.video" class="font-bold text-gray-600">&middot;</span>
      <span class="whitespace-nowrap" :title="formatDate(bookmark.created_at)">Bookmarked {{ formatDistanceToNow(bookmark.created_at) }} ago</span>
      <template v-if="videoHost && bookmark.video?.source_url">
        <span class="font-bold text-gray-600 hidden sm:inline">&middot;</span>
        <a :href="bookmark.video.source_url" target="_blank" rel="noopener noreferrer" class="whitespace-nowrap hover:underline text-primary/80" :title="`Visit video source on ${videoHost}`">
          Host: <strong class="text-text-secondary">{{ videoHost }}</strong>
        </a>
      </template>
    </div>

    <!-- Description -->
    <div class="bg-surface p-4 rounded-lg mb-6 shadow-sm">
      <h3 class="text-base font-semibold text-text-main mb-1">Description</h3>
      <p v-if="bookmark.description" class="text-text-main whitespace-pre-wrap text-sm">{{ bookmark.description }}</p>
      <p v-else class="text-text-secondary italic text-sm">No description provided.</p>
    </div>

    <!-- Tags -->
    <div class="mb-2">
      <h3 class="text-base font-semibold text-text-main mb-1">Tags</h3>
      <div v-if="bookmark.tags && bookmark.tags.length > 0" class="flex flex-wrap gap-2">
        <router-link v-for="tag in bookmark.tags" :key="tag.name || tag" :to="{ name: 'home', query: { tag: tag.name || tag } }" class="bg-primary/10 text-primary px-3 py-1 rounded-full text-xs font-medium hover:bg-primary/20 transition">
          {{ tag.name || tag }}
        </router-link>
      </div>
      <p v-else class="text-text-secondary italic text-xs">No tags for this bookmark.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { fetchBookmarkDetail } from '@/api/index.js'
import { apiClient } from '@/api/index.js'
import Hls from 'hls.js'
import BaseModal from '@/components/BaseModal.vue'

const route = useRoute()
const loading = ref(true)
const error = ref(null)
const bookmark = ref(null)
const isLiked = ref(false)
const currentUserId = ref(null)
const useIframe = ref(false)
const videoPlayer = ref(null)
let hls = null

const id = computed(() => route.params.id)

async function fetchBookmark() {
  loading.value = true
  error.value = null
  try {
    const data = await fetchBookmarkDetail(id.value)
    bookmark.value = data
    useIframe.value = data.video?.player_type === 'iframe'

    if (localStorage.getItem('access')) {
      const likeStatusRes = await apiClient.get(`/videos/${bookmark.value.video.id}/like-status/`)
      isLiked.value = likeStatusRes.data.is_liked
      const userRes = await apiClient.get('/profile/me/')
      currentUserId.value = userRes.data.id
    }
  } catch (err) {
    error.value = err?.response?.data || { message: 'Failed to load bookmark details.' }
  } finally {
    loading.value = false
  }
}

onMounted(fetchBookmark)

const videoHost = computed(() => {
  try {
    return new URL(bookmark.value?.video?.source_url || '').hostname.replace('www.', '')
  } catch { return null }
})

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleString()
}

function formatDistanceToNow(dateStr) {
  const diff = Math.floor((Date.now() - new Date(dateStr).getTime()) / 1000)
  if (diff < 60) return `${diff}s`
  if (diff < 3600) return `${Math.floor(diff / 60)}m`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h`
  return `${Math.floor(diff / 86400)}d`
}

watch([() => bookmark.value?.video?.embed_url, videoPlayer, useIframe], ([newUrl, player, iframeMode]) => {
  if (hls) {
    hls.destroy()
    hls = null
  }
  if (player && newUrl && !iframeMode) {
    if (newUrl.includes('.m3u8') && Hls.isSupported()) {
      hls = new Hls()
      hls.loadSource(newUrl)
      hls.attachMedia(player)
      player.play().catch(() => {})
    } else {
      player.src = newUrl
    }
  }
})

onUnmounted(() => {
  if (hls) {
    hls.destroy()
  }
})
</script>

<style scoped>
.whitespace-pre-wrap {
  white-space: pre-wrap;
}
</style>
