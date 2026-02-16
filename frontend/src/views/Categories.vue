<template>
  <div class="categories-page">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="h3 mb-0">Catégories</h1>
        <p class="text-muted mb-0">Gestion des catégories d'équipements</p>
      </div>
      <button class="btn btn-primary" @click="showCreateModal">
        <i class="bi bi-plus-circle me-2"></i>
        Nouvelle catégorie
      </button>
    </div>

    <div class="card card-custom">
      <div class="card-body">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary mb-3"></div>
          <p class="text-muted">Chargement...</p>
        </div>
        <div v-else class="row g-3">
          <div v-for="category in categories" :key="category.id" class="col-md-6 col-lg-4">
            <div class="card h-100">
              <div class="card-body">
                <h6 class="card-title">{{ category.name }}</h6>
                <p class="card-text text-muted small">{{ category.assets_count }} équipements</p>
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
  name: 'Categories',
  setup() {
    const toast = useToast()
    const loading = ref(true)
    const categories = ref([
      { id: 1, name: 'PC', assets_count: 15 },
      { id: 2, name: 'Écrans', assets_count: 12 },
      { id: 3, name: 'Claviers', assets_count: 8 }
    ])

    const showCreateModal = () => {
      toast.info('Fonctionnalité en cours de développement')
    }

    onMounted(() => {
      setTimeout(() => { loading.value = false }, 500)
    })

    return { loading, categories, showCreateModal }
  }
}
</script>