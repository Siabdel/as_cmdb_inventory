<template>
  <div class="home">
    <!-- Hero Section with Background Image -->
    <div class="hero-section position-relative overflow-hidden">
      <div class="background-overlay"></div>
      <div class="container position-relative z-2 py-5">
        <div class="row align-items-center min-vh-60">
          <div class="col-lg-8 mx-auto text-center text-white">
            <h1 class="display-3 fw-bold mb-4 animate__animated animate__fadeInDown">
              Gestion d'Inventaire <span class="text-warning">Intelligente</span>
            </h1>
            <p class="lead mb-5 fs-4 animate__animated animate__fadeInUp">
              Gérez vos actifs informatiques, scannez les codes QR et optimisez votre inventaire avec une plateforme moderne et intuitive.
            </p>
            
            <!-- Main Search Engine -->
            <div class="search-engine-container animate__animated animate__fadeInUp animate__delay-1s">
              <div class="card shadow-lg border-0 rounded-4 overflow-hidden">
                <div class="card-body p-4">
                  <h3 class="h4 mb-3 text-dark">
                    <i class="bi bi-search me-2"></i>Rechercher un actif
                  </h3>
                  <div class="input-group input-group-lg">
                    <span class="input-group-text bg-primary text-white border-0">
                      <i class="bi bi-pc-display"></i>
                    </span>
                    <input 
                      type="text" 
                      class="form-control border-0 py-3" 
                      placeholder="Entrez le nom, modèle, numéro de série ou tag..."
                      v-model="searchQuery"
                      @keyup.enter="performSearch"
                    >
                    <button 
                      class="btn btn-primary px-4" 
                      type="button"
                      @click="performSearch"
                    >
                      <i class="bi bi-search me-2"></i>Rechercher
                    </button>
                  </div>
                  <div class="mt-3 text-start">
                    <small class="text-muted">
                      <i class="bi bi-lightbulb me-1"></i>
                      Essayez : "Serveur HP", "Laptop Dell", "Switch Cisco"
                    </small>
                  </div>
                </div>
              </div>
            </div>

            <!-- Quick Actions -->
            <div class="row mt-5 g-3 justify-content-center animate__animated animate__fadeInUp animate__delay-2s">
              <div class="col-auto">
                <router-link to="/assets" class="btn btn-light btn-lg px-4 py-3 rounded-pill shadow-sm">
                  <i class="bi bi-box-seam me-2"></i>Explorer les actifs
                </router-link>
              </div>
              <div class="col-auto">
                <router-link to="/scan" class="btn btn-outline-light btn-lg px-4 py-3 rounded-pill border-2">
                  <i class="bi bi-qr-code-scan me-2"></i>Scanner un QR Code
                </router-link>
              </div>
              <div class="col-auto">
                <router-link to="/assets/new" class="btn btn-warning btn-lg px-4 py-3 rounded-pill shadow-sm">
                  <i class="bi bi-plus-circle me-2"></i>Ajouter un actif
                </router-link>
              </div>
              <div class="col-auto">
                <router-link to="/dashboard" class="btn btn-info btn-lg px-4 py-3 rounded-pill shadow-sm">
                  <i class="bi bi-speedometer2 me-2"></i>Tableau de bord
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Features Grid -->
    <div class="container py-5">
      <div class="row mb-5">
        <div class="col-12 text-center">
          <h2 class="display-5 fw-bold mb-3">Fonctionnalités principales</h2>
          <p class="lead text-muted mb-5">Découvrez comment notre plateforme simplifie la gestion de votre inventaire</p>
        </div>
      </div>
      <div class="row g-4">
        <div class="col-md-4">
          <div class="card feature-card h-100 border-0 shadow-lg rounded-4 overflow-hidden">
            <div class="card-header bg-primary text-white py-4">
              <div class="feature-icon text-center">
                <i class="bi bi-pc-display" style="font-size: 3.5rem;"></i>
              </div>
            </div>
            <div class="card-body p-4">
              <h3 class="card-title h4 mb-3">Gestion des actifs</h3>
              <p class="card-text text-muted">
                Enregistrez, suivez et gérez tous vos équipements informatiques (ordinateurs, serveurs, périphériques) avec des détails complets.
              </p>
              <ul class="list-unstyled mb-4">
                <li class="mb-2"><i class="bi bi-check-circle-fill text-success me-2"></i>Fiche détaillée par actif</li>
                <li class="mb-2"><i class="bi bi-check-circle-fill text-success me-2"></i>Historique des modifications</li>
                <li class="mb-2"><i class="bi bi-check-circle-fill text-success me-2"></i>Attribution aux utilisateurs</li>
              </ul>
              <router-link to="/assets" class="btn btn-outline-primary w-100">Explorer</router-link>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card feature-card h-100 border-0 shadow-lg rounded-4 overflow-hidden">
            <div class="card-header bg-success text-white py-4">
              <div class="feature-icon text-center">
                <i class="bi bi-qr-code" style="font-size: 3.5rem;"></i>
              </div>
            </div>
            <div class="card-body p-4">
              <h3 class="card-title h4 mb-3">Scan QR Code</h3>
              <p class="card-text text-muted">
                Scannez les codes QR attachés aux équipements pour accéder instantanément à leurs informations et historique.
              </p>
              <ul class="list-unstyled mb-4">
                <li class="mb-2"><i class="bi bi-check-circle-fill text-success me-2"></i>Scan rapide via caméra</li>
                <li class="mb-2"><i class="bi bi-check-circle-fill text-success me-2"></i>Génération de QR codes</li>
                <li class="mb-2"><i class="bi bi-check-circle-fill text-success me-2"></i>Accès hors ligne possible</li>
              </ul>
              <router-link to="/scan" class="btn btn-outline-success w-100">Scanner</router-link>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card feature-card h-100 border-0 shadow-lg rounded-4 overflow-hidden">
            <div class="card-header bg-warning text-white py-4">
              <div class="feature-icon text-center">
                <i class="bi bi-clipboard-data" style="font-size: 3.5rem;"></i>
              </div>
            </div>
            <div class="card-body p-4">
              <h3 class="card-title h4 mb-3">Tableau de bord</h3>
              <p class="card-text text-muted">
                Visualisez les statistiques et les indicateurs clés de votre inventaire en temps réel avec des graphiques interactifs.
              </p>
              <ul class="list-unstyled mb-4">
                <li class="mb-2"><i class="bi bi-check-circle-fill text-success me-2"></i>Rapports personnalisables</li>
                <li class="mb-2"><i class="bi bi-check-circle-fill text-success me-2"></i>Alertes de maintenance</li>
                <li class="mb-2"><i class="bi bi-check-circle-fill text-success me-2"></i>Export des données</li>
              </ul>
              <router-link to="/dashboard" class="btn btn-outline-warning w-100">Tableau de bord</router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Stats -->
    <div class="container py-5">
      <div class="row mb-5">
        <div class="col-12 text-center">
          <h2 class="display-5 fw-bold mb-3">Aperçu en temps réel</h2>
          <p class="lead text-muted">Statistiques globales de votre inventaire</p>
        </div>
      </div>
      <div class="row g-4">
        <div class="col-md-3 col-sm-6">
          <div class="stat-card text-center p-4 border-0 rounded-4 shadow-sm bg-gradient-primary">
            <div class="stat-icon mb-3">
              <i class="bi bi-pc-display-horizontal text-white" style="font-size: 2.5rem;"></i>
            </div>
            <h3 class="stat-number display-4 fw-bold text-white">150</h3>
            <p class="stat-label text-white-80">Actifs totaux</p>
            <div class="progress mt-3" style="height: 6px;">
              <div class="progress-bar bg-white" style="width: 85%"></div>
            </div>
          </div>
        </div>
        <div class="col-md-3 col-sm-6">
          <div class="stat-card text-center p-4 border-0 rounded-4 shadow-sm bg-gradient-success">
            <div class="stat-icon mb-3">
              <i class="bi bi-tools text-white" style="font-size: 2.5rem;"></i>
            </div>
            <h3 class="stat-number display-4 fw-bold text-white">42</h3>
            <p class="stat-label text-white-80">En maintenance</p>
            <div class="progress mt-3" style="height: 6px;">
              <div class="progress-bar bg-white" style="width: 28%"></div>
            </div>
          </div>
        </div>
        <div class="col-md-3 col-sm-6">
          <div class="stat-card text-center p-4 border-0 rounded-4 shadow-sm bg-gradient-info">
            <div class="stat-icon mb-3">
              <i class="bi bi-tags text-white" style="font-size: 2.5rem;"></i>
            </div>
            <h3 class="stat-number display-4 fw-bold text-white">8</h3>
            <p class="stat-label text-white-80">Catégories</p>
            <div class="progress mt-3" style="height: 6px;">
              <div class="progress-bar bg-white" style="width: 40%"></div>
            </div>
          </div>
        </div>
        <div class="col-md-3 col-sm-6">
          <div class="stat-card text-center p-4 border-0 rounded-4 shadow-sm bg-gradient-warning">
            <div class="stat-icon mb-3">
              <i class="bi bi-geo-alt text-white" style="font-size: 2.5rem;"></i>
            </div>
            <h3 class="stat-number display-4 fw-bold text-white">24</h3>
            <p class="stat-label text-white-80">Localisations</p>
            <div class="progress mt-3" style="height: 6px;">
              <div class="progress-bar bg-white" style="width: 60%"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Call to Action -->
    <div class="container py-5">
      <div class="row">
        <div class="col-12">
          <div class="cta-section p-5 rounded-4 shadow-lg border-0 text-center bg-gradient-dark text-white">
            <h2 class="display-5 fw-bold mb-4">Prêt à optimiser votre inventaire ?</h2>
            <p class="lead mb-5 fs-4">
              Commencez dès maintenant en ajoutant vos premiers actifs ou en explorant les fonctionnalités avancées.
            </p>
            <div class="d-flex flex-wrap justify-content-center gap-3">
              <router-link to="/assets/new" class="btn btn-light btn-lg px-5 py-3 rounded-pill shadow">
                <i class="bi bi-plus-circle me-2"></i>Ajouter un actif
              </router-link>
              <router-link to="/dashboard" class="btn btn-outline-light btn-lg px-5 py-3 rounded-pill border-2">
                <i class="bi bi-bar-chart me-2"></i>Voir les statistiques
              </router-link>
              <a href="#" class="btn btn-primary btn-lg px-5 py-3 rounded-pill shadow" @click.prevent="showDemo">
                <i class="bi bi-play-circle me-2"></i>Voir la démo
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Home',
  data() {
    return {
      searchQuery: ''
    };
  },
  methods: {
    performSearch() {
      if (this.searchQuery.trim()) {
        this.$router.push({ path: '/assets', query: { search: this.searchQuery } });
      }
    },
    showDemo() {
      alert('Fonctionnalité de démonstration à venir !');
    }
  }
};
</script>

