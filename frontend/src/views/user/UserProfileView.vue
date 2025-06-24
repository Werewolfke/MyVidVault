<template>
  <div v-if="loading" class="text-center py-10">Loading profile...</div>
  <div v-else-if="error" class="text-center py-10 text-red-500">Error loading profile.</div>
  <div v-else-if="profile" class="container mx-auto px-4 py-8">
    <!-- Profile Header -->
    <div class="flex flex-col md:flex-row items-center md:items-start mb-8">
      <img :src="profile.avatar_url || defaultAvatar" alt="User avatar"
        class="h-24 w-24 md:h-32 md:w-32 aspect-square rounded-full object-cover mb-4 md:mb-0 md:mr-8 border-2 border-gray-300 dark:border-gray-600 flex-shrink-0" />
      <div class="text-center md:text-left w-full flex-grow">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-2">
          <h1 class="text-3xl font-bold dark:text-white mb-2 sm:mb-0 flex items-center">
            {{ profile.username }}
            <span v-if="profile.is_verified" class="ml-2" title="Verified Subscriber">
              <svg class="w-5 h-5 text-blue-500 inline" fill="currentColor" viewBox="0 0 20 20">
                <circle cx="10" cy="10" r="10" fill="#3b82f6"/>
                <path d="M7.5 10.5l2 2 3-4" stroke="#fff" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </span>
          </h1>
          <button v-if="isOwnProfile" class="px-4 py-2 bg-indigo-600 text-white rounded shadow hover:bg-indigo-700 transition font-semibold text-sm" @click="openEditProfile">
            Edit Profile
          </button>
        </div>
        <p v-if="profile.bio" class="text-gray-600 dark:text-gray-400 mb-4 break-words text-sm">{{ profile.bio }}</p>
        <div class="flex flex-wrap justify-center md:justify-start gap-x-4 sm:gap-x-6 gap-y-2 my-4 text-sm">
          <div @click="switchTab('bookmarks')" class="cursor-pointer hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
            <span class="font-semibold dark:text-white">{{ profile.bookmarks_count ?? 0 }}</span>
            <span class="text-gray-500 dark:text-gray-400 ml-1">Bookmarks</span>
          </div>
          <div @click="switchTab('liked')" class="cursor-pointer hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
            <span class="font-semibold dark:text-white">{{ profile.likes_count ?? 0 }}</span>
            <span class="text-gray-500 dark:text-gray-400 ml-1">Likes</span>
          </div>
          <div @click="showUserListModal('followers')" class="cursor-pointer hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors group">
            <span class="font-semibold dark:text-white group-hover:underline">{{ profile.followers_count ?? 0 }}</span>
            <span class="text-gray-500 dark:text-gray-400 ml-1">Followers</span>
          </div>
          <div @click="showUserListModal('following')" class="cursor-pointer hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors group">
            <span class="font-semibold dark:text-white group-hover:underline">{{ profile.following_count ?? 0 }}</span>
            <span class="text-gray-500 dark:text-gray-400 ml-1">Following</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="mb-12">
      <div class="border-b border-gray-200 dark:border-gray-700">
        <nav class="flex space-x-8 py-3" aria-label="Tabs">
          <button v-for="tab in tabs" :key="tab" @click="switchTab(tab)"
            :class="[activeTab === tab
              ? 'border-indigo-500 text-indigo-600 dark:border-indigo-400 dark:text-indigo-300'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:border-gray-500',
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm']">
            {{ capitalize(tab) }}
          </button>
        </nav>
      </div>
      <div class="mt-6">
        <template v-if="activeTab === 'bookmarks'">
          <div class="flex items-center gap-1 py-1 px-1 rounded-md bg-gray-50 dark:bg-gray-800/50 w-full sm:w-auto mb-4">
            <span class="text-sm font-medium text-gray-600 dark:text-gray-400 hidden sm:inline pl-2">Filter:</span>
            <OrientationFilter />
          </div>
          <BookmarkGrid :fetchBookmarks="fetchUserBookmarks" :filters="mergedBookmarkFilters" :showPagination="true" />
        </template>
        <template v-else-if="activeTab === 'liked'">
          <div class="flex items-center gap-1 py-1 px-1 rounded-md bg-gray-50 dark:bg-gray-800/50 w-full sm:w-auto mb-4">
            <span class="text-sm font-medium text-gray-600 dark:text-gray-400 hidden sm:inline pl-2">Filter:</span>
            <OrientationFilter />
          </div>
          <BookmarkGrid :fetchBookmarks="fetchUserLiked" :filters="mergedLikedFilters" :showPagination="true" />
        </template>
        <template v-else-if="activeTab === 'collections'">
          <div v-if="!selectedCollection && !selectedChannel">
            <div v-if="collectionsLoading" class="text-center py-10">Loading collections...</div>
            <div v-else-if="collectionsError" class="text-center py-10 text-red-500">Failed to load collections.</div>
            <div v-else-if="collections.length > 0" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
              <div v-for="collection in collections" :key="collection.id"
                class="bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer overflow-hidden group block"
                @click="selectCollection(collection)">
                <div class="w-full h-32 bg-gray-200 dark:bg-gray-700 flex items-center justify-center overflow-hidden">
                  <img v-if="collection.display_image_url" :src="collection.display_image_url" :alt="collection.name"
                    class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
                  <span v-else class="text-3xl font-semibold text-gray-500 dark:text-gray-400">{{ collection.name.charAt(0).toUpperCase() }}</span>
                </div>
                <div class="p-4">
                  <h3 class="text-lg font-semibold text-gray-800 dark:text-white truncate group-hover:text-indigo-600 dark:group-hover:text-indigo-400">{{ collection.name }}</h3>
                  <p class="text-sm mt-1 truncate h-10" :class="collection.description ? 'text-gray-600 dark:text-gray-400' : 'text-gray-400 dark:text-gray-500'">
                    {{ collection.description || 'No description available' }}
                  </p>
                </div>
              </div>
            </div>
            <div v-else class="text-center py-10 text-gray-500">No collections found.</div>
          </div>
          <div v-else-if="selectedCollection && !selectedChannel">
            <button @click="selectedCollection = null" class="mb-4 text-indigo-600 hover:underline flex items-center">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/></svg>
              Back to Collections
            </button>
            <h2 class="text-xl font-bold mb-4">{{ selectedCollection.name }}</h2>
            <div v-if="selectedCollection.channels?.length" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
              <div v-for="channel in selectedCollection.channels" :key="channel.id"
                class="bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer overflow-hidden group block"
                @click="selectChannel(channel)">
                <div class="w-full h-24 bg-gray-200 dark:bg-gray-700 flex items-center justify-center overflow-hidden">
                  <img v-if="channel.imageUrl" :src="channel.imageUrl" :alt="channel.name" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
                  <span v-else class="text-2xl font-semibold text-gray-500 dark:text-gray-400">{{ channel.name.charAt(0).toUpperCase() }}</span>
                </div>
                <div class="p-4">
                  <h3 class="text-base font-semibold text-gray-800 dark:text-white truncate group-hover:text-indigo-600 dark:group-hover:text-indigo-400">{{ channel.name }}</h3>
                  <p class="text-sm mt-1 truncate h-8" :class="channel.description ? 'text-gray-600 dark:text-gray-400' : 'text-gray-400 dark:text-gray-500'">
                    {{ channel.description || 'No description available' }}
                  </p>
                </div>
              </div>
            </div>
            <div v-else class="text-center py-10 text-gray-500">No channels found in this collection.</div>
          </div>
          <div v-else-if="selectedChannel">
            <button @click="selectedChannel = null" class="mb-4 text-indigo-600 hover:underline flex items-center">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/></svg>
              Back to Channels
            </button>
            <h2 class="text-xl font-bold mb-4">{{ selectedChannel.name }}</h2>
            <OrientationFilter class="mb-4" />
            <BookmarkGrid :fetchBookmarks="fetchChannelBookmarks" :filters="mergedChannelBookmarkFilters" :showPagination="true" />
          </div>
        </template>
      </div>
    </div>

    <!-- Edit Profile Modal -->
    <BaseModal v-model="showEditModal">
      <h2 class="text-lg font-semibold mb-4 text-gray-800 dark:text-gray-100">Edit Profile</h2>
      <form @submit.prevent="saveProfileEdits">
        <div class="mb-4">
          <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Avatar</label>
          <input type="file" accept="image/*" @change="onAvatarChange" class="block w-full text-sm text-gray-700 dark:text-gray-200" />
          <div v-if="avatarPreview" class="mt-2">
            <img :src="avatarPreview" alt="Avatar Preview" class="h-20 w-20 rounded-full object-cover border" />
          </div>
        </div>
        <div class="mb-4">
          <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Bio</label>
          <textarea v-model="editableProfile.bio" class="w-full px-3 py-2 border rounded dark:bg-gray-700 dark:text-white"></textarea>
        </div>
        <div class="mb-4">
          <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Default Bookmark Orientation</label>
          <select v-model="editableProfile.default_bookmark_orientation" class="w-full px-3 py-2 border rounded dark:bg-gray-700 dark:text-white">
            <option value="">None</option>
            <option value="straight">Straight</option>
            <option value="gay">Gay</option>
            <option value="bi">Bi</option>
            <option value="trans">Trans</option>
            <option value="sfw">SFW</option>
          </select>
        </div>
        <div class="mb-4">
          <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Default Bookmark Collection</label>
          <select v-model="editableProfile.default_bookmark_collection" class="w-full px-3 py-2 border rounded dark:bg-gray-700 dark:text-white">
            <option value="">None</option>
            <option v-for="col in collections" :key="col.id" :value="col.id">{{ col.name }}</option>
          </select>
        </div>
        <div class="mb-4">
          <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Notification Preferences</label>
          <div class="flex flex-col gap-2">
            <label class="inline-flex items-center"><input type="checkbox" v-model="editableProfile.notify_on_follow" class="mr-2" />Notify on Follow</label>
            <label class="inline-flex items-center"><input type="checkbox" v-model="editableProfile.notify_on_own_video_bookmarked" class="mr-2" />Notify on Own Video Bookmarked</label>
            <label class="inline-flex items-center"><input type="checkbox" v-model="editableProfile.notify_on_new_bookmark_from_followed_user" class="mr-2" />Notify on New Bookmark from Followed User</label>
            <label class="inline-flex items-center"><input type="checkbox" v-model="editableProfile.notify_on_own_video_liked" class="mr-2" />Notify on Own Video Liked</label>
          </div>
        </div>
        <div class="flex justify-end">
          <button type="button" class="mr-2 px-4 py-2 rounded bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300" @click="showEditModal = false">Cancel</button>
          <button type="submit" class="px-4 py-2 rounded bg-indigo-600 text-white hover:bg-indigo-700">Save</button>
        </div>
      </form>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import { fetchUserProfile, fetchMyProfile, fetchVideos, updateMyProfile } from '@/api/index.js'
