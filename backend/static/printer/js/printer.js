/**
 * printer.js - Gestion de l'interface et appels API
 */
/**
 * printer.js
 * Gestion de l'interface et appels API avec Axios
 * CMDB Inventory - Impression d'étiquettes
 */

// === ÉTAT GLOBAL ===
const state = {
    assets: [],
    filteredAssets: [],
    loading: false,
    printerOnline: false,
    currentUser: null,
    selectedAsset: null,
    printModal: null,
    printInProgress: false
};

// === INITIALISATION ===
document.addEventListener('DOMContentLoaded', function() {
    console.log('[Printer] Initialisation...');

    // Initialiser le modal Bootstrap
    state.printModal = new bootstrap.Modal(document.getElementById('printModal'));

    // Charger les données
    loadAssets();
    checkPrinterStatus();
    loadCurrentUser();

    // Écouteurs d'événements
    document.getElementById('confirmPrintBtn').addEventListener('click', handlePrint);
    document.getElementById('searchInput').addEventListener('input', filterAssets);

    // Rafraîchissement périodique du statut imprimante (toutes les 30s)
    setInterval(checkPrinterStatus, 30000);

    console.log('[Printer] Initialisation terminée');
});

// === CHARGEMENT DES ASSETS ===

/**
 * Charger la liste des assets depuis l'API
 * GET /api/v1/assets/
 */
async function loadAssets() {
    const grid = document.getElementById('assetsGrid');
    const spinner = document.getElementById('loadingSpinner');
    const emptyState = document.getElementById('emptyState');
    const statsRow = document.getElementById('statsRow');

    state.loading = true;
    spinner.style.display = 'block';
    grid.innerHTML = '';
    emptyState.style.display = 'none';

    try {
        const response = await apiClient.get('/v1/assets/');
        state.assets = response.data || [];
        state.filteredAssets = [...state.assets];

        if (state.assets.length === 0) {
            emptyState.style.display = 'block';
            spinner.style.display = 'none';
            state.loading = false;
            return;
        }

        // Afficher les stats
        document.getElementById('totalAssets').textContent = state.assets.length;
        statsRow.style.display = 'flex';

        // Générer le HTML pour chaque asset
        renderAssetsGrid(state.filteredAssets);

        showToast(`${state.assets.length} assets chargés`, 'success', 3000);

    } catch (error) {
        console.error('[Printer] Erreur chargement assets:', error);
        showErrorAlert('Erreur de chargement des assets. Vérifiez votre connexion.');
        emptyState.style.display = 'block';
    } finally {
        spinner.style.display = 'none';
        state.loading = false;
    }
}

/**
 * Afficher la grille d'assets
 * @param {Array} assets - Liste des assets à afficher
 */
