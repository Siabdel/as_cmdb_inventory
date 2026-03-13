// static/admin_cmdb/js/scanner.js

const { createApp } = Vue;

createApp({
    delimiters: ['[[', ']]'],
    data() {
        return {
            cameraActive: false,
            continuousScan: false,
            scanResult: null,
            scanHistory: [],
            locations: [],
            showManualSearch: false,
            showMoveModal: false,
            manualSearchQuery: '',
            manualSearchResults: [],
            moveLocation: '',
            codeReader: null,
            searchTimeout: null
        }
    },
    mounted() {
        this.initZXing();
        this.loadScanHistory();
        this.fetchLocations();
    },
    beforeUnmount() {
        this.stopCamera();
    },
    methods: {
        initZXing() {
            // Initialisation de ZXing BrowserMultiFormatReader
            this.codeReader = new ZXing.BrowserMultiFormatReader();
        },
        async startCamera() {
            try {
                const videoInputDevices = await ZXing.BrowserMultiFormatReader.listVideoInputDevices();
                
                // Sélection de la caméra arrière par défaut sur mobile
                let selectedDevice = videoInputDevices.find(device => 
                    device.label.toLowerCase().includes('back') || 
                    device.label.toLowerCase().includes('environment')
                ) || videoInputDevices[0];

                await this.codeReader.decodeFromVideoDevice(
                    selectedDevice ? selectedDevice.deviceId : undefined,
                    '#camera-preview',
                    (result, err) => {
                        if (result) {
                            this.handleScanResult(result.getText());
                            if (!this.continuousScan) {
                                this.stopCamera();
                            }
                        }
                    }
                );
                
                this.cameraActive = true;
            } catch (error) {
                console.error('Erreur accès caméra:', error);
                alert('Impossible d\'accéder à la caméra. Vérifiez les permissions.');
            }
        },
        stopCamera() {
            if (this.codeReader) {
                this.codeReader.reset();
            }
            this.cameraActive = false;
        },
        toggleCamera() {
            if (this.cameraActive) {
                this.stopCamera();
            } else {
                this.startCamera();
            }
        },
        async handleScanResult(uuid) {
            // Extraction de l'UUID depuis le QR code
            // Format attendu: qr_asset_<id>_<uuid> ou juste <uuid>
            const extractedUuid = this.extractUuidFromQR(uuid);
            
            try {
                const response = await window.apiClient.get(`/scanner/scan/${extractedUuid}/`);
                this.scanResult = response.data;
                
                // Ajouter à l'historique
                this.addToHistory({
                    uuid: extractedUuid,
                    asset_name: response.data.name,
                    scanned_at: new Date().toISOString()
                });
                
                // Feedback sonore (optionnel)
                this.playBeep();
            } catch (error) {
                if (error.response && error.response.status === 404) {
                    alert('QR code non reconnu dans le système');
                } else {
                    alert('Erreur lors de la résolution du QR code');
                }
            }
        },
        extractUuidFromQR(qrText) {
            // Format: qr_asset_<id>_<uuid> ou <uuid>
            const parts = qrText.split('_');
            if (parts.length >= 3) {
                return parts[parts.length - 1];
            }
            return qrText;
        },
        async loadScanResult(uuid) {
            try {
                const response = await window.apiClient.get(`/scanner/scan/${uuid}/`);
                this.scanResult = response.data;
                this.showManualSearch = false;
            } catch (error) {
                alert('Asset non trouvé');
            }
        },
        addToHistory(scan) {
            // Garder seulement les 10 derniers scans
            this.scanHistory.unshift(scan);
            if (this.scanHistory.length > 10) {
                this.scanHistory.pop();
            }
            // Sauvegarder dans localStorage
            localStorage.setItem('cmdb_scan_history', JSON.stringify(this.scanHistory));
        },
        loadScanHistory() {
            const saved = localStorage.getItem('cmdb_scan_history');
            if (saved) {
                this.scanHistory = JSON.parse(saved);
            }
        },
        async fetchLocations() {
            try {
                const response = await window.apiClient.get('/inventory/location/');
                this.locations = response.data;
            } catch (error) {
                console.error('Erreur fetch locations:', error);
            }
        },
        async manualSearch() {
            if (!this.manualSearchQuery.trim()) return;
            
            clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(async () => {
                try {
                    const response = await window.apiClient.get('/inventory/assets/', {
                        params: { search: this.manualSearchQuery, page_size: 5 }
                    });
                    this.manualSearchResults = response.data.results || response.data;
                } catch (error) {
                    console.error('Erreur recherche:', error);
                }
            }, 300);
        },
        selectManualResult(asset) {
            this.scanResult = asset;
            this.showManualSearch = false;
            this.manualSearchQuery = '';
            this.manualSearchResults = [];
        },
        async moveAsset() {
            if (!this.moveLocation) return;
            
            try {
                await window.apiClient.post(`/inventory/asset/${this.scanResult.id}/move/`, {
                    location_id: this.moveLocation
                });
                alert('Asset déplacé avec succès');
                this.showMoveModal = false;
                this.moveLocation = '';
                // Rafraîchir le résultat
                this.loadScanResult(this.scanResult.uuid);
            } catch (error) {
                alert('Erreur lors du déplacement');
            }
        },
        getStatusClass(status) {
            const map = {
                'active': 'status-active',
                'maintenance': 'status-maintenance',
                'retired': 'status-retired',
                'stock': 'status-stock',
                'repair': 'status-repair'
            };
            return map[status] || 'status-stock';
        },
        formatDate(dateStr) {
            if (!dateStr) return '-';
            return new Date(dateStr).toLocaleDateString('fr-FR', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        },
        playBeep() {
            // Feedback sonore optionnel
            try {
                const audio = new AudioContext();
                const oscillator = audio.createOscillator();
                const gain = audio.createGain();
                oscillator.connect(gain);
                gain.connect(audio.destination);
                oscillator.frequency.value = 800;
                oscillator.type = 'sine';
                gain.gain.value = 0.1;
                oscillator.start();
                setTimeout(() => oscillator.stop(), 150);
            } catch (e) {
                // Ignorer si AudioContext non supporté
            }
        }
    }
}).mount('#scanner-app');