<template>
  <div>
    <form @submit.prevent="handleSubmit" class="bg-white p-6 rounded shadow space-y-6 dark:bg-gray-800 dark:border-gray-700">
      <div>
        <label class="block mb-1 font-medium text-gray-700 dark:text-gray-300" for="video-source-url">Source URL</label>
        <input
          class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring focus:border-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200 dark:placeholder-gray-500"
          type="url"
          id="video-source-url"
          v-model="videoData.source_url"
          placeholder="https://example.com/video.mp4"
          required
        />
      </div>
      <div>
        <label class="block mb-1 font-medium text-gray-700 dark:text-gray-300" for="video-thumbnail-url">Thumbnail URL</label>
        <input
          class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring focus:border-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200 dark:placeholder-gray-500"
          type="url"
          id="video-thumbnail-url"
          v-model="videoData.thumbnail_url"
          placeholder="https://example.com/thumbnail.jpg"
          required
        />
      </div>
      <div>
        <label class="block mb-1 font-medium text-gray-700 dark:text-gray-300" for="video-embed-url">Embed URL</label>
        <input
          class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring focus:border-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200 dark:placeholder-gray-500"
          type="url"
          id="video-embed-url"
          v-model="videoData.embed_url"
          placeholder="https://example.com/embed/video"
          required
        />
      </div>
      <div>
        <label class="block mb-1 font-medium text-gray-700 dark:text-gray-300" for="video-title">Video Title</label>
        <input
          class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring focus:border-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200 dark:placeholder-gray-500"
          type="text"
          id="video-title"
          v-model="videoData.title"
          placeholder="Title of the video"
          required
        />
      </div>
      <div>
        <label class="block mb-1 font-medium text-gray-700 dark:text-gray-300" for="video-orientation">Orientation</label>
        <select
          class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring focus:border-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200"
          id="video-orientation"
          v-model="videoData.orientation"
          required
        >
          <option :value="null" disabled>-- Select Orientation --</option>
          <option v-for="choice in videoOrientationChoices" :key="choice.value" :value="choice.value">
            {{ choice.label }}
          </option>
        </select>
      </div>
      <div>
        <label class="block mb-1 font-medium text-gray-700 dark:text-gray-300" for="tags">Tags (comma-separated)</label>
        <input
          class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring focus:border-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200 dark:placeholder-gray-500"
          type="text"
          id="tags"
          v-model="tagsInput"
          placeholder="tag1, tag2, another tag"
        />
      </div>
      <div>
        <label class="block mb-1 font-medium text-gray-700 dark:text-gray-300" for="bookmark-collection">Collection</label>
        <select
          class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring focus:border-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200"
          id="bookmark-collection"
          v-model="selectedCollectionId"
          required
        >
          <option :value="null" disabled>-- Select Collection --</option>
          <option v-for="collection in userCollections" :key="collection.id" :value="collection.id">
            {{ collection.name }}
          </option>
        </select>
      </div>
      <div>
        <label class="block mb-1 font-medium text-gray-700 dark:text-gray-300" for="bookmark-channel">Channel</label>
        <select
          class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring focus:border-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200"
          id="bookmark-channel"
          v-model="bookmarkData.channel"
          required
          :disabled="!selectedCollectionId"
        >
          <option :value="null" disabled>-- Select Channel --</option>
          <option v-for="channel in userChannels" :key="channel.id" :value="channel.id">
            {{ channel.name }}
          </option>
        </select>
      </div>
      <div>
        <label class="block mb-1 font-medium text-gray-700 dark:text-gray-300" for="bookmark-description">Description</label>
        <textarea
          class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring focus:border-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200"
          id="bookmark-description"
          v-model="bookmarkData.description"
          rows="3"
        ></textarea>
      </div>
      <div>
        <label class="block mb-1 font-medium text-gray-700 dark:text-gray-300" for="bookmark-access">Access</label>
        <select
          class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring focus:border-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200"
          id="bookmark-access"
          v-model="bookmarkData.access"
          required
        >
          <option v-for="choice in bookmarkAccessChoices" :key="choice.value" :value="choice.value">
            {{ choice.label }}
          </option>
        </select>
      </div>
      <button
        v-if="!isEditMode"
        type="submit"
        class="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded shadow disabled:opacity-50 dark:bg-blue-500 dark:hover:bg-blue-600"
        :disabled="isSubmitting"
      >
        {{ isSubmitting ? 'Saving...' : 'Save Bookmark & Video' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted, defineEmits, defineProps } from 'vue'
import axios from 'axios'

// Define props for initial data
const props = defineProps({
  initialVideoData: { type: Object, default: () => ({}) },
  initialBookmarkData: { type: Object, default: () => ({}) },
  initialTagsString: { type: String, default: '' },
  isEditMode: { type: Boolean, default: false },
  apiValidationErrors: { type: Object, default: () => ({}) }
})

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
  access: 'public', // Set default value
})

