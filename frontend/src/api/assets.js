/**
 * Service API pour la gestion des assets
 */

import apiClient, { apiUtils } from './client'

export const assetsApi = {
  /**
   * Récupérer la liste des assets avec filtres et pagination
   */
  async getAssets(params = {}) {
    const url = apiUtils.buildUrl('/v1/assets/', params)
    return apiClient.get(url)
  },

  /**
   * Récupérer un asset par son ID
   */
  async getAsset(id) {
    return apiClient.get(`/v1/assets/${id}/`)
  },

  /**
   * Créer un nouvel asset
   */
  async createAsset(data) {
    // Si des fichiers sont présents, utiliser FormData
    if (data.qr_code_image instanceof File || data.image instanceof File) {
      const formData = apiUtils.toFormData(data)
      return apiClient.post('/v1/assets/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
    }
    return apiClient.post('/v1/assets/', data)
  },

  /**
   * Mettre à jour un asset
   */
  async updateAsset(id, data) {
    // Si des fichiers sont présents, utiliser FormData
    if (data.qr_code_image instanceof File || data.image instanceof File) {
      const formData = apiUtils.toFormData(data)
      return apiClient.put(`/v1/assets/${id}/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
    }
    return apiClient.put(`/v1/assets/${id}/`, data)
  },

  /**
   * Mettre à jour partiellement un asset
   */
  async patchAsset(id, data) {
    return apiClient.patch(`/v1/assets/${id}/`, data)
  },

  /**
   * Supprimer un asset
   */
  async deleteAsset(id) {
    return apiClient.delete(`/v1/assets/${id}/`)
  },

  /**
   * Récupérer l'image QR code d'un asset
   */
  async getAssetQRImage(id) {
    return apiClient.get(`/v1/assets/${id}/qr_image/`, {
      responseType: 'blob'
    })
  },

  /**
   * Télécharger l'image QR code d'un asset
   */
  async downloadQRImage(id, filename) {
    const url = `/v1/assets/${id}/qr_image/`
    return apiUtils.downloadFile(url, filename || `qr_code_${id}.png`)
  },

  /**
   * Récupérer l'historique des mouvements d'un asset
   */
  async getAssetMovements(id, params = {}) {
    const url = apiUtils.buildUrl(`/v1/assets/${id}/movements/`, params)
    return apiClient.get(url)
  },

  /**
   * Déplacer un asset via scan QR
   */
  async moveFromScan(assetId, targetLocationId, note = '') {
    return apiClient.post('/v1/assets/move-from-scan/', {
      asset_id: assetId,
      target_location_id: targetLocationId,
      note
    })
  },

  /**
   * Exporter la liste des assets en CSV
   */
  async exportAssets(params = {}) {
    const url = apiUtils.buildUrl('/v1/assets/export/', params)
    return apiUtils.downloadFile(url, 'assets_export.csv')
  },

  /**
   * Recherche d'assets avec autocomplétion
   */
  async searchAssets(query, limit = 10) {
    return apiClient.get('/v1/assets/', {
      params: {
        search: query,
        page_size: limit
      }
    })
  },

  /**
   * Récupérer les statistiques des assets
   */
  async getAssetStats() {
    return apiClient.get('/v1/assets/stats/')
  },

  /**
   * Dupliquer un asset
   */
  async duplicateAsset(id) {
    return apiClient.post(`/v1/assets/${id}/duplicate/`)
  },

  /**
   * Marquer un asset comme en panne
   */
  async markAsBroken(id, note = '') {
    return apiClient.patch(`/v1/assets/${id}/`, {
      status: 'broken',
      notes: note
    })
  },

  /**
   * Marquer un asset comme en maintenance
   */
  async markAsMaintenance(id, note = '') {
    return apiClient.patch(`/v1/assets/${id}/`, {
      status: 'maintenance',
      notes: note
    })
  },

  /**
   * Marquer un asset comme en stock
   */
  async markAsStock(id) {
    return apiClient.patch(`/v1/assets/${id}/`, {
      status: 'stock'
    })
  },

  /**
   * Assigner un asset à un utilisateur
   */
  async assignAsset(id, userId, locationId = null) {
    const data = {
      assigned_to: userId,
      status: 'use'
    }
    if (locationId) {
      data.current_location = locationId
    }
    return apiClient.patch(`/v1/assets/${id}/`, data)
  },

  /**
   * Désassigner un asset
   */
  async unassignAsset(id) {
    return apiClient.patch(`/v1/assets/${id}/`, {
      assigned_to: null,
      status: 'stock'
    })
  },

  /**
   * Générer un nouveau QR code pour un asset
   */
  async regenerateQRCode(id) {
    return apiClient.post(`/v1/assets/${id}/regenerate-qr/`)
  },

  /**
   * Importer des assets depuis un fichier CSV
   */
  async importAssets(file, onProgress) {
    return apiUtils.uploadFile('/v1/assets/import/', file, onProgress)
  },

  /**
   * Récupérer le template CSV pour l'import
   */
  async getImportTemplate() {
    return apiUtils.downloadFile('/v1/assets/import-template/', 'assets_import_template.csv')
  },

  /**
   * Récupérer la liste des catégories
   */
  async getCategories() {
    return apiClient.get('/v1/assets/category/')
  },

  /**
   * Récupérer la liste des emplacements
   */
  async getLocations() {
    return apiClient.get('/v1/assets/location/')
  }
}

export default assetsApi