<template>
  <div class="sticky top-4">
    <div v-if="!hasData" class="text-center py-10 text-gray-500 dark:text-gray-400">
      <p>Fill the form to see a preview.</p>
    </div>
    <div v-else class="max-w-full mx-auto">

      <!-- Video Player/Thumbnail Area -->
      <div class="mb-4 bg-black rounded-lg overflow-hidden shadow-lg">
        <div v-if="videoData.embed_url" class="relative w-full aspect-video">
          <iframe
            :src="videoData.embed_url"
            frameborder="0"
            allow="autoplay; fullscreen; picture-in-picture"
            allowfullscreen
            class="absolute top-0 left-0 w-full h-full"
            title="Video Preview"
          ></iframe>
        </div>
        <div v-else-if="videoData.thumbnail_url" class="relative w-full aspect-video">
           <img
              :src="videoData.thumbnail_url"
              alt="Video Thumbnail Preview"
              class="absolute top-0 left-0 w-full h-full object-contain bg-gray-800"
           >
        </div>
        <div v-else class="relative w-full bg-gray-700 flex items-center justify-center aspect-video">
          <div class="absolute top-0 left-0 w-full h-full flex items-center justify-center text-gray-400">
            No Video Preview Available
          </div>
        </div>
      </div>

      <!-- Separate Thumbnail Preview -->
      <div class="mb-4">
        <h3 class="text-md font-semibold text-gray-800 dark:text-gray-200 mb-2">Thumbnail Preview</h3>
        <div v-if="videoData.thumbnail_url" class="w-full flex justify-center">
          <img
            :src="videoData.thumbnail_url"
            alt="Thumbnail Preview"
            class="max-h-48 rounded shadow border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 object-contain"
            style="max-width: 100%;"
          >
        </div>
        <div v-else class="text-gray-400 italic text-sm text-center">No thumbnail provided.</div>
      </div>

      <!-- Title -->
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-3 break-words overflow-hidden">
        {{ videoData.title || 'Video Title Preview' }}
      </h1>

      <!-- Metadata Row -->
      <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-4 text-sm text-gray-600 dark:text-gray-400 gap-y-2">
        <div class="flex flex-wrap items-center gap-x-3 gap-y-1">
          <span class="whitespace-nowrap">Added by <strong class="italic">You</strong></span>
          <span class="text-gray-400 dark:text-gray-600">|</span>
          <span class="whitespace-nowrap">Channel: <strong>{{ channelName || 'Selected Channel' }}</strong></span>
          <span class="text-gray-400 dark:text-gray-600">|</span>
          <span class="whitespace-nowrap italic">Just now</span>
          <template v-if="videoData.orientation">
            <span class="text-gray-400 dark:text-gray-600">|</span>
            <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium" :class="orientationClass(videoData.orientation)">
              {{ getOrientationLabel(videoData.orientation) }}
            </span>
          </template>
        </div>
         <div class="flex items-center gap-2">
            <span class="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded-md text-gray-700 bg-gray-100 opacity-50 cursor-not-allowed">
                Save
            </span>
            <a
              :href="videoData.source_url || '#'"
              target="_blank"
              rel="noopener noreferrer"
              :class="[
                'inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded-md',
                videoData.source_url
                  ? 'text-blue-700 bg-blue-100 hover:bg-blue-200 dark:bg-blue-900 dark:text-blue-300 dark:hover:bg-blue-800 cursor-pointer'
                  : 'text-gray-700 bg-gray-100 opacity-50 cursor-not-allowed'
              ]"
              :aria-disabled="!videoData.source_url"
              @click.prevent="!videoData.source_url" 
            >
                View Source
            </a>
         </div>
      </div>

      <!-- Description Box -->
      <div class="bg-gray-100 dark:bg-gray-800 p-4 rounded-lg mb-6 shadow-sm">
        <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-2">Description</h3>
        <p v-if="bookmarkData.description" class="text-gray-700 dark:text-gray-300 whitespace-pre-wrap text-sm">{{ bookmarkData.description }}</p>
        <p v-else class="text-gray-500 dark:text-gray-400 italic text-sm">Description preview will appear here.</p>
      </div>

      <!-- Tags Section -->
      <div v-if="safeTagsArray.length > 0" class="mb-6">
        <span class="font-semibold">Tags:</span>
        <span>
          {{ safeTagsArray.join(', ') }}
        </span>
      </div>

    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({
  videoData: { type: Object, default: () => ({}) },
  bookmarkData: { type: Object, default: () => ({}) },
  tagsArray: { type: [Array, String], default: () => [] },
  channelName: { type: String, default: '' }
})

const safeTagsArray = computed(() => {
  if (Array.isArray(props.tagsArray)) return props.tagsArray
  if (typeof props.tagsArray === 'string') {
    return props.tagsArray.split(',').map(t => t.trim()).filter(Boolean)
  }
  return []
})

const hasData = computed(() =>
  props.videoData && (props.videoData.title || props.videoData.source_url || props.videoData.thumbnail_url)
)

function orientationClass(orientation) {
  if (orientation === 'landscape') return 'bg-green-100 text-green-800 dark:bg-green-700 dark:text-green-100'
  if (orientation === 'portrait') return 'bg-blue-100 text-blue-800 dark:bg-blue-700 dark:text-blue-100'
  return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-100'
}
function getOrientationLabel(orientation) {
  if (orientation === 'landscape') return 'Landscape'
  if (orientation === 'portrait') return 'Portrait'
  if (orientation === 'square') return 'Square'
  return 'Unknown'
}
</script>

<style scoped>
.whitespace-pre-wrap {
  white-space: pre-wrap;
}
.aspect-video {
    position: relative;
    width: 100%;
    padding-bottom: 56.25%;
}
.aspect-video > * {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
}
</style>