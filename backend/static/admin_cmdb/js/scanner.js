// backend/static/admin_cmdb/js/scanner.js
// ============================================================================
// SCANNER QR/Code-Barres — Webcam + USB (HoneyWell)
// CORRECTION: Buffer USB correctement géré
// Version: 3.0 — Correction createApp + USB Buffer
// ============================================================================

// ✅ CORRECTION LIGNE 1 — Utiliser window.VueCreateApp (défini dans api.js)
const createApp = window.VueCreateApp || Vue.createApp;

// Vérification que createApp est disponible
if (typeof createApp !== 'function') {
    console.error('❌ createApp n\'est pas une fonction !');
    console.error('Vérifiez que Vue.js et api.js sont chargés avant scanner.js');
}

createApp({
    delimiters: ['[[', ']]'],
    data() {
        return {
            cameraActive: false,
            continuousScan: false,
            scannerType: 'usb', // 'webcam' ou 'usb'
            scanResult: null,
            scanHistory: [],
            locations: [],
            showManualSearch: false,
            showMoveModal: false,
            manualSearchQuery: '',
            manualSearchResults: [],
            moveLocation: '',
            codeReader: null,
            searchTimeout: null,
            
            // USB Scanner Configuration
            usbBuffer: '',
            usbScanTimeout: null,
            USB_SCAN_DELAY: 100,
            lastKeyTime: 0,
            keyCount: 0,
            isListening: false,
            msg: 'Scanner prêt - Mode USB actif'
        }
    },
    mounted() {
        console.log('🔧 [SCANNER] mounted()');
        this.lastKeyTime = Date.now();
        this.initZXing();
        this.loadScanHistory();
        this.fetchLocations();
        this.setupKeyboardListener();
        console.log('✅ [SCANNER] Initialisation terminée');
    },
    // ❌ SUPPRIMER updated() — Crée des écouteurs multiples
    // updated() {
    //     this.setupKeyboardListener();  // ❌ À SUPPRIMER
    // },
    beforeUnmount() {
        console.log('🔧 [SCANNER] beforeUnmount()');
        this.stopCamera();
        this.removeKeyboardListener();
    },
    methods: {
        // ====================================================================
        // ZXing - Webcam
        // ====================================================================
        initZXing() {
            console.log('📷 [SCANNER] initZXing()');
            this.codeReader = new ZXing.BrowserMultiFormatReader();
        },
        async startCamera() {
            console.log('📷 [SCANNER] startCamera()');
            
            if (this.scannerType === 'usb') {
                console.log('⚠️ [SCANNER] Mode USB - caméra non démarrée');
                return;
            }
            
            try {
                const videoInputDevices = await ZXing.BrowserMultiFormatReader.listVideoInputDevices();
                let selectedDevice = videoInputDevices.find(device =>
                    device.label.toLowerCase().includes('back') ||
                    device.label.toLowerCase().includes('environment')
                ) || videoInputDevices[0];

                await this.codeReader.decodeFromVideoDevice(
                    selectedDevice ? selectedDevice.deviceId : undefined,
                    '#camera-preview',
                    (result, err) => {
                        if (result) {
                            console.log('✅ [SCANNER] QR détecté:', result.getText());
                            this.handleScanResult(result.getText());
                            if (!this.continuousScan) {
                                this.stopCamera();
                            }
                        }
                    }
                );
                this.cameraActive = true;
                console.log('✅ [SCANNER] Caméra démarrée');
            } catch (error) {
                console.error('❌ [SCANNER] Erreur caméra:', error);
                alert('Impossible d\'accéder à la caméra');
            }
        },
        stopCamera() {
            console.log('📷 [SCANNER] stopCamera()');
            if (this.codeReader) {
                this.codeReader.reset();
            }
            this.cameraActive = false;
        },
        toggleCamera() {
            console.log('🔄 [SCANNER] toggleCamera()');
            if (this.cameraActive) {
                this.stopCamera();
            } else {
                this.startCamera();
            }
        },
        
        // ====================================================================
        // USB SCANNER — Gestion Buffer
        // ====================================================================
        setupKeyboardListener() {
            console.log('🔌 [SCANNER] setupKeyboardListener()');
            this.removeKeyboardListener();
            
            if (this.scannerType !== 'usb') {
                console.log('⚠️ [SCANNER] Pas en mode USB');
                return;
            }
            
            document.addEventListener('keydown', this.handleKeyboardInput);
            this.isListening = true;
            console.log('✅ [SCANNER] Écouteur USB ACTIVÉ');
        },
        
        removeKeyboardListener() {
            console.log('🔌 [SCANNER] removeKeyboardListener()');
            if (this.isListening) {
                document.removeEventListener('keydown', this.handleKeyboardInput);
                this.isListening = false;
                console.log('✅ [SCANNER] Écouteur USB DÉSACTIVÉ');
            }
        },
        
        // ✅ MÉTHODE UNIQUE — Pas de double déclaration
        handleKeyboardInput(event) {
            console.log('⌨️ [SCANNER] Touche:', event.key);
            
            if (this.scannerType !== 'usb') return;
            
            // Ignorer touches de modification
            if (event.ctrlKey || event.altKey || event.shiftKey || event.metaKey) {
                return;
            }
            
            const now = Date.now();
            const timeSinceLastKey = now - this.lastKeyTime;
            this.lastKeyTime = now;
            
            console.log('⏱️ [SCANNER] Délai:', timeSinceLastKey, 'ms | Buffer:', this.usbBuffer);
            
            // Entrée = fin de scan
            if (event.key === 'Enter') {
                console.log('⏎ [SCANNER] Enter détecté');
                this.processUSBBuffer();
                event.preventDefault();
                return;
            }
            
            // Délai trop long = saisie humaine
            if (timeSinceLastKey > 150 && this.usbBuffer.length > 0) {
                console.log('⏱️ [SCANNER] Délai trop long - Buffer clear');
                this.usbBuffer = '';
                this.keyCount = 0;
                return;
            }
            
            // Accumuler caractères
            if (event.key.length === 1) {
                this.usbBuffer += event.key;
                this.keyCount++;
                console.log('📝 [SCANNER] Buffer:', this.usbBuffer, '(', this.keyCount, ')');
                
                clearTimeout(this.usbScanTimeout);
                this.usbScanTimeout = setTimeout(() => {
                    console.log('⏰ [SCANNER] Timeout');
                    this.processUSBBuffer();
                }, this.USB_SCAN_DELAY);
            }
        },
        
        processUSBBuffer() {
            console.log('🔄 [SCANNER] processUSBBuffer()');
            const code = this.usbBuffer.trim();
            
            console.log('📝 [SCANNER] Code:', code, '| Length:', code.length);
            
            if (code.length < 3) {
                console.log('❌ [SCANNER] Code trop court');
                this.usbBuffer = '';
                this.keyCount = 0;
                return;
            }
            
            console.log('✅ [SCANNER] Code valide - Appel API');
            this.handleScanResult(code);
            
            this.usbBuffer = '';
            this.keyCount = 0;
            clearTimeout(this.usbScanTimeout);
        },
        
        // ====================================================================
        // TRAITEMENT SCAN
        // ====================================================================
        async handleScanResult(scanCode) {
            console.log('📡 [SCANNER] handleScanResult()', scanCode);
            this.msg = `Scan: ${scanCode}`;
            
            const extractedUuid = this.extractUuidFromQR(scanCode);
            console.log('🔑 [SCANNER] UUID:', extractedUuid);
            
            try {
                console.log('🌐 [SCANNER] Appel API:', `/scanner/scan/${extractedUuid}/`);
                
                const response = await window.apiClient.get(`/scanner/scan/${extractedUuid}/`);
                
                console.log('✅ [SCANNER] Réponse:', response.status);
                
                if (!response.data) {
                    throw new Error('Données vides');
                }
                
                this.scanResult = response.data;
                console.log('✅ [SCANNER] Asset:', response.data.name);
                
                this.addToHistory({
                    uuid: extractedUuid,
                    asset_name: response.data.name || 'Asset sans nom',
                    scanned_at: new Date().toISOString()
                });
                
                this.playBeep();
                this.msg = `✅ ${response.data.name}`;
                
            } catch (error) {
                console.error('❌ [SCANNER] Erreur:', error);
                
                if (error.response && error.response.status === 404) {
                    alert(`❌ Code non reconnu: ${extractedUuid}`);
                } else if (error.response && error.response.status === 401) {
                    alert('⚠️ Session expirée');
                    window.location.href = '/admin/login/';
                } else {
                    alert('❌ Erreur scan');
                }
            }
        },
        
        extractUuidFromQR(qrText) {
            console.log('🔑 [SCANNER] extractUuidFromQR()', qrText);
            
            // Format: qr_asset_<id>_<uuid>
            const parts = qrText.split('_');
            if (parts.length >= 3) {
                return parts[parts.length - 1];
            }
            
            // Format: UUID direct ou Serial/Code
            return qrText;
        },
        
        // ====================================================================
        // HISTORIQUE
        // ====================================================================
        addToHistory(scan) {
            if (!scan) return;
            this.scanHistory.unshift(scan);
            if (this.scanHistory.length > 10) {
                this.scanHistory.pop();
            }
            localStorage.setItem('cmdb_scan_history', JSON.stringify(this.scanHistory));
        },
        loadScanHistory() {
            const saved = localStorage.getItem('cmdb_scan_history');
            if (saved) {
                try {
                    const parsed = JSON.parse(saved);
                    this.scanHistory = parsed.filter(scan => scan && scan.uuid && scan.asset_name);
                } catch (e) {
                    this.scanHistory = [];
                }
            }
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
        
        // ====================================================================
        // RECHERCHE & LOCATIONS
        // ====================================================================
        async fetchLocations() {
            try {
                const response = await window.apiClient.get('/inventory/location/');
                this.locations = response.data || [];
                console.log('📍 [SCANNER] Locations:', this.locations.length);
            } catch (error) {
                console.error('❌ [SCANNER] Erreur locations:', error);
                this.locations = [];
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
                    console.error('❌ [SCANNER] Erreur recherche:', error);
                }
            }, 300);
        },
        selectManualResult(asset) {
            console.log('✅ [SCANNER] selectManualResult()', asset);
            this.scanResult = asset;
            this.showManualSearch = false;
            this.manualSearchQuery = '';
            this.manualSearchResults = [];
        },
        
        // ====================================================================
        // ACTIONS
        // ====================================================================
        async moveAsset() {
            if (!this.moveLocation || !this.scanResult || !this.scanResult.id) {
                alert('Aucun asset sélectionné');
                return;
            }
            
            try {
                await window.apiClient.post(`/inventory/assets/${this.scanResult.id}/move/`, {
                    location_id: this.moveLocation
                });
                alert('✅ Asset déplacé');
                this.showMoveModal = false;
                this.moveLocation = '';
            } catch (error) {
                alert('❌ Erreur déplacement');
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
                day: '2-digit', month: '2-digit', year: 'numeric',
                hour: '2-digit', minute: '2-digit'
            });
        },
        playBeep() {
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
                console.warn('⚠️ AudioContext non supporté');
            }
        },
        switchScannerType(type) {
            console.log('🔄 [SCANNER] switchScannerType()', type);
            this.scannerType = type;
            this.lastKeyTime = Date.now();
            this.msg = `Mode: ${type === 'usb' ? 'Scanner USB' : 'Caméra Web'}`;
            
            if (type === 'webcam') {
                this.removeKeyboardListener();
                this.startCamera();
            } else if (type === 'usb') {
                this.stopCamera();
                this.setupKeyboardListener();
            }
        }
    }
}).mount('#scanner-app');