<template>
  <div class="mb-10 lg:mb-0">
    <!-- Step 1: Enter URL -->
    <div class="mb-8">
      <label for="videoUrl" class="block text-sm font-medium text-gray-700 mb-1 dark:text-gray-300">Video URL</label>
      <div class="mt-1 flex rounded-md shadow-sm">
        <input
          type="url"
          id="videoUrl"
          v-model="urlInput"
          placeholder="Enter video URL to extract metadata..."
          :disabled="fetchLoading"
          class="block w-full flex-1 rounded-none rounded-l-md border-gray-300 focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200 dark:placeholder-gray-500"
          @keyup.enter="handleFetchMetadata"
        />
        <button
          @click="handleFetchMetadata"
          :disabled="fetchLoading || !urlInput.trim()"
          type="button"
          class="relative -ml-px inline-flex items-center space-x-2 rounded-r-md border border-gray-300 bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 disabled:opacity-50 disabled:bg-gray-400 dark:border-gray-600 dark:bg-indigo-500 dark:hover:bg-indigo-600"
        >
          <svg v-if="fetchLoading" class="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>{{ fetchLoading ? 'Extracting...' : 'Extract Info' }}</span>
        </button>
      </div>
      <p v-if="fetchError" class="mt-2 text-sm text-red-600 dark:text-red-400">{{ fetchErrorMessage }}</p>
    </div>

    <!-- Step 2: Review Metadata & Save -->
    <div v-if="fetchedData" class="mt-10 bg-white shadow sm:rounded-lg overflow-hidden dark:bg-gray-800 dark:border-gray-700">
      <div class="px-4 py-5 sm:px-6 border-b border-gray-200 dark:border-gray-600">
        <h3 class="text-lg font-medium leading-6 text-gray-900 dark:text-gray-200">Review & Save</h3>
      </div>
      <div class="px-4 py-5 sm:p-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-8">
          <!-- Manual Form Column -->
          <div class="md:col-span-1">
            <BookmarkManual
              :initialVideoData="initialVideoDataForManual"
              :initialBookmarkData="initialBookmarkDataForManual"
              :initialTagsString="initialTagsStringForManual"
              :isEditMode="true"
              @update:formData="handleManualFormUpdate"
              :apiValidationErrors="manualFormApiErrors"
            />
          </div>
          <!-- Preview Column -->
          <div class="md:col-span-1 sticky top-4 h-max">
            <BookmarkManualPreview
              :video-data="currentManualFormData.video"
              :bookmark-data="currentManualFormData.bookmark"
              :tags-array="currentManualFormData.tags"
              :channel-name="currentManualFormData.channelName"
            />
          </div>
        </div>

        <!-- Save Button -->
        <div class="mt-8 pt-5 border-t border-gray-200 dark:border-gray-600">
          <p v-if="saveError" class="text-sm text-red-600 mb-3 dark:text-red-400">{{ saveErrorMessage }}</p>
          <div class="flex justify-end">
            <button
              @click="handleSaveBookmark"
              type="button"
              :disabled="saveLoading || !currentManualFormData.bookmark.channel || !currentManualFormData.video.title || currentManualFormData.tags.length === 0"
              class="inline-flex justify-center rounded-md border border-transparent bg-green-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 dark:bg-green-500 dark:hover:bg-green-600"
            >
              <svg v-if="saveLoading" class="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ saveLoading ? 'Saving...' : 'Save Bookmark' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Success Message -->
    <div v-if="saveSuccess" class="mt-6 rounded-md bg-green-50 p-4 border border-green-200 dark:bg-green-900 dark:border-green-700 dark:text-green-300">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-green-400 dark:text-green-300" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a 1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <p class="text-sm font-medium text-green-800 dark:text-green-300">
            Bookmark saved successfully!
            <router-link v-if="createdBookmarkId" :to="{ name: 'bookmark-detail', params: { id: createdBookmarkId } }" class="font-medium underline text-green-700 hover:text-green-600 dark:text-green-400 dark:hover:text-green-300 ml-2">View Bookmark</router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import api, { extractVideoMetadata, createManualBookmark } from '@/api'
import BookmarkManual from '@/components/bookmarks/BookmarkManual.vue'
import BookmarkManualPreview from '@/components/bookmarks/BookmarkManualPreview.vue'

