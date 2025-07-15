

<template>
  <div class="min-h-screen flex flex-col bg-gradient-to-br from-gray-100/90 via-white/80 to-blue-50/80 dark:from-gray-900 dark:via-gray-800 dark:to-gray-700">
    <section class="w-full flex flex-col items-center justify-center flex-grow py-20 px-4">
      <img src="/logo.png" alt="MyVidVault Logo" class="mx-auto h-20 mb-8 drop-shadow" />
      <h1 class="text-5xl font-extrabold mb-6 text-gray-900 dark:text-white text-center">
        Welcome to <span class="bg-gradient-to-r from-indigo-500 to-blue-400 bg-clip-text text-transparent">MyVidVault</span>
      </h1>
      <p class="text-xl text-gray-700 dark:text-gray-300 mb-10 max-w-2xl mx-auto text-center">
        Your personal Vault. Save, organize, and discover the best videos from around the web.
      </p>
      <!-- Search Feature -->
      <div class="flex justify-center w-full mb-10">
        <div class="relative w-full max-w-2xl">
          <span class="absolute left-5 top-1/2 -translate-y-1/2 text-gray-400">
            <i class="fas fa-search"></i>
          </span>
          <input
            v-model="search"
            type="search"
            class="w-full py-5 pl-14 pr-4 rounded-full border-2 border-gray-200 bg-gray-50 text-gray-900 dark:bg-gray-900 dark:text-white dark:border-gray-700 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 text-xl transition"
            placeholder="Search public bookmarks by title, user, or tag..."
            @keyup.enter="onSearch"
          />
          <button
            class="absolute right-3 top-1/2 -translate-y-1/2 px-6 py-3 rounded-full bg-blue-600 text-white font-semibold shadow hover:bg-blue-700 transition"
            @click="onSearch"
          >
            Search
          </button>
        </div>
      </div>
      <div class="flex flex-col sm:flex-row gap-4 justify-center mb-6">
        <template v-if="!isLoggedIn">
          <router-link to="/register" class="inline-block px-10 py-4 rounded-full font-semibold bg-blue-600 text-white shadow-lg hover:bg-blue-700 transition text-lg">
            Create Your Vault
          </router-link>
          <router-link to="/login" class="inline-block px-10 py-4 rounded-full font-semibold bg-white text-blue-600 border border-blue-600 shadow hover:bg-blue-50 transition text-lg">
            Sign In
          </router-link>
        </template>
        <template v-else>
          <router-link :to="{ name: 'user-profile', params: { username: username } }" class="inline-block px-10 py-4 rounded-full font-semibold bg-blue-600 text-white shadow-lg hover:bg-blue-700 transition text-lg">
            My Vault
          </router-link>
        </template>
      </div>
      <div class="mt-12 text-center">
        <h2 class="text-3xl font-bold mb-4 text-gray-800 dark:text-gray-200">Why MyVidVault?</h2>
        <p class="text-lg text-gray-600 dark:text-gray-400 mb-8">Organize your favorite videos, create collections, and share with friends. Join a community of Vault enthusiasts.</p>
        <router-link to="/explore" class="inline-block px-8 py-3 rounded-full font-medium border border-blue-600 text-blue-600 bg-white hover:bg-blue-50 transition text-lg">
          Explore Public Bookmarks
        </router-link>
      </div>
    </section>
  </div>
</template>

<script>
import { computed } from 'vue';
import { useAuthStore } from '@/stores/auth';

export default {
  name: 'Home',
  data() {
    return {
      search: ''
    };
  },
  computed: {
    isLoggedIn() {
      return useAuthStore().isAuthenticated;
    },
    username() {
      return useAuthStore().user?.username;
    }
  },
  methods: {
    onSearch() {
      if (this.search.trim()) {
        this.$router.push({ name: 'explore', query: { q: this.search.trim() } });
      }
    }
  }
};
</script>

<!-- No custom CSS needed, all styling is Tailwind utility classes -->