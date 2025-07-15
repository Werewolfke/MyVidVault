<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
    <h2 class="text-2xl font-bold mb-4 text-gray-800 dark:text-gray-200">Moderation Reports</h2>
    <div v-if="loading" class="text-center py-6 text-gray-600 dark:text-gray-400">Loading reports...</div>
    <div v-else-if="reports.length === 0" class="text-center py-6 text-gray-500 dark:text-gray-400">No reports found.</div>
    <div v-else>
      <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead class="bg-gray-50 dark:bg-gray-900">
          <tr>
            <th class="px-4 py-2 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase">ID</th>
            <th class="px-4 py-2 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase">Type</th>
            <th class="px-4 py-2 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase">User</th>
            <th class="px-4 py-2 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase">Bookmark</th>
            <th class="px-4 py-2 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase">Status</th>
            <th class="px-4 py-2 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase">Actions</th>
          </tr>
        </thead>
        <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
          <tr v-for="report in reports" :key="report.id">
            <td class="px-4 py-2">{{ report.id }}</td>
            <td class="px-4 py-2">{{ report.report_type }}</td>
            <td class="px-4 py-2">{{ report.user || 'Unknown' }}</td>
            <td class="px-4 py-2">{{ report.bookmark || 'Unknown' }}</td>
            <td class="px-4 py-2">
              <span :class="report.is_resolved ? 'text-green-600 dark:text-green-400' : 'text-yellow-600 dark:text-yellow-400'">
                {{ report.is_resolved ? 'Resolved' : 'Open' }}
              </span>
            </td>
            <td class="px-4 py-2 flex gap-2">
              <button @click="approve(report.id)" :disabled="report.is_resolved" class="px-3 py-1 rounded bg-green-600 text-white hover:bg-green-700 disabled:opacity-50">Approve</button>
              <button @click="deny(report.id)" :disabled="report.is_resolved" class="px-3 py-1 rounded bg-red-600 text-white hover:bg-red-700 disabled:opacity-50">Deny</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/index.js'

const reports = ref([])
const loading = ref(true)

async function fetchReports() {
  loading.value = true
  try {
    const res = await api.get('/moderation/reports/')
    // If paginated, use res.data.results; else use res.data
    reports.value = res.data.results || res.data
  } catch (e) {
    reports.value = []
  }
  loading.value = false
}

onMounted(fetchReports)

async function approve(reportId) {
  await api.put('/moderation/approve/', { report_id: reportId })
  fetchReports()
}
async function deny(reportId) {
  await api.put('/moderation/deny/', { report_id: reportId })
  fetchReports()
}
</script>

<style scoped>
/* No custom styles needed, Tailwind handles all styling */
</style>
