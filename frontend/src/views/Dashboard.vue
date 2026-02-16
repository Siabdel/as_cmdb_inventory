<template>
  <div class="dashboard">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="h3 mb-0">Dashboard</h1>
        <p class="text-muted mb-0">Vue d'ensemble de votre inventaire matériel</p>
      </div>
      <div>
        <button class="btn btn-primary" @click="refreshData">
          <i class="bi bi-arrow-clockwise me-2"></i>
          Actualiser
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary mb-3"></div>
      <p class="text-muted">Chargement des données...</p>
    </div>

    <!-- Dashboard Content -->
    <div v-else>
      <!-- Stats Cards -->
      <div class="row g-4 mb-4">
        <div class="col-xl-3 col-md-6">
          <div class="card card-custom h-100">
            <div class="card-body">
              <div class="d-flex align-items-center">
                <div class="flex-shrink-0">
                  <div class="bg-primary bg-opacity-10 rounded-3 p-3">
                    <i class="bi bi-laptop text-primary fs-4"></i>
                  </div>
                </div>
                <div class="flex-grow-1 ms-3">
                  <div class="fw-bold text-primary fs-2">{{ stats.totalAssets || 0 }}</div>
                  <div class="text-muted small">Total Équipements</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-xl-3 col-md-6">
          <div class="card card-custom h-100">
            <div class="card-body">
              <div class="d-flex align-items-center">
                <div class="flex-shrink-0">
                  <div class="bg-success bg-opacity-10 rounded-3 p-3">
                    <i class="bi bi-check-circle text-success fs-4"></i>
                  </div>
                </div>
                <div class="flex-grow-1 ms-3">
                  <div class="fw-bold text-success fs-2">{{ stats.assetsInUse || 0 }}</div>
                  <div class="text-muted small">En Utilisation</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-xl-3 col-md-6">
          <div class="card card-custom h-100">
            <div class="card-body">
              <div class="d-flex align-items-center">
                <div class="flex-shrink-0">
                  <div class="bg-info bg-opacity-10 rounded-3 p-3">
                    <i class="bi bi-box text-info fs-4"></i>
                  </div>
                </div>
                <div class="flex-grow-1 ms-3">
                  <div class="fw-bold text-info fs-2">{{ stats.assetsInStock || 0 }}</div>
                  <div class="text-muted small">En Stock</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-xl-3 col-md-6">
          <div class="card card-custom h-100">
            <div class="card-body">
              <div class="d-flex align-items-center">
                <div class="flex-shrink-0">
                  <div class="bg-warning bg-opacity-10 rounded-3 p-3">
                    <i class="bi bi-exclamation-triangle text-warning fs-4"></i>
                  </div>
                </div>
                <div class="flex-grow-1 ms-3">
                  <div class="fw-bold text-warning fs-2">{{ stats.assetsBroken || 0 }}</div>
                  <div class="text-muted small">En Panne</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="row g-4 mb-4">
        <div class="col-lg-8">
          <div class="card card-custom h-100">
            <div class="card-header">
              <h5 class="card-title mb-0">Actions Rapides</h5>
            </div>
            <div class="card-body">
              <div class="row g-3">
                <div class="col-md-4">
                  <router-link to="/assets/new" class="btn btn-outline-primary w-100 h-100 d-flex flex-column align-items-center justify-content-center py-3">
                    <i class="bi bi-plus-circle fs-1 mb-2"></i>
                    <span>Nouvel Équipement</span>
                  </router-link>
                </div>
                <div class="col-md-4">
                  <router-link to="/scan" class="btn btn-outline-success w-100 h-100 d-flex flex-column align-items-center justify-content-center py-3">
                    <i class="bi bi-qr-code-scan fs-1 mb-2"></i>
                    <span>Scanner QR</span>
                  </router-link>
                </div>
                <div class="col-md-4">
                  <router-link to="/assets" class="btn btn-outline-info w-100 h-100 d-flex flex-column align-items-center justify-content-center py-3">
                    <i class="bi bi-list-ul fs-1 mb-2"></i>
                    <span>Voir Tous</span>
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-lg-4">
          <div class="card card-custom h-100">
            <div class="card-header">
              <h5 class="card-title mb-0">Scan Rapide</h5>
            </div>
            <div class="card-body text-center">
              <div class="mb-3">
                <i class="bi bi-qr-code display-1 text-muted"></i>
              </div>
              <p class="text-muted mb-3">Scannez rapidement un QR code pour accéder aux informations d'un équipement</p>
              <router-link to="/scan" class="btn btn-success btn-lg">
                <i class="bi bi-camera me-2"></i>
                Ouvrir Scanner
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Activity & Alerts -->
      <div class="row g-4">
        <div class="col-lg-8">
          <div class="card card-custom">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h5 class="card-title mb-0">Activité Récente</h5>
              <router-link to="/movements" class="btn btn-sm btn-outline-primary">
                Voir tout
              </router-link>
            </div>
            <div class="card-body">
              <div v-if="recentActivity.length === 0" class="text-center py-4">
                <i class="bi bi-clock-history display-1 text-muted mb-3"></i>
                <p class="text-muted">Aucune activité récente</p>
              </div>
              <div v-else>
                <div 
                  v-for="activity in recentActivity" 
                  :key="activity.id"
                  class="d-flex align-items-center py-2 border-bottom"
                >
                  <div class="flex-shrink-0 me-3">
                    <div class="bg-light rounded-circle p-2">
                      <i class="bi bi-arrow-right text-primary"></i>
                    </div>
                  </div>
                  <div class="flex-grow-1">
                    <div class="fw-medium">{{ activity.description }}</div>
                    <small class="text-muted">{{ formatDate(activity.date) }}</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-lg-4">
          <div class="card card-custom">
            <div class="card-header">
              <h5 class="card-title mb-0">Alertes</h5>
            </div>
            <div class="card-body">
              <div v-if="alerts.length === 0" class="text-center py-4">
                <i class="bi bi-check-circle display-1 text-success mb-3"></i>
                <p class="text-muted">Aucune alerte</p>
              </div>
              <div v-else>
                <div 
                  v-for="alert in alerts" 
                  :key="alert.id"
                  class="alert alert-warning alert-dismissible fade show"
                  role="alert"
                >
                  <i class="bi bi-exclamation-triangle me-2"></i>
                  <strong>{{ alert.title }}</strong>
                  <div class="small">{{ alert.message }}</div>
                  <button 
                    type="button" 
                    class="btn-close" 
                    @click="dismissAlert(alert.id)"
                  ></button>
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
import { ref, onMounted, computed } from 'vue'
import { useToast } from 'vue-toastification'
import { format } from 'date-fns'
import { fr } from 'date-fns/locale'

