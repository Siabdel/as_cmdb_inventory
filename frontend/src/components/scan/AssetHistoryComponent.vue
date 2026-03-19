<template>
  <div class="asset-history-component">
    <div class="card">
      <div class="card-header bg-info text-white">
        <h5 class="card-title mb-0">
          <i class="bi bi-clock-history me-2"></i>
          Historique de rétractabilité
        </h5>
      </div>
      <div class="card-body">
        <!-- Recherche par code -->
        <div class="row mb-4">
          <div class="col-md-8">
            <div class="input-group">
              <input
                type="text"
                class="form-control"
                placeholder="Saisissez ou scannez le code de l'asset..."
                v-model="searchCode"
                @keyup.enter="searchAsset"
                ref="searchInput"
              />
              <button class="btn btn-primary" type="button" @click="searchAsset">
                <i class="bi bi-search me-2"></i>
                Rechercher
              </button>
            </div>
          </div>
          <div class="col-md-4">
            <div class="form-text">
              Utilisez un scanner QR code ou code-barres pour remplir automatiquement.
            </div>
          </div>
        </div>

        <!-- Informations de l'asset -->
        <div v-if="currentAsset" class="card mb-4 border-primary">
          <div class="card-header bg-light">
            <h6 class="mb-0">Informations de l'asset</h6>
          </div>
          <div class="card-body">
            <div class="row">
              <div class="col-md-4">
                <h5>{{ currentAsset.name }}</h5>
                <p><strong>Code:</strong> {{ currentAsset.code }}</p>
                <p><strong>Localisation:</strong> {{ currentAsset.location || 'Non spécifiée' }}</p>
                <p><strong>Créé le:</strong> {{ formatDate(currentAsset.created_at) }}</p>
              </div>
              <div class="col-md-4">
                <div v-if="currentAsset.qr_code_url" class="text-center mb-3">
                  <p class="small mb-1">QR Code</p>
                  <img
                    :src="currentAsset.qr_code_url"
                    alt="QR Code"
                    class="img-thumbnail"
                    style="width: 120px; height: 120px;"
                  />
                </div>
              </div>
              <div class="col-md-4">
                <div v-if="currentAsset.barcode_url" class="text-center mb-3">
                  <p class="small mb-1">Code-barres</p>
                  <img
                    :src="currentAsset.barcode_url"
                    alt="Code-barres"
                    class="img-thumbnail"
                    style="width: 180px; height: 80px;"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Historique des scans -->
        <div v-if="scans.length > 0">
          <h6 class="mb-3">
            <i class="bi bi-list-ul me-2"></i>
            Historique des scans ({{ scans.length }} enregistrements)
          </h6>
          <div class="table-responsive">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th>Date/Heure</th>
                  <th>Scanné par</th>
                  <th>Lieu</th>
                  <th>Source</th>
                  <th>Notes</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="scan in scans" :key="scan.id">
                  <td>
                    <div class="fw-semibold">{{ formatDateTime(scan.scanned_at) }}</div>
                    <small class="text-muted">{{ timeAgo(scan.scanned_at) }}</small>
                  </td>
                  <td>{{ scan.scanned_by }}</td>
                  <td>{{ scan.scan_location || '-' }}</td>
                  <td>
                    <span class="badge" :class="getSourceBadgeClass(scan.source)">
                      {{ getSourceLabel(scan.source) }}
                    </span>
                  </td>
                  <td>
                    <small class="text-muted">{{ scan.notes || '-' }}</small>
                  </td>
                  <td>
                    <button
                      class="btn btn-sm btn-outline-info"
                      @click="viewScanDetails(scan)"
                      title="Détails"
                    >
                      <i class="bi bi-eye"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Statistiques -->
          <div class="row mt-4">
            <div class="col-md-3">
              <div class="card bg-light">
                <div class="card-body text-center">
                  <h6 class="card-title">Premier scan</h6>
                  <p class="card-text fw-bold">
                    {{ scans.length > 0 ? formatDate(scans[scans.length - 1].scanned_at) : '-' }}
                  </p>
                </div>
              </div>
            </div>
            <div class="col-md-3">
              <div class="card bg-light">
                <div class="card-body text-center">
                  <h6 class="card-title">Dernier scan</h6>
                  <p class="card-text fw-bold">
                    {{ scans.length > 0 ? formatDate(scans[0].scanned_at) : '-' }}
                  </p>
                </div>
              </div>
            </div>
            <div class="col-md-3">
              <div class="card bg-light">
                <div class="card-body text-center">
                  <h6 class="card-title">Total scans</h6>
                  <p class="card-text fw-bold display-6">{{ scans.length }}</p>
                </div>
              </div>
            </div>
            <div class="col-md-3">
              <div class="card bg-light">
                <div class="card-body text-center">
                  <h6 class="card-title">Sources utilisées</h6>
                  <p class="card-text">
                    <span
                      v-for="source in uniqueSources"
                      :key="source"
                      class="badge me-1"
                      :class="getSourceBadgeClass(source)"
                    >
                      {{ getSourceLabel(source) }}
                    </span>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Aucun résultat -->
        <div v-else-if="searchCode && !loading" class="text-center py-5">
          <i class="bi bi-search display-1 text-muted"></i>
          <h5 class="mt-3">Aucun historique trouvé</h5>
          <p class="text-muted">
            Aucun scan n'a été enregistré pour cet asset.
          </p>
        </div>

        <!-- Instructions initiales -->
        <div v-else class="text-center py-5 text-muted">
          <i class="bi bi-upc-scan display-1"></i>
          <h5 class="mt-3">Rechercher un asset</h5>
          <p>
            Saisissez ou scannez le code d'un asset pour visualiser son historique de rétractabilité.
          </p>
        </div>
      </div>
    </div>

    <!-- Modal de détails du scan -->
    <div
      v-if="selectedScan"
      class="modal fade show"
      style="display: block; background-color: rgba(0,0,0,0.5);"
      tabindex="-1"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Détails du scan</h5>
            <button
              type="button"
              class="btn-close"
              @click="selectedScan = null"
            ></button>
          </div>
          <div class="modal-body">
            <div v-if="selectedScan">
              <p><strong>ID:</strong> {{ selectedScan.id }}</p>
              <p><strong>Date/heure:</strong> {{ formatDateTime(selectedScan.scanned_at) }}</p>
              <p><strong>Asset:</strong> {{ selectedScan.asset_name || selectedScan.asset_code }}</p>
              <p><strong>Scanné par:</strong> {{ selectedScan.scanned_by }}</p>
              <p><strong>Lieu:</strong> {{ selectedScan.scan_location || '-' }}</p>
              <p><strong>Source:</strong> {{ getSourceLabel(selectedScan.source) }}</p>
              <p><strong>Notes:</strong> {{ selectedScan.notes || 'Aucune' }}</p>
            </div>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-secondary"
              @click="selectedScan = null"
            >
              Fermer
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { assetScanApi } from '@/api/assetScanApi'
import { format, formatDistanceToNow } from 'date-fns'
import { fr } from 'date-fns/locale'

