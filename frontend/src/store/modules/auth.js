/**
 * Store Pinia pour la gestion de l'authentification
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '@/api/jwtClient'

export const useAuthStore = defineStore('auth', () => {
  // État
  const user = ref(null)
  const token = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value)
  const userFullName = computed(() => {
    if (!user.value) return ''
    return `${user.value.first_name} ${user.value.last_name}`.trim() || user.value.username
  })

  // Actions
  const login = async (credentials) => {
    loading.value = true
    error.value = null

    try {
      // Appel API pour l'authentification
      const response = await apiClient.post('/api/token/', credentials)
      
      if (response.data.access && response.data.refresh) {
        token.value = response.data.access
        
        // Stocker les tokens dans localStorage
        localStorage.setItem('access_token', response.data.access)
        localStorage.setItem('refresh_token', response.data.refresh)
        
        // Configurer le header Authorization pour les futures requêtes
        apiClient.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
        
        // Récupérer les informations utilisateur
        await fetchUser()
        
        return { success: true }
      } else {
        throw new Error('Tokens non reçus')
      }
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Erreur de connexion'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    try {
      // Optionnel: appel API pour invalider le token côté serveur
      // await apiClient.post('/auth/logout/')
      
      // Nettoyer l'état local
      user.value = null
      token.value = null
      error.value = null
      
      // Supprimer les tokens du localStorage
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      
      // Supprimer le header Authorization
      delete apiClient.defaults.headers.common['Authorization']
      
      return { success: true }
    } catch (err) {
      console.error('Erreur lors de la déconnexion:', err)
      return { success: false, error: err.message }
    }
  }

  const fetchUser = async () => {
    if (!token.value) return

    try {
      // Récupérer les informations de l'utilisateur connecté
      const response = await apiClient.get('/api/auth/user/')
      user.value = response.data
    } catch (err) {
      console.error('Erreur lors de la récupération des données utilisateur:', err)
      // Si l'erreur est 401, le token est invalide
      if (err.response?.status === 401) {
        await logout()
      }
    }
  }

  const restoreSession = async (savedToken) => {
    if (!savedToken) return false

    try {
      token.value = savedToken
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${savedToken}`
      
      // Vérifier la validité du token en récupérant les données utilisateur
      await fetchUser()
      
      return true
    } catch (err) {
      console.error('Erreur lors de la restauration de session:', err)
      await logout()
      return false
    }
  }

  const updateUser = async (userData) => {
    loading.value = true
    error.value = null

    try {
      const response = await apiClient.patch('/auth/user/', userData)
      user.value = { ...user.value, ...response.data }
      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Erreur de mise à jour'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const changePassword = async (passwordData) => {
    loading.value = true
    error.value = null

    try {
      await apiClient.post('/auth/change-password/', passwordData)
      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Erreur de changement de mot de passe'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const clearError = () => {
    error.value = null
  }

  // Initialisation
  const initialize = async () => {
    const savedToken = localStorage.getItem('auth_token')
    if (savedToken) {
      await restoreSession(savedToken)
    }
  }

  return {
    // État
    user,
    token,
    loading,
    error,
    
    // Getters
    isAuthenticated,
    userFullName,
    
    // Actions
    login,
    logout,
    fetchUser,
    restoreSession,
    updateUser,
    changePassword,
    clearError,
    initialize
  }
})