import BookmarkGrid from '@/components/BookmarkGrid.vue'
import OrientationFilter from '@/components/OrientationFilter.vue'
import { useOrientationStore } from '@/stores/orientation.js'
import { isLoggedIn } from '@/composables/useAuthState.js'
import BaseModal from '@/components/BaseModal.vue'
import axios from 'axios'

const route = useRoute()
const username = ref(route.params.username)
const profile = ref(null)
const loading = ref(true)
const error = ref('')
const showEditModal = ref(false)
const editableProfile = ref({
  bio: '', default_bookmark_orientation: '', default_bookmark_collection: '',
  notify_on_follow: true, notify_on_own_video_bookmarked: true,
  notify_on_new_bookmark_from_followed_user: true, notify_on_own_video_liked: true,
})
const avatarPreview = ref(null)
const avatarFile = ref(null)
const activeTab = ref('bookmarks')
const tabs = ['bookmarks', 'liked', 'collections']
const collections = ref([])
const collectionsLoading = ref(false)
const collectionsError = ref('')
const selectedCollection = ref(null)
const selectedChannel = ref(null)
const bookmarkFilters = ref({ user: username.value })
const likedFilters = ref({ liked_by: username.value })
const channelBookmarkFilters = ref({})
const orientationStore = useOrientationStore()

