<template>
    <div class="mb-10 lg:mb-0">
        <!-- New Informational Note -->
        <div class="mb-4 p-3 rounded-md bg-yellow-50 dark:bg-yellow-900/30 border border-yellow-200 dark:border-yellow-800/50">
            <div class="flex">
                <div class="flex-shrink-0">
                    <!-- Heroicon name: solid/exclamation -->
                    <svg class="h-5 w-5 text-yellow-400 dark:text-yellow-300" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                        <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 3.001-1.742 3.001H4.42c-1.53 0-2.493-1.667-1.743-3.001l5.58-9.92zM10 13a1 1 0 110-2 1 1 0 010 2zm-1-8a1 1 0 011-1h.008a1 1 0 011 1v3.006a1 1 0 01-1 1h-.008a1 1 0 01-1-1V5z" clip-rule="evenodd" />
                    </svg>
                </div>
                <div class="ml-3 flex-1 md:flex md:justify-between">
                    <p class="text-sm text-yellow-700 dark:text-yellow-200">
                        Auto Detection is currently disabled. Please add manually.
                    </p>
                </div>
            </div>
        </div>
        <!-- End New Informational Note -->


        <!-- Step 1: Enter URL -->
        <div class="mb-8">

            <label for="videoUrl" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Video URL</label>
            <div class="mt-1 flex rounded-md shadow-sm">
                <input
                    type="url"
                    id="videoUrl"
                    v-model="urlInput"
                    placeholder="Enter URL for auto-detection..."
                    :disabled="true"
                    class="block w-full flex-1 rounded-none rounded-l-md border-gray-300 bg-gray-50 focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:placeholder-gray-400 dark:focus:border-indigo-400 dark:focus:ring-indigo-400"
                    @keyup.enter="handleFetchMetadata"
                />
                <button
                    @click="handleFetchMetadata"
                    :disabled="true" 
                    type="button"
                    class="relative -ml-px inline-flex items-center space-x-2 rounded-r-md border border-gray-300 bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 disabled:opacity-50 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-600 dark:focus:border-indigo-400 dark:focus:ring-indigo-400"
                >
                    <svg v-if="fetchLoading" class="animate-spin -ml-1 mr-2 h-5 w-5 text-gray-500 dark:text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>{{ fetchLoading ? 'Detecting...' : 'Detect Info' }}</span>
                </button>
            </div>
            <p v-if="fetchError" class="mt-2 text-sm text-red-600 dark:text-red-400">{{ fetchErrorMessage }}</p>
        </div>

        <!-- Step 2: Review Metadata & Save -->
        <div v-if="fetchedData" class="mt-10 bg-white dark:bg-gray-800 shadow sm:rounded-lg overflow-hidden">
            <div class="px-4 py-5 sm:px-6 border-b border-gray-200 dark:border-gray-700">
                <h3 class="text-lg font-medium leading-6 text-gray-900 dark:text-white">Review & Save</h3>
            </div>
            <div class="px-4 py-5 sm:p-6">
                <!-- New Layout with Manual Components -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-8">
                    <!-- Manual Form Column -->
                    <div class="md:col-span-1">
                        <BookmarkManual
                            :initial-video-data="initialVideoDataForManual"
                            :initial-bookmark-data="initialBookmarkDataForManual"
                            :initial-tags-string="initialTagsStringForManual"
                            :is-edit-mode="true" 
                            @update:form-data="handleManualFormUpdate"
                            :api-validation-errors="manualFormApiErrors"
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

                <!-- Save Button and Error Message for the URL Form -->
                <div class="mt-8 pt-5 border-t border-gray-200 dark:border-gray-700">
                    <p v-if="saveError" class="text-sm text-red-600 dark:text-red-400 mb-3">{{ saveErrorMessage }}</p>
                    <div class="flex justify-end">
                        <button
                            @click="handleSaveBookmark"
                            type="button" 
                            :disabled="saveLoading || !currentManualFormData.bookmark.channel || !currentManualFormData.video.title || currentManualFormData.tags.length === 0"
                            class="inline-flex justify-center rounded-md border border-transparent bg-green-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 dark:bg-green-700 dark:hover:bg-green-800 dark:focus:ring-offset-gray-800"
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
        <div v-if="saveSuccess" class="mt-6 rounded-md bg-green-50 dark:bg-green-900/50 p-4 border border-green-200 dark:border-green-700/50">
            <div class="flex">
                <div class="flex-shrink-0">
                    <svg class="h-5 w-5 text-green-400 dark:text-green-300" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a 1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                    </svg>
                </div>
                <div class="ml-3">
                    <p class="text-sm font-medium text-green-800 dark:text-green-200">
                        Bookmark saved successfully!
                        <router-link v-if="createdBookmarkId" :to="{ name: 'bookmark-detail', params: { id: createdBookmarkId } }" class="font-medium underline text-green-700 hover:text-green-600 dark:text-green-300 dark:hover:text-green-200 ml-2">View Bookmark</router-link>
                    </p>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>

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