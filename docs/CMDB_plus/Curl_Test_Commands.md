# Commandes Curl pour le Test et le Debuggage des Transitions de Tickets

## Présentation

Ce document documente les commandes curl utilisées pour tester et déboguer les fonctionnalités de transition de statut des tickets de maintenance.

## Prérequis

- Serveur Django en cours d'exécution sur `http://localhost:8000`
- Utilisateur test : `abdel` avec mot de passe `grutil001`
- Ticket ID 1 existant

## Commandes de Test

### 1. Authentification JWT

```bash
# Récupération des tokens JWT
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "abdel", "password": "grutil001"}'
```

**Réponse attendue :**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 2. Test de la transition de statut

```bash
# Transition du ticket de "open" à "assigned"
curl -X PATCH http://localhost:8000/api/v1/maintenance/tickets/1/transition/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{"new_status": "assigned"}'
```

**Réponse attendue :**
```json
{
  "id": 1,
  "ticket_number": "TKT-2026-0001",
  "title": "test RAM",
  "description": "teste la PAM",
  "ticket_type": "repair",
  "priority": "medium",
  "status": "assigned",
  "asset": 203,
  "assigned_tech": "",
  "reported_by": "",
  "due_date": null,
  "resolved_at": null,
  "closed_at": null,
  "resolution_notes": "",
  "labor_cost": "0.00",
  "total_cost": "0.00",
  "is_overdue": false,
  "next_statuses": ["in_progress", "cancelled"],
  "parts": [],
  "comments": [],
  "status_history": [],
  "created_at": "2026-03-23T11:39:23.472580Z",
  "updated_at": "2026-03-24T20:54:20.393847Z"
}
```

### 3. Vérification de l'état du ticket

```bash
# Récupération des détails du ticket
curl -X GET http://localhost:8000/api/v1/maintenance/tickets/1/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### 4. Vérification des transitions autorisées

```bash
# Récupération des transitions autorisées
curl -X GET http://localhost:8000/api/v1/maintenance/tickets/1/transition/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

## Tests d'erreur

### 5. Transition non autorisée

```bash
# Tentative de transition vers un statut non autorisé
curl -X PATCH http://localhost:8000/api/v1/maintenance/tickets/1/transition/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{"new_status": "resolved"}'
```

**Réponse attendue :**
```json
{
  "error": "Transition non autorisée",
  "allowed_transitions": ["in_progress", "cancelled"]
}
```

### 6. Authentification manquante

```bash
# Requête sans authentification
curl -X PATCH http://localhost:8000/api/v1/maintenance/tickets/1/transition/ \
  -H "Content-Type: application/json" \
  -d '{"new_status": "assigned"}'
```

**Réponse attendue :**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

## Commandes de diagnostic

### 7. Vérification des URLs disponibles

```bash
# Liste des URLs Django
python3 backend/manage.py show_urls | grep maintenance
```

### 8. Vérification des permissions

```bash
# Vérification de l'utilisateur
curl -X GET http://localhost:8000/api/auth/user/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

## Scénarios de test

### Scénario 1 : Transition valide
1. Authentification avec `abdel`
2. Transition de "open" → "assigned" 
3. Vérification du statut mis à jour

### Scénario 2 : Transition non autorisée
1. Authentification avec `abdel`
2. Tentative de transition "open" → "resolved" (non autorisée)
3. Vérification de l'erreur 403

### Scénario 3 : Authentification invalide
1. Requête sans token JWT
2. Vérification de l'erreur 401

## Notes importantes

- Le token JWT a une durée de vie limitée (2 heures)
- Les tokens doivent être inclus dans les headers avec le format `Authorization: Bearer <token>`
- Le token CSRF est automatiquement inclus par le client API dans les requêtes POST/PUT/PATCH
- Les transitions sont validées selon les règles définies dans le modèle `MaintenanceTicket`