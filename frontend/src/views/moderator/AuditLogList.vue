<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
    <h3 class="text-xl font-bold mb-4 text-gray-800 dark:text-gray-200">Moderator Audit Log</h3>
    <div v-if="loading" class="text-center py-6 text-gray-600 dark:text-gray-400">Loading audit log...</div>
    <div v-else>
      <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead class="bg-gray-50 dark:bg-gray-900">
          <tr>
            <th class="px-4 py-2 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase">Time</th>
            <th class="px-4 py-2 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase">Moderator</th>
            <th class="px-4 py-2 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase">Action</th>
            <th class="px-4 py-2 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase">Details</th>
          </tr>
        </thead>
        <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
          <tr v-for="log in logs" :key="log.id">
            <td class="px-4 py-2">{{ log.created_at }}</td>
            <td class="px-4 py-2">{{ log.moderator }}</td>
            <td class="px-4 py-2">{{ log.action }}</td>
            <td class="px-4 py-2">{{ log.details }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/index.js'

const logs = ref([])
const loading = ref(true)

async function fetchLogs() {
  loading.value = true
  const res = await api.get('/moderation/audit-log/')
  logs.value = res.data
  loading.value = false
}

onMounted(fetchLogs)
</script>

<style scoped>
/* No custom styles needed, Tailwind handles all styling */
</style>
