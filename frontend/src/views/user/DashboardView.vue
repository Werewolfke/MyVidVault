<template>
  <div class="max-w-4xl mx-auto py-8">
    <h1 class="text-2xl font-bold mb-6">Welcome, {{ user?.username }}</h1>
    <div class="mb-8">
      <h2 class="text-lg font-semibold mb-2">Your Stats</h2>
      <ul class="flex flex-wrap gap-6">
        <li>
          <span class="font-bold text-xl">{{ stats.bookmark_count }}</span>
          <span class="block text-gray-500">Bookmarks</span>
        </li>
        <li>
          <span class="font-bold text-xl">{{ stats.likes_count }}</span>
          <span class="block text-gray-500">Likes</span>
        </li>
        <!-- Add more stats as needed -->
      </ul>
    </div>
    <div>
      <h2 class="text-lg font-semibold mb-2">Your Recent Bookmarks</h2>
      <div v-if="loading" class="text-gray-500">Loading...</div>
      <div v-else-if="bookmarks.length === 0" class="text-gray-500">No bookmarks yet.</div>
      <ul v-else class="divide-y divide-gray-200">
        <li v-for="bookmark in bookmarks" :key="bookmark.id" class="py-4 flex items-center">
          <img :src="bookmark.video?.thumbnail_url" alt="" class="w-16 h-10 object-cover rounded mr-4" v-if="bookmark.video?.thumbnail_url" />
          <router-link :to="{ name: 'bookmark-detail', params: { id: bookmark.id } }" class="font-medium text-blue-600 hover:underline">
            {{ bookmark.title }}
          </router-link>
          <span class="ml-auto text-xs text-gray-400">{{ formatDate(bookmark.created_at) }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { fetchMyDashboard } from '@/api/index.js'

const router = useRouter()
const user = ref(null)
const stats = ref({ bookmark_count: 0, likes_count: 0 })
const bookmarks = ref([])
const loading = ref(true)

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString()
}

onMounted(async () => {
  loading.value = true
  try {
    const data = await fetchMyDashboard()
    user.value = data.user
    stats.value = data.stats
    bookmarks.value = data.bookmarks
  } catch (e) {
    // If not logged in, redirect to login
    router.push({ name: 'login', query: { redirect: '/dashboard' } })
  } finally {
    loading.value = false
  }
})
</script>