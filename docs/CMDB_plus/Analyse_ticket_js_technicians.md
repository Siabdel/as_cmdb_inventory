# Analyse de l'algorithme de ticket.js pour la récupération des utilisateurs "technicien"

## Contexte

Le fichier `backend/static/admin_cmdb/js/tickets.js` contient une logique qui récupère les utilisateurs avec le rôle "technicien" pour alimenter l'interface d'administration des tickets de maintenance.

## Code analysé

### Ligne 72 du fichier tickets.js (Vue Liste des Tickets) :
```javascript
async fetchTechnicians() {
    try {
        const res = await window.apiClient.get('/auth/users/', { params: { role: 'technicien' } });
        this.technicians = res.data;
    } catch (error) {
        // Fallback
        this.technicians = [];
    }
}
```

### Ligne 296 du fichier tickets.js (Vue Détail du Ticket) :
```javascript
async fetchTechnicians() {
    try {
        const res = await window.apiClient.get('/auth/users/');
        this.technicians = res.data;
    } catch (error) {
        this.technicians = [];
    }
}
```

## Algorithme d'exécution

1. **Appel API** : Le frontend effectue un appel HTTP GET vers `/auth/users/` avec un paramètre de requête `role=technicien`
2. **Récupération des données** : Le frontend attend une réponse contenant la liste des utilisateurs avec ce rôle
3. **Stockage dans le state** : Les utilisateurs récupérés sont stockés dans `this.technicians` pour être utilisés dans l'interface

## Problème identifié

Le backend ne disposait pas encore d'un endpoint correspondant à cette URL avec le paramètre `role=technicien`. Cela provoquait une erreur 404 ou une réponse incorrecte.

## Solution implémentée

J'ai créé un endpoint spécifique à `/api/v1/auth/users/technician/` qui :
1. Retourne les utilisateurs avec `is_staff=True` (utilisé comme indication de rôle "technicien")
2. Fournit les champs nécessaires : id, username, email, first_name, last_name, is_staff
3. Applique une authentification requise (IsAuthenticated)

## Structure de réponse attendue

```json
[
  {
    "id": 1,
    "username": "technician1",
    "email": "technician1@example.com",
    "first_name": "Jean",
    "last_name": "Dupont",
    "is_staff": true
  }
]
```

## Intégration dans le frontend

Le frontend utilise cette liste pour :
- Remplir les options de sélection d'assignation de tickets
- Afficher les techniciens dans l'interface d'administration
- Permettre l'assignation de tickets aux utilisateurs avec le rôle "technicien"

## Avantages de cette approche

1. **Séparation des responsabilités** : Le backend gère la logique métier
2. **Sécurité** : L'endpoint nécessite une authentification
3. **Flexibilité** : Le système peut facilement être étendu pour d'autres rôles
4. **Performance** : Récupération directe des utilisateurs avec le rôle spécifique

## Résumé

L'endpoint `/api/v1/auth/users/technician/` fournit exactement ce que le frontend attend pour afficher les techniciens dans l'interface d'administration des tickets de maintenance.

-------
Analyse complète du problème d'authentification pour les transitions de tickets

1. **Problème identifié** :
   - Erreur 401 Unauthorized sur `/api/v1/maintenance/tickets/1/transition/`
   - Le frontend utilise `localStorage.getItem('cmdb_token')` (ligne 24 dans api.js)
   - Mais le backend attend un token généré via `/api/auth/token/` (dans le store auth)

2. **Cause du problème** :
   - Le frontend utilise un token stocké dans `localStorage` avec la clé `cmdb_token`
   - Le backend attend un token généré via l'API `/api/auth/token/` avec la clé `auth_token`
   - Ces deux systèmes de token sont différents

3. **Analyse des fichiers** :
   - `backend/static/admin_cmdb/js/api.js` utilise `cmdb_token` 
   - `frontend/src/store/modules/auth.js` utilise `auth_token`
   - `frontend/src/api/client.js` utilise `auth_token`

4. **Conséquence** :
   - Le frontend tente d'accéder aux endpoints avec un token non valide
   - L'interceptor de réponse redirige vers `/admin/login/` en cas d'erreur 401/403
   - Cela explique pourquoi les tickets redirigent vers la page de login

5. **Solution** :
   - Le frontend doit utiliser le même système de token que le reste de l'application
   - Mettre à jour `api.js` pour utiliser `auth_token` au lieu de `cmdb_token`
   - Ou mettre à jour le frontend pour utiliser le token correctement

6. **Conclusion** :
   - Le problème n'est pas lié à la redirection vers `/admin/login/` mais à l'utilisation incorrecte du token
   - Le frontend utilise un token différent de celui généré par l'API d'authentification
   - Le middleware fonctionne correctement, mais le frontend n'est pas authentifié avec le bon token