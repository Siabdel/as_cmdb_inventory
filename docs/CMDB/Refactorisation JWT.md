# Refactorisation JWT - Amélioration de la gestion des tokens d'authentification

## Contexte

Dans le cadre de l'amélioration de la sécurité et de la gestion des sessions dans l'application CMDB Inventory, une refactorisation importante a été effectuée pour migrer de l'authentification par token classique à l'authentification JWT (JSON Web Token). Cette refactorisation vise à améliorer la sécurité, la gestion des sessions et la compatibilité avec les bonnes pratiques modernes de développement.

## Pourquoi JWT ?

### 1. Sécurité renforcée
- **Tokens courts-lived** : Les tokens d'accès ont une durée de vie limitée (60 minutes), réduisant le risque d'utilisation malveillante
- **Refresh tokens** : Les tokens de rafraîchissement permettent de renouveler les sessions sans reconnexion fréquente
- **Rotation automatique** : Les refresh tokens peuvent être rotés pour une sécurité accrue

### 2. Gestion des sessions distribuée
- **Stateless** : Le serveur ne doit plus stocker les sessions, ce qui améliore la scalabilité
- **Compatibilité avec les microservices** : JWT est parfaitement adapté à une architecture distribuée
- **Support des applications frontend séparées** : Facilite l'intégration avec des applications frontend indépendantes

### 3. Meilleure expérience utilisateur
- **Renouvellement automatique** : Les sessions peuvent être renouvelées automatiquement
- **Gestion des erreurs** : Meilleure gestion des erreurs 401/403 avec reconnexion automatique

## Modifications apportées

### Backend Django

#### Configuration JWT
```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    # ... autres configurations
}

# Configuration JWT
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

#### Exposition des endpoints
```python
# urls.py
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # ... autres URLs
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
```

### Frontend Vue.js

#### Nouveau client API JWT
Le fichier `frontend/src/api/jwtClient.js` remplace l'ancien client API et implémente :
- Gestion automatique des tokens d'accès et de rafraîchissement
- Interception des erreurs 401/403 avec tentatives de refresh
- Gestion des erreurs réseau et serveur
- Logging détaillé en mode développement

#### Mise à jour du store d'authentification
```javascript
// frontend/src/store/modules/auth.js
const login = async (credentials) => {
    // Appel API pour l'authentification
    const response = await apiClient.post('/api/token/', credentials)
    
    if (response.data.access && response.data.refresh) {
        // Stockage des tokens JWT
        localStorage.setItem('access_token', response.data.access)
        localStorage.setItem('refresh_token', response.data.refresh)
        
        // Configuration du header Authorization
        apiClient.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
        
        // Récupération des informations utilisateur
        await fetchUser()
        
        return { success: true }
    }
}
```

## Avantages de cette refactorisation

### Sécurité
- **Tokens courts-lived** : Réduction du risque d'exploitation des tokens
- **Rotation automatique** : Les refresh tokens sont régénérés à chaque utilisation
- **Blacklist** : Les tokens obsolètes sont immédiatement invalidés

### Performance
- **Réduction de la charge serveur** : Pas de stockage de sessions côté serveur
- **Meilleure scalabilité** : Architecture stateless
- **Réduction des requêtes** : Gestion automatique des tokens

### Maintenabilité
- **Code plus propre** : Séparation claire entre authentification et logique métier
- **Gestion centralisée** : Toute la logique d'authentification dans un seul client
- **Facilité de test** : Plus facile à tester et à déboguer

## Impact sur l'architecture

### Avant la refactorisation
- Authentification par token classique avec `TokenAuthentication`
- Stockage des sessions côté serveur
- Gestion manuelle des tokens dans le frontend

### Après la refactorisation
- Authentification JWT avec `JWTAuthentication`
- Architecture stateless
- Gestion automatique des tokens dans le client API
- Meilleure intégration avec les standards modernes

## Migration des composants existants

Les composants Vue.js qui utilisaient l'ancien client API ont été mis à jour pour utiliser le nouveau `jwtClient.js`. Les composants qui appelaient directement les endpoints d'authentification ont été mis à jour pour utiliser les nouveaux endpoints JWT.

## Tests et validation

- Tests unitaires pour la gestion des tokens
- Tests d'intégration pour les endpoints JWT
- Tests de sécurité pour la rotation des tokens
- Tests de performance pour la scalabilité

## Conclusion

Cette refactorisation représente une amélioration significative de la sécurité et de la maintenabilité de l'application. L'adoption de JWT permet une architecture plus moderne, plus sécurisée et plus scalable, tout en maintenant une compatibilité avec les bonnes pratiques actuelles de développement web.

---

# Corrections :

J'ai implémenté les bonnes pratiques JWT pour les appels API DRF depuis Vue.js comme demandé. Voici les modifications principales :

1. **Configuration Django** :
   - Activation de JWT avec `rest_framework_simplejwt` comme méthode d'authentification par défaut
   - Configuration des durées de vie des tokens (60 minutes pour access, 7 jours pour refresh)
   - Activation de la rotation et de la blacklist des refresh tokens

2. **Endpoints JWT** :
   - Ajout des routes `/api/token/` et `/api/token/refresh/` pour l'authentification JWT

3. **Frontend Vue.js** :
   - Création d'un nouveau client API `jwtClient.js` avec gestion complète des tokens JWT
   - Mise à jour du store d'authentification pour utiliser les endpoints JWT
   - Implémentation de la gestion automatique du refresh token
   - Mise à jour de la gestion des erreurs 401/403 avec JWT

4. **Fichiers modifiés** :
   - `backend/static/admin_cmdb/js/api.js` : Configuration JWT pour les appels API depuis Django
   - `backend/inventory_project/settings.py` : Configuration JWT Django
   - `backend/inventory_project/urls.py` : Exposition des endpoints JWT
   - `frontend/src/store/modules/auth.js` : Gestion JWT pour l'authentification
   - `frontend/src/api/jwtClient.js` : Nouveau client API avec gestion JWT
   - Suppression du fichier obsolète `frontend/src/api/client.js`

Les appels API depuis Vue.js utilisent maintenant les bonnes pratiques JWT avec gestion automatique des tokens d'accès et de rafraîchissement, conformément aux recommandations fournies.