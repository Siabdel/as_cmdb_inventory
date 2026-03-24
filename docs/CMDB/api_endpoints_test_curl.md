# Commandes `curl` pour tester les endpoints API

## Endpoints d'inventaire

### Catégories
```bash
# Lister toutes les catégories
curl -X GET http://localhost:8000/api/category/
```

### Localisations
```bash
# Lister toutes les localisations
curl -X GET http://localhost:8000/api/location/
```

### Marques
```bash
# Lister toutes les marques
curl -X GET http://localhost:8000/api/brand/
```

### Dashboard
```bash
# Obtenir les données du dashboard
curl -X GET http://localhost:8000/api/dashboard/

# Obtenir les statistiques du dashboard
curl -X GET http://localhost:8000/api/dashboard/stats/
```

### Actifs
```bash
# Lister tous les actifs
curl -X GET http://localhost:8000/api/

# Créer un nouvel actif
curl -X POST http://localhost:8000/api/ -H "Content-Type: application/json" -d '{"name": "Nouvel Actif", "category": 1}'

# Détails d'un actif
curl -X GET http://localhost:8000/api/1/

# Mettre à jour un actif
curl -X PUT http://localhost:8000/api/1/ -H "Content-Type: application/json" -d '{"name": "Actif Modifié"}'

# Mettre à jour partiellement un actif
curl -X PATCH http://localhost:8000/api/1/ -H "Content-Type: application/json" -d '{"name": "Actif Partiellement Modifié"}'

# Lister les mouvements d'un actif
curl -X GET http://localhost:8000/api/1/movements/

# Lister les actifs par statut
curl -X GET http://localhost:8000/api/by-status/

# Lister les actifs par catégorie
curl -X GET http://localhost:8000/api/by-category/

# Lister les actifs par localisation
curl -X GET http://localhost:8000/api/by-location/

# Déplacer un actif
curl -X POST http://localhost:8000/api/1/move/ -H "Content-Type: application/json" -d '{"location": 2}'

# Lister tous les mouvements
curl -X GET http://localhost:8000/api/movements/

# Actifs avec garantie expirant
curl -X GET http://localhost:8000/api/warranty-expiring/
```

## Endpoints de maintenance

### Tickets
```bash
# Lister tous les tickets
curl -X GET http://localhost:8000/api/tickets/

# Créer un ticket
curl -X POST http://localhost:8000/api/tickets/ -H "Content-Type: application/json" -d '{"title": "Problème réseau", "description": "Le réseau est lent"}'

# Détails d'un ticket
curl -X GET http://localhost:8000/api/tickets/1/

# Mettre à jour un ticket
curl -X PUT http://localhost:8000/api/tickets/1/ -H "Content-Type: application/json" -d '{"status": "resolved"}'

# Supprimer un ticket
curl -X DELETE http://localhost:8000/api/tickets/1/
```

## Endpoints Admin

### Dashboard
```bash
# Dashboard public
curl -X GET http://localhost:8000/api/stats/

# Statistiques API
curl -X GET http://localhost:8000/api/api/stats/