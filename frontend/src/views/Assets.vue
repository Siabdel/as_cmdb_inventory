<template>
  <div class="assets-page">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="h3 mb-0">Équipements</h1>
        <p class="text-muted mb-0">Gestion de votre inventaire matériel</p>
      </div>
      <div>
        <router-link to="/assets/new" class="btn btn-primary">
          <i class="bi bi-plus-circle me-2"></i>
          Nouvel équipement
        </router-link>
      </div>
    </div>

    <!-- Filters and Search -->
    <div class="card card-custom mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-4">
            <div class="input-group">
              <span class="input-group-text">
                <i class="bi bi-search"></i>
              </span>
              <input
                type="text"
                class="form-control"
                placeholder="Rechercher..."
                v-model="filters.search"
                @input="debouncedSearch"
              >
            </div>
          </div>
          <div class="col-md-2">
            <select class="form-select" v-model="filters.status">
              <option value="">Tous les statuts</option>
              <option value="neuf">Neuf</option>
              <option value="stock">En stock</option>
              <option value="installe">Installé</option>
              <option value="use">En utilisation</option>
              <option value="broken">En panne</option>
              <option value="maintenance">En maintenance</option>
              <option value="reparation">En réparation</option>
              <option value="ok">OK</option>
              <option value="occasion">Occasion</option>
              <option value="sold">Vendu</option>
              <option value="disposed">Mis au rebut</option>
              <option value="lost">Perdu</option>
              <option value="hs">Hors service</option>
            </select>
          </div>
          <div class="col-md-2">
            <select class="form-select" v-model="filters.category">
              <option value="">Toutes catégories</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                {{ cat.name }}
              </option>
            </select>
          </div>
          <div class="col-md-2">
            <select class="form-select" v-model="filters.location">
              <option value="">Tous emplacements</option>
              <option v-for="loc in locations" :key="loc.id" :value="loc.id">
                {{ loc.name }}
              </option>
            </select>
          </div>
          <div class="col-md-2">
            <button class="btn btn-outline-secondary w-100" @click="resetFilters">
              <i class="bi bi-arrow-clockwise me-2"></i>
              Reset
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Assets List -->
    <div class="card card-custom">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="card-title mb-0">
          Liste des équipements ({{ totalAssets }})
        </h5>
        <div class="btn-group" role="group">
          <button 
            type="button" 
            class="btn btn-outline-secondary"
            :class="{ active: viewMode === 'table' }"
            @click="viewMode = 'table'"
          >
            <i class="bi bi-table"></i>
          </button>
          <button 
            type="button" 
            class="btn btn-outline-secondary"
            :class="{ active: viewMode === 'cards' }"
            @click="viewMode = 'cards'"
          >
            <i class="bi bi-grid"></i>
          </button>
        </div>
      </div>

      <div class="card-body">
        <!-- Loading State -->
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary mb-3"></div>
          <p class="text-muted">Chargement des équipements...</p>
        </div>

        <!-- Empty State -->
        <div v-else-if="assets.length === 0" class="text-center py-5">
          <i class="bi bi-inbox display-1 text-muted mb-3"></i>
          <h5 class="text-muted">Aucun équipement trouvé</h5>
          <p class="text-muted">
            {{ hasFilters ? 'Aucun équipement ne correspond à vos critères.' : 'Commencez par ajouter votre premier équipement.' }}
          </p>
          <router-link v-if="!hasFilters" to="/assets/new" class="btn btn-primary">
            <i class="bi bi-plus-circle me-2"></i>
            Ajouter un équipement
          </router-link>
        </div>

        <!-- Table View -->
        <div v-else-if="viewMode === 'table'" class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Code</th>
                <th>Nom</th>
                <th>Catégorie</th>
                <th>Statut</th>
                <th>Emplacement</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="asset in assets" :key="asset.id" class="cursor-pointer">
                <td>
                  <strong>{{ asset.internal_code }}</strong>
                </td>
                <td>
                  <div>
                    <div class="fw-medium">{{ asset.name }}</div>
                    <small class="text-muted">{{ asset.brand_name }}</small>
                  </div>
                </td>
                <td>
                  <span class="badge bg-light text-dark">
                    {{ asset.category_name || 'Non définie' }}
                  </span>
                </td>
                <td>
                  <span :class="getStatusClass(asset.status)">
                    {{ getStatusLabel(asset.status) }}
                  </span>
                </td>
                <td>
                  <i class="bi bi-geo-alt me-1"></i>
                  {{ asset.location_name || 'Non défini' }}
                </td>
                <td>
                  <div class="btn-group btn-group-sm">
                    <router-link 
                      :to="`/assets/${asset.id}`" 
                      class="btn btn-outline-primary"
                      title="Voir détails"
                    >
                      <i class="bi bi-eye"></i>
                    </router-link>
                    <router-link 
                      :to="`/assets/${asset.id}/edit`" 
                      class="btn btn-outline-secondary"
                      title="Modifier"
                    >
                      <i class="bi bi-pencil"></i>
                    </router-link>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Cards View -->
        <div v-else class="row g-3">
          <div v-for="asset in assets" :key="asset.id" class="col-md-6 col-lg-4">
            <div class="card asset-card h-100">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-2">
                  <h6 class="card-title mb-0">{{ asset.name }}</h6>
                  <span :class="getStatusClass(asset.status)">
                    {{ getStatusLabel(asset.status) }}
                  </span>
                </div>
                
                <p class="card-text">
                  <small class="text-muted">
                    <strong>{{ asset.internal_code }}</strong>
                    <br>
                    {{ asset.brand_name }} {{ asset.model }}
                  </small>
                </p>
                
                <div class="mb-2">
                  <i class="bi bi-geo-alt me-1"></i>
                  <small>{{ asset.location_name || 'Emplacement non défini' }}</small>
                </div>
                
                <div class="d-flex gap-2">
                  <router-link 
                    :to="`/assets/${asset.id}`" 
                    class="btn btn-sm btn-outline-primary flex-fill"
                  >
                    <i class="bi bi-eye me-1"></i>
                    Voir
                  </router-link>
                  <router-link 
                    :to="`/assets/${asset.id}/edit`" 
                    class="btn btn-sm btn-outline-secondary"
                  >
                    <i class="bi bi-pencil"></i>
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <nav v-if="totalPages > 1" class="mt-4">
          <ul class="pagination justify-content-center">
            <li class="page-item" :class="{ disabled: currentPage === 1 }">
              <button class="page-link" @click="changePage(currentPage - 1)">
                <i class="bi bi-chevron-left"></i>
              </button>
            </li>
            
            <li 
              v-for="page in visiblePages" 
              :key="page"
              class="page-item"
              :class="{ active: page === currentPage }"
            >
              <button class="page-link" @click="changePage(page)">
                {{ page }}
              </button>
            </li>
            
            <li class="page-item" :class="{ disabled: currentPage === totalPages }">
              <button class="page-link" @click="changePage(currentPage + 1)">
                <i class="bi bi-chevron-right"></i>
              </button>
            </li>
          </ul>
        </nav>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { debounce } from 'lodash-es'
