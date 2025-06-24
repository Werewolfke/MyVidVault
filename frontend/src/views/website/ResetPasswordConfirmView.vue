// filepath: myvidvault_frontend/src/views/ResetPasswordConfirmView.vue
<template>
  <div class="max-w-md mx-auto mt-10 p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md">
    <h1 class="text-2xl font-bold mb-6 text-center text-gray-800 dark:text-gray-200">Reset Password</h1>
    <form v-if="!successMessage && displayForm" @submit.prevent="handleResetPassword" class="space-y-4">
      <div>
        <label for="new_password1" class="block text-sm font-medium text-gray-700 dark:text-gray-300">New Password</label>
        <input type="password" id="new_password1" v-model="newPassword1" required
               class="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white">
        <p v-if="errors.new_password1" class="text-red-500 text-xs mt-1">{{ errors.new_password1.join(', ') }}</p>
      </div>
      <div>
        <label for="new_password2" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Confirm New Password</label>
        <input type="password" id="new_password2" v-model="newPassword2" required
               class="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white">
        <p v-if="errors.new_password2" class="text-red-500 text-xs mt-1">{{ errors.new_password2.join(', ') }}</p>
      </div>

      <div v-if="generalErrorMessage" class="text-red-500 text-sm">
        {{ generalErrorMessage }}
      </div>
      <p v-if="errors.uidb64" class="text-red-500 text-xs mt-1">{{ errors.uidb64.join(', ') }}</p>
      <p v-if="errors.token" class="text-red-500 text-xs mt-1">{{ errors.token.join(', ') }}</p>
      <p v-if="errors.detail" class="text-red-500 text-xs mt-1">{{ errors.detail.join(', ') }}</p>


      <div>
        <button type="submit" :disabled="loading"
                class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50">
          {{ loading ? 'Resetting...' : 'Reset Password' }}
        </button>
      </div>
    </form>
    <div v-if="successMessage" class="text-green-500 text-sm text-center py-4">
      {{ successMessage }}
      <div class="mt-4">
        <router-link :to="{ name: 'login' }" class="text-indigo-600 hover:underline dark:text-indigo-400">
          Proceed to Login
        </router-link>
      </div>
    </div>
    <div v-if="!displayForm && !successMessage" class="text-red-500 text-sm text-center py-4">
      <p>{{ generalErrorMessage || "The password reset link is invalid or has expired." }}</p>
      <p>Please <router-link :to="{ name: 'forgot-password' }" class="text-indigo-600 hover:underline dark:text-indigo-400">request a new one</router-link>.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const newPassword1 = ref('')
const newPassword2 = ref('')
const loading = ref(false)
const successMessage = ref('')
const generalErrorMessage = ref('')
const errors = ref({
  new_password1: [],
  new_password2: [],
  uidb64: [],
  token: [],
  detail: []
})
const displayForm = ref(true)

let uidb64 = ''
let token = ''

onMounted(() => {
  // Get uidb64 and token from route params or query
  uidb64 = route.params.uidb64 || route.query.uidb64 || ''
  token = route.params.token || route.query.token || ''
  if (!uidb64 || !token) {
    displayForm.value = false
    generalErrorMessage.value = 'Invalid password reset link.'
  }
})

async function handleResetPassword() {
  loading.value = true
  generalErrorMessage.value = ''
  errors.value = {
    new_password1: [],
    new_password2: [],
    uidb64: [],
    token: [],
    detail: []
  }

  // Basic frontend validation
  if (!newPassword1.value) errors.value.new_password1.push('New password is required.')
  if (!newPassword2.value) errors.value.new_password2.push('Please confirm your new password.')
  if (newPassword1.value && newPassword2.value && newPassword1.value !== newPassword2.value) {
    errors.value.new_password2.push('Passwords do not match.')
  }
  if (errors.value.new_password1.length || errors.value.new_password2.length) {
    loading.value = false
    return
  }

  try {
    // Replace this with your actual API call
    // Example:
    // const response = await fetch('/api/password-reset-confirm/', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({
    //     uidb64,
    //     token,
    //     new_password1: newPassword1.value,
    //     new_password2: newPassword2.value
    //   })
    // })
    // const data = await response.json()
    // if (!response.ok) throw data

    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1200))

    successMessage.value = 'Your password has been reset successfully!'
    displayForm.value = false
  } catch (err) {
    // Example error handling
    // errors.value = err.errors || { detail: ['An error occurred. Please try again.'] }
    errors.value.detail.push('An error occurred. Please try again.')
    displayForm.value = true
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
</style>