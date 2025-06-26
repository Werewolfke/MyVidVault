<template>
    <div class="container mx-auto px-4 py-6">
        <h1 class="text-2xl font-semibold mb-6 text-gray-800 dark:text-gray-200">Add Bookmarks</h1>

        <!-- IMPORTANT NOTICE -->
        <div class="mb-6 p-4 rounded bg-yellow-100 border-l-4 border-yellow-500 text-yellow-900 dark:bg-yellow-900 dark:border-yellow-700 dark:text-yellow-300">
            <strong>Notice:</strong> Your bookmark will be <span class="font-semibold">removed or set to private without warning</span> if you do not provide a proper thumbnail.<br><br>
            <span class="font-semibold">How to get a thumbnail (poster image):</span>
            <ol class="list-decimal list-inside mt-2 mb-2">
                <li>On the video page, <span class="font-semibold">right-click</span> on the video or its title and look for an option like <span class="italic">"Change thumbnail"</span> or <span class="italic">"Poster"</span>.</li>
                <li>When the thumbnail image appears, <span class="font-semibold">right-click</span> on the image and select <span class="italic">"Copy image address"</span> (or similar wording).</li>
                <li>Return to MyVidVault, and <span class="font-semibold">paste</span> the copied address.</li>
            </ol>
            <span class="block mt-2">This process is similar for all video hosts. <span class="font-semibold">Always copy the thumbnail address and paste it in the "Thumbnail URL" field.</span></span>
            <br>
            <span class="block mt-2 text-sm text-gray-700 dark:text-gray-400">If you need to inspect the page for a thumbnail manually: <br>
                1. Right-click anywhere on the page and select <span class="italic">"Inspect"</span> or <span class="italic">"Inspect Element"</span>.<br>
                2. In the Elements panel, look for an <code>&lt;img&gt;</code> tag or a <code>poster</code> attribute on a <code>&lt;video&gt;</code> tag.<br>
                3. Right-click the image or poster URL and copy its address.
            </span>
        </div>

        <!-- Tab Navigation -->
        <div class="mb-6 border-b border-gray-200 dark:border-gray-700">
            <nav class="flex space-x-4">
                <button
                    v-for="tab in tabs"
                    :key="tab.id"
                    :class="[
                        'px-3 py-2 font-medium text-sm rounded-t',
                        activeTab === tab.id
                            ? 'bg-white text-blue-600 border-b-2 border-blue-600 dark:bg-gray-800 dark:text-blue-400 dark:border-blue-400'
                            : 'text-gray-500 hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400'
                    ]"
                    @click="activeTab = tab.id"
                >
                    {{ tab.name }}
                </button>
            </nav>
        </div>

        <!-- Tab Content -->
        <div>
            <BookmarkUrlForm v-if="activeTab === 'url'" />
            <div v-else-if="activeTab === 'manual'" class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <BookmarkManual @update:formData="handleManualFormUpdate" />
                <BookmarkManualPreview
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
import { ref } from 'vue'
import BookmarkManual from '@/components/bookmarks/BookmarkManual.vue'
import BookmarkManualPreview from '@/components/bookmarks/BookmarkManualPreview.vue'
import BookmarkUrlForm from '@/components/bookmarks/BookmarkUrlForm.vue'

const tabs = [
  { id: 'url', name: 'Add via URL' },
  { id: 'manual', name: 'Manual Add' }
]
const activeTab = ref('manual')

// Initialize manualFormData with default structure
const manualFormData = ref({
  video: {},
  bookmark: {},
  tags: [],
  channelName: ''
})

// Handler to update manualFormData from BookmarkManual
function handleManualFormUpdate(newData) {
  manualFormData.value = { ...manualFormData.value, ...newData }
}
</script>

<style scoped>
pre {
  white-space: pre-wrap;
  word-break: break-all;
}
</style>