<style scoped>
.home {
  background-color: #f8f9fa;
}

/* Hero Section with Background Image */
.hero-section {
  background-image: url('https://images.unsplash.com/photo-1558494949-ef010cbdcc31?ixlib=rb-4.0.3&auto=format&fit=crop&w=2074&q=80');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  position: relative;
  min-height: 85vh;
  display: flex;
  align-items: center;
}

.background-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(13, 110, 253, 0.85) 0%, rgba(25, 25, 112, 0.85) 100%);
  z-index: 1;
}

.hero-section .container {
  z-index: 2;
}

.min-vh-60 {
  min-height: 60vh;
}

/* Search Engine */
.search-engine-container {
  max-width: 800px;
  margin: 0 auto;
}

.search-engine-container .card {
  backdrop-filter: blur(10px);
  background-color: rgba(255, 255, 255, 0.95);
}

.search-engine-container input:focus {
  box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
  border-color: #86b7fe;
}

/* Feature Cards */
.feature-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border-top: 5px solid transparent !important;
}

.feature-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15) !important;
}

.feature-card.bg-primary .card-header {
  border-top: 5px solid #0d6efd !important;
}

.feature-card.bg-success .card-header {
  border-top: 5px solid #198754 !important;
}

.feature-card.bg-warning .card-header {
  border-top: 5px solid #ffc107 !important;
}

