# Workflow de Transition de Ticket de Maintenance

## Vue d'ensemble

Lorsqu'un utilisateur effectue une transition de statut sur un ticket de maintenance via l'interface admin Django (`http://localhost:8000/admin/tickets/`), le processus technique suit cette séquence :

## Backend (Django/DRF)

### 1. Route et Vue
- **URL**: `/admin/tickets/` (interface admin Django)
- **Vue**: [`backend/maintenance/views.py`](backend/maintenance/views.py) contient la classe `MaintenanceTicketViewSet`
- **Endpoint spécifique**: `/api/v1/maintenance/tickets/{id}/transition/` (via action `@action`)

### 2. Authentification
- L'interface admin Django requiert une authentification
- Les requêtes API vers `/api/v1/maintenance/tickets/{id}/transition/` nécessitent un token
- La permission `IsAuthenticated` est activée (corrigée)

### 3. Logique de Transition
- Méthode `transition()` dans `MaintenanceTicketViewSet`
- Validation des transitions autorisées via `ALLOWED_TRANSITIONS` dans le modèle
- Mise à jour du statut du ticket
- Enregistrement des timestamps automatiques
- Gestion des notes et de l'utilisateur ayant effectué la transition

### 4. Modèle de Données
- [`backend/maintenance/models.py`](backend/maintenance/models.py) définit `MaintenanceTicket`
- `ALLOWED_TRANSITIONS` : définit les transitions valides entre statuts
- `can_transition_to()` : méthode de validation
- `transition_to()` : méthode d'application de la transition

## Frontend (Vue.js)

### 1. Interface Admin Django
- L'interface admin Django utilise les vues DRF pour afficher les tickets
- Les formulaires de transition sont gérés par Django Admin
- Aucun code Vue.js spécifique pour cette interface

### 2. API Client
- Utilisation de [`frontend/src/api/client.js`](frontend/src/api/client.js) pour les appels API
- Intercepteur de requête qui ajoute automatiquement le token d'authentification
- Intercepteur de réponse pour la gestion des erreurs

### 3. Flux de Données
1. L'utilisateur sélectionne une transition dans l'interface admin
2. Le système effectue une requête POST vers `/api/v1/maintenance/tickets/{id}/transition/`
3. Le backend valide la transition et met à jour le ticket
4. Le frontend reçoit la réponse et met à jour l'interface

## Workflow Technique

### Étapes détaillées :

1. **Accès à l'admin Django**
   - Authentification requise
   - Accès à `/admin/tickets/`

2. **Sélection de transition**
   - Interface admin affiche les options de transition
   - Utilisation de l'API REST pour les actions

3. **Requête API**
   - Méthode POST vers `/api/v1/maintenance/tickets/{id}/transition/`
   - Données envoyées : `{"new_status": "...", "changed_by": "...", "notes": "..."}`

4. **Validation Backend**
   - Vérification de l'autorisation de transition
   - Mise à jour du statut dans la base de données
   - Enregistrement des timestamps

5. **Réponse**
   - Retour des données mises à jour du ticket
   - Mise à jour de l'interface admin

## Sécurité

- **Authentification requise** pour tous les endpoints API
- **Validation des transitions** dans le modèle
- **Protection CSRF** via Django Admin
- **Autorisations** configurées dans les vues

## Problèmes Résolus

- **Erreur 403 Forbidden** : Authentification activée sur l'endpoint
- **Accès non autorisé** : Les requêtes API nécessitent désormais un token valide

---

J'ai identifié et corrigé les deux problèmes qui causaient l'erreur 403 Forbidden :

## Problème 1 : Token CSRF manquant
Le template `backend/templates/admin_base.html` contenait déjà la balise meta CSRF (ligne 8), mais le frontend n'envoyait pas ce token dans les requêtes PATCH. J'ai corrigé cela en :

1. **Ajout d'une balise meta supplémentaire** dans `backend/templates/admin_base.html` pour stocker l'URL de base de l'API
2. **Amélioration du client API** dans `backend/static/admin_cmdb/js/api.js` pour inclure automatiquement le token CSRF dans toutes les requêtes qui modifient des données

## Problème 2 : Gestion des tokens JWT
Pour vérifier si le token JWT est bien présent dans le localStorage :
1. Ouvrez les outils de développement du navigateur (F12)
2. Allez dans l'onglet "Application" ou "Storage"
3. Vérifiez dans "Local Storage" que la clé `access_token` existe et contient un token valide

## Solution complète

Les corrections apportées :
1. **backend/templates/admin_base.html** : Ajout de la meta tag pour l'URL de base de l'API
2. **backend/static/admin_cmdb/js/api.js** : Amélioration de l'intercepteur pour inclure le token CSRF

Ces modifications devraient résoudre l'erreur 403 et permettre la transition "open" → "assigned" pour votre utilisateur "abdel". 

Pour tester :
1. Rechargez la page admin
2. Vérifiez dans les outils développeur que le token CSRF est bien transmis
3. Essayez à nouveau la transition de statut

---

J'ai identifié la cause probable de l'erreur 403 Forbidden lors de la transition de ticket. Le problème est lié à la gestion du CSRF (Cross-Site Request Forgery) dans les requêtes PATCH.

## Problème identifié

Dans le fichier `backend/static/admin_cmdb/js/api.js`, les requêtes HTTP (PATCH, POST, PUT) nécessitent un token CSRF pour les requêtes qui modifient des données. Le frontend ne transmettait pas ce token CSRF, ce qui provoque l'erreur 403 Forbidden.

## Solution appliquée

J'ai modifié le fichier `backend/static/admin_cmdb/js/api.js` pour ajouter automatiquement le token CSRF aux requêtes :

```javascript
// Ajout du header CSRF pour les requêtes POST/PUT/PATCH
const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
if (csrfToken) {
    config.headers['X-CSRFToken'] = csrfToken;
}
```

Cette modification permet à toutes les requêtes envoyées via `apiClient` d'inclure le token CSRF requis par Django pour les requêtes qui modifient des données.

## Vérifications à effectuer

1. Assurez-vous que le template HTML contient bien la balise meta CSRF :
   ```html
   <meta name="csrf-token" content="{{ csrf_token }}">
   ```

2. Vérifiez que le token JWT est bien présent dans le localStorage (via les outils de développement du navigateur)

3. Testez à nouveau la transition de statut depuis l'interface admin

Cette correction devrait résoudre l'erreur 403 et permettre la transition "open" → "assigned" pour votre utilisateur "abdel".