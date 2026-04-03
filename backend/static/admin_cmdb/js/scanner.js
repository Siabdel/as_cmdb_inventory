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
    },
    
    beforeUnmount() {
        console.log('🔧 [SCANNER] beforeUnmount()');
        this.stopCamera();
    },
    
    methods: {
        // ====================================================================
        // USB SCANNER — Gestion via Input (SIMPLIFIÉ)
        // ====================================================================
        focusInput() {
            // ✅ Focus sur l'input caché pour capturer le scanner USB
            const input = document.getElementById('usb-scanner-input');
            if (input) {
                input.focus();
                console.log('✅ [SCANNER] Input focusé');
            }
        },
        
        onInputFocus() {
            console.log('📝 [SCANNER] Input focusé');
        },
        
        onInputBlur() {
            console.log('⚠️ [SCANNER] Input perdu le focus');
            // ✅ Re-focus automatique après 100ms
            setTimeout(() => {
                if (this.scannerType === 'usb' && this.scannerActive) {
                    this.focusInput();
                }
            }, 100);
        },
        
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
        
        resetScanner() {
            this.usbBuffer = '';
            this.focusInput();
        },
        
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
        // WEBCAM — ZXing (Inchangé)
        // ====================================================================
        initZXing() {
            this.codeReader = new ZXing.BrowserMultiFormatReader();
        },
        
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
        
        stopCamera() {
            if (this.codeReader) this.codeReader.reset();
            this.cameraActive = false;
        },
        
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
                
                const response = await window.apiClient.get(`/scanner/scan/${extractedUuid}/`);
                
                if (!response.data) throw new Error('Données vides');
                
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
        
        loadScanHistory() {
            const saved = localStorage.getItem('cmdb_scan_history');
            if (saved) {
                try {
                    const parsed = JSON.parse(saved);
                    this.scanHistory = parsed.filter(s => s && s.uuid && s.asset_name);
                } catch (e) { this.scanHistory = []; }
            }
        },
        
        async fetchLocations() {
            try {
                const response = await window.apiClient.get('/inventory/location/');
                this.locations = response.data || [];
            } catch (error) {
                this.locations = [];
            }
        },
        
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
        
        getStatusClass(status) {
            const map = {
                'active': 'status-active', 'maintenance': 'status-maintenance',
                'retired': 'status-retired', 'stock': 'status-stock', 'repair': 'status-repair'
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
                const osc = audio.createOscillator();
                const gain = audio.createGain();
                osc.connect(gain); gain.connect(audio.destination);
                osc.frequency.value = 800; osc.type = 'sine'; gain.gain.value = 0.1;
                osc.start(); setTimeout(() => osc.stop(), 150);
            } catch (e) {}
        }
    }
}).mount('#scanner-app');