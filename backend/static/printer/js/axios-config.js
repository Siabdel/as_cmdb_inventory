/**
 * axios-config.js
 * Configuration globale d'Axios pour l'application CMDB
 * - Intercepteurs pour CSRF Token Django
 * - Gestion automatique des erreurs
 * - Timeout par défaut
 * - Base URL centralisée
 */

// Configuration de base
const API_BASE_URL = '/api';

// Création de l'instance Axios
const apiClient = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000, // 30 secondes
    headers: {
        'Content-Type': 'application/json',
    }
});

// === INTERCEPTEUR DE REQUÊTE ===
// Ajoute automatiquement le CSRF Token et le Token d'authentification
apiClient.interceptors.request.use(
    function (config) {
        // Récupérer le CSRF Token Django depuis les cookies
        const csrftoken = getCookie('csrftoken');
        if (csrftoken) {
            config.headers['X-CSRFToken'] = csrftoken;
        }

        // Récupérer le Token d'authentification depuis le localStorage
        const authToken = localStorage.getItem('auth_token');
        if (authToken) {
            config.headers['Authorization'] = `Token ${authToken}`;
        }

        // Ajouter un timestamp pour éviter le cache
        config.params = config.params || {};
        config.params._t = Date.now();

        console.log(`[Axios] Requête ${config.method.toUpperCase()} ${config.url}`);
        return config;
    },
    function (error) {
        console.error('[Axios] Erreur requête:', error);
        return Promise.reject(error);
    }
);

// === INTERCEPTEUR DE RÉPONSE ===
// Gestion centralisée des erreurs HTTP
apiClient.interceptors.response.use(
    function (response) {
        console.log(`[Axios] Réponse ${response.status} ${response.config.url}`);
        return response;
    },
    function (error) {
        // Gestion des erreurs HTTP
        if (error.response) {
            const status = error.response.status;
            const data = error.response.data;

            console.error(`[Axios] Erreur ${status}:`, data);

            switch (status) {
                case 401:
                    // Token invalide ou expiré
                    localStorage.removeItem('auth_token');
                    showToast('Session expirée, veuillez vous reconnecter', 'warning');
                    // Optionnel: rediriger vers login
                    // window.location.href = '/login/';
                    break;

                case 403:
                    // Permissions insuffisantes
                    showToast('Permissions insuffisantes pour cette action', 'danger');
                    break;

                case 404:
                    // Ressource non trouvée
                    showToast('Ressource non trouvée', 'warning');
                    break;

                case 500:
                    // Erreur serveur
                    showToast('Erreur serveur, veuillez réessayer', 'danger');
                    break;

                case 503:
                    // Service indisponible (imprimante hors ligne)
                    showToast('Imprimante indisponible', 'danger');
                    break;

                default:
                    showToast(`Erreur ${status}: ${data.detail || data.message || 'Inconnue'}`, 'danger');
            }
        } else if (error.request) {
            // Requête partie mais pas de réponse
            console.error('[Axios] Pas de réponse:', error.request);
            showToast('Pas de réponse du serveur, vérifiez votre connexion', 'danger');
        } else {
            // Erreur de configuration
            console.error('[Axios] Erreur configuration:', error.message);
            showToast(`Erreur: ${error.message}`, 'danger');
        }

        return Promise.reject(error);
    }
);

// === UTILITAIRES ===

/**
 * Récupérer un cookie par son nom
 * @param {string} name - Nom du cookie
 * @returns {string|null} - Valeur du cookie ou null
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Afficher une notification toast
 * @param {string} message - Message à afficher
 * @param {string} type - Type: 'success', 'danger', 'warning', 'info'
 * @param {number} duration - Durée en ms (default 5000)
 */
function showToast(message, type = 'info', duration = 5000) {
    const toastEl = document.getElementById('liveToast');
    const toastHeader = document.getElementById('toastHeader');
    const toastIcon = document.getElementById('toastIcon');
    const toastTitle = document.getElementById('toastTitle');
    const toastMessage = document.getElementById('toastMessage');
    const toastTime = document.getElementById('toastTime');

    // Couleurs selon le type
    const typeConfig = {
        success: { class: 'bg-success text-white', icon: 'fa-check-circle', title: 'Succès' },
        danger: { class: 'bg-danger text-white', icon: 'fa-times-circle', title: 'Erreur' },
        warning: { class: 'bg-warning text-dark', icon: 'fa-exclamation-triangle', title: 'Attention' },
        info: { class: 'bg-info text-white', icon: 'fa-info-circle', title: 'Info' }
    };

    const config = typeConfig[type] || typeConfig.info;

    toastHeader.className = `toast-header ${config.class}`;
    toastIcon.className = `fas ${config.icon} me-2`;
    toastTitle.textContent = config.title;
    toastMessage.textContent = message;
    toastTime.textContent = new Date().toLocaleTimeString();

    const toast = new bootstrap.Toast(toastEl, { delay: duration });
    toast.show();
}

// Export pour utilisation dans d'autres fichiers
window.apiClient = apiClient;
window.showToast = showToast;
window.getCookie = getCookie;
window.API_BASE_URL = API_BASE_URL;

console.log('[Axios] Configuration chargée avec succès');