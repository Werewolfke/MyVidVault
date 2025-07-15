// Add this route to your router/index.js or router.js
export default [
  {
    path: '/moderator',
    name: 'ModeratorDashboard',
    component: () => import('../views/moderator/ModeratorDashboard.vue'),
    meta: { requiresModerator: true },
  },
]
