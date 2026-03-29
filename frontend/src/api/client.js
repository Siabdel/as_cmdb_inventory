/**
 * Client API Axios configuré pour CMDB Inventory
 */
import axios from 'axios'
import { useToast } from 'vue-toastification'

// Configuration de base
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 30000, // 30 secondes
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// Intercepteur de requête
apiClient.interceptors.request.use(
  (config) => {
    // Ajouter le token d'authentification si disponible
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // Log des requêtes en mode développement
    if (import.meta.env.DEV) {
      console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`, {
        data: config.data,
        params: config.params
      })
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Intercepteur de réponse
apiClient.interceptors.response.use(
  (response) => {
    if (import.meta.env.DEV) {
      console.log(`✅ API Response: ${response.status} ${response.config.url}`, {
        data: response.data
      })
    }
    return response
  },
  (error) => {
    // Gestion des erreurs
    if (import.meta.env.DEV) {
      console.error(`❌ API Error: ${error.response?.status} ${error.response?.statusText}`, {
        error: error.response?.data || error.message
      })
    }

    // Afficher un toast d'erreur si disponible
    if (error.response?.status === 401) {
      // Rediriger vers la page de login
      window.location.href = '/login'
    }

    return Promise.reject(error)
  }
)

// Utilitaires pour les URLs
export const apiUtils = {
  buildUrl(basePath, params = {}) {
    const url = new URL(basePath, apiClient.defaults.baseURL)
    Object.entries(params).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        url.searchParams.append(key, value)
      }
    })
    return url.pathname + url.search
  }
}

export default apiClient