// Réactifs
const searchCode = ref('')
const currentAsset = ref(null)
const scans = ref([])
const loading = ref(false)
const selectedScan = ref(null)
const searchInput = ref(null)

// Sources uniques
const uniqueSources = computed(() => {
  const sources = new Set()
  scans.value.forEach(scan => sources.add(scan.source))
  return Array.from(sources)
})

// Rechercher un asset et son historique
const searchAsset = async () => {
  if (!searchCode.value.trim()) {
    return
  }

  loading.value = true
  try {
    // Rechercher l'asset par son code
    const assetResponse = await assetScanApi.getAssetByCode(searchCode.value.trim())
    currentAsset.value = assetResponse.data

    // Récupérer l'historique des scans
    const historyResponse = await assetScanApi.getAssetHistory(currentAsset.value.id)
    scans.value = historyResponse.data.scans || []
    
  } catch (error) {
    console.error('Erreur lors de la recherche:', error)
    currentAsset.value = null
    scans.value = []
  } finally {
    loading.value = false
  }
}

// Formater les dates
const formatDate = (dateString) => {
  if (!dateString) return ''
  return format(new Date(dateString), 'dd/MM/yyyy', { locale: fr })
}

const formatDateTime = (dateString) => {
  if (!dateString) return ''
  return format(new Date(dateString), 'dd/MM/yyyy HH:mm:ss', { locale: fr })
}

const timeAgo = (dateString) => {
  if (!dateString) return ''
  return formatDistanceToNow(new Date(dateString), { addSuffix: true, locale: fr })
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

// Voir les détails d'un scan
const viewScanDetails = (scan) => {
  selectedScan.value = scan
}

// Focus sur le champ de recherche au chargement
onMounted(() => {
  if (searchInput.value) {
    searchInput.value.focus()
  }
})
</script>

<style scoped>
.asset-history-component .modal {
  z-index: 1055;
}

.asset-history-component .table {
  font-size: 0.9rem;
}

.asset-history-component .badge {
  font-size: 0.75rem;
}
</style>