function renderAssetsGrid(assets) {
    const grid = document.getElementById('assetsGrid');

    if (assets.length === 0) {
        grid.innerHTML = `
            <div class="col-12 text-center py-5">
                <i class="fas fa-search fa-3x text-muted mb-3"></i>
                <p class="text-muted">Aucun asset ne correspond à votre recherche</p>
            </div>
        `;
        return;
    }

    grid.innerHTML = assets.map(asset => `
        <div class="col-md-4 mb-4">
            <div class="card asset-card h-100" data-asset-id="${asset.id}" onclick="openPrintModal('${asset.id}')">
                <div class="card-body d-flex flex-column">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <h5 class="card-title mb-0 text-primary">
                            <i class="fas fa-server"></i> ${escapeHtml(asset.id)}
                        </h5>
                        <span class="badge bg-${asset.status === 'active' ? 'success' : 'secondary'}">
                            ${escapeHtml(asset.status)}
                        </span>
                    </div>
                    <p class="card-text text-muted mb-1 flex-grow-1">
                        <strong>Nom:</strong> ${escapeHtml(asset.name || 'N/A')}
                    </p>
                    <p class="card-text small text-muted mb-3">
                        <i class="fas fa-map-marker-alt"></i> 
                        ${escapeHtml(asset.location || 'Non spécifié')}
                    </p>
                    <div class="mt-auto">
                        <button class="btn btn-sm btn-primary w-100" 
                                onclick="event.stopPropagation(); openPrintModal('${asset.id}')">
                            <i class="fas fa-print"></i> Imprimer étiquette
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

/**
 * Filtrer les assets par recherche
 */
function filterAssets() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase().trim();

    if (!searchTerm) {
        state.filteredAssets = [...state.assets];
    } else {
        state.filteredAssets = state.assets.filter(asset => 
            asset.id.toLowerCase().includes(searchTerm) ||
            (asset.name && asset.name.toLowerCase().includes(searchTerm)) ||
            (asset.location && asset.location.toLowerCase().includes(searchTerm))
        );
    }

    renderAssetsGrid(state.filteredAssets);

    // Mettre à jour le compteur
    document.getElementById('totalAssets').textContent = state.filteredAssets.length;
}

// === MODAL D'IMPRESSION ===

/**
 * Ouvrir le modal de confirmation d'impression
 * @param {string} assetId - ID de l'asset
 */
async function openPrintModal(assetId) {
    try {
        // Récupérer les détails de l'asset
        const response = await apiClient.get(`/v1/assets/${assetId}/`);
        state.selectedAsset = response.data;

        // Remplir le modal
        document.getElementById('modalAssetId').textContent = state.selectedAsset.id;
        document.getElementById('modalAssetName').textContent = state.selectedAsset.name || 'N/A';
        document.getElementById('modalAssetLocation').textContent = state.selectedAsset.location || 'N/A';
        document.getElementById('modalAssetStatus').textContent = state.selectedAsset.status;
        document.getElementById('modalQRContent').textContent = 
            `http://cmdb.local/assets/${state.selectedAsset.id}`;
        document.getElementById('copiesInput').value = 1;

        // Réinitialiser la barre de progression
        document.getElementById('printProgress').style.display = 'none';
        document.getElementById('printProgressBar').style.width = '0%';

        // Afficher le modal
        state.printModal.show();

    } catch (error) {
        console.error('[Printer] Erreur chargement asset:', error);
        showToast('Asset non trouvé', 'danger');
    }
}

// === IMPRESSION ===

/**
 * Gérer l'impression (appel API avec Axios)
 * POST /api/printer/labels/
 */
async function handlePrint() {
    if (!state.selectedAsset || state.printInProgress) return;

    const copies = parseInt(document.getElementById('copiesInput').value) || 1;
    const btn = document.getElementById('confirmPrintBtn');
    const progressContainer = document.getElementById('printProgress');
    const progressBar = document.getElementById('printProgressBar');
    const progressText = document.getElementById('printProgressText');

    state.printInProgress = true;
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Impression...';
    progressContainer.style.display = 'flex';

    try {
        // Construction du payload
        const payload = {
            asset_id: state.selectedAsset.id,
            qr_content: `http://cmdb.local/assets/${state.selectedAsset.id}`,
            barcode_content: `ASSET${state.selectedAsset.id.replace('-', '').toUpperCase()}`,
            custom_text: state.selectedAsset.location || '',
            copies: copies
        };

        console.log('[Printer] Envoi demande impression:', payload);

        // Appel API avec Axios
        const response = await apiClient.post('/printer/labels/', payload, {
            // Timeout spécifique pour l'impression (plus long)
            timeout: 60000,
            // Progress simulation (car pas de vrai progress pour USB)
            onDownloadProgress: (progressEvent) => {
                const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                progressBar.style.width = `${percentCompleted}%`;
                progressText.textContent = `${percentCompleted}%`;
            }
        });

        const result = response.data;

        // Simulation de progression pour impression USB
        simulateProgress(progressBar, progressText, copies);

        if (result.status === 'success') {
            showToast(`✅ ${result.message}`, 'success', 5000);
            
            // Mettre à jour les stats
            updatePrintStats(copies);
            
            // Fermer le modal après délai
            setTimeout(() => {
                state.printModal.hide();
            }, 1500);
        } else {
            showToast(`❌ Erreur: ${result.message}`, 'danger', 7000);
        }

    } catch (error) {
        console.error('[Printer] Erreur impression:', error);
        
        const errorMessage = error.response?.data?.message || 
                            error.message || 
                            'Erreur de connexion au serveur';
        showToast(`❌ Échec impression: ${errorMessage}`, 'danger', 7000);
    } finally {
        state.printInProgress = false;
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-print"></i> Imprimer';
        
        setTimeout(() => {
            progressContainer.style.display = 'none';
            progressBar.style.width = '0%';
        }, 2000);
    }
}