export default {
  name: 'Dashboard',
  setup() {
    const toast = useToast()

    // État réactif
    const loading = ref(true)
    const stats = ref({
      totalAssets: 0,
      assetsInUse: 0,
      assetsInStock: 0,
      assetsBroken: 0
    })
    const recentActivity = ref([])
    const alerts = ref([])

    // Computed
    const formattedStats = computed(() => {
      return {
        ...stats.value,
        totalAssets: stats.value.totalAssets.toLocaleString(),
        assetsInUse: stats.value.assetsInUse.toLocaleString(),
        assetsInStock: stats.value.assetsInStock.toLocaleString(),
        assetsBroken: stats.value.assetsBroken.toLocaleString()
      }
    })

    // Méthodes
    const loadDashboardData = async () => {
      loading.value = true
      
      try {
        // Simuler le chargement des données
        // En production, ceci ferait appel à l'API
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // Données simulées
        stats.value = {
          totalAssets: 156,
          assetsInUse: 89,
          assetsInStock: 52,
          assetsBroken: 15
        }

        recentActivity.value = [
          {
            id: 1,
            description: 'PC-001 déplacé vers Bureau 201',
            date: new Date(Date.now() - 1000 * 60 * 30) // 30 minutes ago
          },
          {
            id: 2,
            description: 'Nouvel équipement ECR-045 ajouté',
            date: new Date(Date.now() - 1000 * 60 * 60 * 2) // 2 hours ago
          },
          {
            id: 3,
            description: 'IMP-012 marqué en panne',
            date: new Date(Date.now() - 1000 * 60 * 60 * 4) // 4 hours ago
          }
        ]

        alerts.value = [
          {
            id: 1,
            title: 'Garanties expirées',
            message: '3 équipements ont une garantie expirée'
          },
          {
            id: 2,
            title: 'Maintenance requise',
            message: '2 équipements nécessitent une maintenance'
          }
        ]

      } catch (error) {
        console.error('Erreur lors du chargement du dashboard:', error)
        toast.error('Erreur lors du chargement des données')
      } finally {
        loading.value = false
      }
    }

    const refreshData = () => {
      toast.info('Actualisation des données...')
      loadDashboardData()
    }

    const formatDate = (date) => {
      return format(date, 'dd/MM/yyyy à HH:mm', { locale: fr })
    }

    const dismissAlert = (alertId) => {
      alerts.value = alerts.value.filter(alert => alert.id !== alertId)
    }

    // Lifecycle
    onMounted(() => {
      loadDashboardData()
    })

    return {
      loading,
      stats: formattedStats,
      recentActivity,
      alerts,
      refreshData,
      formatDate,
      dismissAlert
    }
  }
}
</script>

<style scoped>
.dashboard {
  animation: fadeIn 0.5s ease-out;
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

.card-custom {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card-custom:hover {
  transform: translateY(-2px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

.btn:hover {
  transform: translateY(-1px);
}

.alert {
  border: none;
  border-left: 4px solid #ffc107;
}
</style>