import { ref } from 'vue'

export const isLoggedIn = ref(!!localStorage.getItem('access'))
export const username = ref(localStorage.getItem('username'))

export function updateAuthState() {
  isLoggedIn.value = !!localStorage.getItem('access')
  username.value = localStorage.getItem('username')
}

// Listen for storage changes (multi-tab sync)
window.addEventListener('storage', () => {
  isLoggedIn.value = !!localStorage.getItem('access')
  username.value = localStorage.getItem('username')
})

// After successful login:
// localStorage.setItem('username', response.data.username)