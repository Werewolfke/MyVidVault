<template>
  <div>
    <form @submit.prevent="handleSubmit" class="bg-white dark:bg-gray-800 p-6 rounded shadow space-y-6">
      <div>
        <label class="block mb-1 font-medium text-gray-700 dark:text-gray-200" for="video-source-url">Source URL</label>
        <input class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring focus:border-blue-500 dark:bg-gray-700 dark:text-white" type="url" id="video-source-url" v-model="videoData.source_url" placeholder="https://example.com/video.mp4" required>
      </div>
      <div>
        <label class="block mb-1 font-medium text-gray-700 dark:text-gray-200" for="video-thumbnail-url">Thumbnail URL</label>
        <input class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring focus:border-blue-500 dark:bg-gray-700 dark:text-white" type="url" id="video-thumbnail-url" v-model="videoData.thumbnail_url" placeholder="https://example.com/thumbnail.jpg" required>
      </div>
      <div>
        <label class="block mb-1 font-medium text-gray-700 dark:text-gray-200" for="video-embed-url">Embed URL</label>
        <input class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring focus:border-blue-500 dark:bg-gray-700 dark:text-white" type="url" id="video-embed-url" v-model="videoData.embed_url" placeholder="https://example.com/embed/video" required>
      </div>
      <div>
        <label class="block mb-1 font-medium text-gray-700 dark:text-gray-200" for="video-title">Video Title</label>
        <input class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring focus:border-blue-500 dark:bg-gray-700 dark:text-white" type="text" id="video-title" v-model="videoData.title" placeholder="Title of the video" required>
      </div>
      <div>
        <label class="block mb-1 font-medium text-gray-700 dark:text-gray-200" for="video-orientation">Orientation</label>
        <select class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring focus:border-blue-500 dark:bg-gray-700 dark:text-white" id="video-orientation" v-model="videoData.orientation" required>
          <option :value="null" disabled>-- Select Orientation --</option>
          <option v-for="choice in videoOrientationChoices" :key="choice.value" :value="choice.value">
            {{ choice.label }}
          </option>
        </select>
      </div>
      <div>
        <label class="block mb-1 font-medium text-gray-700 dark:text-gray-200" for="tags">Tags (comma-separated)</label>
        <input class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring focus:border-blue-500 dark:bg-gray-700 dark:text-white" type="text" id="tags" v-model="tagsInput" placeholder="tag1, tag2, another tag">
      </div>
      <div>
        <label class="block mb-1 font-medium text-gray-700 dark:text-gray-200" for="bookmark-collection">Collection</label>
        <select class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring focus:border-blue-500 dark:bg-gray-700 dark:text-white" id="bookmark-collection" v-model="selectedCollectionId" required>
          <option :value="null" disabled>-- Select Collection --</option>
          <option v-for="collection in userCollections" :key="collection.id" :value="collection.id">
            {{ collection.name }}
          </option>
        </select>
      </div>
      <div>
        <label class="block mb-1 font-medium text-gray-700 dark:text-gray-200" for="bookmark-channel">Channel</label>
        <select class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring focus:border-blue-500 dark:bg-gray-700 dark:text-white" id="bookmark-channel" v-model="bookmarkData.channel" required :disabled="!selectedCollectionId">
          <option :value="null" disabled>-- Select Channel --</option>
          <option v-for="channel in userChannels" :key="channel.id" :value="channel.id">
            {{ channel.name }}
          </option>
        </select>
      </div>
      <div>
        <label class="block mb-1 font-medium text-gray-700 dark:text-gray-200" for="bookmark-description">Description</label>
        <textarea class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring focus:border-blue-500 dark:bg-gray-700 dark:text-white" id="bookmark-description" v-model="bookmarkData.description" rows="3"></textarea>
      </div>
      <div>
        <label class="block mb-1 font-medium text-gray-700 dark:text-gray-200" for="bookmark-access">Access</label>
        <select class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring focus:border-blue-500 dark:bg-gray-700 dark:text-white" id="bookmark-access" v-model="bookmarkData.access" required>
          <option v-for="choice in bookmarkAccessChoices" :key="choice.value" :value="choice.value">
            {{ choice.label }}
          </option>
        </select>
      </div>
      <button type="submit" class="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded shadow" :disabled="isSubmitting">
        {{ isSubmitting ? 'Saving...' : 'Save Bookmark & Video' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted, defineEmits } from 'vue'
import axios from 'axios'

const isSubmitting = ref(false)
const userCollections = ref([])
const userChannels = ref([])
const loadingCollections = ref(false)
const loadingChannels = ref(false)
const selectedCollectionId = ref(null)

const videoData = reactive({
  source_url: '',
  title: '',
  thumbnail_url: '',
  embed_url: '',
  orientation: null,
  tags: [],
})

const bookmarkData = reactive({
  channel: null,
  description: '',
  access: null,
})

const tagsInput = ref('')

const videoOrientationChoices = [
  { value: 'landscape', label: 'Landscape' },
  { value: 'portrait', label: 'Portrait' },
  { value: 'square', label: 'Square' },
]

const bookmarkAccessChoices = [
  { value: 'public', label: 'Public' },
  { value: 'private', label: 'Private' },
]

const emit = defineEmits(['update:formData'])

watch(
  [videoData, bookmarkData, tagsInput],
  () => {
    emit('update:formData', {
      video: { ...videoData },
      bookmark: { ...bookmarkData },
      tags: tagsInput.value.split(',').map(t => t.trim()).filter(Boolean),
    })
  },
  { deep: true }
)

onMounted(async () => {
  await fetchCollections()
})

watch(
  selectedCollectionId,
  async (newVal) => {
    if (newVal) {
      await fetchChannels(newVal)
    } else {
      userChannels.value = []
    }
  }
)

async function fetchCollections() {
  loadingCollections.value = true
  try {
    const token = localStorage.getItem('access')
    const response = await axios.get('/api/collections/', {
      headers: { Authorization: `Bearer ${token}` },
    })
    userCollections.value = response.data
  } catch (error) {
    userCollections.value = []
  } finally {
    loadingCollections.value = false
  }
}

async function fetchChannels(collectionId) {
  loadingChannels.value = true
  try {
    const token = localStorage.getItem('access')
    const response = await axios.get(`/api/collections/${collectionId}/channels/`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    userChannels.value = response.data
  } catch (error) {
    userChannels.value = []
  } finally {
    loadingChannels.value = false
  }
}

async function handleSubmit() {
  isSubmitting.value = true

  const payload = {
    video: {
      source_url: videoData.source_url,
      title: videoData.title,
      thumbnail_url: videoData.thumbnail_url,
      embed_url: videoData.embed_url,
      orientation: videoData.orientation,
      tags: tagsInput.value.split(',').map(t => t.trim()).filter(Boolean),
    },
    bookmark: {
      channel_id: bookmarkData.channel,
      description: bookmarkData.description,
      access: bookmarkData.access,
      tags: tagsInput.value.split(',').map(t => t.trim()).filter(Boolean),
    }
  }

  try {
    const token = localStorage.getItem('access')
    await axios.post(
      '/api/bookmarks/manual-create/',
      payload,
      { headers: { Authorization: `Bearer ${token}` } }
    )
    // Optionally reset form or show a message
  } catch (error) {
    // Optionally handle error
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
/* Keep styles for form elements, remove container styles */

h2 { /* Style the new h2 */
  /* text-align: center; */ /* Remove centering */
  /* margin-bottom: 20px; */ /* Adjust as needed */
  /* color: #333; */ /* Use Tailwind */
}

fieldset {
  border: 1px solid #ddd; /* Consider Tailwind borders: border border-gray-300 dark:border-gray-600 */
  padding: 15px; /* Tailwind: p-4 */
  margin-bottom: 20px; /* Tailwind: mb-5 */
  border-radius: 4px; /* Tailwind: rounded */
}

legend {
  font-weight: bold; /* Tailwind: font-semibold */
  color: #555; /* Tailwind: text-gray-700 dark:text-gray-300 */
  padding: 0 5px; /* Tailwind: px-1 */
}

.form-group {
  margin-bottom: 15px; /* Tailwind: mb-4 */
}

label {
  display: block; /* Tailwind: block */
  margin-bottom: 5px; /* Tailwind: mb-1.5 */
  font-weight: 500; /* Tailwind: font-medium */
  color: #444; /* Tailwind: text-gray-700 dark:text-gray-300 */
}

/* Apply Tailwind classes directly in template or use @apply here */
input[type="text"],
input[type="url"],
textarea,
select {
  /* Example using Tailwind classes (apply in template for better practice) */
  /* @apply block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500; */
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
}

textarea {
    resize: vertical;
}

select {
  appearance: none;
  background-color: white; /* Add dark mode bg */
}

small {
    display: block;
    margin-top: 4px; /* Tailwind: mt-1 */
    font-size: 0.85em; /* Tailwind: text-xs */
    color: #666; /* Tailwind: text-gray-500 dark:text-gray-400 */
}

button[type="submit"] {
  /* Example using Tailwind classes */
  /* @apply w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed; */
  display: block;
  width: 100%;
  padding: 12px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1em;
  transition: background-color 0.2s ease;
}

button[type="submit"]:hover:not(:disabled) {
  background-color: #0056b3;
}

button[type="submit"]:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.error-message {
  /* Example using Tailwind classes */
  /* @apply mt-2 text-sm text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/50 border border-red-200 dark:border-red-700/50 rounded p-3 text-center mb-4; */
  color: #dc3545;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
  text-align: center;
  white-space: pre-wrap; /* Allow wrapping for longer messages */
  text-align: left; /* Align text left for better readability */
}

.success-message {
   /* Example using Tailwind classes */
  /* @apply mt-2 text-sm text-green-600 dark:text-green-300 bg-green-50 dark:bg-green-900/50 border border-green-200 dark:border-green-700/50 rounded p-3 text-center mb-4; */
  color: #155724;
  background-color: #d4edda;
  border: 1px solid #c3e6cb;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
  text-align: center;
}

/* Optional: Style for validation errors */
.validation-error {
    color: #dc3545; /* Red color for errors */
    font-size: 0.8em;
    margin-top: 4px;
}

/* Add styles to highlight fields with errors */
input.error, select.error, textarea.error {
    border-color: #dc3545;
}
label.error {
    color: #dc3545;
}
</style>