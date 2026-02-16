/**
 * Point d'entrée principal de l'application Vue.js CMDB Inventory
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

// Import Bootstrap CSS et JS
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

// Import des styles personnalisés
import './assets/css/main.css'

// Import des plugins de notification
import Toast from 'vue-toastification'
import 'vue-toastification/dist/index.css'

// Configuration des notifications
const toastOptions = {
  position: 'top-right',
  timeout: 5000,
  closeOnClick: true,
  pauseOnFocusLoss: true,
  pauseOnHover: true,
  draggable: true,
  draggablePercent: 0.6,
  showCloseButtonOnHover: false,
  hideProgressBar: false,
  closeButton: 'button',
  icon: true,
  rtl: false
}

// Création de l'application Vue
const app = createApp(App)

// Configuration des plugins
app.use(createPinia())
app.use(router)
app.use(Toast, toastOptions)

// Variables globales
app.config.globalProperties.$appName = import.meta.env.VITE_APP_NAME || 'CMDB Inventory'
app.config.globalProperties.$appVersion = import.meta.env.VITE_APP_VERSION || '1.0.0'
app.config.globalProperties.$apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
app.config.globalProperties.$mediaBaseUrl = import.meta.env.VITE_MEDIA_BASE_URL || 'http://localhost:8000/media'

// Gestion des erreurs globales
app.config.errorHandler = (err, vm, info) => {
  console.error('Erreur Vue.js:', err, info)
  
  // En production, envoyer l'erreur à un service de monitoring
  if (import.meta.env.PROD) {
    // Exemple: Sentry.captureException(err)
  }
}

// Montage de l'application
app.mount('#app')

// Configuration PWA (si nécessaire)
if ('serviceWorker' in navigator && import.meta.env.PROD) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then((registration) => {
        console.log('SW registered: ', registration)
      })
      .catch((registrationError) => {
        console.log('SW registration failed: ', registrationError)
      })
  })
}