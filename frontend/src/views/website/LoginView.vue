<template>
  <h1 class="text-2xl font-bold mb-6 text-center text-gray-800 dark:text-gray-200">Login</h1>
  <form @submit.prevent="handleLogin" class="space-y-4">
    <div>
      <label for="username" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Username</label>
      <input
        type="text"
        id="username"
        v-model="username"
        required
        :disabled="loading"
        class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200 disabled:opacity-50"
      />
    </div>
    <div>
      <label for="password" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Password</label>
      <input
        type="password"
        id="password"
        v-model="password"
        required
        :disabled="loading"
        class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200 disabled:opacity-50"
      />
    </div>
    <div>
      <label class="flex items-center text-sm text-gray-700 dark:text-gray-300">
        <input
          type="checkbox"
          v-model="rememberMe"
          :disabled="loading"
          class="mr-2 h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded disabled:opacity-50"
        />
        Keep me logged in for a week
      </label>
    </div>
    <div v-if="error" class="text-red-500 text-sm bg-red-50 dark:bg-red-900/20 p-3 rounded-md border border-red-200 dark:border-red-800">
      {{ errorMessage }}
    </div>
    <div class="flex items-center justify-end mt-2 text-sm">
      <router-link :to="{ name: 'forgot-password' }" class="font-medium text-indigo-600 hover:text-indigo-500 dark:text-indigo-400 dark:hover:text-indigo-300">
        Forgot your password?
      </router-link>
    </div>
    <div>
      <button
        type="submit"
        :disabled="loading"
        class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-indigo-500 dark:hover:bg-indigo-600"
      >
        <svg v-if="loading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        {{ loading ? 'Logging in...' : 'Login' }}
      </button>
    </div>
    <div class="text-center text-sm mt-4 text-gray-700 dark:text-gray-300">
      Don't have an account? <router-link :to="{ name: 'register' }" class="text-indigo-600 hover:underline dark:text-indigo-400">Register here</router-link>
    </div>
  </form>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const username = ref('')
const password = ref('')
const rememberMe = ref(true) // Default to keeping user logged in
const loading = ref(false)
const error = ref(false)
const errorMessage = ref('')

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// Redirect if already authenticated
onMounted(() => {
  if (authStore.isAuthenticated) {
    const profileUsername = localStorage.getItem('username')
    const redirectTo = route.query.redirect || (profileUsername ? `/users/${profileUsername}` : '/')
    router.push(redirectTo)
  }
})

async function handleLogin() {
  loading.value = true
  error.value = false
  errorMessage.value = ''

  if (!username.value || !password.value) {
    error.value = true
    errorMessage.value = 'Username and password are required.'
    loading.value = false
    return
  }

  try {
    await authStore.login(username.value, password.value)
    
    // Start auto-refresh if user wants to stay logged in
    if (rememberMe.value) {
      authStore.startAutoRefresh()
    }
    
    // Redirect to intended page or profile
    const profileUsername = localStorage.getItem('username')
    const redirectTo = route.query.redirect || (profileUsername ? `/users/${profileUsername}` : '/')
    router.push(redirectTo)
    
  } catch (err) {
    error.value = true
    
    // Handle specific error types
    if (err.response?.status === 401) {
      errorMessage.value = 'Invalid username or password.'
    } else if (err.response?.status === 429) {
      errorMessage.value = 'Too many login attempts. Please try again later.'
    } else if (err.response?.data?.detail) {
      errorMessage.value = err.response.data.detail
    } else if (err.response?.data?.non_field_errors) {
      errorMessage.value = err.response.data.non_field_errors[0]
    } else {
      errorMessage.value = 'Login failed. Please check your connection and try again.'
    }
    
    console.error('Login error:', err)
  } finally {
    loading.value = false
  }
}
</script>