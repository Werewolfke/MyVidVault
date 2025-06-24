<template>
  <div class="text-center py-12">
    <h2 class="text-2xl font-semibold mb-6 text-gray-800 dark:text-gray-200">Contact Us</h2>
    <div class="mb-6 text-gray-600 dark:text-gray-300">
      Our contact form is currently unavailable.<br>
      Please email us directly at
      <a href="mailto:myvidvault506@gmail.com" class="text-indigo-600 underline">myvidvault506@gmail.com</a>
    </div>
    <form class="opacity-50 pointer-events-none select-none">
      <div class="mb-4">
        <label for="name" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Name</label>
        <input type="text" id="name" disabled class="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-gray-100 dark:bg-gray-800" />
      </div>
      <div class="mb-4">
        <label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Email</label>
        <input type="email" id="email" disabled class="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-gray-100 dark:bg-gray-800" />
      </div>
      <div class="mb-4">
        <label for="subject" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Reason for Contact</label>
        <select id="subject" disabled class="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-gray-100 dark:bg-gray-800">
          <option>-- Please select a reason --</option>
        </select>
      </div>
      <div class="mb-6">
        <label for="message" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Message</label>
        <textarea id="message" rows="5" disabled class="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-gray-100 dark:bg-gray-800"></textarea>
      </div>
      <div class="flex justify-end">
        <button type="submit" disabled class="px-4 py-2 bg-indigo-400 text-white rounded-md opacity-50 cursor-not-allowed">Send Message</button>
      </div>
    </form>
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