<template>
  <div class="text-center py-12">
    <h2 class="text-2xl font-semibold mb-6 text-gray-800 dark:text-gray-200">Contact Us</h2>
    <div class="mb-6 text-gray-600 dark:text-gray-400">
      Our contact form is currently unavailable.<br>
      Please email us directly at
      <a href="mailto:myvidvault506@gmail.com" class="text-indigo-600 underline dark:text-indigo-400">myvidvault506@gmail.com</a>
    </div>
  </div>
</template>

<script setup>
// No logic needed while form is disabled
</script>

<style scoped>
select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e");
  background-position: right 0.5rem center;
  background-repeat: no-repeat;
  background-size: 1.5em 1.5em;
  padding-right: 2.5rem;
}
.dark select {
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%239ca3af' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e"); /* Dark mode arrow color */
}
</style>