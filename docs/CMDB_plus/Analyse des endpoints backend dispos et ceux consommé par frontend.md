# Analyse des endpoints backend dispos et ceux consommé par frontend 

> created 13 mars 2026 



J'ai répertorié les endpoints disponibles dans le backend et ceux consommés côté frontend par Vue.js. Voici la synthèse des endpoints :

### Endpoints Disponibles (Backend)
| Endpoint                                     | Méthode          | Description                                          |
| -------------------------------------------- | ---------------- | ---------------------------------------------------- |
| `/api/v1/inventory/category/`                | GET, POST        | Liste et création des catégories                     |
| `/api/v1/inventory/category/{id}/`           | GET, PUT, DELETE | Détails, mise à jour et suppression d'une catégorie  |
| `/api/v1/inventory/brand/`                   | GET, POST        | Liste et création des marques                        |
| `/api/v1/inventory/brand/{id}/`              | GET, PUT, DELETE | Détails, mise à jour et suppression d'une marque     |
| `/api/v1/inventory/location/`                | GET, POST        | Liste et création des emplacements                   |
| `/api/v1/inventory/location/{id}/`           | GET, PUT, DELETE | Détails, mise à jour et suppression d'un emplacement |
| `/api/v1/inventory/tag/`                     | GET, POST        | Liste et création des tags                           |
| `/api/v1/inventory/tag/{id}/`                | GET, PUT, DELETE | Détails, mise à jour et suppression d'un tag         |
| `/api/v1/inventory/asset/`                   | GET, POST        | Liste et création des actifs                         |
| `/api/v1/inventory/asset/{id}/`              | GET, PUT, DELETE | Détails, mise à jour et suppression d'un actif       |
| `/api/v1/inventory/asset/{id}/move/`         | POST             | Déplacer un actif                                    |
| `/api/v1/inventory/asset/{id}/assign/`       | POST             | Assigner un actif                                    |
| `/api/v1/inventory/asset/{id}/retire/`       | POST             | Archiver un actif                                    |
| `/api/v1/inventory/asset/warranty-expiring/` | GET              | Actifs dont la garantie expire bientôt               |
| `/api/v1/inventory/asset/by-status/`         | GET              | Répartition des actifs par statut                    |
| `/api/v1/inventory/asset/by-category/`       | GET              | Répartition des actifs par catégorie                 |
| `/api/v1/inventory/asset-movement/`          | GET, POST        | Liste et création des mouvements d'actifs            |
| `/api/v1/inventory/asset-movement/{id}/`     | GET, DELETE      | Détails et suppression d'un mouvement d'actif        |
| `/api/v1/inventory/dashboard/stats/`         | GET              | Statistiques pour le tableau de bord                 |

### Endpoints Consommés (Frontend)
| Endpoint                      | Méthode | Description                              |
| ----------------------------- | ------- | ---------------------------------------- |
| `/assets/`                    | GET     | Liste des actifs                         |
| `/assets/{id}/`               | GET     | Détails d'un actif                       |
| `/assets/`                    | POST    | Créer un nouvel actif                    |
| `/assets/{id}/`               | PUT     | Mettre à jour un actif                   |
| `/assets/{id}/`               | PATCH   | Mettre à jour partiellement un actif     |
| `/assets/{id}/`               | DELETE  | Supprimer un actif                       |
| `/assets/{id}/qr_image/`      | GET     | Récupérer l'image QR code d'un actif     |
| `/assets/move-from-scan/`     | POST    | Déplacer un actif via scan QR            |
| `/assets/export/`             | GET     | Exporter la liste des actifs en CSV      |
| `/assets/`                    | GET     | Recherche d'actifs avec autocomplétion   |
| `/assets/stats/`              | GET     | Récupérer les statistiques des actifs    |
| `/assets/{id}/duplicate/`     | POST    | Dupliquer un actif                       |
| `/assets/{id}/`               | PATCH   | Marquer un actif comme en panne          |
| `/assets/{id}/`               | PATCH   | Marquer un actif comme en maintenance    |
| `/assets/{id}/`               | PATCH   | Marquer un actif comme en stock          |
| `/assets/{id}/`               | PATCH   | Assigner un actif à un utilisateur       |
| `/assets/{id}/`               | PATCH   | Désassigner un actif                     |
| `/assets/{id}/regenerate-qr/` | POST    | Générer un nouveau QR code pour un actif |
| `/assets/{id}/movements/`     | GET     | Historique des mouvements d'un actif     |

Ces listes montrent les endpoints disponibles et ceux qui sont actuellement consommés par le frontend. Les endpoints consommés couvrent une bonne partie des fonctionnalités disponibles, mais il y a encore des endpoints du backend qui ne sont pas utilisés.

