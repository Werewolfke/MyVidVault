<template>
  <div>
    <form @submit.prevent="handleSubmit" class="bg-surface p-6 rounded shadow space-y-6">
      <div>
        <label class="block mb-1 font-medium text-text-secondary" for="video-source-url">Source URL</label>
        <input
          class="block w-full px-3 py-2 border border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring focus:border-primary bg-background text-text-main placeholder-text-secondary"
          type="url"
          id="video-source-url"
          v-model="videoData.source_url"
          placeholder="https://example.com/video.mp4"
          required
        />
      </div>
      <div>
        <label class="block mb-1 font-medium text-text-secondary" for="video-thumbnail-url">Thumbnail URL</label>
        <input
          class="block w-full px-3 py-2 border border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring focus:border-primary bg-background text-text-main placeholder-text-secondary"
          type="url"
          id="video-thumbnail-url"
          v-model="videoData.thumbnail_url"
          placeholder="https://example.com/thumbnail.jpg"
          required
        />
      </div>
      <div>
        <label class="block mb-1 font-medium text-text-secondary" for="video-embed-url">Embed URL</label>
        <input
          class="block w-full px-3 py-2 border border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring focus:border-primary bg-background text-text-main placeholder-text-secondary"
          type="url"
          id="video-embed-url"
          v-model="videoData.embed_url"
          placeholder="https://example.com/embed/video"
          required
        />
      </div>
      <div>
        <label class="block mb-1 font-medium text-text-secondary" for="video-title">Video Title</label>
        <input
          class="block w-full px-3 py-2 border border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring focus:border-primary bg-background text-text-main placeholder-text-secondary"
          type="text"
          id="video-title"
          v-model="videoData.title"
          placeholder="Title of the video"
          required
        />
      </div>
      <div>
        <label class="block mb-1 font-medium text-text-secondary" for="video-orientation">Orientation</label>
        <select
          class="block w-full px-3 py-2 border border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring focus:border-primary bg-background text-text-main"
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
        <label class="block mb-1 font-medium text-text-secondary" for="tags">Tags (comma-separated)</label>
        <input
          class="block w-full px-3 py-2 border border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring focus:border-primary bg-background text-text-main placeholder-text-secondary"
          type="text"
          id="tags"
          v-model="tagsInput"
          placeholder="tag1, tag2, another tag"
        />
      </div>
      <div>
        <label class="block mb-1 font-medium text-text-secondary" for="bookmark-collection">Collection</label>
        <select
          class="block w-full px-3 py-2 border border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring focus:border-primary bg-background text-text-main"
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
        <label class="block mb-1 font-medium text-text-secondary" for="bookmark-channel">Channel</label>
        <select
          class="block w-full px-3 py-2 border border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring focus:border-primary bg-background text-text-main"
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
        <label class="block mb-1 font-medium text-text-secondary" for="bookmark-description">Description</label>
        <textarea
          class="block w-full px-3 py-2 border border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring focus:border-primary bg-background text-text-main"
          id="bookmark-description"
          v-model="bookmarkData.description"
          rows="3"
        ></textarea>
      </div>
      <div>
        <label class="block mb-1 font-medium text-text-secondary" for="bookmark-access">Access</label>
        <select
          class="block w-full px-3 py-2 border border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring focus:border-primary bg-background text-text-main"
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
        type="submit"
        :class="[
          'w-full py-2 px-4 text-white font-semibold rounded shadow disabled:opacity-50 transition',
          submissionError ? 'bg-red-500 hover:bg-red-600' : 'bg-primary hover:bg-primary/80'
        ]"
        :disabled="isSubmitting"
      >
        <span v-if="isSubmitting">Saving...</span>
        <span v-else-if="submissionError">{{ submissionError }}</span>
        <span v-else>Save Bookmark & Video</span>
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted, defineEmits, defineProps } from 'vue'
import { apiClient } from '@/api/index.js' // Using the centralized apiClient

const props = defineProps({
  initialData: {
    type: Object,
    default: () => ({})
  },
  useIframe: {
    type: Boolean,
    default: false
  },
  submissionError: {
    type: [String, Object],
    default: null
  }
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
  access: null,
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

const emit = defineEmits(['update:formData', 'submit'])

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

// Watch for incoming scraped data and populate the form
watch(() => props.initialData, (newData) => {
  if (newData) {
    videoData.source_url = newData.source_url || '';
    videoData.title = newData.title || '';
    videoData.thumbnail_url = newData.thumbnail_url || '';
    videoData.embed_url = newData.embed_url || ''; // Use the embed_url from the API
    bookmarkData.description = newData.description || '';
    if (newData.tags && newData.tags.length > 0) {
      tagsInput.value = newData.tags.join(', ');
    } else {
      tagsInput.value = ''; // Explicitly clear if no tags are returned
    }
  }
}, { immediate: true, deep: true });

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
    const response = await apiClient.get('/collections/') // Use apiClient
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
    const response = await apiClient.get(`/collections/${collectionId}/channels/`) // Use apiClient
    userChannels.value = response.data
  } catch (error) {
    userChannels.value = []
  } finally {
    loadingChannels.value = false
  }
}

function handleSubmit() {
  const payload = {
    video: {
      source_url: videoData.source_url,
      title: videoData.title,
      thumbnail_url: videoData.thumbnail_url,
      embed_url: videoData.embed_url,
      orientation: videoData.orientation,
      player_type: props.useIframe ? 'iframe' : 'direct',
      tags: tagsInput.value.split(',').map(t => t.trim()).filter(Boolean),
    },
    bookmark: {
      channel_id: bookmarkData.channel,
      description: bookmarkData.description,
      access: bookmarkData.access,
      tags: tagsInput.value.split(',').map(t => t.trim()).filter(Boolean),
    }
  }
  emit('submit', payload);
}
</script>

<style scoped>
/* All custom styles have been replaced with Tailwind utility classes in the template. */
</style>
