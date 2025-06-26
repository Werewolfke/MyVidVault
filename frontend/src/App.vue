<template>
  <div class="min-h-screen flex flex-col bg-gradient-to-br from-gray-100/90 via-white/80 to-blue-50/80 dark:from-gray-900 dark:via-gray-800 dark:to-gray-700">
    <!-- Header -->
    <header class="sticky top-0 z-50 bg-white/70 backdrop-blur-md shadow-md dark:bg-gray-800">
      <div class="container mx-auto">
        <div class="flex items-center justify-between h-16 px-4">
          <!-- Logo -->
          <router-link :to="{ name: 'home' }" class="flex items-center space-x-2 group">
            <img src="/logo.png" alt="Site Logo" class="site-logo" />
            <span class="ml-2 px-2 py-0.5 rounded-full bg-blue-100/70  text-xs font-semibold text-blue-700  uppercase tracking-wider shadow-sm">
              Beta
            </span>
          </router-link>
          <!-- Desktop Navigation -->
          <nav class="hidden md:flex items-center space-x-4">
            <router-link
              :to="{ name: 'home' }"
              class="text-sm font-medium text-gray-700  hover:text-blue-600  transition"
            >
              Home
            </router-link>
            <router-link
              v-if="isLoggedIn"
              :to="{ name: 'user-profile', params: { username: username } }"
              class="text-sm font-medium text-gray-700  hover:text-blue-600  transition"
            >
              Profile
            </router-link>
            <button
              v-if="isLoggedIn"
              @click="goToAddBookmark"
              class="inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium bg-blue-600/90 text-white shadow-lg hover:bg-blue-700/90 transition focus:outline-none focus:ring-2 focus:ring-blue-400/40"
            >
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
              </svg>
              Add Bookmark
            </button>
          </nav>
          <!-- Mobile Hamburger -->
          <button
            class="md:hidden flex items-center justify-center p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
            @click="mobileNavOpen = !mobileNavOpen"
            aria-label="Open navigation"
          >
            <svg v-if="!mobileNavOpen" class="w-7 h-7 text-gray-700 " fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16"/>
            </svg>
            <svg v-else class="w-7 h-7 text-gray-700 " fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
          <!-- Auth Buttons (Desktop) -->
          <div class="hidden md:flex items-center space-x-2">
            <template v-if="!isLoggedIn">
              <router-link
                :to="{ name: 'login' }"
                class="px-4 py-1.5 rounded-full text-sm font-medium text-gray-800  bg-white/60  shadow hover:bg-blue-50/80  transition focus:outline-none focus:ring-2 focus:ring-blue-400/40"
              >
                Log in
              </router-link>
              <router-link
                :to="{ name: 'register' }"
                class="px-4 py-1.5 rounded-full text-sm font-semibold bg-blue-600/90 text-white shadow-lg hover:bg-blue-700/90 transition focus:outline-none focus:ring-2 focus:ring-blue-400/40"
              >
                Sign up
              </router-link>
            </template>
            <template v-else>
              <button
                @click="handleLogout"
                class="px-4 py-1.5 rounded-full text-sm font-medium text-gray-800  bg-white/60  shadow hover:bg-red-50/80  transition focus:outline-none focus:ring-2 focus:ring-red-400/40"
              >
                Log out
              </button>
            </template>
          </div>
        </div>
      </div>
    </header>

    <!-- Mobile slide-out menu -->
    <transition name="slide">
      <div v-if="mobileNavOpen" class="md:hidden fixed top-16 inset-x-0 bottom-0 z-40">
        <!-- Overlay -->
        <div @click="mobileNavOpen = false" class="absolute inset-0 bg-black/40 backdrop-blur-sm" aria-hidden="true"></div>

        <!-- Menu panel -->
        <div class="relative flex w-full max-w-xs flex-col h-full bg-white  p-4 sm:p-6 shadow-2xl">
          <!-- Navigation Links -->
          <nav class="flex-1 space-y-2">
            <router-link
              :to="{ name: 'home' }"
              @click="mobileNavOpen = false"
              class="flex items-center px-3 py-2 rounded-md text-base font-medium text-gray-800  hover:bg-gray-100  transition-colors"
            >
              Home
            </router-link>

            <router-link
              v-if="isLoggedIn"
              :to="{ name: 'user-profile', params: { username: username } }"
              @click="mobileNavOpen = false"
              class="flex items-center px-3 py-2 rounded-md text-base font-medium text-gray-800  hover:bg-gray-100  transition-colors"
            >
              Profile
            </router-link>
          </nav>

          <!-- Actions and Auth -->
          <div class="mt-auto pt-6 border-t border-gray-200/80 ">
            <div class="space-y-3">
              <button
                v-if="isLoggedIn"
                @click="goToAddBookmark"
                class="w-full inline-flex items-center justify-center px-4 py-2.5 rounded-lg text-base font-medium bg-blue-600/90 text-white shadow-lg hover:bg-blue-700/90 transition"
              >
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
                </svg>
                Add Bookmark
              </button>
              <template v-if="!isLoggedIn">
                <router-link
                  :to="{ name: 'login' }"
                  @click="mobileNavOpen = false"
                  class="w-full flex items-center justify-center px-4 py-2.5 rounded-lg text-base font-medium text-gray-800  bg-gray-100  hover:bg-gray-200  transition"
                >
                  Log in
                </router-link>
                <router-link
                  :to="{ name: 'register' }"
                  @click="mobileNavOpen = false"
                  class="w-full flex items-center justify-center px-4 py-2.5 rounded-lg text-base font-semibold bg-blue-600/90 text-white shadow-lg hover:bg-blue-700/90 transition"
                >
                  Sign up
                </router-link>
              </template>
              <button
                v-else
                @click="handleLogout"
                class="w-full flex items-center justify-center px-4 py-2.5 rounded-lg text-base font-medium text-gray-800  bg-gray-100  hover:bg-gray-200  transition"
              >
                Log out
              </button>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- Main Content -->
    <main class="flex-grow container mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="rounded-2xl bg-white/80 shadow-xl border border-gray-200/60 backdrop-blur-lg transition-all dark:bg-gray-800 dark:border-gray-700">
        <div class="p-4 sm:p-6">
          <router-view />
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="bg-white/70 backdrop-blur-md border-t border-gray-200/60 shadow-inner mt-auto dark:bg-gray-800 dark:border-gray-700">
      <div class="container mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
          <!-- Brand -->
          <div class="col-span-1 md:col-span-2">
            <div class="flex items-center mb-4">
              <img src="/logo.png" alt="MyVidVault Logo"
                class="h-9 aspect-square object-contain drop-shadow-md" />
            </div>
            <p class="text-gray-700  text-sm mb-4 max-w-md">
              Your personal video collection manager. Save, organize, and discover videos from across the web in one convenient place.
            </p>
            <!-- Social Icons -->
            <div class="flex space-x-4">
              <a href="https://discord.gg/eevztZDqg3" target="_blank" rel="noopener noreferrer"
                class="rounded-full bg-white/70  p-2 shadow hover:bg-blue-100/80  transition">
                <span class="sr-only">Discord</span>
                <svg class="h-6 w-6 text-blue-600 " fill="currentColor" viewBox="0 0 24 24">
                  <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028 14.09 14.09 0 0 0 1.226-1.994.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"></path>
                </svg>
              </a>
              <a href="https://x.com/Myvidvault" target="_blank" rel="noopener noreferrer"
                class="rounded-full bg-white/70  p-2 shadow hover:bg-blue-100/80  transition">
                <span class="sr-only">Twitter</span>
                <svg class="h-6 w-6 text-blue-600 " fill="currentColor" viewBox="0 0 24 24">
                  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"></path>
                </svg>
              </a>
            </div>
          </div>
          <!-- Links Column 1 -->
          <div class="col-span-1">
            <h3 class="text-sm font-semibold uppercase tracking-wider text-gray-500  mb-4">
              Resources
            </h3>
            <ul class="space-y-2">
              <li>
                <router-link :to="{ name: 'contact' }"
                  class="text-base text-gray-700 hover:text-blue-600   transition">
                  Contact Us
                </router-link>
              </li>
              <li>
                <router-link :to="{ name: 'careers' }"
                  class="text-base text-blue-700 hover:underline  ">
                  Volunteer Opportunities
                </router-link>
              </li>
            </ul>
          </div>
          <!-- Links Column 2 -->
          <div class="col-span-1">
            <h3 class="text-sm font-semibold uppercase tracking-wider text-gray-500  mb-4">
              Legal
            </h3>
            <ul class="space-y-2">
              <li>
                <router-link :to="{ name: 'privacy' }"
                  class="text-base text-gray-700 hover:text-blue-600   transition">
                  Privacy Policy
                </router-link>
              </li>
              <li>
                <router-link :to="{ name: 'terms' }"
                  class="text-base text-gray-700 hover:text-blue-600   transition">
                  Terms of Service
                </router-link>
              </li>
            </ul>
          </div>
        </div>
        <div class="mt-8 pt-4 border-t border-gray-200  text-center">
          <p class="text-sm text-gray-500 ">
            &copy; {{ currentYear }} MyVidVault. All rights reserved.
          </p>
          <p class="mt-2 text-sm">
            <a href="https://throne.com/myvidvault" target="_blank" rel="noopener noreferrer"
              class="text-blue-600  hover:underline">
              Support MyVidVault
            </a>
          </p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { ref, computed } from 'vue';
import { logout as apiLogout } from '@/api/index.js';
import { isLoggedIn, updateAuthState, username as authUsername } from '@/composables/useAuthState.js';

const router = useRouter();
const currentYear = new Date().getFullYear();
const mobileNavOpen = ref(false);

// Get the username from auth state or localStorage
const username = computed(() => authUsername.value || localStorage.getItem('username'));

const handleLogout = async () => {
  try {
    await apiLogout();
    updateAuthState();
    router.push({ name: 'home' });
  } catch (e) {
    updateAuthState();
    router.push({ name: 'home' });
  }
  mobileNavOpen.value = false;
};

const goToAddBookmark = () => {
  router.push({ name: 'CreateBookmark' });
  mobileNavOpen.value = false;
};
</script>

<style>
.site-logo {
    height: 2.5rem;
    width: auto;
    display: block;
    margin: 0 auto;
}
.slide-enter-active, .slide-leave-active {
  transition: transform 0.25s cubic-bezier(.4,0,.2,1), opacity 0.2s;
}
.slide-enter-from, .slide-leave-to {
  transform: translateX(-100%);
  opacity: 0;
}
.slide-enter-to, .slide-leave-from {
  transform: translateX(0%);
  opacity: 1;
}
</style>