/* Stat Cards */
.stat-card {
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.1);
  z-index: 1;
}

.stat-card > * {
  position: relative;
  z-index: 2;
}

.stat-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2) !important;
}

.bg-gradient-primary {
  background: linear-gradient(135deg, #0d6efd 0%, #0b5ed7 100%);
}

.bg-gradient-success {
  background: linear-gradient(135deg, #198754 0%, #157347 100%);
}

.bg-gradient-info {
  background: linear-gradient(135deg, #0dcaf0 0%, #0ba8d0 100%);
}

.bg-gradient-warning {
  background: linear-gradient(135deg, #ffc107 0%, #e0a800 100%);
}

.bg-gradient-dark {
  background: linear-gradient(135deg, #212529 0%, #343a40 100%);
}

.text-white-80 {
  color: rgba(255, 255, 255, 0.8);
}

/* CTA Section */
.cta-section {
  background: linear-gradient(135deg, #2c3e50 0%, #4a6491 100%);
}

/* Animations */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate__animated {
  animation-duration: 1s;
  animation-fill-mode: both;
}

.animate__fadeInDown {
  animation-name: fadeInDown;
}

.animate__fadeInUp {
  animation-name: fadeInUp;
}

.animate__delay-1s {
  animation-delay: 1s;
}

.animate__delay-2s {
  animation-delay: 2s;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .hero-section {
    min-height: 70vh;
    padding-top: 3rem;
    padding-bottom: 3rem;
  }
  
  .display-3 {
    font-size: 2.5rem;
  }
  
  .search-engine-container .input-group {
    flex-direction: column;
  }
  
  .search-engine-container .input-group > * {
    width: 100%;
    border-radius: 0.375rem !important;
    margin-bottom: 0.5rem;
  }
  
  .search-engine-container button {
    margin-top: 0.5rem;
  }
}
</style>