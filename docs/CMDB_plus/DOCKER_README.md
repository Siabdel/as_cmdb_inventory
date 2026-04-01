# Configuration Docker pour CMDB Inventory

Cette documentation explique comment utiliser la configuration Docker pour le projet CMDB Inventory.

## Fichiers de configuration

- `docker-compose.yml` : Configuration principale pour le développement/production
- `docker-compose.test.yml` : Configuration simplifiée pour les tests
- `Dockerfile.backend` : Image Docker pour le backend Django
- `Dockerfile.frontend` : Image Docker pour le frontend Vue.js
- `backend/entrypoint.sh` : Script d'initialisation du backend
- `backend/.env.prod` : Variables d'environnement pour Docker

## Services disponibles

1. **PostgreSQL** (`db`) : Base de données sur le port 5433 (externe) → 5432 (interne)
2. **Redis** (`redis`) : Cache et broker Celery sur le port 6380 → 6379
3. **Backend Django** (`backend`) : API Django sur le port 8300
4. **Frontend Vue.js** (`frontend`) : Application Vue.js sur le port 3000
5. **Celery Worker** (`celery`) : Worker pour les tâches asynchrones
6. **Celery Beat** (`celery-beat`) : Planificateur de tâches périodiques

## Démarrage rapide

### 1. Construction et démarrage
```bash
# Construire les images
docker-compose build

# Démarrer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f
```

### 2. Arrêt des services
```bash
# Arrêter les services
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v
```

### 3. Tests de fonctionnement
```bash
# Vérifier l'état des services
docker-compose ps

# Tester l'API backend
curl http://localhost:8300/api/v1/assets/

# Accéder à l'interface frontend
# Ouvrir http://localhost:3000 dans un navigateur
```

## Configuration des variables d'environnement

### Backend
Les variables sont définies dans `backend/.env.prod` :
- `INVENTORY_DB_*` : Configuration de la base de données
- `INVENTORY_SECRET_KEY` : Clé secrète Django
- `INVENTORY_REDIS_URL` : URL Redis pour Celery
- `INVENTORY_ALLOWED_HOSTS` : Hôtes autorisés
- `INVENTORY_CORS_ALLOWED_ORIGINS` : Origines CORS autorisées

### Frontend
Les variables sont définies dans `docker-compose.yml` :
- `VITE_API_BASE_URL` : URL de l'API backend (http://backend:8300/api dans Docker)
- `VITE_MEDIA_BASE_URL` : URL des médias

## Résolution des problèmes courants

### 1. Connexion à la base de données échoue
- Vérifier que le mot de passe dans `.env.prod` correspond à celui dans `docker-compose.yml`
- Vérifier que PostgreSQL est accessible : `docker-compose exec db pg_isready -U inventory_user`

### 2. Le frontend ne peut pas joindre le backend
- Vérifier que l'URL `VITE_API_BASE_URL` est correcte (http://backend:8300/api dans Docker)
- Vérifier que le backend est en cours d'exécution : `docker-compose logs backend`

### 3. Problèmes de permissions avec les volumes
- Les répertoires `qr_codes/`, `media/` et `static/` doivent être accessibles en écriture
- Exécuter : `chmod -R 755 qr_codes media static`

### 4. Migrations non appliquées
L'entrypoint.sh exécute automatiquement les migrations, mais vous pouvez les exécuter manuellement :
```bash
docker-compose exec backend python manage.py migrate
```

## Développement local sans Docker

Si vous préférez développer sans Docker :

1. Backend :
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py runserver 0.0.0.0:8000
```

2. Frontend :
```bash
cd frontend
npm install
npm run dev
```

## Production

Pour la production, modifiez :
1. `SECRET_KEY` dans `.env.prod`
2. `DEBUG=False` dans `.env.prod`
3. Utilisez `gunicorn` au lieu du serveur de développement
4. Configurez un reverse proxy (Nginx, Traefik)

## Commandes utiles

```bash
# Accéder au shell du conteneur backend
docker-compose exec backend bash

# Exécuter les tests
docker-compose exec backend python manage.py test

# Créer un superutilisateur
docker-compose exec backend python manage.py createsuperuser

# Voir les logs d'un service spécifique
docker-compose logs -f backend

# Reconstruire un service spécifique
docker-compose build backend

# Redémarrer un service
docker-compose restart backend