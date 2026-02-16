<template>
  <div class="locations-page">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="h3 mb-0">Emplacements</h1>
        <p class="text-muted mb-0">Gestion des emplacements physiques</p>
      </div>
      <div>
        <button class="btn btn-primary" @click="showCreateModal">
          <i class="bi bi-plus-circle me-2"></i>
          Nouvel emplacement
        </button>
      </div>
    </div>

    <!-- Locations List -->
    <div class="card card-custom">
      <div class="card-header">
        <h5 class="card-title mb-0">Liste des emplacements</h5>
      </div>
      <div class="card-body">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary mb-3"></div>
          <p class="text-muted">Chargement des emplacements...</p>
        </div>

        <div v-else-if="locations.length === 0" class="text-center py-5">
          <i class="bi bi-geo-alt display-1 text-muted mb-3"></i>
          <h5 class="text-muted">Aucun emplacement</h5>
          <p class="text-muted">Commencez par ajouter votre premier emplacement.</p>
          <button class="btn btn-primary" @click="showCreateModal">
            <i class="bi bi-plus-circle me-2"></i>
            Ajouter un emplacement
          </button>
        </div>

        <div v-else class="row g-3">
          <div v-for="location in locations" :key="location.id" class="col-md-6 col-lg-4">
            <div class="card location-card h-100">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-2">
                  <h6 class="card-title mb-0">{{ location.name }}</h6>
                  <span class="badge bg-light text-dark">{{ location.type }}</span>
                </div>
                
                <p class="card-text text-muted small">
                  {{ location.description || 'Aucune description' }}
                </p>
                
                <div class="mb-2">
                  <i class="bi bi-laptop me-1"></i>
                  <small>{{ location.assets_count || 0 }} équipements</small>
                </div>
                
                <div class="d-flex gap-2">
                  <button class="btn btn-sm btn-outline-primary flex-fill">
                    <i class="bi bi-eye me-1"></i>
                    Voir
                  </button>
                  <button class="btn btn-sm btn-outline-secondary">
                    <i class="bi bi-pencil"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useToast } from 'vue-toastification'

export default {
  name: 'Locations',
  setup() {
    const toast = useToast()

    // État réactif
    const loading = ref(false)
    const locations = ref([])

    // Méthodes
    const loadLocations = async () => {
      loading.value = true

      try {
        // Simuler l'appel API
        await new Promise(resolve => setTimeout(resolve, 500))

        // Données simulées
        locations.value = [
          {
            id: 1,
            name: 'Bureau 101',
            type: 'Bureau',
            description: 'Bureau principal du directeur',
            assets_count: 5
          },
          {
            id: 2,
            name: 'Salle de réunion A',
            type: 'Salle',
            description: 'Grande salle de réunion',
            assets_count: 3
          },
          {
            id: 3,
            name: 'Stock principal',
            type: 'Entrepôt',
            description: 'Entrepôt principal de stockage',
            assets_count: 25
          }
        ]

      } catch (error) {
        console.error('Erreur lors du chargement des emplacements:', error)
        toast.error('Erreur lors du chargement des emplacements')
      } finally {
        loading.value = false
      }
    }

    const showCreateModal = () => {
      toast.info('Fonctionnalité en cours de développement')
    }

    // Lifecycle
    onMounted(() => {
      loadLocations()
    })

    return {
      loading,
      locations,
      showCreateModal
    }
  }
}
</script>

<style scoped>
.locations-page {
  animation: fadeIn 0.5s ease-out;
}

.location-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  cursor: pointer;
}

.location-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
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