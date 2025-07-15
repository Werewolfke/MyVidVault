<template>
  <div v-if="authStore.isAuthenticated" class="flex items-center space-x-4">
    <!-- User info -->
    <div v-if="authStore.user" class="flex items-center space-x-2">
      <img 
        :src="authStore.user.avatar_url || '/default-avatar.png'" 
        :alt="authStore.user.username"
        class="w-8 h-8 rounded-full"
      />
      <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
        {{ authStore.user.username }}
      </span>
    </div>
    
    <!-- Token expiry indicator -->
    <div v-if="authStore.isTokenExpired" class="text-xs text-yellow-600 dark:text-yellow-400">
      <span class="flex items-center">
        <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
        </svg>
        Session expiring soon
      </span>
    </div>
    
    <!-- Logout button -->
    <button
      @click="handleLogout"
      :disabled="loggingOut"
      class="text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200 disabled:opacity-50"
    >
      {{ loggingOut ? 'Logging out...' : 'Logout' }}
    </button>
  </div>
  
  <div v-else class="flex items-center space-x-4">
    <router-link 
      :to="{ name: 'login' }"
      class="text-sm text-indigo-600 hover:text-indigo-700 dark:text-indigo-400 dark:hover:text-indigo-300"
    >
      Login
    </router-link>
    <router-link 
      :to="{ name: 'register' }"
      class="text-sm bg-indigo-600 text-white px-3 py-1 rounded hover:bg-indigo-700 dark:bg-indigo-500 dark:hover:bg-indigo-600"
    >
      Sign Up
    </router-link>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()
const loggingOut = ref(false)

const handleLogout = async () => {
  loggingOut.value = true
  
  try {
    await authStore.logout()
    authStore.stopAutoRefresh()
    router.push({ name: 'home' })
  } catch (error) {
    console.error('Logout failed:', error)
    // Still redirect to home even if logout fails
    router.push({ name: 'home' })
  } finally {
    loggingOut.value = false
  }
}
</script>
