<template>
  <div class="asset-form-page">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="h3 mb-0">{{ isEdit ? 'Modifier' : 'Nouvel' }} équipement</h1>
        <p class="text-muted mb-0">{{ isEdit ? 'Modification des informations' : 'Ajout d\'un nouvel équipement' }}</p>
      </div>
      <router-link to="/assets" class="btn btn-outline-secondary">
        <i class="bi bi-arrow-left me-2"></i>
        Retour
      </router-link>
    </div>

    <div class="card card-custom">
      <div class="card-body">
        <form @submit.prevent="handleSubmit">
          <div class="row g-4">
            <!-- Informations de base -->
            <div class="col-lg-8">
              <h5 class="mb-3">Informations générales</h5>
              
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label">Code interne</label>
                  <input
                    type="text"
                    class="form-control"
                    v-model="form.internal_code"
                    :class="{ 'is-invalid': errors.internal_code }"
                    placeholder="PC-001"
                  >
                  <div v-if="errors.internal_code" class="invalid-feedback">
                    {{ errors.internal_code }}
                  </div>
                </div>

                <div class="col-md-6">
                  <label class="form-label">Nom *</label>
                  <input
                    type="text"
                    class="form-control"
                    v-model="form.name"
                    :class="{ 'is-invalid': errors.name }"
                    placeholder="Dell OptiPlex 7090"
                    required
                  >
                  <div v-if="errors.name" class="invalid-feedback">
                    {{ errors.name }}
                  </div>
                </div>

                <div class="col-md-6">
                  <label class="form-label">Catégorie</label>
                  <select class="form-select" v-model="form.category">
                    <option value="">Sélectionner une catégorie</option>
                    <option value="1">PC</option>
                    <option value="2">Écran</option>
                    <option value="3">Clavier</option>
                  </select>
                </div>

                <div class="col-md-6">
                  <label class="form-label">Marque</label>
                  <select class="form-select" v-model="form.brand">
                    <option value="">Sélectionner une marque</option>
                    <option value="1">Dell</option>
                    <option value="2">HP</option>
                    <option value="3">Samsung</option>
                  </select>
                </div>

                <div class="col-md-6">
                  <label class="form-label">Modèle</label>
                  <input
                    type="text"
                    class="form-control"
                    v-model="form.model"
                    placeholder="OptiPlex 7090"
                  >
                </div>

                <div class="col-md-6">
                  <label class="form-label">Numéro de série</label>
                  <input
                    type="text"
                    class="form-control"
                    v-model="form.serial_number"
                    placeholder="ABC123456789"
                  >
                </div>

                <div class="col-12">
                  <label class="form-label">Description</label>
                  <textarea
                    class="form-control"
                    v-model="form.description"
                    rows="3"
                    placeholder="Description détaillée de l'équipement..."
                  ></textarea>
                </div>
              </div>
            </div>

            <!-- Informations complémentaires -->
            <div class="col-lg-4">
              <h5 class="mb-3">Statut et localisation</h5>
              
              <div class="mb-3">
                <label class="form-label">Statut</label>
                <select class="form-select" v-model="form.status">
                  <option value="stock">En stock</option>
                  <option value="use">En utilisation</option>
                  <option value="broken">En panne</option>
                  <option value="maintenance">En maintenance</option>
                </select>
              </div>

              <div class="mb-3">
                <label class="form-label">Emplacement</label>
                <select class="form-select" v-model="form.current_location">
                  <option value="">Sélectionner un emplacement</option>
                  <option value="1">Bureau 101</option>
                  <option value="2">Bureau 102</option>
                  <option value="3">Stock principal</option>
                </select>
              </div>

              <div class="mb-3">
                <label class="form-label">Date d'achat</label>
                <input
                  type="date"
                  class="form-control"
                  v-model="form.purchase_date"
                >
              </div>

              <div class="mb-3">
                <label class="form-label">Prix d'achat (€)</label>
                <input
                  type="number"
                  class="form-control"
                  v-model="form.purchase_price"
                  step="0.01"
                  min="0"
                  placeholder="0.00"
                >
              </div>

              <div class="mb-3">
                <label class="form-label">Fin de garantie</label>
                <input
                  type="date"
                  class="form-control"
                  v-model="form.warranty_end"
                >
              </div>
            </div>

            <!-- Notes -->
            <div class="col-12">
              <h5 class="mb-3">Notes</h5>
              <textarea
                class="form-control"
                v-model="form.notes"
                rows="3"
                placeholder="Notes additionnelles..."
              ></textarea>
            </div>
          </div>

          <!-- Actions -->
          <div class="d-flex justify-content-end gap-2 mt-4 pt-4 border-top">
            <router-link to="/assets" class="btn btn-secondary">
              Annuler
            </router-link>
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="loading"
            >
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              <i class="bi bi-check me-2" v-else></i>
              {{ isEdit ? 'Mettre à jour' : 'Créer' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'

export default {
  name: 'AssetForm',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const toast = useToast()

    const loading = ref(false)
    const isEdit = computed(() => !!route.params.id)

    const form = reactive({
      internal_code: '',
      name: '',
      category: '',
      brand: '',
      model: '',
      serial_number: '',
      description: '',
      status: 'stock',
      current_location: '',
      purchase_date: '',
      purchase_price: '',
      warranty_end: '',
      notes: ''
    })

    const errors = reactive({
      internal_code: '',
      name: ''
    })

    const loadAsset = async () => {
      if (!isEdit.value) return

      loading.value = true
      try {
        // Simuler l'appel API
        await new Promise(resolve => setTimeout(resolve, 500))
        
        // Données simulées pour l'édition
        Object.assign(form, {
          internal_code: 'PC-001',
          name: 'Dell OptiPlex 7090',
          category: '1',
          brand: '1',
          model: 'OptiPlex 7090',
          status: 'use',
          current_location: '1'
        })
      } catch (error) {
        console.error('Erreur:', error)
        toast.error('Erreur lors du chargement')
      } finally {
        loading.value = false
      }
    }

    const validateForm = () => {
      // Reset errors
      errors.internal_code = ''
      errors.name = ''
      
      let isValid = true

      if (!form.name.trim()) {
        errors.name = 'Le nom est requis'
        isValid = false
      }

      return isValid
    }

    const handleSubmit = async () => {
      if (!validateForm()) {
        return
      }

      loading.value = true

      try {
        // Simuler l'appel API
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        toast.success(isEdit.value ? 'Équipement mis à jour' : 'Équipement créé')
        router.push('/assets')
      } catch (error) {
        console.error('Erreur:', error)
        toast.error('Erreur lors de la sauvegarde')
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      loadAsset()
    })

    return {
      loading,
      isEdit,
      form,
      errors,
      handleSubmit
    }
  }
}
</script>

<style scoped>
.asset-form-page {
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.form-control:focus,
.form-select:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
}
</style>