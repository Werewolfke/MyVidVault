<template>
  <div class="max-w-md mx-auto mt-10">
    <!-- Success notification banner -->
    <div v-if="registrationSuccess" class="mb-6 p-4 bg-green-50 border-l-4 border-green-500 rounded-md">
      <div class="flex">
        <div class="flex-shrink-0">
          <!-- Success icon -->
          <svg class="h-6 w-6 text-green-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <h3 class="text-lg font-medium text-green-800">Registration successful!</h3>
          <div class="mt-2 text-green-700">
            <p v-if="autoLoginSuccessful" class="text-base">
              Your account has been created and you're now logged in!
              <span class="block mt-2 font-semibold">
                Redirecting to home page in {{ redirectCountdown }} seconds...
              </span>
            </p>
            <p v-else class="text-base">
              Your account has been created. Please log in with your credentials.
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Registration form section -->
    <div v-if="!registrationSuccess">
      <h1 class="text-2xl font-bold mb-6 text-center">Register</h1>
      
      <form @submit.prevent="handleRegister" class="space-y-4">
        <div>
          <label for="username" class="block text-sm font-medium">Username</label>
          <input type="text" id="username" v-model="username" required class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600">
        </div>
        <div>
          <label for="email" class="block text-sm font-medium">Email</label>
          <input type="email" id="email" v-model="email" required class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600">
        </div>
        <div>
          <label for="password" class="block text-sm font-medium">Password</label>
          <input type="password" id="password" v-model="password" required class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600">
        </div>
        <div>
          <label for="password2" class="block text-sm font-medium">Confirm Password</label>
          <input type="password" id="password2" v-model="password2" required class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600">
        </div>
        <div v-if="error && errorMessages.length > 0" class="bg-red-50 border border-red-400 text-red-700 px-4 py-3 rounded relative mt-4" role="alert">
          <strong class="font-bold">Registration error:</strong>
          <ul class="mt-2 list-disc list-inside">
            <li v-for="(msg, index) in errorMessages" :key="index">{{ msg }}</li>
          </ul>
        </div>
        <div>
          <button type="submit" :disabled="loading" class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50">
            <span v-if="loading" class="inline-flex items-center">
              <!-- Loading spinner -->
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Registering...
            </span>
            <span v-else>Register</span>
          </button>
        </div>
        <div class="text-center text-sm">
          Already have an account? <router-link :to="{ name: 'login' }" class="text-indigo-600 hover:underline">Login here</router-link>
        </div>
      </form>
    </div>
    
    <!-- Post-registration options -->
    <div v-if="registrationSuccess" class="space-y-4 mt-6">
      <div v-if="!autoLoginSuccessful" class="flex flex-col space-y-4">
        <button @click="goToLogin" class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
          Go to Login
        </button>
      </div>
      <div v-else class="flex flex-col space-y-4">
        <button @click="goToHome" class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
          Continue to Home Now
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { register, login } from '@/api/index.js'
import { updateAuthState } from '@/composables/useAuthState.js'

const username = ref('')
const email = ref('')
const password = ref('')
const password2 = ref('')

const loading = ref(false)
const error = ref(false)
const errorMessages = ref([])

const registrationSuccess = ref(false)
const autoLoginSuccessful = ref(false)
const redirectCountdown = ref(5)
let countdownInterval = null

const router = useRouter()

function validateForm() {
  errorMessages.value = []
  if (!username.value) errorMessages.value.push('Username is required.')
  if (!email.value) errorMessages.value.push('Email is required.')
  if (!password.value) errorMessages.value.push('Password is required.')
  if (password.value !== password2.value) errorMessages.value.push('Passwords do not match.')
  return errorMessages.value.length === 0
}

async function handleRegister() {
  loading.value = true
  error.value = false
  errorMessages.value = []

  if (!validateForm()) {
    error.value = true
    loading.value = false
    return
  }

  try {
    await register(username.value, email.value, password.value, password2.value)
    registrationSuccess.value = true

    // Auto-login after registration
    try {
      await login(username.value, password.value)
      autoLoginSuccessful.value = true
      updateAuthState()
      startRedirectCountdown()
    } catch {
      autoLoginSuccessful.value = false
    }
  } catch (err) {
    error.value = true
    if (err.response?.data) {
      const data = err.response.data
      errorMessages.value = Object.values(data).flat()
    } else {
      errorMessages.value = ['Registration failed. Please try again.']
    }
  } finally {
    loading.value = false
  }
}

function startRedirectCountdown() {
  redirectCountdown.value = 5
  countdownInterval = setInterval(() => {
    redirectCountdown.value--
    if (redirectCountdown.value <= 0) {
      clearInterval(countdownInterval)
      goToHome()
    }
  }, 1000)
}

function goToLogin() {
  router.push({ name: 'login' })
}

function goToHome() {
  router.push({ name: 'home' })
}
</script>

<style scoped>
/* Add any component-specific styles here */
</style>