<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="mb-0">Liste des Actifs</h2>
      <router-link to="/assets/new" class="btn btn-primary">
        <i class="bi bi-plus-lg"></i> Ajouter un actif
      </router-link>
    </div>

    <!-- Barre de recherche -->
    <div class="row mb-4">
      <div class="col-md-6">
        <div class="input-group">
          <span class="input-group-text">
            <i class="bi bi-search"></i>
          </span>
          <input
            v-model="searchTerm"
            type="text"
            class="form-control"
            placeholder="Rechercher un actif..."
          />
        </div>
      </div>
    </div>

    <!-- Tableau des actifs -->
    <div class="table-responsive">
      <table class="table table-striped table-hover">
        <thead class="table-dark">
          <tr>
            <th scope="col">Nom</th>
            <th scope="col">Code Interne</th>
            <th scope="col">Catégorie</th>
            <th scope="col">Marque</th>
            <th scope="col">Statut</th>
            <th scope="col">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="asset in filteredAssets" :key="asset.id">
            <td>{{ asset.name }}</td>
            <td>{{ asset.internal_code }}</td>
            <td>{{ asset.category }}</td>
            <td>{{ asset.brand }}</td>
            <td>
              <span
                :class="`badge ${
                  asset.status === 'disponible'
                    ? 'bg-success'
                    : asset.status === 'en_utilisation'
                    ? 'bg-warning'
                    : 'bg-secondary'
                }`"
              >
                {{ asset.status }}
              </span>
            </td>
            <td>
              <div class="btn-group" role="group">
                <router-link
                  :to="`/assets/${asset.id}`"
                  class="btn btn-sm btn-outline-primary"
                >
                  <i class="bi bi-eye"></i>
                </router-link>
                <router-link
                  :to="`/assets/edit/${asset.id}`"
                  class="btn btn-sm btn-outline-secondary"
                >
                  <i class="bi bi-pencil"></i>
                </router-link>
                <button
                  @click="deleteAsset(asset.id)"
                  class="btn btn-sm btn-outline-danger"
                >
                  <i class="bi bi-trash"></i>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <nav aria-label="Page navigation">
      <ul class="pagination justify-content-center">
        <li class="page-item" :class="{ disabled: currentPage === 1 }">
          <a class="page-link" href="#" @click.prevent="prevPage">Précédent</a>
        </li>
        <li
          v-for="page in totalPages"
          :key="page"
          class="page-item"
          :class="{ active: currentPage === page }"
        >
          <a class="page-link" href="#" @click.prevent="goToPage(page)">{{ page }}</a>
        </li>
        <li class="page-item" :class="{ disabled: currentPage === totalPages }">
          <a class="page-link" href="#" @click.prevent="nextPage">Suivant</a>
        </li>
      </ul>
    </nav>
  </div>
</template>

<script>
import { fetchAssets, deleteAsset } from '@/api/assets'

export default {
  name: 'AssetsView',
  data() {
    return {
      assets: [],
      searchTerm: '',
      currentPage: 1,
      itemsPerPage: 10
    }
  },
  computed: {
    filteredAssets() {
      const filtered = this.assets.filter(asset =>
        asset.name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        asset.internal_code.toLowerCase().includes(this.searchTerm.toLowerCase())
      )
      const start = (this.currentPage - 1) * this.itemsPerPage
      const end = start + this.itemsPerPage
      return filtered.slice(start, end)
    },
    totalPages() {
      const filtered = this.assets.filter(asset =>
        asset.name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        asset.internal_code.toLowerCase().includes(this.searchTerm.toLowerCase())
      )
      return Math.ceil(filtered.length / this.itemsPerPage)
    }
  },
  async mounted() {
    await this.loadAssets()
  },
  methods: {
    async loadAssets() {
      try {
        const response = await fetchAssets()
        this.assets = response.data
      } catch (error) {
        console.error('Erreur lors du chargement des actifs:', error)
      }
    },
    async deleteAsset(id) {
      if (confirm('Êtes-vous sûr de vouloir supprimer cet actif ?')) {
        try {
          await deleteAsset(id)
          this.assets = this.assets.filter(asset => asset.id !== id)
        } catch (error) {
          console.error('Erreur lors de la suppression de l\'actif:', error)
        }
      }
    },
    goToPage(page) {
      this.currentPage = page
    },
    prevPage() {
      if (this.currentPage > 1) {
        this.currentPage--
      }
    },
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++
      }
    }
  }
}
</script>

<style scoped>
/* Styles spécifiques pour le composant Assets.vue */
</style>