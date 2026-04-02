// backend/static/admin_cmdb/js/api.js
// ============================================================================
// FICHIER DOIT ÊTRE CHARGÉ APRÈS Vue.js ET AVANT TOUS LES AUTRES JS
// ============================================================================
// Configuration de l'API client avec JWT pour les appels DRF depuis Django + Vue.js

if (typeof Vue === 'undefined') {
    console.error('❌ Vue.js doit être chargé AVANT api.js !');
}

const apiClient = axios.create({
    baseURL: '/api/v1/',
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
});

// ============================================================================
// UNIQUE DÉCLARATION DE createApp POUR TOUT LE PROJET
// ============================================================================
window.VueCreateApp = Vue.createApp;

console.log('✅ window.VueCreateApp défini:', typeof window.VueCreateApp);

// Interceptors
apiClient.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    // Ajout du header CSRF pour les requêtes POST/PUT/PATCH
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    if (csrfToken) {
        config.headers['X-CSRFToken'] = csrfToken;
    }
    // Ajout de l'URL de base pour les logs
    config.headers['X-API-Base-URL'] = document.querySelector('meta[name="api-base-url"]')?.getAttribute('content') || '/api/v1/';
    return config;
}, (error) => Promise.reject(error));

// Ajout d'une méthode pour afficher les messages dans l'interface
window.showMessage = function(message, type = 'info') {
    // Création d'un ID unique pour le message
    const messageId = Date.now() + Math.random();
    
    // Si Vue est disponible, on peut utiliser le système de messages Vue
    if (typeof window.VueCreateApp !== 'undefined' && document.getElementById('vue-messages')) {
        // Pour l'instant, on affiche simplement dans la console
        console.log(`[${type.toUpperCase()}] ${message}`);
    } else {
        // Affichage basique dans la console
        console.log(`[${type.toUpperCase()}] ${message}`);
    }
};

apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;
        
        // Gestion des erreurs 401 (token invalide ou expiré)
        if (error.response && error.response.status === 401) {
            const refreshToken = localStorage.getItem('refresh_token');
            
            if (refreshToken && !originalRequest._retry) {
                originalRequest._retry = true;
                
                try {
                    // Tenter de rafraîchir le token
                    const refreshResponse = await axios.post('/api/token/refresh/', {
                        refresh: refreshToken
                    });
                    
                    const { access } = refreshResponse.data;
                    localStorage.setItem('access_token', access);
                    
                    // Réessayer la requête originale avec le nouveau token
                    originalRequest.headers.Authorization = `Bearer ${access}`;
                    return apiClient(originalRequest);
                    
                } catch (refreshError) {
                    // Si le refresh échoue, déconnecter l'utilisateur
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                    if (window.location.pathname !== '/admin/login/') {
                        window.location.href = '/admin/login/';
                    }
                }
            } else {
                // Si pas de refresh token ou déjà tenté, déconnecter
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                if (window.location.pathname !== '/admin/login/') {
                    window.location.href = '/admin/login/';
                }
            }
        }
        
        // Gestion des erreurs 403 (accès interdit)
        if (error.response && error.response.status === 403) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            if (window.location.pathname !== '/admin/login/') {
                window.location.href = '/admin/login/';
            }
        }
        
        return Promise.reject(error);
    }
);

window.apiClient = apiClient;