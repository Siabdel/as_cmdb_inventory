<template>
  <div class="qr-scanner">
    <!-- Scanner Container -->
    <div class="scanner-container" v-if="!scannedData">
      <div class="scanner-header text-center mb-3">
        <h4 class="text-white">
          <i class="bi bi-qr-code-scan me-2"></i>
          Scanner un QR Code
        </h4>
        <p class="text-white-50 mb-0">
          Pointez la caméra vers le QR code de l'équipement
        </p>
      </div>

      <!-- Video Container -->
      <div class="video-container position-relative">
        <div id="qr-reader" class="qr-reader"></div>
        
        <!-- Overlay avec cadre de scan -->
        <div class="scan-overlay">
          <div class="scan-frame">
            <div class="corner top-left"></div>
            <div class="corner top-right"></div>
            <div class="corner bottom-left"></div>
            <div class="corner bottom-right"></div>
          </div>
        </div>

        <!-- Instructions -->
        <div class="scan-instructions">
          <div class="instruction-text">
            <i class="bi bi-camera me-2"></i>
            Alignez le QR code dans le cadre
          </div>
        </div>
      </div>

      <!-- Controls -->
      <div class="scanner-controls mt-3">
        <div class="row g-2">
          <div class="col-6">
            <button 
              class="btn btn-outline-light w-100"
              @click="toggleCamera"
              :disabled="loading"
            >
              <i class="bi bi-camera-video" v-if="isScanning"></i>
              <i class="bi bi-camera-video-off" v-else></i>
              {{ isScanning ? 'Arrêter' : 'Démarrer' }}
            </button>
          </div>
          <div class="col-6">
            <button 
              class="btn btn-outline-light w-100"
              @click="switchCamera"
              :disabled="!isScanning || cameras.length <= 1"
            >
              <i class="bi bi-arrow-repeat me-1"></i>
              Changer
            </button>
          </div>
        </div>
      </div>

      <!-- Camera Selection -->
      <div class="camera-selection mt-3" v-if="cameras.length > 1">
        <select 
          class="form-select form-select-sm"
          v-model="selectedCameraId"
          @change="changeCamera"
        >
          <option value="">Sélectionner une caméra</option>
          <option 
            v-for="camera in cameras" 
            :key="camera.id" 
            :value="camera.id"
          >
            {{ camera.label || `Caméra ${camera.id}` }}
          </option>
        </select>
      </div>
    </div>

    <!-- Scan Result -->
    <div class="scan-result" v-if="scannedData">
      <div class="result-header text-center mb-4">
        <div class="success-icon">
          <i class="bi bi-check-circle-fill text-success"></i>
        </div>
        <h5 class="mt-2">QR Code scanné avec succès !</h5>
      </div>

      <div class="result-content">
        <div class="card">
          <div class="card-body">
            <h6 class="card-title">Données scannées :</h6>
            <p class="card-text font-monospace small">{{ scannedData }}</p>
            
            <div class="d-grid gap-2">
              <button 
                class="btn btn-primary"
                @click="handleScanResult"
                :disabled="processing"
              >
                <span v-if="processing" class="spinner-border spinner-border-sm me-2"></span>
                <i class="bi bi-search me-2" v-else></i>
                Rechercher l'équipement
              </button>
              
              <button 
                class="btn btn-outline-secondary"
                @click="resetScanner"
              >
                <i class="bi bi-arrow-clockwise me-2"></i>
                Scanner un autre code
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div class="loading-state text-center" v-if="loading">
      <div class="spinner-border text-light mb-3"></div>
      <p class="text-white">Initialisation de la caméra...</p>
    </div>

    <!-- Error State -->
    <div class="error-state text-center" v-if="error">
      <div class="error-icon mb-3">
        <i class="bi bi-exclamation-triangle-fill text-warning"></i>
      </div>
      <h6 class="text-white">{{ error }}</h6>
      <button 
        class="btn btn-outline-light mt-2"
        @click="initializeScanner"
      >
        <i class="bi bi-arrow-clockwise me-2"></i>
        Réessayer
      </button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { Html5QrcodeScanner, Html5Qrcode } from 'html5-qrcode'
