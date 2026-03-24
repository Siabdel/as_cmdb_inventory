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

## Frontend (Vue.js - Admin Django)

### 1. Interface Admin Django
- L'interface admin Django utilise les vues DRF pour afficher les tickets
- Les composants Vue.js sont chargés via `static/admin_cmdb/js/tickets.js`
- Le fichier `static/admin_cmdb/js/api.js` gère les appels API avec authentification

### 2. API Client
- [`backend/static/admin_cmdb/js/api.js`](backend/static/admin_cmdb/js/api.js) :
  - Configuration de `axios` avec base URL `/api/v1/`
  - Intercepteur de requête qui ajoute automatiquement le token d'authentification
  - Intercepteur de réponse pour la gestion des erreurs 401/403

### 3. Flux de Transition
1. L'utilisateur déplace un ticket via drag & drop dans l'interface admin
2. Le composant Vue `tickets.js` détecte le drop et appelle l'API :
   ```javascript
   window.apiClient.patch(`/maintenance/tickets/${ticket.id}/transition/`, {
       to_status: newStatus
   });
   ```
3. Le backend valide la transition et met à jour le ticket
4. Le frontend reçoit la réponse et met à jour l'interface

## Workflow Technique

### Étapes détaillées :

1. **Accès à l'admin Django**
   - Authentification requise via `/admin/login/`
   - Chargement de l'interface avec `tickets.js`

2. **Sélection de transition**
   - Interface admin affiche les tickets dans un tableau Kanban
   - Drag & drop pour modifier le statut

3. **Requête API**
   - Méthode PATCH vers `/api/v1/maintenance/tickets/{id}/transition/`
   - Données envoyées : `{"to_status": "..."}`

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
- **Gestion des tokens** via `localStorage` dans le frontend

## Problèmes Résolus

- **Erreur 403 Forbidden** : Authentification activée sur l'endpoint
- **Accès non autorisé** : Les requêtes API nécessitent désormais un token valide
- **Intégration avec Django Admin** : Le frontend Vue.js est intégré dans l'admin Django

## Fichiers Clés

- [`backend/static/admin_cmdb/js/api.js`](backend/static/admin_cmdb/js/api.js) : Configuration API avec authentification
- [`backend/static/admin_cmdb/js/tickets.js`](backend/static/admin_cmdb/js/tickets.js) : Composant Vue pour les tickets
- [`backend/maintenance/views.py`](backend/maintenance/views.py) : Vue DRF pour les tickets
- [`backend/maintenance/models.py`](backend/maintenance/models.py) : Modèle de données avec validation des transitions