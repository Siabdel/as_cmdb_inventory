<template>
  <div class="tags-page">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="h3 mb-0">Étiquettes</h1>
        <p class="text-muted mb-0">Gestion des étiquettes pour la classification</p>
      </div>
      <button class="btn btn-primary" @click="showCreateModal">
        <i class="bi bi-plus-circle me-2"></i>
        Nouvelle étiquette
      </button>
    </div>

    <div class="card card-custom">
      <div class="card-body">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary mb-3"></div>
          <p class="text-muted">Chargement...</p>
        </div>
        <div v-else class="row g-3">
          <div v-for="tag in tags" :key="tag.id" class="col-md-6 col-lg-4">
            <div class="card h-100">
              <div class="card-body">
                <div class="d-flex align-items-center mb-2">
                  <span 
                    class="badge me-2" 
                    :style="{ backgroundColor: tag.color, color: getTextColor(tag.color) }"
                  >
                    {{ tag.name }}
                  </span>
                </div>
                <p class="card-text text-muted small">{{ tag.assets_count }} équipements</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useToast } from 'vue-toastification'

export default {
  name: 'Tags',
  setup() {
    const toast = useToast()
    const loading = ref(true)
    const tags = ref([
      { id: 1, name: 'Urgent', color: '#dc3545', assets_count: 5 },
      { id: 2, name: 'Nouveau', color: '#28a745', assets_count: 8 },
      { id: 3, name: 'VIP', color: '#ffc107', assets_count: 3 }
    ])

    const showCreateModal = () => {
      toast.info('Fonctionnalité en cours de développement')
    }

    const getTextColor = (backgroundColor) => {
      // Simple fonction pour déterminer si le texte doit être blanc ou noir
      const hex = backgroundColor.replace('#', '')
      const r = parseInt(hex.substr(0, 2), 16)
      const g = parseInt(hex.substr(2, 2), 16)
      const b = parseInt(hex.substr(4, 2), 16)
      const brightness = (r * 299 + g * 587 + b * 114) / 1000
      return brightness > 128 ? '#000000' : '#ffffff'
    }

    onMounted(() => {
      setTimeout(() => { loading.value = false }, 500)
    })

    return { loading, tags, showCreateModal, getTextColor }
  }
}
</script>