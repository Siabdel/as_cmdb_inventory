// static/admin_cmdb/js/api.js

// Création de l'instance Axios
const apiClient = axios.create({
    baseURL: '/api/v1/',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Interceptor Request : Ajout du Token
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('cmdb_token');
        if (token) {
            config.headers.Authorization = `Token ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Interceptor Response : Gestion 401/403
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && (error.response.status === 401 || error.response.status === 403)) {
            // Nettoyage du token invalide
            localStorage.removeItem('cmdb_token');
            // Redirection sauf si on est déjà sur la page de login
            if (window.location.pathname !== '/admin/login/') {
                window.location.href = '/admin/login/';
            }
        }
        return Promise.reject(error);
    }
);

// Export pour utilisation dans les autres modules
window.apiClient = apiClient;