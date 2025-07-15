import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Initialize auth after pinia is available
const authStore = useAuthStore()

// Initialize auth state and start auto-refresh if authenticated
authStore.initializeAuth().then(() => {
  if (authStore.isAuthenticated) {
    authStore.startAutoRefresh()
  }
})

// Navigation guard to check authentication
router.beforeEach(async (to, from, next) => {
  // Routes that require authentication
  const protectedRoutes = [
    // '/profile/me', // removed, use /users/:username instead
    '/bookmarks/create',
    // Add other protected routes here
  ]
  
  const requiresAuth = protectedRoutes.some(route => 
    to.path.startsWith(route)
  )
  
  if (requiresAuth) {
    const isValidAuth = await authStore.checkAndRefreshToken()
    
    if (!isValidAuth) {
      // Redirect to login with return URL
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
      return
    }
  }
  
  next()
})

app.mount('#app')
