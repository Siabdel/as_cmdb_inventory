// backend/static/admin_cmdb/js/scanner.js
// ============================================================================
// SCANNER QR/Code-Barres — Webcam + USB (HoneyWell)
// CORRECTION: Buffer USB correctement géré
// ============================================================================

if (typeof window.VueCreateApp === 'undefined') {
    console.error('❌ window.VueCreateApp non défini !');
    if (typeof Vue !== 'undefined') {
        window.VueCreateApp = Vue.createApp;
    }
}

const createApp = window.VueCreateApp;

createApp({
    delimiters: ['[[', ']]'],
    data() {
        return {
            cameraActive: false,
            continuousScan: false,
            scannerType: 'usb',
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
            
            // === USB SCANNER CONFIGURATION ===
            usbBuffer: '',
            usbScanTimeout: null,
            USB_SCAN_DELAY: 50,   // ⚠️ RÉDUIT à 50ms (scanners envoient très vite)
            MIN_SCAN_LENGTH: 3,
            lastKeyTime: 0,
            isListening: false,
            keyCount: 0,          // 🔍 DEBUG: Compteur de touches
            msg: 'Scanner prêt - Mode USB actif'
        }
    },
    mounted() {
        console.log('🔧 [SCANNER] mounted() appelé');
        
        // ⚠️ CRITIQUE: Initialiser lastKeyTime MAINTENANT
        this.lastKeyTime = Date.now();
        console.log('⏱️ [SCANNER] lastKeyTime initialisé:', this.lastKeyTime);
        
        this.initZXing();
        this.loadScanHistory();
        this.fetchLocations();
        this.setupUSBScannerListener();
        
        console.log('✅ [SCANNER] Initialisation terminée');
        console.log('📡 [SCANNER] Mode:', this.scannerType);
        console.log('🔌 [SCANNER] Écouteur USB:', this.isListening ? 'ACTIF' : 'INACTIF');
    },
    beforeUnmount() {
        console.log('🔧 [SCANNER] beforeUnmount() appelé');
        this.stopCamera();
        this.removeUSBScannerListener();
    },
    methods: {
        // ====================================================================
        // ZXing - Webcam Scanner
        // ====================================================================
        initZXing() {
            console.log('📷 [SCANNER] initZXing()');
            this.codeReader = new ZXing.BrowserMultiFormatReader();
        },
        async startCamera() {
            console.log('📷 [SCANNER] startCamera() appelé');
            
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
                            console.log('✅ [SCANNER] QR détecté par caméra:', result.getText());
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
                console.error('❌ [SCANNER] Erreur accès caméra:', error);
                alert('Impossible d\'accéder à la caméra. Vérifiez les permissions.');
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
        // USB SCANNER — GESTION DU BUFFER (HoneyWell)
        // ====================================================================
        setupUSBScannerListener() {
            console.log('🔌 [SCANNER] setupUSBScannerListener() appelé');
            this.removeUSBScannerListener();
            
            if (this.scannerType !== 'usb') {
                console.log('⚠️ [SCANNER] Pas en mode USB - écouteur non activé');
                return;
            }
            
            document.addEventListener('keydown', this.handleUSBKeyboardInput);
            this.isListening = true;
            console.log('✅ [SCANNER] Écouteur USB scanner ACTIVÉ');
            console.log('📝 [SCANNER] usbBuffer initial:', this.usbBuffer);
        },
        
        removeUSBScannerListener() {
            console.log('🔌 [SCANNER] removeUSBScannerListener() appelé');
            if (this.isListening) {
                document.removeEventListener('keydown', this.handleUSBKeyboardInput);
                this.isListening = false;
                console.log('✅ [SCANNER] Écouteur USB scanner DÉSACTIVÉ');
            }
        },
        
        // ⚠️ MÉTHODE CRITIQUE - CORRECTION COMPLÈTE
        handleUSBKeyboardInput(event) {
            // 🔍 DEBUG: TOUTES les touches sont logguées
            console.log('⌨️ [SCANNER] handleUSBKeyboardInput() déclenché');
            console.log('🔑 [SCANNER] Touche:', event.key, '| Code:', event.keyCode, '| Length:', event.key.length);
            
            // Ignorer si on n'est pas en mode USB
            if (this.scannerType !== 'usb') {
                console.log('⚠️ [SCANNER] Pas en mode USB - ignoré');
                return;
            }
            
            // Ignorer les touches de modification (Ctrl, Alt, Shift, etc.)
            if (event.ctrlKey || event.altKey || event.shiftKey || event.metaKey) {
                console.log('⚠️ [SCANNER] Touche de modification - ignorée');
                return;
            }
            
            const now = Date.now();
            const timeSinceLastKey = now - this.lastKeyTime;
            
            // 🔍 DEBUG: Afficher le délai
            console.log('⏱️ [SCANNER] Délai depuis dernière touche:', timeSinceLastKey, 'ms');
            console.log('📝 [SCANNER] Buffer avant:', JSON.stringify(this.usbBuffer), '(', this.usbBuffer.length, 'chars)');
            console.log('🔢 [SCANNER] Compteur touches:', this.keyCount);
            
            // Touche Entrée = fin de scan
            if (event.key === 'Enter') {
                console.log('⏎ [SCANNER] Entrée détectée - Traitement du buffer');
                console.log('📝 [SCANNER] Buffer final:', JSON.stringify(this.usbBuffer));
                this.processUSBBuffer();
                event.preventDefault();
                return;
            }
            
            // ⚠️ CORRECTION: Ne PAS clear buffer si length === 0 (1er caractère)
            // Les scanners envoient très vite (< 50ms), les humains > 150ms
            if (timeSinceLastKey > 150 && this.usbBuffer.length > 0) {
                console.log('⏱️ [SCANNER] Délai trop long - Buffer ignoré (saisie humaine)');
                this.usbBuffer = '';
                this.keyCount = 0;
                return;
            }
            
            // Accumuler les caractères (uniquement les caractères imprimables)
            if (event.key.length === 1) {
                this.usbBuffer += event.key;
                this.keyCount++;
                console.log('✅ [SCANNER] Caractère ajouté:', JSON.stringify(event.key));
                console.log('📝 [SCANNER] Buffer après:', JSON.stringify(this.usbBuffer), '(', this.usbBuffer.length, 'chars)');
                
                // Réinitialiser le timeout de fin de saisie
                clearTimeout(this.usbScanTimeout);
                this.usbScanTimeout = setTimeout(() => {
                    console.log('⏰ [SCANNER] Timeout atteint - Traitement automatique');
                    this.processUSBBuffer();
                }, this.USB_SCAN_DELAY);
            } else {
                console.log('⚠️ [SCANNER] Touche non imprimable ignorée:', event.key);
            }
            
            // Mettre à jour lastKeyTime TOUJOURS
            this.lastKeyTime = now;
        },
        
        processUSBBuffer() {
            console.log('🔄 [SCANNER] processUSBBuffer() appelé');
            const code = this.usbBuffer.trim();
            
            console.log('📝 [SCANNER] Code à traiter:', JSON.stringify(code), '| Longueur:', code.length);
            console.log('🔢 [SCANNER] Total touches reçues:', this.keyCount);
            
            // Valider la longueur minimum
            if (code.length < this.MIN_SCAN_LENGTH) {
                console.log('❌ [SCANNER] Code trop court - Ignoré (', code.length, '<', this.MIN_SCAN_LENGTH, ')');
                this.usbBuffer = '';
                this.keyCount = 0;
                return;
            }
            
            console.log('✅ [SCANNER] Code valide - Appel de handleScanResult');
            
            // Traiter le code scanné
            this.handleScanResult(code);
            
            // Réinitialiser le buffer
            this.usbBuffer = '';
            this.keyCount = 0;
            clearTimeout(this.usbScanTimeout);
        },
        
        // ====================================================================
        // TRAITEMENT DU SCAN (Commun Webcam + USB)
        // ====================================================================
        async handleScanResult(scanCode) {
            console.log('📡 [SCANNER] handleScanResult() appelé');
            console.log('📝 [SCANNER] Code reçu:', scanCode);
            
            this.msg = `Scan reçu: ${scanCode}`;
            
            const extractedUuid = this.extractUuidFromQR(scanCode);
            console.log('🔑 [SCANNER] UUID extrait:', extractedUuid);
            
            try {
                console.log('🌐 [SCANNER] Appel API:', `/scanner/scan/${extractedUuid}/`);
                
                const response = await window.apiClient.get(`/scanner/scan/${extractedUuid}/`);
                
                console.log('✅ [SCANNER] Réponse API reçue:', response.status);
                console.log('📦 [SCANNER] Données:', response.data);
                
                if (!response.data) {
                    throw new Error('Données de réponse vides');
                }
                
                this.scanResult = response.data;
                console.log('✅ [SCANNER] Asset trouvé:', response.data.name);
                
                this.addToHistory({
                    uuid: extractedUuid,
                    asset_name: response.data.name || 'Asset sans nom',
                    scanned_at: new Date().toISOString()
                });
                
                this.playBeep();
                this.msg = `✅ Scan réussi: ${response.data.name}`;
                
            } catch (error) {
                console.error('❌ [SCANNER] Erreur handleScanResult:', error);
                console.error('❌ [SCANNER] Error response:', error.response);
                
                if (error.response && error.response.status === 404) {
                    this.msg = `❌ Code non reconnu: ${extractedUuid}`;
                    alert(`❌ Code non reconnu dans le système\n\nCode: ${extractedUuid}`);
                } else if (error.response && error.response.status === 401) {
                    this.msg = `⚠️ Session expirée`;
                    alert('⚠️ Session expirée - Veuillez vous reconnecter');
                    window.location.href = '/admin/login/';
                } else {
                    this.msg = `❌ Erreur: ${error.message}`;
                    alert('❌ Erreur lors de la résolution du code');
                }
            }
        },
        
        extractUuidFromQR(qrText) {
            console.log('🔑 [SCANNER] extractUuidFromQR() - Texte:', qrText);
            
            const parts = qrText.split('_');
            if (parts.length >= 3) {
                const uuid = parts[parts.length - 1];
                console.log('🔑 [SCANNER] UUID extrait (format QR):', uuid);
                return uuid;
            }
            
            console.log('🔑 [SCANNER] Retour texte brut (code-barres):', qrText);
            return qrText;
        },
        
        // ====================================================================
        // HISTORIQUE DES SCANS
        // ====================================================================
        addToHistory(scan) {
            console.log('📜 [SCANNER] addToHistory()', scan);
            if (!scan) return;
            
            this.scanHistory.unshift(scan);
            if (this.scanHistory.length > 10) {
                this.scanHistory.pop();
            }
            localStorage.setItem('cmdb_scan_history', JSON.stringify(this.scanHistory));
        },
        
        loadScanHistory() {
            console.log('📜 [SCANNER] loadScanHistory()');
            const saved = localStorage.getItem('cmdb_scan_history');
            if (saved) {
                try {
                    const parsed = JSON.parse(saved);
                    this.scanHistory = parsed.filter(scan => scan && scan.uuid && scan.asset_name);
                    console.log('📜 [SCANNER] Historique chargé:', this.scanHistory.length, 'scans');
                } catch (e) {
                    console.error('❌ [SCANNER] Erreur parse historique:', e);
                    this.scanHistory = [];
                }
            }
        },
        
        async loadScanResult(uuid) {
            console.log('📡 [SCANNER] loadScanResult()', uuid);
            try {
                const response = await window.apiClient.get(`/scanner/scan/${uuid}/`);
                this.scanResult = response.data;
                this.showManualSearch = false;
            } catch (error) {
                alert('Asset non trouvé');
            }
        },
        
        // ====================================================================
        // RECHERCHE MANUELLE
        // ====================================================================
        async fetchLocations() {
            console.log('📍 [SCANNER] fetchLocations()');
            try {
                const response = await window.apiClient.get('/inventory/location/');
                this.locations = response.data.results || response.data || [];
                console.log('📍 [SCANNER] Locations chargées:', this.locations.length);
            } catch (error) {
                console.error('❌ [SCANNER] Erreur fetch locations:', error);
                this.locations = [];
            }
        },
        
        async manualSearch() {
            console.log('🔍 [SCANNER] manualSearch()', this.manualSearchQuery);
            if (!this.manualSearchQuery.trim()) return;
            
            clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(async () => {
                try {
                    const response = await window.apiClient.get('/inventory/assets/', {
                        params: { search: this.manualSearchQuery, page_size: 5 }
                    });
                    this.manualSearchResults = response.data.results || response.data;
                    console.log('🔍 [SCANNER] Résultats:', this.manualSearchResults.length);
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
        // ACTIONS SUR ASSET
        // ====================================================================
        async moveAsset() {
            console.log('📍 [SCANNER] moveAsset()');
            if (!this.moveLocation || !this.scanResult || !this.scanResult.id) {
                alert('Aucun asset sélectionné');
                return;
            }
            
            try {
                await window.apiClient.post(`/inventory/asset/${this.scanResult.id}/move/`, {
                    location_id: this.moveLocation
                });
                alert('✅ Asset déplacé avec succès');
                this.showMoveModal = false;
                this.moveLocation = '';
                if (this.scanResult && this.scanResult.uuid) {
                    this.loadScanResult(this.scanResult.uuid);
                }
            } catch (error) {
                alert('❌ Erreur lors du déplacement');
            }
        },
        
        // ====================================================================
        // UTILITAIRES
        // ====================================================================
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
            console.log('🔊 [SCANNER] playBeep()');
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
                console.warn('⚠️ [SCANNER] AudioContext non supporté');
            }
        },
        
        switchScannerType(type) {
            console.log('🔄 [SCANNER] switchScannerType()', type);
            this.scannerType = type;
            this.msg = `Mode: ${type === 'usb' ? 'Scanner USB' : 'Caméra Web'}`;
            
            // ⚠️ CRITIQUE: Réinitialiser lastKeyTime lors du switch
            this.lastKeyTime = Date.now();
            
            if (type === 'webcam') {
                this.removeUSBScannerListener();
                this.startCamera();
            } else if (type === 'usb') {
                this.stopCamera();
                this.setupUSBScannerListener();
            }
        }
    }
}).mount('#scanner-app');