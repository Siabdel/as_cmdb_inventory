<template>
  <div class="scan-page">
    <!-- Mobile-first header -->
    <div class="scan-header text-center mb-4">
      <h1 class="h3 text-white mb-2">
        <i class="bi bi-qr-code-scan me-2"></i>
        Scanner QR Code
      </h1>
      <p class="text-white-50 mb-0">
        Scannez le QR code d'un équipement pour accéder rapidement à ses informations
      </p>
    </div>

    <!-- QR Scanner Component -->
    <div class="scanner-wrapper">
      <QRScanner 
        @scan-success="handleScanSuccess"
        @scan-error="handleScanError"
      />
    </div>

    <!-- Asset Info Modal -->
    <div 
      class="modal fade" 
      id="assetModal" 
      tabindex="-1" 
      ref="assetModal"
    >
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="bi bi-laptop me-2"></i>
              Informations Équipement
            </h5>
            <button 
              type="button" 
              class="btn-close" 
              data-bs-dismiss="modal"
            ></button>
          </div>
          
          <div class="modal-body" v-if="selectedAsset">
            <!-- Asset Details -->
            <div class="row g-3 mb-4">
              <div class="col-md-6">
                <div class="card h-100">
                  <div class="card-body">
                    <h6 class="card-title">
                      <i class="bi bi-info-circle me-2"></i>
                      Détails
                    </h6>
                    <div class="mb-2">
                      <strong>Code:</strong> {{ selectedAsset.internal_code }}
                    </div>
                    <div class="mb-2">
                      <strong>Nom:</strong> {{ selectedAsset.name }}
                    </div>
                    <div class="mb-2">
                      <strong>Catégorie:</strong> {{ selectedAsset.category?.name || 'Non définie' }}
                    </div>
                    <div class="mb-2">
                      <strong>Marque:</strong> {{ selectedAsset.brand?.name || 'Non définie' }}
                    </div>
                    <div class="mb-2">
                      <strong>Statut:</strong>
                      <span :class="getStatusClass(selectedAsset.status)">
                        {{ getStatusLabel(selectedAsset.status) }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="col-md-6">
                <div class="card h-100">
                  <div class="card-body">
                    <h6 class="card-title">
                      <i class="bi bi-geo-alt me-2"></i>
                      Localisation
                    </h6>
                    <div class="mb-2">
                      <strong>Emplacement:</strong>
                      {{ selectedAsset.current_location?.name || 'Non défini' }}
                    </div>
                    <div class="mb-2">
                      <strong>Assigné à:</strong> 
                      {{ selectedAsset.assigned_to_name || 'Personne' }}
                    </div>
                    <div class="mb-2">
                      <strong>Dernière mise à jour:</strong>
                      {{ formatDate(selectedAsset.updated_at) }}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Quick Actions -->
            <div class="row g-2">
              <div class="col-md-4">
                <button 
                  class="btn btn-primary w-100"
                  @click="viewAssetDetails"
                >
                  <i class="bi bi-eye me-2"></i>
                  Voir Détails
                </button>
              </div>
              <div class="col-md-4">
                <button 
                  class="btn btn-success w-100"
                  @click="showMoveModal"
                  :disabled="selectedAsset.status === 'broken'"
                >
                  <i class="bi bi-arrow-right me-2"></i>
                  Déplacer
                </button>
              </div>
              <div class="col-md-4">
                <div class="dropdown w-100">
                  <button 
                    class="btn btn-outline-secondary dropdown-toggle w-100"
                    type="button"
                    data-bs-toggle="dropdown"
                  >
                    <i class="bi bi-three-dots me-2"></i>
                    Actions
                  </button>
                  <ul class="dropdown-menu">
                    <li>
                      <a class="dropdown-item" href="#" @click="markAsBroken">
                        <i class="bi bi-exclamation-triangle me-2"></i>
                        Marquer en panne
                      </a>
                    </li>
                    <li>
                      <a class="dropdown-item" href="#" @click="markAsMaintenance">
                        <i class="bi bi-tools me-2"></i>
                        Envoyer en maintenance
                      </a>
                    </li>
                    <li><hr class="dropdown-divider"></li>
                    <li>
                      <a class="dropdown-item" href="#" @click="editAsset">
                        <i class="bi bi-pencil me-2"></i>
                        Modifier
                      </a>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Move Asset Modal -->
    <div 
      class="modal fade" 
      id="moveModal" 
      tabindex="-1" 
      ref="moveModal"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="bi bi-arrow-right me-2"></i>
              Déplacer l'équipement
            </h5>
            <button 
              type="button" 
              class="btn-close" 
              data-bs-dismiss="modal"
            ></button>
          </div>
          
          <div class="modal-body">
            <form @submit.prevent="moveAsset">
              <div class="mb-3">
                <label class="form-label">Nouvel emplacement</label>
                <select 
                  class="form-select" 
                  v-model="moveForm.locationId"
                  required
                >
                  <option value="">Sélectionner un emplacement</option>
                  <option 
                    v-for="location in locations" 
                    :key="location.id" 
                    :value="location.id"
                  >
                    {{ location.name }}
                  </option>
                </select>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Note (optionnel)</label>
                <textarea 
                  class="form-control" 
                  v-model="moveForm.note"
                  rows="3"
                  placeholder="Raison du déplacement..."
                ></textarea>
              </div>
              
              <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                <button 
                  type="button" 
                  class="btn btn-secondary"
                  data-bs-dismiss="modal"
                >
                  Annuler
                </button>
                <button 
                  type="submit" 
                  class="btn btn-success"
                  :disabled="!moveForm.locationId || moving"
                >
                  <span v-if="moving" class="spinner-border spinner-border-sm me-2"></span>
                  <i class="bi bi-check me-2" v-else></i>
                  Déplacer
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { Modal } from 'bootstrap'
import { format } from 'date-fns'
import { fr } from 'date-fns/locale'
import QRScanner from '@/components/scan/QRScanner.vue'
import assetsApi from '@/api/assets'

export default {
  name: 'ScanQR',
  components: {
    QRScanner
  },
  setup() {
    const router = useRouter()
    const toast = useToast()

    // Refs pour les modals
    const assetModal = ref(null)
    const moveModal = ref(null)
    let assetModalInstance = null
    let moveModalInstance = null

    // État réactif
    const selectedAsset = ref(null)
    const locations = ref([])
    const moveForm = ref({
      locationId: '',
      note: ''
    })
    const moving = ref(false)

    // Méthodes
    const handleScanSuccess = async (scanData) => {
      try {
        let assetId = null

        // Extraire l'ID de l'asset
        if (scanData.assetId) {
          assetId = scanData.assetId
        } else {
          // Essayer d'extraire depuis le texte scanné
          assetId = extractAssetId(scanData.text)
        }

        if (!assetId) {
          throw new Error('QR code invalide. Impossible d\'identifier l\'équipement.')
        }

        // Récupérer les informations de l'asset
        const response = await assetsApi.getAsset(assetId)
        selectedAsset.value = response.data

        // Afficher le modal avec les informations
        showAssetModal()

        toast.success('Équipement trouvé !')

      } catch (error) {
        console.error('Erreur lors du traitement du scan:', error)
        toast.error(error.message || 'Erreur lors de la recherche de l\'équipement')
      }
    }

    const handleScanError = (error) => {
      console.error('Erreur de scan:', error)
      toast.error('Erreur lors du scan du QR code')
    }

    const extractAssetId = (qrData) => {
      try {
        // Essayer d'extraire l'UUID depuis une URL
        const urlPattern = /\/assets\/([a-f0-9-]{36})\/?/i
        const match = qrData.match(urlPattern)
        
        if (match) {
          return match[1]
        }
        
        // Essayer de parser comme UUID direct
        const uuidPattern = /^[a-f0-9-]{36}$/i
        if (uuidPattern.test(qrData)) {
          return qrData
        }
        
        return null
      } catch (err) {
        return null
      }
    }

    const showAssetModal = () => {
      if (assetModalInstance) {
        assetModalInstance.show()
      }
    }

    const showMoveModal = () => {
      if (moveModalInstance) {
        moveModalInstance.show()
      }
    }

    const viewAssetDetails = () => {
      if (selectedAsset.value) {
        router.push(`/assets/${selectedAsset.value.id}`)
      }
    }

    const editAsset = () => {
      if (selectedAsset.value) {
        router.push(`/assets/${selectedAsset.value.id}/edit`)
      }
    }

    const markAsBroken = async () => {
      try {
        await assetsApi.markAsBroken(selectedAsset.value.id, 'Marqué en panne via scan QR')
        selectedAsset.value.status = 'broken'
        toast.success('Équipement marqué en panne')
      } catch (error) {
        toast.error('Erreur lors de la mise à jour du statut')
      }
    }

    const markAsMaintenance = async () => {
      try {
        await assetsApi.markAsMaintenance(selectedAsset.value.id, 'Envoyé en maintenance via scan QR')
        selectedAsset.value.status = 'maintenance'
        toast.success('Équipement envoyé en maintenance')
      } catch (error) {
        toast.error('Erreur lors de la mise à jour du statut')
      }
    }

    const moveAsset = async () => {
      if (!moveForm.value.locationId) return

      moving.value = true

      try {
        await assetsApi.moveFromScan(
          selectedAsset.value.id,
          moveForm.value.locationId,
          moveForm.value.note
        )

        // Mettre à jour l'asset local
        const newLocation = locations.value.find(l => l.id == moveForm.value.locationId)
        selectedAsset.value.current_location = moveForm.value.locationId
        selectedAsset.value.location_name = newLocation?.name

        // Fermer le modal
        moveModalInstance.hide()

        // Reset form
        moveForm.value = { locationId: '', note: '' }

        toast.success('Équipement déplacé avec succès')

      } catch (error) {
        toast.error('Erreur lors du déplacement')
      } finally {
        moving.value = false
      }
    }

    const loadLocations = async () => {
      try {
        // Simuler le chargement des emplacements
        // En production, ceci ferait appel à l'API
        locations.value = [
          { id: 1, name: 'Bureau 101' },
          { id: 2, name: 'Bureau 102' },
          { id: 3, name: 'Salle de réunion A' },
          { id: 4, name: 'Stock principal' },
          { id: 5, name: 'Atelier maintenance' }
        ]
      } catch (error) {
        console.error('Erreur lors du chargement des emplacements:', error)
      }
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

    const formatDate = (dateString) => {
      if (!dateString) return 'Non défini'
      return format(new Date(dateString), 'dd/MM/yyyy à HH:mm', { locale: fr })
    }

    // Lifecycle
    onMounted(() => {
      // Initialiser les modals Bootstrap
      if (assetModal.value) {
        assetModalInstance = new Modal(assetModal.value)
      }
      if (moveModal.value) {
        moveModalInstance = new Modal(moveModal.value)
      }

      // Charger les données
      loadLocations()
    })

    return {
      assetModal,
      moveModal,
      selectedAsset,
      locations,
      moveForm,
      moving,
      handleScanSuccess,
      handleScanError,
      showMoveModal,
      viewAssetDetails,
      editAsset,
      markAsBroken,
      markAsMaintenance,
      moveAsset,
      getStatusClass,
      getStatusLabel,
      formatDate
    }
  }
}
</script>

<style scoped>
.scan-page {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  padding: 2rem 1rem;
}

.scanner-wrapper {
  max-width: 500px;
  margin: 0 auto;
}

.scan-header {
  margin-bottom: 2rem;
}

/* Mobile optimizations */
@media (max-width: 768px) {
  .scan-page {
    padding: 1rem 0.5rem;
  }
  
  .modal-dialog {
    margin: 1rem;
  }
}

/* Animations */
.scan-page {
  animation: slideIn 0.5s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>