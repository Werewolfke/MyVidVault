<template>
  <div class="min-h-screen flex flex-col bg-gradient-to-br from-gray-100/90 via-white/80 to-blue-50/80 dark:from-gray-900 dark:via-gray-800 dark:to-gray-700">
    <!-- Header -->
    <header class="sticky top-0 z-50 bg-white/70 backdrop-blur-md shadow-md dark:bg-gray-800">
      <div class="container mx-auto">
        <div class="flex items-center justify-between h-16 px-4 gap-2">
          <!-- Logo & Brand -->
          <router-link :to="{ name: 'home' }" class="flex items-center gap-2 group">
            <img src="/logo.png" alt="Site Logo" class="site-logo rounded-lg shadow-sm" />
            <span class="ml-2 px-2 py-0.5 rounded-full bg-blue-100/80 text-xs font-semibold text-blue-700 uppercase tracking-wider shadow-sm">Beta</span>
          </router-link>
          <!-- Navigation & Actions -->
          <div class="flex-1 flex items-center justify-center">
            <nav class="hidden md:flex items-center gap-3">
              <router-link :to="{ name: 'home' }" class="text-base font-medium text-gray-700 hover:text-blue-600 transition">Home</router-link>
              <router-link :to="{ name: 'explore' }" class="text-base font-medium text-gray-700 hover:text-blue-600 transition">Explore</router-link>
              <router-link v-if="isLoggedIn && username" :to="{ name: 'user-profile', params: { username: username } }" class="text-base font-medium text-gray-700 hover:text-blue-600 transition">Profile</router-link>
    <router-link v-if="isModerator" to="/moderator" class="text-base font-medium text-gray-700 hover:text-blue-600 transition">Moderator Tools</router-link>
            </nav>
          </div>
          <!-- Top Right Actions -->
          <div class="flex items-center gap-2">
            <button v-if="isLoggedIn" @click="goToAddBookmark" class="inline-flex items-center px-3 py-1.5 rounded-full text-base font-semibold bg-blue-600 text-white shadow-lg hover:bg-blue-700 transition focus:outline-none focus:ring-2 focus:ring-blue-400">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
              </svg>
              Add Bookmark
            </button>
            <div class="hidden md:flex items-center gap-2">
              <template v-if="!isLoggedIn">
                <router-link :to="{ name: 'login' }" class="px-4 py-1.5 rounded-full text-base font-medium text-gray-800 bg-white/70 shadow hover:bg-blue-50/80 transition focus:outline-none focus:ring-2 focus:ring-blue-400/40">Log in</router-link>
                <router-link :to="{ name: 'register' }" class="px-4 py-1.5 rounded-full text-base font-semibold bg-blue-600/90 text-white shadow-lg hover:bg-blue-700/90 transition focus:outline-none focus:ring-2 focus:ring-blue-400/40">Sign up</router-link>
              </template>
              <template v-else>
                <button @click="handleLogout" class="px-4 py-1.5 rounded-full text-base font-medium text-gray-800 bg-white/70 shadow hover:bg-red-50/80 transition focus:outline-none focus:ring-2 focus:ring-red-400/40">Log out</button>
              </template>
            </div>
            <!-- Mobile Hamburger -->
            <button class="md:hidden flex items-center justify-center p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-400" @click="mobileNavOpen = !mobileNavOpen" aria-label="Open navigation">
              <svg v-if="!mobileNavOpen" class="w-7 h-7 text-gray-700" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16"/>
              </svg>
              <svg v-else class="w-7 h-7 text-gray-700" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
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
              class="flex items-center px-3 py-2 rounded-md text-base font-medium text-gray-800 hover:bg-gray-100 transition-colors"
            >Home</router-link>
            <router-link
              :to="{ name: 'explore' }"
              @click="mobileNavOpen = false"
              class="flex items-center px-3 py-2 rounded-md text-base font-medium text-gray-800 hover:bg-gray-100 transition-colors"
            >Explore</router-link>
            <router-link
              v-if="isLoggedIn && username"
              :to="{ name: 'user-profile', params: { username: username } }"
              @click="mobileNavOpen = false"
              class="flex items-center px-3 py-2 rounded-md text-base font-medium text-gray-800 hover:bg-gray-100 transition-colors"
            >Profile</router-link>
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
    <main class="flex-grow w-full">
      <router-view v-slot="{ Component, route }">
        <template v-if="route.meta && route.meta.fullPage">
          <component :is="Component" />
        </template>
        <template v-else>
          <div class="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <component :is="Component" />
          </div>
        </template>
      </router-view>
    </main>

    <!-- Footer -->
    <footer class="bg-white/80 border-t border-gray-200 shadow-inner mt-auto dark:bg-gray-800 dark:border-gray-700">
      <div class="container mx-auto px-4 py-4 flex flex-col md:flex-row items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <img src="/logo.png" alt="MyVidVault Logo" class="h-8 aspect-square object-contain drop-shadow-md" />
          <span class="text-gray-700 text-sm dark:text-gray-300">&copy; {{ currentYear }} MyVidVault</span>
        </div>
        <div class="flex items-center gap-4">
          <a href="https://discord.gg/eevztZDqg3" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 transition" title="Discord">
            <i class="fab fa-discord fa-lg"></i>
          </a>
          <a href="https://x.com/Myvidvault" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 transition" title="Twitter">
            <i class="fab fa-twitter fa-lg"></i>
          </a>
          <a href="https://throne.com/myvidvault" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 transition" title="Support">
            <i class="fas fa-heart fa-lg"></i>
          </a>
        </div>
        <div class="flex items-center gap-4 text-sm">
          <router-link :to="{ name: 'privacy' }" class="text-gray-700 hover:text-blue-600 transition dark:text-gray-300">Privacy</router-link>
          <router-link :to="{ name: 'terms' }" class="text-gray-700 hover:text-blue-600 transition dark:text-gray-300">Terms</router-link>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { ref, computed } from 'vue';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const auth = useAuthStore();
const currentYear = new Date().getFullYear();
const mobileNavOpen = ref(false);

// Simple computed properties
const isLoggedIn = computed(() => auth.isAuthenticated);
const user = computed(() => auth.user || {});
const username = computed(() => user.value.username || '');
const isModerator = computed(() => user.value.is_moderator === true);

// Simple logout
const handleLogout = async () => {
  await auth.logout();
  auth.stopAutoRefresh();
  router.push({ name: 'home' });
  mobileNavOpen.value = false;
};

// Simple navigation
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
