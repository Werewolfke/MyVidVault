<template>
  <div class="sticky top-4">
    <div v-if="!hasData" class="text-center py-10 text-gray-500 dark:text-gray-400">
      <p>Fill the form to see a preview.</p>
    </div>
    <div v-else class="max-w-full mx-auto">

      <!-- Video Player/Thumbnail Area -->
      <div class="mb-4">
        <!-- Player Toggle -->
        <div v-if="videoData.embed_url" class="flex justify-end mb-2">
          <button @click="$emit('update:useIframe', !props.useIframe)" class="px-2 py-1 text-xs bg-surface hover:bg-background text-text-secondary rounded">
            Switch to {{ props.useIframe ? 'Direct Player' : 'Iframe Player' }}
          </button>
        </div>
        <div class="bg-black rounded-lg overflow-hidden shadow-lg">
          <div v-if="videoData.embed_url" class="relative w-full aspect-video">
            <!-- User-Controlled Player -->
            <video
              v-if="!useIframe"
              ref="videoPlayer"
              controls
              autoplay
              muted
              playsinline
              class="absolute top-0 left-0 w-full h-full"
              title="Video Preview"
            ></video>
            <iframe
              v-if="useIframe"
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
              class="absolute top-0 left-0 w-full h-full object-contain bg-gray-800 dark:bg-gray-700"
            />
          </div>
          <div v-else class="relative w-full bg-gray-700 flex items-center justify-center aspect-video dark:bg-gray-800">
            <div class="absolute top-0 left-0 w-full h-full flex items-center justify-center text-gray-400 dark:text-gray-500">
              No Video Preview Available
            </div>
          </div>
        </div>
      </div>

      <!-- Separate Thumbnail Preview -->
      <div class="mb-4">
        <h3 class="text-md font-semibold text-text-main mb-2">Thumbnail Preview</h3>
        <div v-if="videoData.thumbnail_url" class="w-full flex justify-center">
          <img
            :src="videoData.thumbnail_url"
            alt="Thumbnail Preview"
            class="max-h-48 rounded shadow border border-gray-600 bg-surface object-contain"
            style="max-width: 100%;"
          />
        </div>
        <div v-else class="text-text-secondary italic text-sm text-center">No thumbnail provided.</div>
      </div>

      <!-- Title -->
      <h1 class="text-2xl font-bold text-text-main mb-3 break-words overflow-hidden">
        {{ videoData.title || 'Video Title Preview' }}
      </h1>

      <!-- Metadata Row -->
      <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-4 text-sm text-text-secondary gap-y-2">
        <div class="flex flex-wrap items-center gap-x-3 gap-y-1">
          <span class="whitespace-nowrap">Added by <strong class="italic text-text-main">You</strong></span>
          <span class="text-gray-500">|</span>
          <span class="whitespace-nowrap">Channel: <strong class="text-text-main">{{ channelName || 'Selected Channel' }}</strong></span>
          <span class="text-gray-500">|</span>
          <span class="whitespace-nowrap italic">Just now</span>
          <template v-if="videoData.orientation">
            <span class="text-gray-500">|</span>
            <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-primary/10 text-primary">
              {{ videoData.orientation }}
            </span>
          </template>
        </div>
        <div class="flex items-center gap-2">
          <span class="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded-md text-text-secondary bg-surface opacity-50 cursor-not-allowed">
            Save
          </span>
          <a
            :href="videoData.source_url || '#'"
            target="_blank"
            rel="noopener noreferrer"
            :class="[
              'inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded-md',
              videoData.source_url
                ? 'text-primary bg-primary/10 hover:bg-primary/20 cursor-pointer'
                : 'text-text-secondary bg-surface opacity-50 cursor-not-allowed'
            ]"
            :aria-disabled="!videoData.source_url"
            @click.prevent="!videoData.source_url"
          >
            View Source
          </a>
        </div>
      </div>

      <!-- Description Box -->
      <div class="bg-surface p-4 rounded-lg mb-6 shadow-sm">
        <h3 class="text-lg font-semibold text-text-main mb-2">Description</h3>
        <p v-if="bookmarkData.description" class="text-text-main whitespace-pre-wrap text-sm">
          {{ bookmarkData.description }}
        </p>
        <p v-else class="text-text-secondary italic text-sm">Description preview will appear here.</p>
      </div>

      <!-- Tags Section -->
      <div v-if="safeTagsArray.length > 0" class="mb-6">
        <span class="font-semibold text-text-main">Tags:</span>
        <span class="text-text-secondary">
          {{ safeTagsArray.join(', ') }}
        </span>
      </div>

    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch, onUnmounted } from 'vue'
import Hls from 'hls.js'

const props = defineProps({
  videoData: { type: Object, default: () => ({}) },
  bookmarkData: { type: Object, default: () => ({}) },
  tagsArray: { type: [Array, String], default: () => [] },
  channelName: { type: String, default: '' },
  useIframe: { type: Boolean, default: false }
})

const emit = defineEmits(['update:useIframe'])

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

const videoPlayer = ref(null)
let hls = null

// This watcher now also depends on the toggle
watch([() => props.videoData.embed_url, videoPlayer, () => props.useIframe], ([newUrl, player, iframeMode]) => {
  if (hls) {
    hls.destroy();
    hls = null;
  }

  // Only initialize the player if we are in the correct mode and the element is ready
  if (player && newUrl && !iframeMode) {
    if (newUrl.includes('.m3u8') && Hls.isSupported()) {
      hls = new Hls();
      hls.loadSource(newUrl);
      hls.attachMedia(player);
      player.play().catch(() => {});
    } else {
      player.src = newUrl;
    }
  }
});

onUnmounted(() => {
  if (hls) {
    hls.destroy();
  }
});
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
