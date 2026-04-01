# Synthèse des Endpoints Disponibles

## Tableau Récapitulatif

| URL | Méthode | Description | Module |
|-----|---------|-------------|--------|
| `/api/v1/staff/auth/users/` | GET | Renvoie la liste des utilisateurs avec filtre par rôle | staff |
| `/api/v1/staff/auth/users/technician/` | GET | Renvoie la liste des utilisateurs avec le rôle 'technicien' | staff |
| `/api/v1/staff/auth/user/` | GET | Renvoie les informations de l'utilisateur connecté | staff |
| `/api/v1/assets/` | GET | Liste des actifs | inventory |
| `/api/v1/assets/<id>/` | GET | Détail d'un actif | inventory |
| `/api/v1/assets/<id>/assign/` | POST | Assignation d'un actif à un utilisateur | inventory |
| `/api/v1/assets/<id>/move/` | POST | Déplacement d'un actif | inventory |
| `/api/v1/assets/<id>/retire/` | POST | Retrait d'un actif | inventory |
| `/api/v1/inventory/categories/` | GET | Liste des catégories | inventory |
| `/api/v1/inventory/brands/` | GET | Liste des marques | inventory |
| `/api/v1/inventory/locations/` | GET | Liste des emplacements | inventory |
| `/api/v1/inventory/tags/` | GET | Liste des tags | inventory |
| `/api/v1/maintenance/tickets/` | GET | Liste des tickets de maintenance | maintenance |
| `/api/v1/maintenance/tickets/<id>/` | GET | Détail d'un ticket | maintenance |
| `/api/v1/maintenance/tickets/<id>/assign/` | POST | Assignation d'un ticket à un utilisateur | maintenance |
| `/api/v1/maintenance/tickets/<id>/comments/` | GET | Commentaires d'un ticket | maintenance |
| `/api/v1/maintenance/tickets/<id>/history/` | GET | Historique d'un ticket | maintenance |
| `/api/v1/maintenance/tickets/<id>/parts/` | GET | Pièces d'un ticket | maintenance |
| `/api/v1/maintenance/tickets/<id>/status/` | POST | Changement de statut d'un ticket | maintenance |
| `/api/v1/scanner/scan/<uuid>/` | GET | Résolution d'un QR code | scanner |
| `/api/v1/scanner/resolve/<uuid>/` | GET | Résolution d'un QR code | scanner |
| `/api/v1/stock/items/` | GET | Liste des éléments de stock | stock |
| `/api/v1/stock/movements/` | GET | Liste des mouvements de stock | stock |
| `/api/v1/stock/items/<id>/` | GET | Détail d'un élément de stock | stock |
| `/api/v1/stock/movements/<id>/` | GET | Détail d'un mouvement de stock | stock |
| `/api/v1/auth/token/` | POST | Authentification par token | DRF |
| `/api/v1/auth/user/` | GET | Informations utilisateur connecté | DRF |

## Détails des Endpoints

### Endpoints Utilisateurs (Module staff)
- **`/api/v1/staff/auth/users/`** : Endpoint principal pour récupérer les utilisateurs avec filtre par rôle. Supporte le paramètre `role`.
- **`/api/v1/staff/auth/users/technician/`** : Endpoint spécifique pour récupérer les utilisateurs avec le rôle 'technicien'.
- **`/api/v1/staff/auth/user/`** : Endpoint pour récupérer les informations de l'utilisateur connecté.

### Endpoints Inventaire (Module inventory)
- **`/api/v1/assets/`** : Gestion des actifs (CRUD).
- **`/api/v1/inventory/categories/`** : Gestion des catégories.
- **`/api/v1/inventory/brands/`** : Gestion des marques.
- **`/api/v1/inventory/locations/`** : Gestion des emplacements.
- **`/api/v1/inventory/tags/`** : Gestion des tags.

### Endpoints Maintenance (Module maintenance)
- **`/api/v1/maintenance/tickets/`** : Gestion des tickets de maintenance.

### Endpoints Scanner (Module scanner)
- **`/api/v1/scanner/scan/<uuid>/`** : Résolution d'un QR code.
- **`/api/v1/scanner/resolve/<uuid>/`** : Résolution d'un QR code.

### Endpoints Stock (Module stock)
- **`/api/v1/stock/items/`** : Gestion des éléments de stock.
- **`/api/v1/stock/movements/`** : Gestion des mouvements de stock.

### Endpoints Authentification (Module DRF)
- **`/api/v1/auth/token/`** : Authentification par token.
- **`/api/v1/auth/user/`** : Informations utilisateur connecté.

## Notes

- Les endpoints avec le préfixe `/api/v1/staff/` sont dédiés à la gestion des utilisateurs et sont accessibles uniquement aux utilisateurs authentifiés.
- Les endpoints avec le préfixe `/api/v1/` sont les principaux endpoints de l'API REST.
- Les endpoints avec le préfixe `/api/v1/inventory/` sont dédiés à la gestion de l'inventaire.
- Les endpoints avec le préfixe `/api/v1/maintenance/` sont dédiés à la gestion de la maintenance.
- Les endpoints avec le préfixe `/api/v1/scanner/` sont dédiés à la gestion du scanner.
- Les endpoints avec le préfixe `/api/v1/stock/` sont dédiés à la gestion du stock.