/**
 * Configuration Vue Router pour CMDB Inventory
 */

import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/modules/auth'

// Import des vues (lazy loading pour optimiser les performances)
const Dashboard = () => import('@/views/Dashboard.vue')
const Assets = () => import('@/views/Assets.vue')
const AssetDetail = () => import('@/views/AssetDetail.vue')
const AssetForm = () => import('@/views/AssetForm.vue')
const ScanQR = () => import('@/views/ScanQR.vue')
const Locations = () => import('@/views/Locations.vue')
const Categories = () => import('@/views/Categories.vue')
const Brands = () => import('@/views/Brands.vue')
const Tags = () => import('@/views/Tags.vue')
const Login = () => import('@/views/Login.vue')
const NotFound = () => import('@/views/NotFound.vue')

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: {
      requiresAuth: true,
      breadcrumb: 'Dashboard',
      title: 'Dashboard - CMDB Inventory'
    }
  },
  {
    path: '/assets',
    name: 'Assets',
    component: Assets,
    meta: {
      requiresAuth: true,
      breadcrumb: 'Équipements',
      title: 'Équipements - CMDB Inventory'
    }
  },
  {
    path: '/assets/new',
    name: 'AssetCreate',
    component: AssetForm,
    meta: {
      requiresAuth: true,
      breadcrumb: 'Nouvel équipement',
      title: 'Nouvel équipement - CMDB Inventory'
    }
  },
  {
    path: '/assets/:id',
    name: 'AssetDetail',
    component: AssetDetail,
    meta: {
      requiresAuth: true,
      breadcrumb: 'Détail équipement',
      title: 'Détail équipement - CMDB Inventory'
    },
    props: true
  },
  {
    path: '/assets/:id/edit',
    name: 'AssetEdit',
    component: AssetForm,
    meta: {
      requiresAuth: true,
      breadcrumb: 'Modifier équipement',
      title: 'Modifier équipement - CMDB Inventory'
    },
    props: true
  },
  {
    path: '/scan',
    name: 'Scan',
    component: ScanQR,
    meta: {
      requiresAuth: true,
      breadcrumb: 'Scanner QR',
      title: 'Scanner QR - CMDB Inventory',
      mobileOptimized: true
    }
  },
  {
    path: '/locations',
    name: 'Locations',
    component: Locations,
    meta: {
      requiresAuth: true,
      breadcrumb: 'Emplacements',
      title: 'Emplacements - CMDB Inventory'
    }
  },
  {
    path: '/categories',
    name: 'Categories',
    component: Categories,
    meta: {
      requiresAuth: true,
      breadcrumb: 'Catégories',
      title: 'Catégories - CMDB Inventory'
    }
  },
  {
    path: '/brands',
    name: 'Brands',
    component: Brands,
    meta: {
      requiresAuth: true,
      breadcrumb: 'Marques',
      title: 'Marques - CMDB Inventory'
    }
  },
  {
    path: '/tags',
    name: 'Tags',
    component: Tags,
    meta: {
      requiresAuth: true,
      breadcrumb: 'Étiquettes',
      title: 'Étiquettes - CMDB Inventory'
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: {
      requiresAuth: false,
      hideNavigation: true,
      title: 'Connexion - CMDB Inventory'
    }
  },
  {
    path: '/404',
    name: 'NotFound',
    component: NotFound,
    meta: {
      title: 'Page non trouvée - CMDB Inventory'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/404'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // Comportement de défilement personnalisé
    if (savedPosition) {
      return savedPosition
    } else if (to.hash) {
      return {
        el: to.hash,
        behavior: 'smooth'
      }
    } else {
      return { top: 0 }
    }
  }
})

// Guards de navigation
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Mettre à jour le titre de la page
  if (to.meta.title) {
    document.title = to.meta.title
  }
  
  // Vérifier l'authentification
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      // Essayer de restaurer la session depuis le localStorage
      const token = localStorage.getItem('auth_token')
      if (token) {
        try {
          await authStore.restoreSession(token)
          next()
        } catch (error) {
          console.error('Erreur lors de la restauration de session:', error)
          next('/login')
        }
      } else {
        next('/login')
      }
    } else {
      next()
    }
  } else {
    // Route publique
    if (to.name === 'Login' && authStore.isAuthenticated) {
      // Rediriger vers le dashboard si déjà connecté
      next('/')
    } else {
      next()
    }
  }
})

router.afterEach((to, from) => {
  // Analytics ou tracking (optionnel)
  if (import.meta.env.PROD) {
    // Exemple: gtag('config', 'GA_MEASUREMENT_ID', { page_path: to.path })
  }
  
  // Ajouter une classe CSS pour les pages mobile-optimized
  if (to.meta.mobileOptimized) {
    document.body.classList.add('mobile-optimized')
  } else {
    document.body.classList.remove('mobile-optimized')
  }
})

// Gestion des erreurs de navigation
router.onError((error) => {
  console.error('Erreur de navigation:', error)
  
  // En production, envoyer l'erreur à un service de monitoring
  if (import.meta.env.PROD) {
    // Exemple: Sentry.captureException(error)
  }
})

export default router