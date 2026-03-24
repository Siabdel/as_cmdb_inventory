# Synthèse du Workflow de Transition de Ticket de Maintenance

## Architecture et Fichiers Utilisés

| Type de Fichier | Chemin | Description | Rôle |
|----------------|--------|-------------|------|
| **Template HTML** | `backend/templates/admin_base.html` | Template principal de l'interface admin | Base de l'interface avec CSRF token |
| **Template HTML** | `backend/templates/admin/tickets/list.html` | Liste des tickets | Interface principale de gestion des tickets |
| **Fichier JS** | `backend/static/admin_cmdb/js/api.js` | Client API | Gestion des requêtes HTTP avec JWT et CSRF |
| **Fichier JS** | `backend/static/admin_cmdb/js/tickets.js` | Logique des tickets | Gestion des transitions et interface utilisateur |
| **Vue Django** | `backend/maintenance/views.py` | ViewSet de maintenance | Gestion des transitions de statut |
| **Modèle Django** | `backend/maintenance/models.py` | Modèle de ticket | Définition des transitions autorisées |
| **Fichier CSS** | `backend/static/admin_cmdb/css/tickets.css` | Styles des tickets | Style de l'interface de gestion des tickets |

## Flux de Transition

### 1. Chargement de la Page
1. **URL** : `http://localhost:8000/admin/tickets/`
2. **Template utilisé** : `backend/templates/admin/tickets/list.html`
3. **JS chargé** : `backend/static/admin_cmdb/js/tickets.js`
4. **Requêtes API** :
   - `GET /api/v1/maintenance/tickets/` - Liste des tickets
   - `GET /api/v1/maintenance/tickets/stats/` - Statistiques
   - `GET /api/v1/staff/auth/users/?role=technicien` - Liste des techniciens

### 2. Transition de Statut
1. **Action utilisateur** : Clic sur un statut ou glisser-déposer
2. **Fonction JS appelée** : `transitionTicket()` ou `dragAndDropTicket()`
3. **Requête API** : `PATCH /api/v1/maintenance/tickets/{id}/transition/`
4. **Données envoyées** : `{"new_status": "assigned"}`
5. **Validation backend** : 
   - Vérification de l'authentification
   - Vérification de la transition autorisée
   - Mise à jour du statut dans le modèle

### 3. Réponse et Mise à Jour
1. **Réponse serveur** : `200 OK` avec les données mises à jour
2. **Mise à jour frontend** : 
   - Mise à jour de l'état local du ticket
   - Raffraîchissement des transitions autorisées
   - Affichage d'une notification de succès

## Composants Principaux

### Templates HTML
- **admin_base.html** : Template de base avec CSRF token et meta tags
- **admin/tickets/list.html** : Interface de liste des tickets avec Kanban

### Fichiers JavaScript
- **api.js** : Client API avec gestion JWT et CSRF
- **tickets.js** : Logique métier des tickets avec transitions

### Modèles et Vues
- **MaintenanceTicket** : Modèle avec `ALLOWED_TRANSITIONS` 
- **MaintenanceTicketViewSet** : ViewSet avec méthode `transition`

## Transitions Autorisées

| Statut Actuel | Transitions Autorisées |
|---------------|------------------------|
| open | assigned, cancelled |
| assigned | in_progress, cancelled |
| in_progress | waiting_parts, resolved, cancelled |
| waiting_parts | in_progress, resolved, cancelled |
| resolved | closed |
| closed | - |
| cancelled | - |

## Authentification

- **Méthodes** : JWTAuthentication, SessionAuthentication
- **Permissions** : IsAuthenticated
- **Utilisateurs** : Techniciens et administrateurs

## Gestion des Erreurs

- **401 Unauthorized** : Authentification manquante
- **403 Forbidden** : Transition non autorisée
- **400 Bad Request** : Données invalides
- **405 Method Not Allowed** : Méthode non autorisée (résolu)