import { useToast } from 'vue-toastification'

export default {
  name: 'QRScanner',
  emits: ['scan-success', 'scan-error'],
  setup(props, { emit }) {
    const toast = useToast()

    // État réactif
    const scanner = ref(null)
    const isScanning = ref(false)
    const loading = ref(false)
    const error = ref(null)
    const scannedData = ref(null)
    const processing = ref(false)
    const cameras = ref([])
    const selectedCameraId = ref('')

    // Configuration du scanner
    const scannerConfig = {
      fps: parseInt(import.meta.env.VITE_QR_SCANNER_FPS) || 10,
      qrbox: {
        width: parseInt(import.meta.env.VITE_QR_SCANNER_QRBOX_SIZE) || 250,
        height: parseInt(import.meta.env.VITE_QR_SCANNER_QRBOX_SIZE) || 250
      },
      aspectRatio: 1.0,
      disableFlip: false,
      videoConstraints: {
        facingMode: 'environment' // Caméra arrière par défaut
      }
    }

    // Méthodes
    const initializeScanner = async () => {
      loading.value = true
      error.value = null

      try {
        // Vérifier les permissions de caméra
        await checkCameraPermissions()
        
        // Obtenir la liste des caméras
        await getCameras()
        
        // Initialiser le scanner
        scanner.value = new Html5QrcodeScanner(
          'qr-reader',
          scannerConfig,
          false // verbose
        )

        // Démarrer le scanner
        scanner.value.render(onScanSuccess, onScanError)
        isScanning.value = true

      } catch (err) {
        console.error('Erreur d\'initialisation du scanner:', err)
        error.value = getErrorMessage(err)
      } finally {
        loading.value = false
      }
    }

    const checkCameraPermissions = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true })
        // Fermer immédiatement le stream de test
        stream.getTracks().forEach(track => track.stop())
      } catch (err) {
        throw new Error('Accès à la caméra refusé. Veuillez autoriser l\'accès à la caméra.')
      }
    }

    const getCameras = async () => {
      try {
        const devices = await Html5Qrcode.getCameras()
        cameras.value = devices
        
        if (devices.length > 0) {
          // Sélectionner la caméra arrière par défaut si disponible
          const backCamera = devices.find(camera => 
            camera.label.toLowerCase().includes('back') || 
            camera.label.toLowerCase().includes('rear')
          )
          selectedCameraId.value = backCamera ? backCamera.id : devices[0].id
        }
      } catch (err) {
        console.warn('Impossible de récupérer la liste des caméras:', err)
      }
    }

    const onScanSuccess = (decodedText, decodedResult) => {
      console.log('QR Code scanné:', decodedText)
      
      scannedData.value = decodedText
      stopScanner()
      
      // Vibration si supportée
      if (navigator.vibrate) {
        navigator.vibrate(200)
      }

      emit('scan-success', {
        text: decodedText,
        result: decodedResult
      })
    }

    const onScanError = (error) => {
      // Ne pas afficher les erreurs de scan normales (pas de QR code détecté)
      if (!error.includes('No QR code found')) {
        console.warn('Erreur de scan:', error)
      }
    }

    const stopScanner = () => {
      if (scanner.value) {
        try {
          scanner.value.clear()
          isScanning.value = false
        } catch (err) {
          console.warn('Erreur lors de l\'arrêt du scanner:', err)
        }
      }
    }

    const toggleCamera = () => {
      if (isScanning.value) {
        stopScanner()
      } else {
        initializeScanner()
      }
    }

    const switchCamera = async () => {
      if (cameras.value.length <= 1) return

      const currentIndex = cameras.value.findIndex(c => c.id === selectedCameraId.value)
      const nextIndex = (currentIndex + 1) % cameras.value.length
      selectedCameraId.value = cameras.value[nextIndex].id
      
      await changeCamera()
    }

    const changeCamera = async () => {
      if (!selectedCameraId.value) return

      stopScanner()
      await nextTick()
      
      // Mettre à jour la configuration avec la nouvelle caméra
      scannerConfig.videoConstraints = {
        deviceId: { exact: selectedCameraId.value }
      }
      
      await initializeScanner()
    }

    const resetScanner = () => {
      scannedData.value = null
      processing.value = false
      error.value = null
      initializeScanner()
    }

    const handleScanResult = async () => {
      processing.value = true
      
      try {
        // Extraire l'ID de l'asset depuis l'URL du QR code
        const assetId = extractAssetId(scannedData.value)
        
        if (assetId) {
          emit('scan-success', {
            text: scannedData.value,
            assetId: assetId
          })
        } else {
          throw new Error('QR code invalide. Impossible d\'extraire l\'ID de l\'équipement.')
        }
      } catch (err) {
        toast.error(err.message)
        emit('scan-error', err)
      } finally {
        processing.value = false
      }
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

    const getErrorMessage = (error) => {
      if (error.message) {
        return error.message
      }
      
      if (error.name === 'NotAllowedError') {
        return 'Accès à la caméra refusé. Veuillez autoriser l\'accès à la caméra.'
      }
      
      if (error.name === 'NotFoundError') {
        return 'Aucune caméra trouvée sur cet appareil.'
      }
      
      if (error.name === 'NotSupportedError') {
        return 'Votre navigateur ne supporte pas l\'accès à la caméra.'
      }
      
      return 'Erreur lors de l\'initialisation de la caméra.'
    }

    // Lifecycle
    onMounted(() => {
      initializeScanner()
    })

    onUnmounted(() => {
      stopScanner()
    })

    return {
      scanner,
      isScanning,
      loading,
      error,
      scannedData,
      processing,
      cameras,
      selectedCameraId,
      initializeScanner,
      toggleCamera,
      switchCamera,
      changeCamera,
      resetScanner,
      handleScanResult
    }
  }
}
</script>

