import { createRouter, createWebHistory } from 'vue-router';
import LandingPage from '../views/LandingPage.vue';

const routes = [
  {
    path: '/',
    redirect: '/home'
  },
  {
    path: '/landing',
    name: 'LandingPage',
    component: LandingPage
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/assets',
    name: 'Assets',
    component: () => import('../views/Assets.vue')
  },
  {
    path: '/assets/new',
    name: 'AssetCreate',
    component: () => import('../views/AssetForm.vue')
  },
  {
    path: '/assets/:id',
    name: 'AssetDetail',
    component: () => import('../views/AssetDetail.vue'),
    props: true
  },
  {
    path: '/assets/:id/edit',
    name: 'AssetEdit',
    component: () => import('../views/AssetForm.vue'),
    props: true
  },
  {
    path: '/scan',
    name: 'ScanQR',
    component: () => import('../views/ScanQR.vue')
  },
  {
    path: '/locations',
    name: 'Locations',
    component: () => import('../views/Locations.vue')
  },
  {
    path: '/categories',
    name: 'Categories',
    component: () => import('../views/Categories.vue')
  },
  {
    path: '/brands',
    name: 'Brands',
    component: () => import('../views/Brands.vue')
  },
  {
    path: '/tags',
    name: 'Tags',
    component: () => import('../views/Tags.vue')
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue')
  },
  {
    path: '/stats',
    name: 'DashboardStats',
    component: () => import('../views/Dashboard.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  // Route 404 pour les chemins non trouvés
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue')
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL || '/'),
  routes
});

export default router;