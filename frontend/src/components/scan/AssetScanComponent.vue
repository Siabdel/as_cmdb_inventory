<template>
  <div class="asset-scan-component">
    <div class="card">
      <div class="card-header bg-primary text-white">
        <h5 class="card-title mb-0">
          <i class="bi bi-upc-scan me-2"></i>
          Simulation de scan d'asset
        </h5>
      </div>
      <div class="card-body">
        <!-- Instructions -->
        <div class="alert alert-info mb-4">
          <i class="bi bi-info-circle me-2"></i>
          Utilisez une douchette USB (qui émule le clavier) ou saisissez manuellement le code de l'asset.
          Appuyez sur Entrée ou cliquez sur "Valider le scan" pour enregistrer.
        </div>

        <!-- Formulaire de scan -->
        <div class="row">
          <div class="col-md-8">
            <div class="mb-3">
              <label for="assetCode" class="form-label">
                Code de l'asset (QR Code ou code-barres)
              </label>
              <div class="input-group">
                <input
                  type="text"
                  id="assetCode"
                  class="form-control form-control-lg"
                  placeholder="Scannez ou saisissez le code..."
                  v-model="assetCode"
                  @keyup.enter="handleScan"
                  ref="codeInput"
                  autofocus
                />
                <button class="btn btn-primary" type="button" @click="handleScan">
                  <i class="bi bi-check-circle me-2"></i>
                  Valider le scan
                </button>
              </div>
              <div class="form-text">
                Le champ capture automatiquement les entrées des scanners USB.
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="mb-3">
              <label for="scanLocation" class="form-label">Lieu du scan</label>
              <input
                type="text"
                id="scanLocation"
                class="form-control"
                placeholder="Ex: Entrepôt A, Bureau 101"
                v-model="scanLocation"
              />
            </div>
          </div>
        </div>

        <!-- Informations de l'asset trouvé -->
        <div v-if="currentAsset" class="card mt-4 border-success">
          <div class="card-header bg-success text-white">
            <h6 class="mb-0">
              <i class="bi bi-check-circle me-2"></i>
              Asset trouvé
            </h6>
          </div>
          <div class="card-body">
            <div class="row">
              <div class="col-md-6">
                <h5>{{ currentAsset.name }}</h5>
                <p class="mb-1">
                  <strong>Code:</strong> {{ currentAsset.code }}
                </p>
                <p class="mb-1">
                  <strong>Localisation:</strong> {{ currentAsset.location || 'Non spécifiée' }}
                </p>
                <p class="mb-1">
                  <strong>Créé le:</strong> {{ formatDate(currentAsset.created_at) }}
                </p>
              </div>
              <div class="col-md-6">
                <div class="d-flex gap-3">
                  <div v-if="currentAsset.qr_code_url" class="text-center">
                    <p class="small mb-1">QR Code</p>
                    <img
                      :src="currentAsset.qr_code_url"
                      alt="QR Code"
                      class="img-thumbnail"
                      style="width: 100px; height: 100px;"
                    />
                  </div>
                  <div v-if="currentAsset.barcode_url" class="text-center">
                    <p class="small mb-1">Code-barres</p>
                    <img
                      :src="currentAsset.barcode_url"
                      alt="Code-barres"
                      class="img-thumbnail"
                      style="width: 150px; height: 80px;"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Derniers scans -->
        <div class="mt-4">
          <h6 class="mb-3">
            <i class="bi bi-clock-history me-2"></i>
            Derniers scans enregistrés
          </h6>
          <div v-if="recentScans.length > 0" class="table-responsive">
            <table class="table table-sm table-hover">
              <thead>
                <tr>
                  <th>Date/Heure</th>
                  <th>Asset</th>
                  <th>Scanné par</th>
                  <th>Lieu</th>
                  <th>Source</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="scan in recentScans" :key="scan.id">
                  <td>{{ formatDateTime(scan.scanned_at) }}</td>
                  <td>
                    <router-link :to="`/assets/${scan.asset.id}`">
                      {{ scan.asset_name || scan.asset_code }}
                    </router-link>
                  </td>
                  <td>{{ scan.scanned_by }}</td>
                  <td>{{ scan.scan_location || '-' }}</td>
                  <td>
                    <span class="badge" :class="getSourceBadgeClass(scan.source)">
                      {{ getSourceLabel(scan.source) }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="alert alert-light">
            Aucun scan enregistré récemment.
          </div>
        </div>
      </div>
      <div class="card-footer">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <button class="btn btn-outline-secondary" @click="clearForm">
              <i class="bi bi-x-circle me-2"></i>
              Effacer
            </button>
          </div>
          <div class="text-muted small">
            <i class="bi bi-lightning-charge me-1"></i>
            Scans aujourd'hui: {{ scanCountToday }}
          </div>
        </div>
      </div>
    </div>

    <!-- Toast de notification -->
    <div class="toast-container position-fixed bottom-0 end-0 p-3">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="toast show"
        :class="`bg-${toast.type}`"
        role="alert"
      >
        <div class="toast-header">
          <strong class="me-auto">{{ toast.title }}</strong>
          <button
            type="button"
            class="btn-close"
            @click="removeToast(toast.id)"
          ></button>
        </div>
        <div class="toast-body text-white">
          {{ toast.message }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { assetScanApi } from '@/api/assetScanApi'
import { format } from 'date-fns'

// Réactifs
const assetCode = ref('')
const scanLocation = ref('')
const currentAsset = ref(null)
const recentScans = ref([])
const scanCountToday = ref(0)
const toasts = ref([])
const codeInput = ref(null)

// Focus automatique sur le champ de code
onMounted(() => {
  if (codeInput.value) {
    codeInput.value.focus()
  }
  loadRecentScans()
})

// Gestionnaire de scan
const handleScan = async () => {
  if (!assetCode.value.trim()) {
    showToast('warning', 'Champ vide', 'Veuillez saisir ou scanner un code.')
    return
  }

  try {
    // 1. Rechercher l'asset par son code
    const response = await assetScanApi.getAssetByCode(assetCode.value.trim())
    currentAsset.value = response.data

    // 2. Enregistrer le scan
    const scanData = {
      asset_code: assetCode.value.trim(),
      scanned_by: 'Utilisateur Web', // À remplacer par l'utilisateur connecté
      scan_location: scanLocation.value || 'Interface web',
      source: 'web_frontend',
      notes: `Scan via interface web`
    }

    const scanResponse = await assetScanApi.recordScan(scanData)
    
    // 3. Afficher un message de succès
    showToast('success', 'Scan enregistré', `Scan de "${currentAsset.value.name}" enregistré avec succès.`)
    
    // 4. Recharger les scans récents
    loadRecentScans()
    
    // 5. Réinitialiser le champ de code (mais garder la localisation)
    assetCode.value = ''
    
    // 6. Remettre le focus sur le champ
    if (codeInput.value) {
      codeInput.value.focus()
    }

  } catch (error) {
    console.error('Erreur lors du scan:', error)
    showToast(
      'danger',
      'Erreur',
      error.response?.data?.detail || `Asset avec le code "${assetCode.value}" non trouvé.`
    )
    currentAsset.value = null
  }
}

// Charger les scans récents
const loadRecentScans = async () => {
  try {
    const response = await assetScanApi.getRecentScans(10)
    recentScans.value = response.data.results || response.data
  } catch (error) {
    console.error('Erreur lors du chargement des scans:', error)
  }
}

// Formater les dates
const formatDate = (dateString) => {
  if (!dateString) return ''
  return format(new Date(dateString), 'dd/MM/yyyy')
}

const formatDateTime = (dateString) => {
  if (!dateString) return ''
  return format(new Date(dateString), 'dd/MM/yyyy HH:mm')
}

// Gestion des badges de source
const getSourceLabel = (source) => {
  const labels = {
    'scanner_usb': 'Scanner USB',
    'mobile_app': 'App mobile',
    'web_frontend': 'Web',
    'bluetooth': 'Bluetooth',
    'manual': 'Manuel'
  }
  return labels[source] || source
}

const getSourceBadgeClass = (source) => {
  const classes = {
    'scanner_usb': 'bg-primary',
    'mobile_app': 'bg-success',
    'web_frontend': 'bg-info',
    'bluetooth': 'bg-warning',
    'manual': 'bg-secondary'
  }
  return classes[source] || 'bg-light text-dark'
}

// Gestion des toasts
const showToast = (type, title, message) => {
  const toast = {
    id: Date.now(),
    type,
    title,
    message
  }
  toasts.value.push(toast)
  
  // Supprimer automatiquement après 5 secondes
  setTimeout(() => {
    removeToast(toast.id)
  }, 5000)
}

const removeToast = (id) => {
  toasts.value = toasts.value.filter(toast => toast.id !== id)
}

// Effacer le formulaire
const clearForm = () => {
  assetCode.value = ''
  scanLocation.value = ''
  currentAsset.value = null
  if (codeInput.value) {
    codeInput.value.focus()
  }
}
</script>

<style scoped>
.asset-scan-component .toast-container {
  z-index: 1055;
}

.asset-scan-component .toast {
  min-width: 300px;
}

.asset-scan-component .table {
  font-size: 0.9rem;
}

.asset-scan-component .form-control-lg {
  font-size: 1.25rem;
}
</style>