// Reactive data
const urlInput = ref('')
const fetchLoading = ref(false)
const fetchError = ref(false)
const fetchErrorMessage = ref('')
const fetchedData = ref(null)
const saveLoading = ref(false)
const saveError = ref(false)
const saveErrorMessage = ref('')
const saveSuccess = ref(false)
const createdBookmarkId = ref(null)
const manualFormApiErrors = ref({})

// Manual form data
const currentManualFormData = ref({
  video: {},
  bookmark: {},
  tags: [],
  channelName: ''
})

// Computed properties for manual form initial data
const initialVideoDataForManual = computed(() => {
  if (!fetchedData.value) return {}
  return fetchedData.value.video
})

const initialBookmarkDataForManual = computed(() => {
  if (!fetchedData.value) return {}
  return {
    title: fetchedData.value.video.title || '',
    orientation: fetchedData.value.video.orientation || 'sfw',
    access: 'public'
  }
})

const initialTagsStringForManual = computed(() => {
  if (!fetchedData.value) return ''
  return fetchedData.value.suggested_tags.join(', ')
})

// Methods
async function handleFetchMetadata() {
  if (!urlInput.value.trim()) return
  
  fetchLoading.value = true
  fetchError.value = false
  fetchErrorMessage.value = ''
  fetchedData.value = null
  
  try {
    const response = await extractVideoMetadata(urlInput.value.trim())
    
    fetchedData.value = response
    
    // Initialize manual form data with extracted data
    currentManualFormData.value = {
      video: { ...response.video },
      bookmark: {
        title: response.video.title || '',
        orientation: response.video.orientation || 'sfw',
        access: 'public'
      },
      tags: response.suggested_tags || [],
      channelName: response.channel_name || ''
    }
    
  } catch (error) {
    fetchError.value = true
    if (error.response?.data?.error) {
      fetchErrorMessage.value = error.response.data.error
    } else {
      fetchErrorMessage.value = 'Failed to extract metadata from URL'
    }
    console.error('Metadata extraction error:', error)
  } finally {
    fetchLoading.value = false
  }
}

function handleManualFormUpdate(newData) {
  currentManualFormData.value = { ...currentManualFormData.value, ...newData }
}

async function handleSaveBookmark() {
  if (!currentManualFormData.value.bookmark.channel || 
      !currentManualFormData.value.video.title || 
      currentManualFormData.value.tags.length === 0) {
    return
  }
  
  saveLoading.value = true
  saveError.value = false
  saveErrorMessage.value = ''
  manualFormApiErrors.value = {}
  
  try {
    const payload = {
      video: {
        source_url: currentManualFormData.value.video.source_url || '',
        title: currentManualFormData.value.video.title || '',
        thumbnail_url: currentManualFormData.value.video.thumbnail_url || '',
        embed_url: currentManualFormData.value.video.embed_url || '',
        orientation: currentManualFormData.value.video.orientation || 'sfw',
        tags: currentManualFormData.value.tags // Array of tag names
      },
      bookmark: {
        channel_id: currentManualFormData.value.bookmark.channel, // Use channel_id
        description: currentManualFormData.value.bookmark.description || '',
        access: currentManualFormData.value.bookmark.access || 'public',
        tags: currentManualFormData.value.tags // Array of tag names
      }
    }
    
    console.log('Sending payload:', payload) // Debug log
    
    const response = await createManualBookmark(payload)
    
    saveSuccess.value = true
    createdBookmarkId.value = response.id
    
    // Reset form after successful save
    setTimeout(() => {
      urlInput.value = ''
      fetchedData.value = null
      currentManualFormData.value = {
        video: {},
        bookmark: {},
        tags: [],
        channelName: ''
      }
      saveSuccess.value = false
      createdBookmarkId.value = null
    }, 3000)
    
  } catch (error) {
    saveError.value = true
    
    if (error.response?.data) {
      if (typeof error.response.data === 'string') {
        saveErrorMessage.value = error.response.data
      } else if (error.response.data.error) {
        saveErrorMessage.value = error.response.data.error
      } else {
        // Handle validation errors
        manualFormApiErrors.value = error.response.data
        saveErrorMessage.value = 'Please check the form for errors'
      }
    } else {
      saveErrorMessage.value = 'Failed to save bookmark'
    }
    console.error('Save bookmark error:', error)
  } finally {
    saveLoading.value = false
  }
}
</script>

<style scoped>
/* Add any component-specific styles if needed */
.aspect-video {
    position: relative;
    width: 100%;
    padding-bottom: 56.25%; /* 16:9 */
}
.aspect-video > img,
.aspect-video > div { /* Ensure both img and placeholder div fill the container */
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
}
</style>