<template>
  <div id="app" class="app-container">
    <!-- Sidebar Navigation -->
    <nav class="sidebar" :class="{ collapsed: sidebarCollapsed, show: sidebarVisible }">
      <div class="sidebar-header p-3">
        <h5 class="text-white mb-0" v-if="!sidebarCollapsed">
          <i class="bi bi-boxes me-2"></i>
          CMDB Inventory
        </h5>
        <i class="bi bi-boxes text-white fs-4" v-else></i>
      </div>
      
      <ul class="sidebar-nav nav flex-column">
        <li class="nav-item">
          <router-link :to="{ name: 'Dashboard' }" class="nav-link" :class="{ active: $route.name === 'Dashboard' }">
            <i class="bi bi-speedometer2"></i>
            <span>Dashboard</span>
          </router-link>
        </li>
        <li class="nav-item">
          <router-link to="/assets" class="nav-link" :class="{ active: $route.name === 'Assets' }">
            <i class="bi bi-laptop"></i>
            <span>Équipements</span>
          </router-link>
        </li>
        <li class="nav-item">
          <router-link to="/scan" class="nav-link" :class="{ active: $route.name === 'Scan' }">
            <i class="bi bi-qr-code-scan"></i>
            <span>Scanner QR</span>
          </router-link>
        </li>
        <li class="nav-item">
          <router-link to="/locations" class="nav-link" :class="{ active: $route.name === 'Locations' }">
            <i class="bi bi-geo-alt"></i>
            <span>Emplacements</span>
          </router-link>
        </li>
        <li class="nav-item">
          <router-link to="/categories" class="nav-link" :class="{ active: $route.name === 'Categories' }">
            <i class="bi bi-tags"></i>
            <span>Catégories</span>
          </router-link>
        </li>
        <li class="nav-item">
          <router-link to="/brands" class="nav-link" :class="{ active: $route.name === 'Brands' }">
            <i class="bi bi-award"></i>
            <span>Marques</span>
          </router-link>
        </li>
        <li class="nav-item">
          <router-link to="/tags" class="nav-link" :class="{ active: $route.name === 'Tags' }">
            <i class="bi bi-bookmark"></i>
            <span>Étiquettes</span>
          </router-link>
        </li>
      </ul>
      
      <!-- User Section -->
      <div class="sidebar-footer mt-auto p-3" v-if="!sidebarCollapsed">
        <div class="d-flex align-items-center text-white">
          <i class="bi bi-person-circle me-2"></i>
          <div class="flex-grow-1">
            <div class="fw-bold">{{ user.username || 'Utilisateur' }}</div>
            <small class="opacity-75">{{ user.email || 'user@example.com' }}</small>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="main-content" :class="{ expanded: sidebarCollapsed }">
      <!-- Top Navbar -->
      <nav class="navbar navbar-expand-lg navbar-light navbar-custom">
        <div class="container-fluid">
          <!-- Sidebar Toggle -->
          <button 
            class="btn btn-outline-secondary me-3"
            @click="toggleSidebar"
            type="button"
          >
            <i class="bi bi-list"></i>
          </button>

          <!-- Mobile Sidebar Toggle -->
          <button 
            class="btn btn-outline-secondary d-lg-none me-3"
            @click="toggleMobileSidebar"
            type="button"
          >
            <i class="bi bi-menu-button-wide"></i>
          </button>

          <!-- Search Bar -->
          <div class="flex-grow-1 me-3">
            <div class="input-group" style="max-width: 400px;">
              <input 
                type="text" 
                class="form-control" 
                placeholder="Rechercher un équipement..."
                v-model="searchQuery"
                @keyup.enter="performSearch"
              >
              <button class="btn btn-outline-secondary" @click="performSearch">
                <i class="bi bi-search"></i>
              </button>
            </div>
          </div>

          <!-- Notifications -->
          <div class="dropdown me-3">
            <button 
              class="btn btn-outline-secondary position-relative"
              type="button"
              data-bs-toggle="dropdown"
            >
              <i class="bi bi-bell"></i>
              <span 
                class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger"
                v-if="notifications.length > 0"
              >
                {{ notifications.length }}
              </span>
            </button>
            <ul class="dropdown-menu dropdown-menu-end">
              <li v-if="notifications.length === 0">
                <span class="dropdown-item-text">Aucune notification</span>
              </li>
              <li v-for="notification in notifications" :key="notification.id">
                <a class="dropdown-item" href="#">
                  <div class="fw-bold">{{ notification.title }}</div>
                  <small class="text-muted">{{ notification.message }}</small>
                </a>
              </li>
            </ul>
          </div>

          <!-- User Menu -->
          <div class="dropdown">
            <button 
              class="btn btn-outline-secondary"
              type="button"
              data-bs-toggle="dropdown"
            >
              <i class="bi bi-person-circle"></i>
            </button>
            <ul class="dropdown-menu dropdown-menu-end">
              <li><a class="dropdown-item" href="#"><i class="bi bi-person me-2"></i>Profil</a></li>
              <li><a class="dropdown-item" href="#"><i class="bi bi-gear me-2"></i>Paramètres</a></li>
              <li><hr class="dropdown-divider"></li>
              <li><a class="dropdown-item" href="#" @click="logout"><i class="bi bi-box-arrow-right me-2"></i>Déconnexion</a></li>
            </ul>
          </div>
        </div>
      </nav>

      <!-- Page Content -->
      <div class="container-fluid p-4">
        <!-- Breadcrumb -->
        <nav aria-label="breadcrumb" v-if="breadcrumbs.length > 0">
          <ol class="breadcrumb">
            <li 
              v-for="(crumb, index) in breadcrumbs" 
              :key="index"
              class="breadcrumb-item"
              :class="{ active: index === breadcrumbs.length - 1 }"
            >
              <router-link v-if="crumb.to && index !== breadcrumbs.length - 1" :to="crumb.to">
                {{ crumb.text }}
              </router-link>
              <span v-else>{{ crumb.text }}</span>
            </li>
          </ol>
        </nav>

        <!-- Router View -->
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>

    <!-- Mobile Overlay -->
    <div 
      class="position-fixed top-0 start-0 w-100 h-100 bg-dark bg-opacity-50 d-lg-none"
      v-if="sidebarVisible"
      @click="closeMobileSidebar"
      style="z-index: 999;"
    ></div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/modules/auth'
