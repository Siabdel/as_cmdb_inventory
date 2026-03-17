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
                  <select class="form-select" v-model="form.category_id">
                    <option value="">Sélectionner une catégorie</option>
                    <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                      {{ cat.name }}
                    </option>
                  </select>
                </div>

                <div class="col-md-6">
                  <label class="form-label">Marque</label>
                  <select class="form-select" v-model="form.brand_id">
                    <option value="">Sélectionner une marque</option>
                    <option v-for="brand in brands" :key="brand.id" :value="brand.id">
                      {{ brand.name }}
                    </option>
                  </select>
                </div>

                <div class="col-md-6">
                  <label class="form-label">Modèle *</label>
                  <input
                    type="text"
                    class="form-control"
                    v-model="form.model"
                    :class="{ 'is-invalid': errors.model }"
                    placeholder="OptiPlex 7090"
                    required
                  >
                  <div v-if="errors.model" class="invalid-feedback">
                    {{ errors.model }}
                  </div>
                </div>

                <div class="col-md-6">
                  <label class="form-label">Numéro de série *</label>
                  <input
                    type="text"
                    class="form-control"
                    v-model="form.serial_number"
                    :class="{ 'is-invalid': errors.serial_number }"
                    placeholder="ABC123456789"
                    required
                  >
                  <div v-if="errors.serial_number" class="invalid-feedback">
                    {{ errors.serial_number }}
                  </div>
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
                  <option value="active">En utilisation</option>
                  <option value="inactive">En stock</option>
                  <option value="maintenance">En maintenance</option>
                  <option value="repair">En réparation</option>
                  <option value="broken">En panne</option>
                  <option value="archived">Archivé</option>
                </select>
              </div>

              <div class="mb-3">
                <label class="form-label">État physique</label>
                <select class="form-select" v-model="form.condition_state">
                  <option value="new">Neuf</option>
                  <option value="used">Occasion</option>
                  <option value="damaged">Endommagé</option>
                </select>
              </div>

              <div class="mb-3">
                <label class="form-label">Emplacement</label>
                <select class="form-select" v-model="form.current_location_id">
                  <option value="">Sélectionner un emplacement</option>
                  <option v-for="loc in locations" :key="loc.id" :value="loc.id">
                    {{ loc.name }}
                  </option>
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
import { assetsApi } from '@/api/assets'
import apiClient from '@/api/client'

export default {
  name: 'AssetForm',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const toast = useToast()

    const loading = ref(false)
    const isEdit = computed(() => !!route.params.id)

    const categories = ref([])
    const brands = ref([])
    const locations = ref([])

    const form = reactive({
      internal_code: '',
      name: '',
      category_id: null,
      brand_id: null,
      model: '',
      serial_number: '',
      description: '',
      status: 'active',
      condition_state: 'new',
      current_location_id: null,
      purchase_date: '',
      purchase_price: '',
      warranty_end: '',
      notes: ''
    })

    const errors = reactive({
      internal_code: '',
      name: '',
      model: '',
      serial_number: ''
    })

    const loadReferenceData = async () => {
      try {
        const [catRes, brandRes, locRes] = await Promise.all([
          apiClient.get('/v1/inventory/category/'),
          apiClient.get('/v1/inventory/brand/'),
          apiClient.get('/v1/inventory/location/')
        ])
        categories.value = catRes.data.results || []
        brands.value = brandRes.data.results || []
        locations.value = locRes.data.results || []
      } catch (error) {
        console.error('Erreur lors du chargement des données de référence:', error)
        toast.error('Impossible de charger les listes')
      }
    }

    const loadAsset = async () => {
      if (!isEdit.value) return

      loading.value = true
      try {
        const response = await assetsApi.getAsset(route.params.id)
        const asset = response.data

        // Mapper les champs de l'API vers le formulaire
        form.internal_code = asset.internal_code || ''
        form.name = asset.name || ''
        form.category_id = asset.category?.id || null
        form.brand_id = asset.brand?.id || null
        form.model = asset.model || ''
        form.serial_number = asset.serial_number || ''
        form.description = asset.description || ''
        form.status = asset.status || 'active'
        form.condition_state = asset.condition_state || 'new'
        form.current_location_id = asset.current_location?.id || null
        form.purchase_date = asset.purchase_date || ''
        form.purchase_price = asset.purchase_price || ''
        form.warranty_end = asset.warranty_end || ''
        form.notes = asset.notes || ''
      } catch (error) {
        console.error('Erreur:', error)
        toast.error('Erreur lors du chargement de l\'équipement')
      } finally {
        loading.value = false
      }
    }

    const validateForm = () => {
      // Reset errors
      errors.internal_code = ''
      errors.name = ''
      errors.model = ''
      errors.serial_number = ''
      
      let isValid = true

      if (!form.name.trim()) {
        errors.name = 'Le nom est requis'
        isValid = false
      }

      if (!form.model.trim()) {
        errors.model = 'Le modèle est requis'
        isValid = false
      }

      if (!form.serial_number.trim()) {
        errors.serial_number = 'Le numéro de série est requis'
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
        // Préparer les données pour l'API
        const payload = {
          name: form.name,
          category_id: form.category_id,
          brand_id: form.brand_id,
          model: form.model,
          serial_number: form.serial_number,
          description: form.description,
          status: form.status,
          condition_state: form.condition_state,
          current_location_id: form.current_location_id,
          purchase_date: form.purchase_date || null,
          purchase_price: form.purchase_price ? parseFloat(form.purchase_price) : 0.00,
          warranty_end: form.warranty_end || null,
        }

        // Supprimer les champs vides ou null (sauf purchase_price qui a une valeur par défaut)
        Object.keys(payload).forEach(key => {
          if (payload[key] === '' || payload[key] === null) {
            delete payload[key]
          }
        })

        if (isEdit.value) {
          await assetsApi.updateAsset(route.params.id, payload)
          toast.success('Équipement mis à jour avec succès')
        } else {
          await assetsApi.createAsset(payload)
          toast.success('Équipement créé avec succès')
        }
        
        router.push('/assets')
      } catch (error) {
        console.error('Erreur:', error)
        if (error.response?.data) {
          // Afficher les erreurs de validation
          const data = error.response.data
          if (data.name) errors.name = data.name
          if (data.internal_code) errors.internal_code = data.internal_code
          toast.error('Erreur de validation')
        } else {
          toast.error('Erreur lors de la sauvegarde')
        }
      } finally {
        loading.value = false
      }
    }

    onMounted(async () => {
      await loadReferenceData()
      await loadAsset()
    })

    return {
      loading,
      isEdit,
      form,
      errors,
      categories,
      brands,
      locations,
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