const tagsInput = ref('')

const videoOrientationChoices = [
  { value: 'straight', label: 'Straight' },
  { value: 'gay', label: 'Gay' },
  { value: 'bi', label: 'Bi' },
  { value: 'trans', label: 'Trans' },
  { value: 'sfw', label: 'SFW' },
]

const bookmarkAccessChoices = [
  { value: 'public', label: 'Public' },
  { value: 'private', label: 'Private' },
]

const emit = defineEmits(['update:formData'])

// Function to populate form with initial data
function populateForm() {
  // Populate video data
  if (props.initialVideoData) {
    Object.assign(videoData, {
      source_url: props.initialVideoData.source_url || '',
      title: props.initialVideoData.title || '',
      thumbnail_url: props.initialVideoData.thumbnail_url || '',
      embed_url: props.initialVideoData.embed_url || '',
      orientation: props.initialVideoData.orientation || null,
    })
  }
  
  // Populate bookmark data
  if (props.initialBookmarkData) {
    Object.assign(bookmarkData, {
      channel: props.initialBookmarkData.channel || null,
      description: props.initialBookmarkData.description || '',
      access: props.initialBookmarkData.access || 'public',
    })
  }
  
  // Populate tags
  if (props.initialTagsString) {
    tagsInput.value = props.initialTagsString
  }
  
  // Get channel name for preview
  emitFormData()
}

function emitFormData() {
  const selectedChannel = userChannels.value.find(channel => channel.id === bookmarkData.channel)
  emit('update:formData', {
    video: { ...videoData },
    bookmark: { ...bookmarkData },
    tags: tagsInput.value.split(',').map(t => t.trim()).filter(Boolean),
    channelName: selectedChannel ? selectedChannel.name : ''
  })
}

watch(
  [videoData, bookmarkData, tagsInput],
  () => {
    emitFormData()
  },
  { deep: true }
)

// Watch for changes in userChannels to update form data with channel name
watch(
  userChannels,
  () => {
    emitFormData()
  },
  { deep: true }
)

// Watch for props changes and repopulate form
watch(
  () => [props.initialVideoData, props.initialBookmarkData, props.initialTagsString],
  () => {
    populateForm()
  },
  { deep: true, immediate: true }
)

onMounted(async () => {
  await fetchCollections()
  populateForm() // Populate after collections are loaded
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

fieldset {
  border: 1px solid #ddd; /* Consider Tailwind borders: border border-gray-300  */
  padding: 15px; /* Tailwind: p-4 */
  margin-bottom: 20px; /* Tailwind: mb-5 */
  border-radius: 4px; /* Tailwind: rounded */
}

legend {
  font-weight: bold; /* Tailwind: font-semibold */
  color: #555; /* Tailwind: text-gray-700  */
  padding: 0 5px; /* Tailwind: px-1 */
}

.form-group {
  margin-bottom: 15px; /* Tailwind: mb-4 */
}

label {
  display: block; /* Tailwind: block */
  margin-bottom: 5px; /* Tailwind: mb-1.5 */
  font-weight: 500; /* Tailwind: font-medium */
  color: #444; /* Tailwind: text-gray-700  */
}

/* Apply Tailwind classes directly in template or use @apply here */
input[type="text"],
input[type="url"],
textarea,
select {
  /* Example using Tailwind classes (apply in template for better practice) */
  /* @apply block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm       */
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
    color: #666; /* Tailwind: text-gray-500  */
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
  /* @apply mt-2 text-sm text-red-600  bg-red-50  border border-red-200  rounded p-3 text-center mb-4; */
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
  /* @apply mt-2 text-sm text-green-600  bg-green-50  border border-green-200  rounded p-3 text-center mb-4; */
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