const mergedBookmarkFilters = computed(() => ({
  ...bookmarkFilters.value,
  ...(orientationStore.selectedOrientation !== 'all' ? { orientation: orientationStore.selectedOrientation } : {})
}))
const mergedLikedFilters = computed(() => ({
  ...likedFilters.value,
  ...(orientationStore.selectedOrientation !== 'all' ? { orientation: orientationStore.selectedOrientation } : {})
}))
const mergedChannelBookmarkFilters = computed(() => ({
  ...channelBookmarkFilters.value,
  ...(orientationStore.selectedOrientation !== 'all' ? { orientation: orientationStore.selectedOrientation } : {})
}))

function capitalize(str) { return str.charAt(0).toUpperCase() + str.slice(1) }
function switchTab(tab) {
  activeTab.value = tab
  if (tab !== 'collections') {
    selectedCollection.value = null
    selectedChannel.value = null
  }
}
function selectCollection(collection) { selectedCollection.value = collection; selectedChannel.value = null }
function selectChannel(channel) { selectedChannel.value = channel }

const fetchUserBookmarks = async (params = {}) => {
  return await fetchVideos({ ...params, user: username.value }) // <-- use fetchVideos
}
const fetchUserLiked = async (params = {}) => {
  return await fetchVideos({ ...params, liked_by: username.value }) // <-- use fetchVideos
}
const fetchChannelBookmarks = async (params = {}) => {
  if (!selectedChannel.value) return { results: [], count: 0 }
  return await fetchVideos({ ...params, channel: selectedChannel.value.id, user: username.value }) // <-- use fetchVideos
}

