import { createRouter, createWebHistory } from 'vue-router';
import Home from '@/views/Home.vue';
import Explore from '@/views/Explore.vue';
import BookmarkDetailView from '@/views/bookmarks/BookmarkDetailView.vue';
import UserProfileView from '@/views/user/UserProfileView.vue';
import CreateBookmarkView from '@/views/bookmarks/CreateBookmarkView.vue';

// Website pages
import Careers from '../views/website/Careers.vue'
import ContactView from '../views/website/ContactView.vue'
import ForgotPasswordView from '../views/website/ForgotPasswordView.vue'
import LoginView from '../views/website/LoginView.vue'
import PrivacyView from '../views/website/PrivacyView.vue'
import RegisterView from '../views/website/RegisterView.vue'
import ResetPasswordConfirmView from '../views/website/ResetPasswordConfirmView.vue'
import TermsView from '../views/website/TermsView.vue'
import moderatorRoutes from './moderator.js'

const routes = [
  {
    path: '/',
    name: 'home',
    component: Home,
    meta: { fullPage: true },
  },
  {
    path: '/explore',
    name: 'explore',
    component: Explore,
  },
  {
    path: '/bookmarks/:id',
    name: 'bookmark-detail',
    component: BookmarkDetailView,
    props: true,
  },
  { path: '/careers', name: 'careers', component: Careers },
  { path: '/contact', name: 'contact', component: ContactView },
  { path: '/forgot-password', name: 'forgot-password', component: ForgotPasswordView },
  { path: '/login', name: 'login', component: LoginView },
  { path: '/privacy', name: 'privacy', component: PrivacyView },
  { path: '/register', name: 'register', component: RegisterView },
  {
    path: '/reset-password/:uidb64/:token',
    name: 'reset-password-confirm',
    component: ResetPasswordConfirmView,
    props: true,
  },
  {
    path: '/reset-password-confirm',
    name: 'reset-password-confirm-query',
    component: ResetPasswordConfirmView,
  },
  { path: '/terms', name: 'terms', component: TermsView },
  {
    path: '/users/:username',
    name: 'user-profile',
    component: UserProfileView,
    props: true,
  },
  {
    // Redirect incorrect singular 'user' to correct plural 'users'
    path: '/user/:username',
    redirect: to => {
      return { name: 'user-profile', params: { username: to.params.username } }
    }
  },
  // Removed /profile/me route; use /users/:username for profile
  {
    path: '/bookmarks/create',
    name: 'CreateBookmark',
    component: CreateBookmarkView,
    meta: { requiresAuth: true }
  },
  // All previous routes
  ...moderatorRoutes,
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Add debug logging to see route changes
router.beforeEach((to, from, next) => {
  console.log('Router navigation:', { 
    from: from.fullPath, 
    to: to.fullPath,
    toName: to.name,
    toParams: to.params 
  });
  next();
});

export default router;
