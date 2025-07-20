<template>
  <div class="container mx-auto px-4 py-6">
    <h1 class="text-2xl font-semibold mb-6 text-text-main">Add New Bookmark</h1>

    <!-- Step 1: URL Input -->
    <div v-if="!submissionSuccess" class="mb-6">
      <label for="sourceUrl" class="block text-sm font-medium text-text-secondary mb-1">Video URL</label>
      <div class="flex gap-2">
        <input
          id="sourceUrl"
          v-model="sourceUrl"
          type="url"
          placeholder="Enter the URL of the video you want to bookmark..."
          class="w-full px-3 py-2 border border-gray-600 rounded shadow-sm focus:outline-none focus:ring focus:border-primary bg-surface text-text-main placeholder-text-secondary"
          :disabled="isLoading"
        />
        <button
          @click="fetchMetadata"
          :disabled="!sourceUrl || isLoading"
          class="px-4 py-2 bg-primary text-white rounded hover:bg-primary/80 transition disabled:opacity-50"
        >
          <span v-if="!isLoading">Fetch Details</span>
          <span v-else>Fetching...</span>
        </button>
      </div>
      <p v-if="fetchError" class="text-red-400 text-sm mt-1">{{ fetchError }}</p>
    </div>

    <!-- Step 2: Details Form (appears after fetching) -->
    <div v-if="detailsFetched" class="animate-fade-in">
      <!-- Embed URL Selector -->
      <div v-if="embedUrlOptions.length > 1" class="mb-6">
        <label for="embedUrlSelect" class="block text-sm font-medium text-text-secondary mb-1">Multiple embed URLs found. Please select the best one:</label>
        <select
          id="embedUrlSelect"
          v-model="scrapedData.embed_url"
          class="block w-full px-3 py-2 border border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring focus:border-primary bg-surface text-text-main"
        >
          <option v-for="url in embedUrlOptions" :key="url" :value="url">{{ url }}</option>
        </select>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Hide form on success -->
        <BookmarkManual
          v-if="!submissionSuccess"
          :initial-data="scrapedData"
          :use-iframe="useIframe"
          :submission-error="submissionError"
          @update:formData="handleManualFormUpdate"
          @submit="handleSave"
        />
        <!-- Success Message -->
        <div v-if="submissionSuccess" class="bg-surface p-6 rounded shadow flex flex-col items-center justify-center text-center">
            <h2 class="text-2xl font-bold text-green-400 mb-4">Bookmark Saved!</h2>
            <p class="text-text-secondary mb-6">Your video has been successfully added to your collection.</p>
            <div class="flex gap-4">
                <button @click="resetForm" class="px-4 py-2 bg-primary/20 text-primary rounded hover:bg-primary/30 transition">Add Another Bookmark</button>
                <router-link :to="{ name: 'home' }" class="px-4 py-2 bg-surface hover:bg-background text-text-main rounded transition">Go to Homepage</router-link>
            </div>
        </div>

        <BookmarkManualPreview
          :use-iframe="useIframe"
          @update:useIframe="useIframe = $event"
          :videoData="manualFormData.video"
          :bookmarkData="manualFormData.bookmark"
          :tagsArray="manualFormData.tags"
          :channelName="manualFormData.channelName"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { scrapeUrlMetadata, createManualBookmark } from '@/api/index.js';
import BookmarkManual from '@/components/bookmarks/BookmarkManual.vue';
import BookmarkManualPreview from '@/components/bookmarks/BookmarkManualPreview.vue';

const router = useRouter();
const sourceUrl = ref('');
const isLoading = ref(false);
const detailsFetched = ref(false);
const fetchError = ref(null);
const embedUrlOptions = ref([]);
const useIframe = ref(false);

const submissionSuccess = ref(false);
const submissionError = ref(null);

const scrapedData = ref({});
const manualFormData = ref({
  video: {},
  bookmark: {},
  tags: [],
  channelName: ''
});

async function fetchMetadata() {
  isLoading.value = true;
  detailsFetched.value = false;
  fetchError.value = null;
  try {
    const data = await scrapeUrlMetadata(sourceUrl.value);
    embedUrlOptions.value = data.embed_url_options || [];
    scrapedData.value = {
      source_url: sourceUrl.value,
      title: data.title,
      description: data.description,
      thumbnail_url: data.thumbnail_url,
      embed_url: data.embed_url,
      tags: data.tags || [],
    };
    detailsFetched.value = true;
  } catch (e) {
    fetchError.value = e.response?.data?.error || 'Failed to fetch metadata from the URL.';
  } finally {
    isLoading.value = false;
  }
}

function handleManualFormUpdate(newData) {
  manualFormData.value = { ...manualFormData.value, ...newData };
  // Clear error when user starts editing
  if (submissionError.value) {
    submissionError.value = null;
  }
}

async function handleSave(payload) {
  submissionError.value = null;
  try {
    await createManualBookmark(payload);
    submissionSuccess.value = true;
  } catch (e) {
    submissionError.value = e.response?.data?.detail || e.response?.data || 'An unknown error occurred.';
  }
}

function resetForm() {
    submissionSuccess.value = false;
    detailsFetched.value = false;
    sourceUrl.value = '';
    scrapedData.value = {};
    manualFormData.value = { video: {}, bookmark: {}, tags: [], channelName: '' };
}
</script>

<style scoped>
@keyframes fade-in {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fade-in {
  animation: fade-in 0.5s ease-in-out;
}
</style>