Voici l'analyse de la correspondance entre les endpoints consommés par le frontend et les endpoints disponibles en backend :

1. **Liste des actifs**
   - **Backend**: `/api/v1/inventory/asset/` (GET)
   - **Frontend**: `/assets/` (GET)
   - **Correspondance**: Oui

2. **Détails d'un actif**
   - **Backend**: `/api/v1/inventory/asset/{id}/` (GET)
   - **Frontend**: `/assets/{id}/` (GET)
   - **Correspondance**: Oui

3. **Créer un nouvel actif**
   - **Backend**: `/api/v1/inventory/asset/` (POST)
   - **Frontend**: `/assets/` (POST)
   - **Correspondance**: Oui

4. **Mettre à jour un actif**
   - **Backend**: `/api/v1/inventory/asset/{id}/` (PUT)
   - **Frontend**: `/assets/{id}/` (PUT)
   - **Correspondance**: Oui

5. **Mettre à jour partiellement un actif**
   - **Backend**: `/api/v1/inventory/asset/{id}/` (PATCH)
   - **Frontend**: `/assets/{id}/` (PATCH)
   - **Correspondance**: Oui

6. **Supprimer un actif**
   - **Backend**: `/api/v1/inventory/asset/{id}/` (DELETE)
   - **Frontend**: `/assets/{id}/` (DELETE)
   - **Correspondance**: Oui

7. **Récupérer l'image QR code d'un actif**
   - **Backend**: Pas disponible
   - **Frontend**: `/assets/{id}/qr_image/` (GET)
   - **Correspondance**: Non

8. **Déplacer un actif via scan QR**
   - **Backend**: `/api/v1/inventory/asset/{id}/move/` (POST)
   - **Frontend**: `/assets/move-from-scan/` (POST)
   - **Correspondance**: Non (le frontend utilise un endpoint différent)

9. **Exporter la liste des actifs en CSV**
   - **Backend**: Pas disponible
   - **Frontend**: `/assets/export/` (GET)
   - **Correspondance**: Non

10. **Recherche d'actifs avec autocomplétion**
    - **Backend**: `/api/v1/inventory/asset/` (GET avec paramètre `search`)
    - **Frontend**: `/assets/` (GET avec paramètre `search`)
    - **Correspondance**: Oui

11. **Récupérer les statistiques des actifs**
    - **Backend**: `/api/v1/inventory/dashboard/stats/` (GET)
    - **Frontend**: `/assets/stats/` (GET)
    - **Correspondance**: Non (le frontend utilise un endpoint différent)

12. **Dupliquer un actif**
    - **Backend**: Pas disponible
    - **Frontend**: `/assets/{id}/duplicate/` (POST)
    - **Correspondance**: Non

13. **Marquer un actif comme en panne**
    - **Backend**: `/api/v1/inventory/asset/{id}/` (PATCH)
    - **Frontend**: `/assets/{id}/` (PATCH)
    - **Correspondance**: Oui

14. **Marquer un actif comme en maintenance**
    - **Backend**: `/api/v1/inventory/asset/{id}/` (PATCH)
    - **Frontend**: `/assets/{id}/` (PATCH)
    - **Correspondance**: Oui

15. **Marquer un actif comme en stock**
    - **Backend**: `/api/v1/inventory/asset/{id}/` (PATCH)
    - **Frontend**: `/assets/{id}/` (PATCH)
    - **Correspondance**: Oui

16. **Assigner un actif à un utilisateur**
    - **Backend**: `/api/v1/inventory/asset/{id}/assign/` (POST)
    - **Frontend**: `/assets/{id}/` (PATCH)
    - **Correspondance**: Non (le frontend utilise un endpoint différent)

17. **Désassigner un actif**
    - **Backend**: `/api/v1/inventory/asset/{id}/` (PATCH)
    - **Frontend**: `/assets/{id}/` (PATCH)
    - **Correspondance**: Oui

18. **Générer un nouveau QR code pour un actif**
    - **Backend**: Pas disponible
    - **Frontend**: `/assets/{id}/regenerate-qr/` (POST)
    - **Correspondance**: Non

19. **Historique des mouvements d'un actif**
    - **Backend**: `/api/v1/inventory/asset-movement/` (GET)
    - **Frontend**: `/assets/{id}/movements/` (GET)
    - **Correspondance**: Non (le frontend utilise un endpoint différent)

### Conclusion
Les endpoints consommés par le frontend couvrent une partie des fonctionnalités disponibles en backend. Cependant, certains endpoints consommés par le frontend ne correspondent pas exactement aux endpoints disponibles en backend. Des ajustements ou des mises à jour peuvent être nécessaires pour aligner les endpoints consommés avec ceux disponibles.