<template>
  <div class="asset-detail-page">
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary mb-3"></div>
      <p class="text-muted">Chargement des détails...</p>
    </div>

    <div v-else-if="asset">
      <!-- Header -->
      <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 class="h3 mb-0">{{ asset.name }}</h1>
          <p class="text-muted mb-0">{{ asset.internal_code }}</p>
        </div>
        <div>
          <router-link :to="`/assets/${asset.id}/edit`" class="btn btn-primary me-2">
            <i class="bi bi-pencil me-2"></i>
            Modifier
          </router-link>
          <button class="btn btn-outline-secondary" @click="downloadQR">
            <i class="bi bi-download me-2"></i>
            QR Code
          </button>
        </div>
      </div>

      <!-- Asset Info -->
      <div class="row g-4">
        <div class="col-lg-8">
          <div class="card card-custom">
            <div class="card-header">
              <h5 class="card-title mb-0">Informations générales</h5>
            </div>
            <div class="card-body">
              <div class="row g-3">
                <div class="col-md-6">
                  <strong>Nom :</strong> {{ asset.name }}
                </div>
                <div class="col-md-6">
                  <strong>Code interne :</strong> {{ asset.internal_code }}
                </div>
                <div class="col-md-6">
                  <strong>Catégorie :</strong> {{ asset.category_name || 'Non définie' }}
                </div>
                <div class="col-md-6">
                  <strong>Marque :</strong> {{ asset.brand_name || 'Non définie' }}
                </div>
                <div class="col-md-6">
                  <strong>Modèle :</strong> {{ asset.model || 'Non défini' }}
                </div>
                <div class="col-md-6">
                  <strong>Statut :</strong>
                  <span :class="getStatusClass(asset.status)">
                    {{ getStatusLabel(asset.status) }}
                  </span>
                </div>
                <div class="col-md-6">
                  <strong>Emplacement :</strong> {{ asset.location_name || 'Non défini' }}
                </div>
                <div class="col-md-6">
                  <strong>Assigné à :</strong> {{ asset.assigned_to_name || 'Personne' }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-lg-4">
          <div class="card card-custom">
            <div class="card-header">
              <h5 class="card-title mb-0">QR Code</h5>
            </div>
            <div class="card-body text-center">
              <div class="qr-code-placeholder mb-3">
                <i class="bi bi-qr-code display-1 text-muted"></i>
              </div>
              <p class="text-muted small">QR Code pour accès rapide</p>
              <button class="btn btn-outline-primary btn-sm" @click="downloadQR">
                <i class="bi bi-download me-2"></i>
                Télécharger
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="text-center py-5">
      <i class="bi bi-exclamation-triangle display-1 text-warning mb-3"></i>
      <h5 class="text-muted">Équipement non trouvé</h5>
      <router-link to="/assets" class="btn btn-primary">
        Retour à la liste
      </router-link>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from 'vue-toastification'

export default {
  name: 'AssetDetail',
  setup() {
    const route = useRoute()
    const toast = useToast()

    const loading = ref(true)
    const asset = ref(null)

    const loadAsset = async () => {
      loading.value = true
      try {
        // Simuler l'appel API
        await new Promise(resolve => setTimeout(resolve, 500))
        
        // Données simulées
        asset.value = {
          id: route.params.id,
          internal_code: 'PC-001',
          name: 'Dell OptiPlex 7090',
          brand_name: 'Dell',
          model: 'OptiPlex 7090',
          category_name: 'PC',
          status: 'use',
          location_name: 'Bureau 101',
          assigned_to_name: 'Jean Dupont'
        }
      } catch (error) {
        console.error('Erreur:', error)
        toast.error('Erreur lors du chargement')
      } finally {
        loading.value = false
      }
    }

    const downloadQR = () => {
      toast.info('Fonctionnalité en cours de développement')
    }

    const getStatusClass = (status) => {
      const classes = {
        'stock': 'badge bg-info',
        'use': 'badge bg-success',
        'broken': 'badge bg-danger',
        'maintenance': 'badge bg-warning text-dark'
      }
      return classes[status] || 'badge bg-secondary'
    }

    const getStatusLabel = (status) => {
      const labels = {
        'stock': 'En stock',
        'use': 'En utilisation',
        'broken': 'En panne',
        'maintenance': 'En maintenance'
      }
      return labels[status] || status
    }

    onMounted(() => {
      loadAsset()
    })

    return {
      loading,
      asset,
      downloadQR,
      getStatusClass,
      getStatusLabel
    }
  }
}
</script>

<style scoped>
.asset-detail-page {
  animation: fadeIn 0.5s ease-out;
}

.qr-code-placeholder {
  padding: 2rem;
  border: 2px dashed #dee2e6;
  border-radius: 0.5rem;
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