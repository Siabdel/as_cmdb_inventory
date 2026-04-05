// ============================================================================
// static/admin_cmdb/js/scanner.js
// ============================================================================
// SCANNER QR/Code-Barres — Correction Finale (this Context + Buffer)
// ============================================================================// static/admin_cmdb/js/scanner.js
// ============================================================================
// SCANNER QR/Code-Barres — Version Quagga.js (Webcam)
// Remplace l'approche USB HID par détection visuelle
// ============================================================================
if (typeof window.VueCreateApp === 'undefined') {
    console.error('❌ window.VueCreateApp non défini !');
    if (typeof Vue !== 'undefined') {
        window.VueCreateApp = Vue.createApp;
    }
}

// static/admin_cmdb/js/scanner.js
// ============================================================================
// SCANNER QR/Code-Barres — Version Input Formulaire (RECOMMANDÉ)
// Capture le scanner USB via un input caché au lieu de document keydown
// ============================================================================

const createApp = window.VueCreateApp || Vue.createApp;

createApp({
    delimiters: ['[[', ']]'],
    data() {
        return {
            // UI State
            scannerActive: true,
            cameraActive: false,
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
            msg: 'Scanner prêt - Mode USB actif',
            
            // ✅ USB Scanner — Input Buffer (PLUS DE GESTION MANUELLE)
            usbBuffer: '',
            lastScanTime: 0,
            SCAN_DEBOUNCE: 1000, // 1 seconde entre scans
             // ✅ NOUVEAU: Contexte et location pour traçabilité
            scanContext: 'inventory', // inventory, maintenance, movement, audit
            currentLocationId: null,
             // ✅ NOUVEAU: Contrôle du focus
            shouldRefocus: true,  // Flag pour contrôler le re-focus
            focusTimeout: null,   // Timeout pour re-focus
        }
    },
    
    mounted() {
        console.log('🔧 [SCANNER] mounted()');
        this.loadScanHistory();
        this.fetchLocations();
        
        // ✅ Focus automatique sur l'input USB au chargement
        if (this.scannerType === 'usb') {
            this.focusInput();
        }
          // ✅ NOUVEAU: Empêcher la perte de focus sur click document
        document.addEventListener('click', this.handleDocumentClick);
        document.addEventListener('mousedown', this.handleDocumentClick);
    },
    
    beforeUnmount() {
        console.log('🔧 [SCANNER] beforeUnmount()');
        this.stopCamera();
        
        // ✅ Cleanup event listeners
        document.removeEventListener('click', this.handleDocumentClick);
        document.removeEventListener('mousedown', this.handleDocumentClick);
        
        if (this.focusTimeout) {
            clearTimeout(this.focusTimeout);
        }
    },
    
    methods: {
        // ====================================================================
        // USB SCANNER — Gestion via Input (SIMPLIFIÉ)
        // ====================================================================
        // ====================================================================
        // ✅ NOUVEAU: Gestion intelligente du focus
        // ====================================================================
        // ✅ DÉTECTER CLICKS INTENTIONNELS
        handleDocumentClick(event) {
            const target = event.target;
            const isInteractive = target.matches(
                'button, a, input, select, textarea, [role="button"], .modal, .modal *'
            );
            
            if (isInteractive) {
                console.log('🖱️ [SCANNER] Click interactif détecté, pas de re-focus');
                this.shouldRefocus = false;
                
                if (this.focusTimeout) {
                    clearTimeout(this.focusTimeout);
                }
                this.focusTimeout = setTimeout(() => {
                    this.shouldRefocus = true;
                    console.log('✅ [SCANNER] Re-focus réactivé');
                }, 2000);
            }
        },
    
        //--------------------------------------------------------------------------
        // ✅ Focus intelligent sur l'input USB
        //--------------------------------------------------------------------------
        focusInput() {
            // ✅ Focus sur l'input caché pour capturer le scanner USB
            const input = document.getElementById('usb-scanner-input');
            if (input) {
                input.focus();
                console.log('✅ [SCANNER] Input focusé');
            }
        },
        //-------------------------------------------------------------------------
        // ✅ Gestion des événements de focus pour maintenir le focus sur l'input
        //-------------------------------------------------------------------------
        onInputFocus() {
            console.log('📝 [SCANNER] Input focusé');
        },
        
        //--------------------------------------------------------------------------
        // ✅ Re-focus automatique si l'input perd le focus (et que c'est autorisé)
        //--------------------------------------------------------------------------
        onInputBlur() {
            console.log('⚠️ [SCANNER] Input perdu le focus');
            
            // ✅ CONTRÔLE: Ne re-focus que si shouldRefocus = true
            if (this.shouldRefocus && this.scannerType === 'usb' && this.scannerActive) {
                if (this.focusTimeout) {
                    clearTimeout(this.focusTimeout);
                }
                this.focusTimeout = setTimeout(() => {
                    if (this.shouldRefocus) {
                        this.focusInput();
                    }
                }, 300);  // ✅ 300ms au lieu de 100ms
            } else {
                console.log('⚠️ [SCANNER] Re-focus désactivé (click intentionnel)');
            }
        },

        //--------------------------------------------------------------------------
        // ✅ Gestion de la saisie dans l'input USB
        //--------------------------------------------------------------------------
        onEnterPressed() {
            // ✅ Entrée pressée = fin du scan
            console.log('⏎ [SCANNER] Enter détecté');
            
            const code = this.usbBuffer.trim();
            
            if (code.length >= 3) {
                console.log('✅ [SCANNER] Code valide:', code);
                this.handleScanResult(code);
            } else {
                console.log('⚠️ [SCANNER] Code trop court:', code);
            }
            
            // ✅ Reset buffer
            this.usbBuffer = '';
            
            // ✅ Garder le focus
            this.focusInput();
        },
       //-------------------------------------------------------------------------- 
       // ✅ Réinitialiser le scanner (ex: bouton reset)
       //-------------------------------------------------------------------------- 
        resetScanner() {
            this.usbBuffer = '';
            this.focusInput();
        },
        //--------------------------------------------------------------------------
        // ✅ Changer de type de scanner (USB/Webcam)
        //-------------------------------------------------------------------------- 
        switchScannerType(type) {
            console.log('🔄 [SCANNER] switchScannerType()', type);
            this.scannerType = type;
            this.msg = `Mode: ${type === 'usb' ? 'Scanner USB' : 'Caméra Web'}`;
            
            if (type === 'usb') {
                this.stopCamera();
                this.focusInput();
            } else if (type === 'webcam') {
                this.startCamera();
            }
        },
        
        // ====================================================================
        // Gestion modals — Désactiver re-focus pendant modal ouverte
        // ====================================================================
        openModal(modalName) {
            this[modalName] = true;
            this.shouldRefocus = false;  // ✅ Désactiver re-focus pendant modal
        },
        
        closeModal(modalName) {
            this[modalName] = false;
            // ✅ Réactiver re-focus après 500ms (après fermeture modal)
            setTimeout(() => {
                this.shouldRefocus = true;
                this.focusInput();
            }, 500);
        },
        
        // ====================================================================
        // WEBCAM — ZXing (Inchangé)
        // ====================================================================
        initZXing() {
            this.codeReader = new ZXing.BrowserMultiFormatReader();
        },
        //--------------------------------------------------------------------------
        // ✅ Démarrer la caméra et le scanner ZXing
        //--------------------------------------------------------------------------
        async startCamera() {
            if (this.scannerType === 'usb') return;
            
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
                            this.handleScanResult(result.getText());
                            if (!this.continuousScan) this.stopCamera();
                        }
                    }
                );
                this.cameraActive = true;
            } catch (error) {
                console.error('❌ Erreur caméra:', error);
                alert('Impossible d\'accéder à la caméra');
            }
        },
        //--------------------------------------------------------------------------
        // Arrêter la caméra et le scanner ZXing
        //--------------------------------------------------------------------------
        stopCamera() {
            if (this.codeReader) this.codeReader.reset();
            this.cameraActive = false;
        },

        //--------------------------------------------------------------------------
        // ✅ Basculer entre caméra active/inactive
        //--------------------------------------------------------------------------
        
        toggleCamera() {
            if (this.cameraActive) this.stopCamera();
            else this.startCamera();
        },
        
        // ====================================================================
        // TRAITEMENT SCAN — Commun USB/Webcam
        // ====================================================================
        async handleScanResult(code) {
            console.log('📡 [SCANNER] handleScanResult()', code);
            this.msg = `Scan: ${code}`;
            
            // Anti-doublon
            const now = Date.now();
            if (now - this.lastScanTime < this.SCAN_DEBOUNCE) {
                console.log('⏱️ [SCANNER] Scan trop rapide - ignoré');
                return;
            }
            this.lastScanTime = now;
            
            const extractedUuid = this.extractUuidFromQR(code);
            console.log('🔑 [SCANNER] UUID extrait:', extractedUuid);
            
            try {
                console.log('🌐 [SCANNER] Appel API:', `/scanner/scan/${extractedUuid}/`);
                
                const response = await window.apiClient.get(`/scanner/scan/${extractedUuid}/`, {
                    params: {
                        context: this.scanContext,
                        location_id: this.currentLocationId,
                        user: window.currentUser ? window.currentUser.username : 'unknown',
                    }
                });
                
                if (!response.data) throw new Error('Données vides');
                
                this.scanResult = response.data;
                console.log('✅ [SCANNER] Asset:', response.data.name);
                
                // ✅ NOUVEAU: Stocker scan_log_id pour référence
                if (response.data.scan_log_id) {
                    localStorage.setItem('last_scan_log_id', response.data.scan_log_id);
                    console.log('📝 [SCANNER] ScanLog ID:', response.data.scan_log_id);
                }
                
                this.addToHistory({
                    uuid: extractedUuid,
                    asset_name: response.data.name || 'Asset sans nom',
                    scanned_at: new Date().toISOString(),
                    code_type: response.data.code_type, // ✅ Nouveau
                    scan_log_id: response.data.scan_log_id, // ✅ Nouveau
                    scanned_at: new Date().toISOString()
                });
                
                this.playBeep();
                this.msg = `✅ ${response.data.name}`;
                
            } catch (error) {
                console.error('❌ [SCANNER] Erreur:', error);
                
                if (error.response?.status === 404) {
                    // Fallback avec code brut
                    try {
                        const fallbackResp = await window.apiClient.get(`/scanner/scan/${encodeURIComponent(code)}/`);
                        if (fallbackResp.data) {
                            this.scanResult = fallbackResp.data;
                            this.msg = `✅ ${fallbackResp.data.name} (fallback)`;
                            return;
                        }
                    } catch (fbErr) {}
                    alert(`❌ Code non reconnu: ${code}`);
                } else if (error.response?.status === 401) {
                    alert('⚠️ Session expirée');
                    window.location.href = '/admin/login/';
                } else {
                    alert('❌ Erreur scan');
                }
            }
        },
        
        //--------------------------------------------------------------------------
        // ✅ Extraire l'UUID d'un QR Code ou code-barres
        // Supporte les formats personnalisés et les UUID bruts
        //--------------------------------------------------------------------------
        extractUuidFromQR(qrText) {
            if (!qrText || typeof qrText !== 'string') return qrText;
            
            // Format: qr_asset_<id>_<uuid>
            if (qrText.startsWith('qr_asset_')) {
                const parts = qrText.split('_');
                if (parts.length >= 4) {
                    return parts.slice(3).join('_');
                }
            }
            
            // Regex UUID
            const uuidPattern = /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i;
            const match = qrText.match(uuidPattern);
            if (match) return match[0];
            
            return qrText;
        },
        
        // ====================================================================
        // UTILITAIRES
        // ====================================================================
        addToHistory(scan) {
            if (!scan) return;
            this.scanHistory.unshift(scan);
            if (this.scanHistory.length > 10) this.scanHistory.pop();
            localStorage.setItem('cmdb_scan_history', JSON.stringify(this.scanHistory));
        },
        //--------------------------------------------------------------------------
        // ✅ Charger l'historique des scans depuis localStorage
        //--------------------------------------------------------------------------
        loadScanHistory() {
            const saved = localStorage.getItem('cmdb_scan_history');
            if (saved) {
                try {
                    const parsed = JSON.parse(saved);
                    this.scanHistory = parsed.filter(s => s && s.uuid && s.asset_name);
                } catch (e) { this.scanHistory = []; }
            }
        },
        //--------------------------------------------------------------------------
        // ✅ Fetch des locations pour le déplacement d'assets
        //--------------------------------------------------------------------------
        async fetchLocations() {
            try {
                const response = await window.apiClient.get('/inventory/location/');
                this.locations = response.data || [];
            } catch (error) {
                this.locations = [];
            }
        },
        //--------------------------------------------------------------------------
        // ✅ Déplacer un asset vers une nouvelle location
        //--------------------------------------------------------------------------
        async moveAsset() {
            if (!this.moveLocation || !this.scanResult?.id) {
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
        //--------------------------------------------------------------------------
        // ✅ Obtenir la classe CSS pour le statut d'un asset
        //--------------------------------------------------------------------------
        getStatusClass(status) {
            const map = {
                'active': 'status-active', 'maintenance': 'status-maintenance',
                'retired': 'status-retired', 'stock': 'status-stock', 'repair': 'status-repair'
            };
            return map[status] || 'status-stock';
        },
        //--------------------------------------------------------------------------
        // ✅ Formater une date pour l'affichage
        //--------------------------------------------------------------------------
        formatDate(dateStr) {
            if (!dateStr) return '-';
            return new Date(dateStr).toLocaleDateString('fr-FR', {
                day: '2-digit', month: '2-digit', year: 'numeric',
                hour: '2-digit', minute: '2-digit'
            });
        },
        //--------------------------------------------------------------------------
        // ✅ Jouer un son de beep pour confirmer le scan
        //--------------------------------------------------------------------------    
        playBeep() {
            try {
                const audio = new AudioContext();
                const osc = audio.createOscillator();
                const gain = audio.createGain();
                osc.connect(gain); gain.connect(audio.destination);
                osc.frequency.value = 800; osc.type = 'sine'; gain.gain.value = 0.1;
                osc.start(); setTimeout(() => osc.stop(), 150);
            } catch (e) {}
        }
    }
}).mount('#scanner-app');