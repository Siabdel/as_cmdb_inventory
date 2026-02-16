/**
 * Configuration principale du store Pinia pour CMDB Inventory
 */

import { createPinia } from 'pinia'

// Créer l'instance Pinia
const pinia = createPinia()

// Plugin pour la persistance (optionnel)
pinia.use(({ store }) => {
  // Sauvegarder certaines données dans localStorage
  const persistedStores = ['auth', 'settings']
  
  if (persistedStores.includes(store.$id)) {
    // Restaurer les données depuis localStorage
    const savedState = localStorage.getItem(`pinia-${store.$id}`)
    if (savedState) {
      try {
        const parsedState = JSON.parse(savedState)
        store.$patch(parsedState)
      } catch (error) {
        console.error(`Erreur lors de la restauration du store ${store.$id}:`, error)
      }
    }
    
    // Sauvegarder les changements dans localStorage
    store.$subscribe((mutation, state) => {
      try {
        localStorage.setItem(`pinia-${store.$id}`, JSON.stringify(state))
      } catch (error) {
        console.error(`Erreur lors de la sauvegarde du store ${store.$id}:`, error)
      }
    })
  }
})

export default pinia