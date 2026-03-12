import { createRouter, createWebHistory } from 'vue-router';
import LandingPage from '../views/LandingPage.vue';

const routes = [
  {
    path: '/',
    name: 'LandingPage',
    component: LandingPage
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('../views/Home.vue')
  }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
});

export default router;