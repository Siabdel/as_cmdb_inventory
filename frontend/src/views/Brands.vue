<template>
  <div class="brands-page">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="h3 mb-0">Marques</h1>
        <p class="text-muted mb-0">Gestion des marques d'équipements</p>
      </div>
      <button class="btn btn-primary" @click="showCreateModal">
        <i class="bi bi-plus-circle me-2"></i>
        Nouvelle marque
      </button>
    </div>

    <div class="card card-custom">
      <div class="card-body">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary mb-3"></div>
          <p class="text-muted">Chargement...</p>
        </div>
        <div v-else class="row g-3">
          <div v-for="brand in brands" :key="brand.id" class="col-md-6 col-lg-4">
            <div class="card h-100">
              <div class="card-body">
                <h6 class="card-title">{{ brand.name }}</h6>
                <p class="card-text text-muted small">{{ brand.assets_count }} équipements</p>
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
  name: 'Brands',
  setup() {
    const toast = useToast()
    const loading = ref(true)
    const brands = ref([
      { id: 1, name: 'Dell', assets_count: 25 },
      { id: 2, name: 'HP', assets_count: 18 },
      { id: 3, name: 'Samsung', assets_count: 12 }
    ])

    const showCreateModal = () => {
      toast.info('Fonctionnalité en cours de développement')
    }

    onMounted(() => {
      setTimeout(() => { loading.value = false }, 500)
    })

    return { loading, brands, showCreateModal }
  }
}
</script>