/**
 * Simuler la progression d'impression (pour UX)
 */
function simulateProgress(progressBar, progressText, copies) {
    let progress = 0;
    const target = 100;
    const increment = target / (copies * 10);
    
    const interval = setInterval(() => {
        progress += increment;
        if (progress >= target) {
            progress = target;
            clearInterval(interval);
        }
        progressBar.style.width = `${progress}%`;
        progressText.textContent = `${Math.round(progress)}%`;
    }, 200);
}

// === DIAGNOSTIC ===

/**
 * Vérifier l'état de l'imprimante
 * GET /api/printer/labels/status/
 */
async function checkPrinterStatus() {
    try {
        const response = await apiClient.get('/printer/labels/status/');
        const data = response.data;

        const statusEl = document.getElementById('printerStatus');
        const uptimeEl = document.getElementById('printerUptime');

        if (data.printer?.status === 'online') {
            state.printerOnline = true;
            statusEl.innerHTML = `
                <i class="fas fa-print printer-status-online"></i>
                <span class="badge bg-success">Imprimante prête</span>
            `;
            uptimeEl.textContent = 'En ligne';
            uptimeEl.className = 'text-success';
        } else {
            state.printerOnline = false;
            statusEl.innerHTML = `
                <i class="fas fa-print printer-status-offline"></i>
                <span class="badge bg-danger">Hors ligne</span>
            `;
            uptimeEl.textContent = 'Hors ligne';
            uptimeEl.className = 'text-danger';
        }

        // Mettre à jour les permissions
        if (data.permissions?.udev_ok) {
            console.log('[Printer] Permissions USB OK');
        } else {
            console.warn('[Printer] Permissions USB à vérifier');
        }

    } catch (error) {
        console.error('[Printer] Erreur status:', error);
        state.printerOnline = false;
        document.getElementById('printerStatus').innerHTML = `
            <i class="fas fa-print printer-status-offline"></i>
            <span class="badge bg-danger">Erreur</span>
        `;
    }
}

/**
 * Charger les informations de l'utilisateur connecté
 * GET /api/auth/user/
 */
async function loadCurrentUser() {
    try {
        const response = await apiClient.get('/auth/user/');
        state.currentUser = response.data;
        document.getElementById('usernameDisplay').textContent = state.currentUser.username;
    } catch (error) {
        console.error('[Printer] Erreur chargement user:', error);
        document.getElementById('usernameDisplay').textContent = 'Invité';
    }
}

/**
 * Mettre à jour les statistiques d'impression
 */
function updatePrintStats(copies) {
    const printedTodayEl = document.getElementById('printedToday');
    const current = parseInt(printedTodayEl.textContent) || 0;
    printedTodayEl.textContent = current + copies;
}

/**
 * Afficher une alerte d'erreur
 */
function showErrorAlert(message) {
    const alertEl = document.getElementById('errorAlert');
    const messageEl = document.getElementById('errorMessage');
    
    messageEl.textContent = message;
    alertEl.style.display = 'block';
    
    // Auto-hide après 10 secondes
    setTimeout(() => {
        alertEl.style.display = 'none';
    }, 10000);
}

/**
 * Échapper le HTML pour prévenir les XSS
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// === GESTIONNAIRE D'ERREURS GLOBAL ===
window.addEventListener('error', function(event) {
    console.error('[Printer] Erreur globale:', event.error);
    showToast('Une erreur est survenue, veuillez rafraîchir la page', 'danger');
});

window.addEventListener('unhandledrejection', function(event) {
    console.error('[Printer] Promise rejetée non gérée:', event.reason);
});

console.log('[Printer] Module chargé avec Axios');