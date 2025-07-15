<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
    <h3 class="text-xl font-bold mb-4 text-gray-800 dark:text-gray-200">Lookup & Edit Bookmark/Video</h3>
    <form @submit.prevent="lookupBookmark" class="flex gap-2 mb-4">
      <input v-model="bookmarkId" placeholder="Enter Bookmark ID" class="px-3 py-2 rounded border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-gray-200" />
      <button type="submit" class="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700">Lookup</button>
    </form>
    <div v-if="bookmark" class="mb-6">
      <h4 class="text-lg font-semibold mb-2 text-gray-800 dark:text-gray-200">Bookmark Details</h4>
      <form @submit.prevent="saveBookmark" class="space-y-2">
        <div v-for="(value, key) in bookmark" :key="key" class="flex items-center gap-2">
          <label class="w-32 text-gray-700 dark:text-gray-300">{{ key }}</label>
          <input v-model="bookmark[key]" :disabled="key === 'id'" class="flex-1 px-3 py-2 rounded border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-gray-200" />
        </div>
        <button type="submit" class="px-4 py-2 rounded bg-green-600 text-white hover:bg-green-700">Save</button>
      </form>
    </div>
    <div v-if="video">
      <h4 class="text-lg font-semibold mb-2 text-gray-800 dark:text-gray-200">Video Details</h4>
      <form @submit.prevent="saveVideo" class="space-y-2">
        <div v-for="(value, key) in video" :key="key" class="flex items-center gap-2">
          <label class="w-32 text-gray-700 dark:text-gray-300">{{ key }}</label>
          <input v-model="video[key]" :disabled="key === 'id'" class="flex-1 px-3 py-2 rounded border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-gray-200" />
        </div>
        <button type="submit" class="px-4 py-2 rounded bg-green-600 text-white hover:bg-green-700">Save</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/api/index.js'

const bookmarkId = ref('')
const bookmark = ref(null)
const video = ref(null)

async function lookupBookmark() {
  const res = await api.get(`/moderation/lookup-bookmark/${bookmarkId.value}/`)
  bookmark.value = res.data
  if (bookmark.value.video) {
    const vidRes = await api.get(`/videos/${bookmark.value.video}/`)
    video.value = vidRes.data
  }
}

async function saveBookmark() {
  await api.put('/moderation/edit-bookmark/', { bookmark_id: bookmark.value.id, ...bookmark.value })
  alert('Bookmark updated!')
}

async function saveVideo() {
  await api.put('/moderation/edit-video/', { video_id: video.value.id, ...video.value })
  alert('Video updated!')
}
</script>

<style scoped>
/* No custom styles needed, Tailwind handles all styling */
</style>
