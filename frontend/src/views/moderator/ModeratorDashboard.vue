<template>
  <div class="moderator-dashboard">
    <h1 class="text-3xl font-bold mb-6 text-gray-800 dark:text-gray-200">Moderator Dashboard</h1>
    <section>
      <h2 class="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-200">Reports</h2>
      <ReportList />
    </section>
    <section>
      <h2 class="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-200">Edit Bookmark/Video</h2>
      <EditLookup />
    </section>
    <!-- Audit log removed for moderators; only admins should see it -->
  </div>
</template>

<script setup>
// Import child components
import ReportList from './ReportList.vue'
import EditLookup from './EditLookup.vue'
// import AuditLogList from './AuditLogList.vue' // Only for admin dashboard
</script>

<style scoped>
.moderator-dashboard {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
}
section {
  margin-bottom: 2rem;
}
</style>
