<template>
  <div class="not-found-page">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-8 col-lg-6">
          <div class="text-center">
            <!-- 404 Icon -->
            <div class="error-icon mb-4">
              <i class="bi bi-exclamation-triangle-fill text-warning"></i>
            </div>

            <!-- Error Message -->
            <h1 class="display-1 fw-bold text-primary mb-3">404</h1>
            <h2 class="h4 mb-3">Page non trouvée</h2>
            <p class="text-muted mb-4">
              Désolé, la page que vous recherchez n'existe pas ou a été déplacée.
            </p>

            <!-- Actions -->
            <div class="d-grid gap-2 d-md-block">
              <button 
                class="btn btn-primary btn-lg me-md-2"
                @click="goHome"
              >
                <i class="bi bi-house me-2"></i>
                Retour à l'accueil
              </button>
              
              <button 
                class="btn btn-outline-secondary btn-lg"
                @click="goBack"
              >
                <i class="bi bi-arrow-left me-2"></i>
                Page précédente
              </button>
            </div>

            <!-- Quick Links -->
            <div class="quick-links mt-5">
              <h6 class="text-muted mb-3">Liens utiles :</h6>
              <div class="row g-3">
                <div class="col-md-4">
                  <router-link to="/" class="btn btn-outline-primary w-100">
                    <i class="bi bi-speedometer2 me-2"></i>
                    Dashboard
                  </router-link>
                </div>
                <div class="col-md-4">
                  <router-link to="/assets" class="btn btn-outline-primary w-100">
                    <i class="bi bi-laptop me-2"></i>
                    Équipements
                  </router-link>
                </div>
                <div class="col-md-4">
                  <router-link to="/scan" class="btn btn-outline-primary w-100">
                    <i class="bi bi-qr-code-scan me-2"></i>
                    Scanner QR
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'

export default {
  name: 'NotFound',
  setup() {
    const router = useRouter()

    const goHome = () => {
      router.push('/')
    }

    const goBack = () => {
      if (window.history.length > 1) {
        router.go(-1)
      } else {
        router.push('/')
      }
    }

    return {
      goHome,
      goBack
    }
  }
}
</script>

<style scoped>
.not-found-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  display: flex;
  align-items: center;
  padding: 2rem 0;
}

.error-icon i {
  font-size: 5rem;
}

.display-1 {
  font-size: 8rem;
  line-height: 1;
}

.quick-links {
  border-top: 1px solid #dee2e6;
  padding-top: 2rem;
}

/* Animation */
.not-found-page {
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

/* Responsive */
@media (max-width: 576px) {
  .display-1 {
    font-size: 6rem;
  }
  
  .error-icon i {
    font-size: 4rem;
  }
}
</style>