watch(selectedChannel, (channel) => {
  channelBookmarkFilters.value = channel ? { channel: channel.id, user: username.value } : {}
})
watch(() => route.params.username, async (newUsername) => {
  username.value = newUsername
  bookmarkFilters.value = { user: newUsername }
  likedFilters.value = { liked_by: newUsername }
  selectedCollection.value = null
  selectedChannel.value = null
  await loadProfile()
})

const isOwnProfile = computed(() => {
  if (typeof window !== 'undefined' && window.localStorage) {
    const loggedInUsername = window.localStorage.getItem('username')
    return isLoggedIn.value && loggedInUsername && loggedInUsername.toLowerCase() === username.value.toLowerCase()
  }
  return false
})

async function openEditProfile() {
  // Always fetch collections before opening the modal
  if (isOwnProfile.value) {
    try {
      const access = localStorage.getItem('access')
      const res = await axios.get('/api/collections/', {
        headers: { Authorization: `Bearer ${access}` }
      })
      collections.value = res.data || []
    } catch {
      collections.value = []
    }
  }
  editableProfile.value = {
    bio: profile.value.bio || '',
    default_bookmark_orientation: profile.value.default_bookmark_orientation || '',
    default_bookmark_collection: profile.value.default_bookmark_collection?.id || profile.value.default_bookmark_collection || '',
    notify_on_follow: profile.value.notify_on_follow ?? true,
    notify_on_own_video_bookmarked: profile.value.notify_on_own_video_bookmarked ?? true,
    notify_on_new_bookmark_from_followed_user: profile.value.notify_on_new_bookmark_from_followed_user ?? true,
    notify_on_own_video_liked: profile.value.notify_on_own_video_liked ?? true,
  }
  avatarPreview.value = profile.value.avatar_url || null
  avatarFile.value = null
  showEditModal.value = true
}

async function saveProfileEdits() {
  try {
    const formData = new FormData()
    Object.entries(editableProfile.value).forEach(([k, v]) => formData.append(k, v ?? ''))
    if (avatarFile.value) formData.append('avatar', avatarFile.value)
    const res = await updateMyProfile(formData)
    profile.value = { ...profile.value, ...res }
    showEditModal.value = false
  } catch {
    showEditModal.value = false
  }
}
function onAvatarChange(event) {
  const file = event.target.files[0]
  if (file) {
    avatarFile.value = file
    avatarPreview.value = URL.createObjectURL(file)
  }
}
function showUserListModal(type) {}

async function loadProfile() {
  loading.value = true
  error.value = ''
  try {
    let res
    if (isOwnProfile.value) {
      res = await fetchMyProfile()
    } else {
      res = await fetchUserProfile(username.value)
    }
    profile.value = res
    collections.value = res.collections || []
  } catch (e) {
    error.value = e?.detail || 'Failed to load profile.'
  } finally {
    loading.value = false
  }
}

onMounted(loadProfile)
</script>

<style scoped>
/* Add any component-specific styles here */
</style>