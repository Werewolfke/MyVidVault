<template>
    <h1 class="text-2xl font-bold mb-6 text-center text-gray-800 dark:text-gray-200">Forgot Password</h1>
    <form @submit.prevent="handleRequestReset" class="space-y-4">
      <div>
        <label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Email Address</label>
        <input type="email" id="email" v-model="email" required
               class="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white placeholder-gray-400 dark:placeholder-gray-500">
        <p v-if="errors.email" class="text-red-500 text-xs mt-1">{{ errors.email.join(', ') }}</p>
      </div>
      <div v-if="message" :class="isError ? 'text-red-500' : 'text-green-500'" class="text-sm">
        {{ message }}
      </div>
      <p v-if="errors.detail" class="text-red-500 text-xs mt-1">{{ errors.detail.join(', ') }}</p>
      <div>
        <button type="submit" :disabled="loading"
                class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50">
          {{ loading ? 'Sending...' : 'Send Password Reset Email' }}
        </button>
      </div>
    </form>
    <div class="mt-4 text-center text-sm">
      <router-link :to="{ name: 'login' }" class="text-indigo-600 hover:underline dark:text-indigo-400">
        Back to Login
      </router-link>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import { requestPasswordReset } from '@/api/index.js'

const email = ref('')
const loading = ref(false)
const message = ref('')
const isError = ref(false)
const errors = ref({ email: [], detail: [] })

async function handleRequestReset() {
  loading.value = true
  message.value = ''
  isError.value = false
  errors.value = { email: [], detail: [] }

  if (!email.value) {
    errors.value.email.push('Email is required.')
    loading.value = false
    return
  }

  try {
    await requestPasswordReset(email.value)
    message.value = 'If an account with that email exists, a password reset link has been sent.'
    isError.value = false
    email.value = ''
  } catch (err) {
    isError.value = true
    if (err.response?.data) {
      const data = err.response.data
      errors.value = { ...errors.value, ...data }
    } else {
      errors.value.detail.push('An error occurred. Please try again.')
    }
  } finally {
    loading.value = false
  }
}
</script>