<style scoped>
.qr-scanner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 1rem;
  padding: 2rem;
  min-height: 500px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.scanner-container {
  max-width: 400px;
  margin: 0 auto;
  width: 100%;
}

.video-container {
  position: relative;
  border-radius: 1rem;
  overflow: hidden;
  background: #000;
}

.qr-reader {
  width: 100% !important;
  border: none !important;
}

.qr-reader video {
  border-radius: 1rem;
}

.scan-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  display: flex;
  align-items: center;
  justify-content: center;
}

.scan-frame {
  position: relative;
  width: 250px;
  height: 250px;
  border: 2px solid rgba(255, 255, 255, 0.5);
  border-radius: 1rem;
}

.corner {
  position: absolute;
  width: 30px;
  height: 30px;
  border: 3px solid #fff;
}

.corner.top-left {
  top: -3px;
  left: -3px;
  border-right: none;
  border-bottom: none;
  border-top-left-radius: 1rem;
}

.corner.top-right {
  top: -3px;
  right: -3px;
  border-left: none;
  border-bottom: none;
  border-top-right-radius: 1rem;
}

.corner.bottom-left {
  bottom: -3px;
  left: -3px;
  border-right: none;
  border-top: none;
  border-bottom-left-radius: 1rem;
}

.corner.bottom-right {
  bottom: -3px;
  right: -3px;
  border-left: none;
  border-top: none;
  border-bottom-right-radius: 1rem;
}

.scan-instructions {
  position: absolute;
  bottom: 1rem;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 2rem;
  font-size: 0.875rem;
}

.success-icon i {
  font-size: 3rem;
}

.error-icon i {
  font-size: 3rem;
}

.result-content {
  max-width: 400px;
  margin: 0 auto;
}

/* Responsive */
@media (max-width: 576px) {
  .qr-scanner {
    padding: 1rem;
    border-radius: 0;
    min-height: 100vh;
  }
  
  .scan-frame {
    width: 200px;
    height: 200px;
  }
  
  .corner {
    width: 25px;
    height: 25px;
  }
}

/* Animations */
@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(255, 255, 255, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(255, 255, 255, 0);
  }
}

.scan-frame {
  animation: pulse 2s infinite;
}
</style>