import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api, { login as apiLogin, logout as apiLogout, refreshToken as apiRefreshToken } from '@/api/index.js'

export const useAuthStore = defineStore('auth', () => {
  // State
  const accessToken = ref(localStorage.getItem('access') || null)
  const refreshToken = ref(localStorage.getItem('refresh') || null)
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const tokenExpiry = ref(localStorage.getItem('token_expiry') || null)
  const isRefreshing = ref(false)

  // Getters
  const isAuthenticated = computed(() => {
    return !!accessToken.value && !!refreshToken.value
  })

  const isTokenExpired = computed(() => {
    if (!tokenExpiry.value) return true
    const expiry = new Date(tokenExpiry.value)
    const now = new Date()
    // Consider token expired if it expires within 5 minutes
    const fiveMinutes = 5 * 60 * 1000
    return expiry.getTime() - now.getTime() < fiveMinutes
  })

  // Actions
  const setTokens = (tokens) => {
    accessToken.value = tokens.access
    refreshToken.value = tokens.refresh
    
    // Calculate token expiry (7 days from now)
    const expiry = new Date()
    expiry.setDate(expiry.getDate() + 7)
    tokenExpiry.value = expiry.toISOString()
    
    // Store in localStorage
    localStorage.setItem('access', tokens.access)
    localStorage.setItem('refresh', tokens.refresh)
    localStorage.setItem('token_expiry', tokenExpiry.value)
  }

  const setUser = (userData) => {
    user.value = userData
    localStorage.setItem('user', JSON.stringify(userData))
    // Also store username separately for backward compatibility
    if (userData.username) {
      localStorage.setItem('username', userData.username)
    }
  }

  const clearTokens = () => {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    tokenExpiry.value = null
    
    localStorage.removeItem('access')
    localStorage.removeItem('refresh')
    localStorage.removeItem('user')
    localStorage.removeItem('token_expiry')
    localStorage.removeItem('username')
  }

  const login = async (username, password) => {
    try {
      const response = await apiLogin(username, password)
      setTokens(response)
      
      // Fetch user profile after login using username argument
      try {
        if (username) {
          const userProfile = await api.get(`/profile/${username}/`)
          setUser(userProfile.data)
        }
      } catch (profileError) {
        console.warn('Failed to fetch user profile:', profileError)
      }
      
      return response
    } catch (error) {
      clearTokens()
      throw error
    }
  }

  const logout = async () => {
    try {
      // Try to blacklist the refresh token on the server
      if (refreshToken.value) {
        await api.post('/token/blacklist/', { 
          refresh: refreshToken.value 
        })
      }
    } catch (error) {
      console.warn('Failed to blacklist token on server:', error)
    } finally {
      clearTokens()
      await apiLogout()
    }
  }

  const refreshTokens = async () => {
    if (isRefreshing.value) {
      // If already refreshing, wait for completion
      return new Promise((resolve, reject) => {
        const checkRefresh = () => {
          if (!isRefreshing.value) {
            if (accessToken.value) {
              resolve()
            } else {
              reject(new Error('Token refresh failed'))
            }
          } else {
            setTimeout(checkRefresh, 100)
          }
        }
        checkRefresh()
      })
    }

    if (!refreshToken.value) {
      throw new Error('No refresh token available')
    }

    isRefreshing.value = true
    
    try {
      const response = await apiRefreshToken()
      setTokens(response)
      return response
    } catch (error) {
      console.error('Token refresh failed:', error)
      clearTokens()
      // Redirect to login page
      window.location.href = '/login'
      throw error
    } finally {
      isRefreshing.value = false
    }
  }

  const checkAndRefreshToken = async () => {
    if (!isAuthenticated.value) {
      return false
    }

    if (isTokenExpired.value) {
      try {
        await refreshTokens()
        return true
      } catch (error) {
        return false
      }
    }

    return true
  }

  // Initialize auth state on store creation
  const initializeAuth = async () => {
    if (isAuthenticated.value) {
      // Check if token needs refresh
      if (isTokenExpired.value) {
        try {
          await refreshTokens()
        } catch (error) {
          console.warn('Auto-refresh failed on init:', error)
          clearTokens()
        }
      }
      
      // Fetch user profile if we don't have it
      if (!user.value && accessToken.value) {
        try {
          const username = localStorage.getItem('username')
          if (username) {
            const userProfile = await api.get(`/profile/${username}/`)
            setUser(userProfile.data)
          }
        } catch (error) {
          console.warn('Failed to fetch user profile on init:', error)
        }
      }
    }
  }

  // Auto-refresh timer
  let refreshTimer = null
  
  const startAutoRefresh = () => {
    if (refreshTimer) {
      clearInterval(refreshTimer)
    }
    
    // Check token every hour
    refreshTimer = setInterval(async () => {
      if (isAuthenticated.value && isTokenExpired.value) {
        try {
          await refreshTokens()
        } catch (error) {
          console.warn('Auto-refresh failed:', error)
        }
      }
    }, 60 * 60 * 1000) // 1 hour
  }

  const stopAutoRefresh = () => {
    if (refreshTimer) {
      clearInterval(refreshTimer)
      refreshTimer = null
    }
  }

  // Start auto-refresh when store is created
  if (isAuthenticated.value) {
    startAutoRefresh()
  }

  return {
    // State
    accessToken,
    refreshToken,
    user,
    tokenExpiry,
    isRefreshing,
    
    // Getters
    isAuthenticated,
    isTokenExpired,
    
    // Actions
    login,
    logout,
    refreshTokens,
    checkAndRefreshToken,
    initializeAuth,
    startAutoRefresh,
    stopAutoRefresh,
    setUser,
    clearTokens
  }
})
