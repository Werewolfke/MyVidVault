<template>
  <div class="max-w-md mx-auto mt-10">
    <h1 class="text-2xl font-bold mb-6 text-center">Login</h1>
    <form @submit.prevent="handleLogin" class="space-y-4">
      <div>
        <label for="username" class="block text-sm font-medium">Username</label>
        <input type="text" id="username" v-model="username" required class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600">
      </div>
      <div>
        <label for="password" class="block text-sm font-medium">Password</label>
        <input type="password" id="password" v-model="password" required class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600">
      </div>
      <div v-if="error" class="text-red-500 text-sm">
        {{ errorMessage }}
      </div>
      <div class="flex items-center justify-end mt-2 text-sm">
        <router-link :to="{ name: 'forgot-password' }" class="font-medium text-indigo-600 hover:text-indigo-500 dark:text-indigo-400 dark:hover:text-indigo-300">
          Forgot your password?
        </router-link>
      </div>
      <div>
        <button type="submit" :disabled="loading" class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 mt-4">
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>
      </div>
      <div class="text-center text-sm mt-4">
        Don't have an account? <router-link :to="{ name: 'register' }" class="text-indigo-600 hover:underline">Register here</router-link>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '@/api/index.js'
import { updateAuthState } from '@/composables/useAuthState.js'

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref(false)
const errorMessage = ref('')

const router = useRouter()

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
    const response = await login(username.value, password.value)
    // Store username in localStorage for profile checks
    localStorage.setItem('username', username.value)
    updateAuthState()
    router.push({ name: 'home' })
  } catch (err) {
    error.value = true
    errorMessage.value = err.response?.data?.detail || 'Login failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>