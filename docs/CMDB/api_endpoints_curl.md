# API Endpoints - Commandes CURL

## Authentification

### Obtenir un token d'authentification
```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "motdepasse"}'
```

## Maintenance Tickets

### Obtenir les détails d'un ticket
```bash
curl -X GET http://localhost:8000/api/v1/maintenance/tickets/1/ \
  -H "Authorization: Token votre_token"
```

### Obtenir les transitions possibles pour un ticket
```bash
curl -X GET http://localhost:8000/api/v1/maintenance/tickets/1/transition/ \
  -H "Authorization: Token votre_token"
```

### Effectuer une transition de statut
```bash
curl -X PATCH http://localhost:8000/api/v1/maintenance/tickets/1/transition/ \
  -H "Authorization: Token votre_token" \
  -H "Content-Type: application/json" \
  -d '{"new_status": "in_progress", "changed_by": "tech01", "notes": "Notes de transition"}'
```

### Assigner un technicien
```bash
curl -X POST http://localhost:8000/api/v1/maintenance/tickets/1/assign/ \
  -H "Authorization: Token votre_token" \
  -H "Content-Type: application/json" \
  -d '{"assigned_tech": "tech01"}'
```

### Résoudre un ticket
```bash
curl -X POST http://localhost:8000/api/v1/maintenance/tickets/1/resolve/ \
  -H "Authorization: Token votre_token" \
  -H "Content-Type: application/json" \
  -d '{"resolution_notes": "Ticket résolu avec succès"}'
```

### Fermer un ticket
```bash
curl -X POST http://localhost:8000/api/v1/maintenance/tickets/1/close/ \
  -H "Authorization: Token votre_token" \
  -H "Content-Type: application/json" \
  -d '{"notes": "Ticket fermé"}'
```

### Annuler un ticket
```bash
curl -X POST http://localhost:8000/api/v1/maintenance/tickets/1/cancel/ \
  -H "Authorization: Token votre_token" \
  -H "Content-Type: application/json" \
  -d '{"notes": "Ticket annulé"}'
```

### Obtenir les commentaires d'un ticket
```bash
curl -X GET http://localhost:8000/api/v1/maintenance/tickets/1/comments/ \
  -H "Authorization: Token votre_token"
```

### Ajouter un commentaire à un ticket
```bash
curl -X POST http://localhost:8000/api/v1/maintenance/tickets/1/comments/ \
  -H "Authorization: Token votre_token" \
  -H "Content-Type: application/json" \
  -d '{"comment": "Nouveau commentaire sur le ticket"}'
```

### Obtenir les pièces d'un ticket
```bash
curl -X GET http://localhost:8000/api/v1/maintenance/tickets/1/parts/ \
  -H "Authorization: Token votre_token"
```

### Ajouter une pièce à un ticket
```bash
curl -X POST http://localhost:8000/api/v1/maintenance/tickets/1/parts/ \
  -H "Authorization: Token votre_token" \
  -H "Content-Type: application/json" \
  -d '{"part_name": "Pièce de rechange", "quantity": 2}'
```

### Obtenir les tickets en retard
```bash
curl -X GET http://localhost:8000/api/v1/maintenance/tickets/overdue/ \
  -H "Authorization: Token votre_token"
```

### Obtenir les tickets ouverts
```bash
curl -X GET http://localhost:8000/api/v1/maintenance/tickets/open/ \
  -H "Authorization: Token votre_token"