import { assetsApi } from '@/api/assets'

export default {
  name: 'Assets',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const toast = useToast()

    // Données pour les filtres dynamiques
    const categories = ref([])
    const locations = ref([])

    // État réactif
    const loading = ref(false)
    const assets = ref([])
    const totalAssets = ref(0)
    const currentPage = ref(1)
    const totalPages = ref(1)
    const viewMode = ref('table')

    const filters = reactive({
      search: '',
      status: '',
      category: '',
      location: ''
    })

    // Computed
    const hasFilters = computed(() => {
      return filters.search || filters.status || filters.category || filters.location
    })

    const visiblePages = computed(() => {
      const pages = []
      const start = Math.max(1, currentPage.value - 2)
      const end = Math.min(totalPages.value, currentPage.value + 2)
      
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      
      return pages
    })

    // Charger les données pour les filtres
    const loadFilterData = async () => {
      try {
        // Charger les catégories
        const catsResponse = await assetsApi.getCategories()
        categories.value = catsResponse.data.results || catsResponse.data

        // Charger les emplacements
        const locsResponse = await assetsApi.getLocations()
        locations.value = locsResponse.data.results || locsResponse.data
      } catch (error) {
        console.error('Erreur lors du chargement des filtres:', error)
      }
    }

    // Méthodes
    const loadAssets = async () => {
      loading.value = true

      try {
        // Préparer les paramètres de filtrage
        const params = {
          page: currentPage.value,
          search: filters.search,
          status: filters.status,
          category: filters.category,
          location: filters.location
        }

        // Appel API réel
        const response = await assetsApi.getAssets(params)
        
        // Gérer la réponse paginée
        if (response.data.results) {
          assets.value = response.data.results
          totalAssets.value = response.data.count
          totalPages.value = Math.ceil(response.data.count / (response.data.page_size || 20))
        } else {
          // Si pas de pagination
          assets.value = response.data
          totalAssets.value = response.data.length
          totalPages.value = 1
        }

      } catch (error) {
        console.error('Erreur lors du chargement des assets:', error)
        toast.error('Erreur lors du chargement des équipements')
      } finally {
        loading.value = false
      }
    }

    const debouncedSearch = debounce(() => {
      currentPage.value = 1
      loadAssets()
    }, 300)

    const resetFilters = () => {
      filters.search = ''
      filters.status = ''
      filters.category = ''
      filters.location = ''
      currentPage.value = 1
      loadAssets()
    }

    const changePage = (page) => {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
        loadAssets()
      }
    }

    const getStatusClass = (status) => {
      const classes = {
        'neuf': 'badge bg-primary',
        'stock': 'badge bg-info',
        'installe': 'badge bg-secondary',
        'use': 'badge bg-success',
        'broken': 'badge bg-danger',
        'maintenance': 'badge bg-warning text-dark',
        'reparation': 'badge bg-warning text-dark',
        'ok': 'badge bg-success',
        'occasion': 'badge bg-info',
        'sold': 'badge bg-dark',
        'disposed': 'badge bg-secondary',
        'lost': 'badge bg-dark',
        'hs': 'badge bg-danger'
      }
      return classes[status] || 'badge bg-secondary'
    }

    const getStatusLabel = (status) => {
      const labels = {
        'neuf': 'Neuf',
        'stock': 'En stock',
        'installe': 'Installé',
        'use': 'En utilisation',
        'broken': 'En panne',
        'maintenance': 'En maintenance',
        'reparation': 'En réparation',
        'ok': 'OK',
        'occasion': 'Occasion',
        'sold': 'Vendu',
        'disposed': 'Mis au rebut',
        'lost': 'Perdu',
        'hs': 'Hors service'
      }
      return labels[status] || status
    }

    // Watchers
    watch([() => filters.status, () => filters.category, () => filters.location], () => {
      currentPage.value = 1
      loadAssets()
    })

    // Lifecycle
    onMounted(() => {
      // Récupérer les filtres depuis l'URL
      if (route.query.search) {
        filters.search = route.query.search
      }
      
      // Charger les données des filtres et les assets
      loadFilterData()
      loadAssets()
    })

    return {
      loading,
      assets,
      totalAssets,
      currentPage,
      totalPages,
      viewMode,
      filters,
      hasFilters,
      visiblePages,
      categories,
      locations,
      loadAssets,
      debouncedSearch,
      resetFilters,
      changePage,
      getStatusClass,
      getStatusLabel
    }
  }
}
</script>

<style scoped>
.assets-page {
  animation: fadeIn 0.5s ease-out;
}

.asset-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  cursor: pointer;
}

.asset-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

.table tbody tr {
  transition: background-color 0.2s ease;
}

.table tbody tr:hover {
  background-color: rgba(0, 123, 255, 0.05);
}

.btn-group .btn.active {
  background-color: var(--bs-primary);
  border-color: var(--bs-primary);
  color: white;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>