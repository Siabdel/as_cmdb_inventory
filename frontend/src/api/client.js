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
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Token ${token}`
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
    console.error('❌ Request Error:', error)
    return Promise.reject(error)
  }
)

// Intercepteur de réponse
apiClient.interceptors.response.use(
  (response) => {
    // Log des réponses en mode développement
    if (import.meta.env.DEV) {
      console.log(`✅ API Response: ${response.config.method?.toUpperCase()} ${response.config.url}`, {
        status: response.status,
        data: response.data
      })
    }

    return response
  },
  (error) => {
    const toast = useToast()

    // Log des erreurs
    console.error('❌ API Error:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      data: error.response?.data
    })

    // Gestion des erreurs communes
    if (error.response) {
      const { status, data } = error.response

      switch (status) {
        case 400:
          // Erreur de validation
          if (data.detail) {
            toast.error(data.detail)
          } else if (typeof data === 'object') {
            // Afficher les erreurs de validation de champs
            Object.keys(data).forEach(field => {
              if (Array.isArray(data[field])) {
                data[field].forEach(message => {
                  toast.error(`${field}: ${message}`)
                })
              }
            })
          }
          break

        case 401:
          // Non autorisé - rediriger vers la page de connexion
          toast.error('Session expirée. Veuillez vous reconnecter.')
          localStorage.removeItem('auth_token')
          
          // Redirection vers login (si on n'y est pas déjà)
          if (window.location.pathname !== '/login') {
            window.location.href = '/login'
          }
          break

        case 403:
          // Accès interdit
          toast.error('Accès interdit. Vous n\'avez pas les permissions nécessaires.')
          break

        case 404:
          // Ressource non trouvée
          toast.error('Ressource non trouvée.')
          break

        case 422:
          // Erreur de validation (Unprocessable Entity)
          toast.error(data.detail || 'Données invalides.')
          break

        case 429:
          // Trop de requêtes
          toast.error('Trop de requêtes. Veuillez patienter.')
          break

        case 500:
          // Erreur serveur
          toast.error('Erreur serveur. Veuillez réessayer plus tard.')
          break

        case 502:
        case 503:
        case 504:
          // Erreurs de service
          toast.error('Service temporairement indisponible.')
          break

        default:
          // Autres erreurs
          toast.error(data.detail || `Erreur ${status}`)
      }
    } else if (error.request) {
      // Erreur réseau
      toast.error('Erreur de connexion. Vérifiez votre connexion internet.')
    } else {
      // Autre erreur
      toast.error('Une erreur inattendue s\'est produite.')
    }

    return Promise.reject(error)
  }
)

// Méthodes utilitaires
export const apiUtils = {
  /**
   * Construire une URL avec des paramètres de requête
   */
  buildUrl(endpoint, params = {}) {
    const url = new URL(endpoint, apiClient.defaults.baseURL)
    Object.keys(params).forEach(key => {
      if (params[key] !== null && params[key] !== undefined && params[key] !== '') {
        url.searchParams.append(key, params[key])
      }
    })
    return url.pathname + url.search
  },

  /**
   * Formater les données pour FormData (pour les uploads)
   */
  toFormData(data) {
    const formData = new FormData()
    Object.keys(data).forEach(key => {
      if (data[key] !== null && data[key] !== undefined) {
        if (data[key] instanceof File) {
          formData.append(key, data[key])
        } else if (Array.isArray(data[key])) {
          data[key].forEach(item => {
            formData.append(key, item)
          })
        } else {
          formData.append(key, data[key])
        }
      }
    })
    return formData
  },

  /**
   * Télécharger un fichier
   */
  async downloadFile(url, filename) {
    try {
      const response = await apiClient.get(url, {
        responseType: 'blob'
      })
      
      const blob = new Blob([response.data])
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(downloadUrl)
    } catch (error) {
      console.error('Erreur lors du téléchargement:', error)
      throw error
    }
  },

  /**
   * Upload de fichier avec progression
   */
  async uploadFile(url, file, onProgress) {
    const formData = new FormData()
    formData.append('file', file)

    return apiClient.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      }
    })
  }
}

export default apiClient