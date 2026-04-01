# Workflow de Transition des Tickets - Interface Admin

## Vue d'ensemble

Cette documentation décrit le workflow complet de gestion des transitions de statut des tickets de maintenance dans l'interface d'administration Django à l'URL `http://localhost:8000/admin/tickets/`.

## Architecture Technique

### Endpoints API

- **GET** `/api/v1/maintenance/tickets/{id}/transition/` - Récupère les transitions autorisées
- **PATCH** `/api/v1/maintenance/tickets/{id}/transition/` - Effectue la transition de statut

### ViewSet et Classes associées

- **Classe** : `MaintenanceTicketViewSet` dans `backend/maintenance/views.py`
- **Méthode** : `transition` décorée avec `@action`
- **Authentification** : JWTAuthentication, SessionAuthentication
- **Permissions** : IsAuthenticated

### Modèles

- **Modèle** : `MaintenanceTicket` dans `backend/maintenance/models.py`
- **Attribut** : `ALLOWED_TRANSITIONS` - Dictionnaire définissant les transitions autorisées
- **Méthode** : `can_transition_to()` - Validation de la transition

## Workflow de Transition

### 1. Initialisation de l'interface

Lorsque l'utilisateur accède à `http://localhost:8000/admin/tickets/` :
- Le frontend charge le composant Vue `tickets.js` 
- Une requête GET est envoyée vers `/api/v1/maintenance/tickets/1/transition/` pour récupérer les transitions autorisées
- Les données du ticket sont chargées via l'API REST

### 2. Séquence de transition

1. **Sélection du statut** : L'utilisateur sélectionne un nouveau statut dans l'interface (par exemple "in_progress")
2. **Validation côté frontend** : Le frontend vérifie si la transition est autorisée
3. **Appel API** : Le frontend envoie une requête PATCH vers `/api/v1/maintenance/tickets/{id}/transition/` avec le body :
   ```json
   {
     "new_status": "in_progress",
     "changed_by": "technicien01",
     "notes": "Notes de transition"
   }
   ```
4. **Validation côté backend** :
   - Le serializer `TicketTransitionSerializer` valide les données
   - La méthode `can_transition_to()` vérifie si la transition est autorisée
   - Si non autorisée, une erreur 403 est retournée
5. **Mise à jour du statut** : Si valide, le statut du ticket est mis à jour
6. **Mise à jour de l'interface** : Le frontend met à jour l'affichage avec le nouveau statut

## Transitions Autorisées

Les transitions sont définies dans le modèle `MaintenanceTicket` :

```python
ALLOWED_TRANSITIONS = {
    'open': ['assigned', 'cancelled'],
    'assigned': ['in_progress', 'cancelled'],
    'in_progress': ['waiting_parts', 'resolved', 'cancelled'],
    'waiting_parts': ['in_progress', 'resolved', 'cancelled'],
    'resolved': ['closed'],
    'closed': [],
    'cancelled': []
}
```

## Authentification

- **Méthodes d'authentification** : JWTAuthentication, SessionAuthentication
- **Permissions requises** : IsAuthenticated
- **Utilisateurs autorisés** : Techniciens et administrateurs

## Interface Utilisateur

L'interface admin utilise :
- `backend/static/admin_cmdb/js/tickets.js` pour la logique client
- `backend/templates/admin/inventory/maintenanceticket/change_list.html` pour le rendu HTML
- `backend/static/admin_cmdb/css/tickets.css` pour le style

## Erreurs Courantes

- **403 Forbidden** : La transition n'est pas autorisée pour le statut actuel
- **401 Unauthorized** : L'utilisateur n'est pas authentifié
- **400 Bad Request** : Données invalides dans le body de la requête