/**
 * Service API pour la gestion des scans d'assets et la rétractabilité
 */

import apiClient from './client'

export const assetScanApi = {
  /**
   * Récupérer la liste des assets avec QR code et code-barres
   */
  async getAssets(params = {}) {
    return apiClient.get('/api/assets/', { params })
  },

  /**
   * Récupérer un asset par son ID
   */
  async getAsset(id) {
    return apiClient.get(`/api/assets/${id}/`)
  },

  /**
   * Récupérer un asset par son code
   */
  async getAssetByCode(code) {
    return apiClient.get(`/api/assets/by-code/${code}/`)
  },

  /**
   * Créer un nouvel asset
   */
  async createAsset(data) {
    return apiClient.post('/api/assets/', data)
  },

  /**
   * Enregistrer un scan
   */
  async recordScan(scanData) {
    return apiClient.post('/api/scans/', scanData)
  },

  /**
   * Récupérer l'historique des scans d'un asset
   */
  async getAssetHistory(assetId) {
    return apiClient.get(`/api/assets/${assetId}/history/`)
  },

  /**
   * Générer une étiquette d'impression
   */
  async printLabel(assetId) {
    return apiClient.post(`/api/assets/${assetId}/print-label/`)
  },

  /**
   * Récupérer l'URL du QR code
   */
  getQRCodeUrl(assetId) {
    return `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/assets/${assetId}/qrcode/`
  },

  /**
   * Récupérer l'URL du code-barres
   */
  getBarcodeUrl(assetId) {
    return `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/assets/${assetId}/barcode/`
  },

  /**
   * Récupérer les scans récents
   */
  async getRecentScans(limit = 10) {
    return apiClient.get('/api/asset-scans/', {
      params: {
        ordering: '-scanned_at',
        limit
      }
    })
  }
}