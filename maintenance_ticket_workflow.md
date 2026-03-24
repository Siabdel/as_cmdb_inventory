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