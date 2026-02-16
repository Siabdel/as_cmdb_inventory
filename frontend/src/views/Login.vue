<template>
  <div class="login-page">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-6 col-lg-4">
          <div class="login-card">
            <!-- Logo/Header -->
            <div class="text-center mb-4">
              <div class="login-logo">
                <i class="bi bi-boxes display-1 text-primary"></i>
              </div>
              <h2 class="h4 mb-2">CMDB Inventory</h2>
              <p class="text-muted">Connectez-vous à votre compte</p>
            </div>

            <!-- Login Form -->
            <form @submit.prevent="handleLogin">
              <div class="mb-3">
                <label for="username" class="form-label">Nom d'utilisateur</label>
                <div class="input-group">
                  <span class="input-group-text">
                    <i class="bi bi-person"></i>
                  </span>
                  <input
                    type="text"
                    class="form-control"
                    id="username"
                    v-model="form.username"
                    :class="{ 'is-invalid': errors.username }"
                    placeholder="Votre nom d'utilisateur"
                    required
                  >
                </div>
                <div v-if="errors.username" class="invalid-feedback">
                  {{ errors.username }}
                </div>
              </div>

              <div class="mb-4">
                <label for="password" class="form-label">Mot de passe</label>
                <div class="input-group">
                  <span class="input-group-text">
                    <i class="bi bi-lock"></i>
                  </span>
                  <input
                    :type="showPassword ? 'text' : 'password'"
                    class="form-control"
                    id="password"
                    v-model="form.password"
                    :class="{ 'is-invalid': errors.password }"
                    placeholder="Votre mot de passe"
                    required
                  >
                  <button
                    type="button"
                    class="btn btn-outline-secondary"
                    @click="togglePassword"
                  >
                    <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                  </button>
                </div>
                <div v-if="errors.password" class="invalid-feedback">
                  {{ errors.password }}
                </div>
              </div>

              <!-- Error Message -->
              <div v-if="error" class="alert alert-danger" role="alert">
                <i class="bi bi-exclamation-triangle me-2"></i>
                {{ error }}
              </div>

              <!-- Submit Button -->
              <div class="d-grid">
                <button
                  type="submit"
                  class="btn btn-primary btn-lg"
                  :disabled="loading"
                >
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                  <i class="bi bi-box-arrow-in-right me-2" v-else></i>
                  Se connecter
                </button>
              </div>
            </form>

            <!-- Demo Credentials -->
            <div class="demo-info mt-4">
              <div class="alert alert-info">
                <h6 class="alert-heading">
                  <i class="bi bi-info-circle me-2"></i>
                  Compte de démonstration
                </h6>
                <p class="mb-2">Utilisez ces identifiants pour tester l'application :</p>
                <div class="row">
                  <div class="col-6">
                    <strong>Utilisateur :</strong> admin
                  </div>
                  <div class="col-6">
                    <strong>Mot de passe :</strong> admin123
                  </div>
                </div>
                <button 
                  class="btn btn-sm btn-outline-info mt-2"
                  @click="fillDemoCredentials"
                  type="button"
                >
                  Utiliser ces identifiants
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/modules/auth'
import { useToast } from 'vue-toastification'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const toast = useToast()

    // État réactif
    const loading = ref(false)
    const error = ref('')
    const showPassword = ref(false)
    
    const form = reactive({
      username: '',
      password: ''
    })

    const errors = reactive({
      username: '',
      password: ''
    })

    // Méthodes
    const validateForm = () => {
      // Reset errors
      errors.username = ''
      errors.password = ''
      
      let isValid = true

      if (!form.username.trim()) {
        errors.username = 'Le nom d\'utilisateur est requis'
        isValid = false
      }

      if (!form.password) {
        errors.password = 'Le mot de passe est requis'
        isValid = false
      } else if (form.password.length < 3) {
        errors.password = 'Le mot de passe doit contenir au moins 3 caractères'
        isValid = false
      }

      return isValid
    }

    const handleLogin = async () => {
      if (!validateForm()) {
        return
      }

      loading.value = true
      error.value = ''

      try {
        const result = await authStore.login({
          username: form.username.trim(),
          password: form.password
        })

        if (result.success) {
          toast.success('Connexion réussie !')
          
          // Rediriger vers la page demandée ou le dashboard
          const redirectTo = router.currentRoute.value.query.redirect || '/'
          router.push(redirectTo)
        } else {
          error.value = result.error || 'Erreur de connexion'
        }
      } catch (err) {
        console.error('Erreur de connexion:', err)
        error.value = 'Une erreur inattendue s\'est produite'
      } finally {
        loading.value = false
      }
    }

    const togglePassword = () => {
      showPassword.value = !showPassword.value
    }

    const fillDemoCredentials = () => {
      form.username = 'admin'
      form.password = 'admin123'
      
      // Clear any existing errors
      errors.username = ''
      errors.password = ''
      error.value = ''
    }

    return {
      form,
      errors,
      error,
      loading,
      showPassword,
      handleLogin,
      togglePassword,
      fillDemoCredentials
    }
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  padding: 2rem 0;
}

.login-card {
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 1rem 3rem rgba(0, 0, 0, 0.175);
  animation: slideUp 0.5s ease-out;
}

.login-logo {
  margin-bottom: 1rem;
}

.input-group-text {
  background-color: #f8f9fa;
  border-right: none;
}

.input-group .form-control {
  border-left: none;
}

.input-group .form-control:focus {
  border-left: none;
  box-shadow: none;
}

.input-group:focus-within .input-group-text {
  border-color: #86b7fe;
  background-color: #e7f1ff;
}

.demo-info {
  border-top: 1px solid #dee2e6;
  padding-top: 1rem;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: transform 0.2s ease;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

.btn-primary:disabled {
  transform: none;
  opacity: 0.6;
}

/* Animations */
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive */
@media (max-width: 576px) {
  .login-page {
    padding: 1rem;
  }
  
  .login-card {
    padding: 1.5rem;
    margin: 0 0.5rem;
  }
}

/* Focus states */
.form-control:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
}

.btn:focus {
  box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
}
</style>