import { useToast } from 'vue-toastification'

export default {
  name: 'App',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const authStore = useAuthStore()
    const toast = useToast()

    // État réactif
    const sidebarCollapsed = ref(false)
    const sidebarVisible = ref(false)
    const searchQuery = ref('')
    const notifications = ref([])

    // Computed
    const user = computed(() => authStore.user || {})
    const breadcrumbs = computed(() => {
      const crumbs = []
      
      // Générer les breadcrumbs basés sur la route actuelle
      if (route.matched.length > 0) {
        route.matched.forEach((match, index) => {
          if (match.meta?.breadcrumb) {
            crumbs.push({
              text: match.meta.breadcrumb,
              to: index === route.matched.length - 1 ? null : match.path
            })
          }
        })
      }
      
      return crumbs
    })

    // Méthodes
    const toggleSidebar = () => {
      sidebarCollapsed.value = !sidebarCollapsed.value
      localStorage.setItem('sidebarCollapsed', sidebarCollapsed.value)
    }

    const toggleMobileSidebar = () => {
      sidebarVisible.value = !sidebarVisible.value
    }

    const closeMobileSidebar = () => {
      sidebarVisible.value = false
    }

    const performSearch = () => {
      if (searchQuery.value.trim()) {
        router.push({
          name: 'Assets',
          query: { search: searchQuery.value.trim() }
        })
      }
    }

    const logout = async () => {
      try {
        await authStore.logout()
        toast.success('Déconnexion réussie')
        router.push('/login')
      } catch (error) {
        toast.error('Erreur lors de la déconnexion')
      }
    }

    const loadNotifications = async () => {
      // Simuler le chargement des notifications
      // En production, ceci ferait appel à l'API
      notifications.value = [
        {
          id: 1,
          title: 'Garantie expirée',
          message: '3 équipements ont une garantie expirée'
        },
        {
          id: 2,
          title: 'Maintenance requise',
          message: '2 équipements nécessitent une maintenance'
        }
      ]
    }

    // Lifecycle
    onMounted(() => {
      // Restaurer l'état de la sidebar
      const savedState = localStorage.getItem('sidebarCollapsed')
      if (savedState !== null) {
        sidebarCollapsed.value = JSON.parse(savedState)
      }

      // Charger les notifications
      loadNotifications()
    })

    // Watchers
    watch(route, () => {
      // Fermer la sidebar mobile lors du changement de route
      sidebarVisible.value = false
    })

    return {
      sidebarCollapsed,
      sidebarVisible,
      searchQuery,
      notifications,
      user,
      breadcrumbs,
      toggleSidebar,
      toggleMobileSidebar,
      closeMobileSidebar,
      performSearch,
      logout
    }
  }
}
</script>

<style scoped>
/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Sidebar responsive */
@media (max-width: 991.98px) {
  .sidebar {
    transform: translateX(-100%);
  }
  
  .sidebar.show {
    transform: translateX(0);
  }
}
</style>