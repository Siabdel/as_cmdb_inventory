# Guide de Déploiement - CMDB Application

## Installation et Configuration

### Prérequis
- Docker et Docker Compose
- Git
- Node.js 18+ (pour développement local)
- Python 3.11+ (pour développement local)

### Installation Rapide avec Docker

```bash
# Cloner le projet
git clone <repository-url>
cd inventory_app

# Copier les fichiers d'environnement
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Démarrer tous les services
docker-compose up -d

# Créer les migrations et la base de données
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate

# Créer un superutilisateur
docker-compose exec backend python manage.py createsuperuser

# Charger les données de test (optionnel)
docker-compose exec backend python manage.py loaddata fixtures/initial_data.json
```

L'application sera accessible sur :
- Frontend : http://localhost:3000
- Backend API : http://localhost:8000
- Admin Django : http://localhost:8000/admin

### Configuration des Variables d'Environnement

#### Backend (.env)
```env
# Django
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database
DATABASE_URL=postgresql://inventory_user:inventory_pass@db:5432/inventory_db

# Redis
REDIS_URL=redis://redis:6379/0

# Media files
MEDIA_URL=/media/
MEDIA_ROOT=/app/media

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# QR Code
QR_CODE_BASE_URL=http://localhost:3000/assets

# Email (optionnel)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

#### Frontend (.env)
```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000/api
VITE_MEDIA_BASE_URL=http://localhost:8000/media

# App Configuration
VITE_APP_NAME=CMDB Inventory
VITE_APP_VERSION=1.0.0

# QR Scanner
VITE_QR_SCANNER_FPS=10
VITE_QR_SCANNER_QRBOX_SIZE=250
```

## Déploiement en Production

### Configuration NGINX

```nginx
# /etc/nginx/sites-available/inventory-app
server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL Configuration
    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/private.key;
    
    # Frontend (Vue.js)
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Django Admin
    location /admin/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Media files
    location /media/ {
        alias /path/to/media/files/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Static files
    location /static/ {
        alias /path/to/static/files/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### Docker Compose Production

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    networks:
      - app-network

  backend:
    build:
      context: ./backend
      dockerfile: ../Dockerfile.backend
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - ALLOWED_HOSTS=${ALLOWED_HOSTS}
    depends_on:
      - db
      - redis
    volumes:
      - media_files:/app/media
      - static_files:/app/static
    restart: unless-stopped
    networks:
      - app-network

  celery:
    build:
      context: ./backend
      dockerfile: ../Dockerfile.backend
    command: celery -A inventory_project worker -l info
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - media_files:/app/media
    restart: unless-stopped
    networks:
      - app-network

  celery-beat:
    build:
      context: ./backend
      dockerfile: ../Dockerfile.backend
    command: celery -A inventory_project beat -l info
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    restart: unless-stopped
    networks:
      - app-network

  frontend:
    build:
      context: ./frontend
      dockerfile: ../Dockerfile.frontend.prod
      args:
        - VITE_API_BASE_URL=${VITE_API_BASE_URL}
    restart: unless-stopped
    networks:
      - app-network

networks:
  app-network:
    driver: bridge

volumes:
  postgres_data:
  media_files:
  static_files:
```

### Dockerfile Production

#### Dockerfile.backend
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Create media directory
RUN mkdir -p /app/media/qr_codes

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "inventory_project.wsgi:application"]
```

#### Dockerfile.frontend.prod
```dockerfile
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

# Build for production
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

## Sauvegarde et Maintenance

### Script de Sauvegarde

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_NAME="inventory_db"

# Créer le répertoire de sauvegarde
mkdir -p $BACKUP_DIR

# Sauvegarde de la base de données
docker-compose exec -T db pg_dump -U inventory_user $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql

# Sauvegarde des fichiers media
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz -C /path/to/media .

# Nettoyer les anciennes sauvegardes (garder 30 jours)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Sauvegarde terminée: $DATE"
```

### Tâches de Maintenance

```python
# backend/inventory/management/commands/maintenance.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from inventory.models import Asset

class Command(BaseCommand):
    help = 'Tâches de maintenance périodiques'
    
    def handle(self, *args, **options):
        # Nettoyer les QR codes orphelins
        self.cleanup_orphaned_qr_codes()
        
        # Vérifier les garanties expirantes
        self.check_warranty_expiration()
        
        # Générer les rapports automatiques
        self.generate_reports()
    
    def cleanup_orphaned_qr_codes(self):
        # Logique de nettoyage
        pass
    
    def check_warranty_expiration(self):
        # Vérifier les garanties qui expirent dans 30 jours
        expiring_soon = Asset.objects.filter(
            warranty_end__lte=timezone.now().date() + timedelta(days=30),
            warranty_end__gte=timezone.now().date()
        )
        # Envoyer notifications
        pass
```

## Monitoring et Logs

### Configuration Logging

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/app/logs/django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}
```

### Métriques et Alertes

```python
# Middleware pour métriques
class MetricsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time
        
        # Log des métriques
        logger.info(f"Request: {request.method} {request.path} - {response.status_code} - {duration:.2f}s")
        
        return response
```

## Sécurité

### Checklist Sécurité Production

- [ ] HTTPS activé avec certificats valides
- [ ] Variables d'environnement sécurisées
- [ ] Base de données avec mots de passe forts
- [ ] Firewall configuré (ports 80, 443 uniquement)
- [ ] Sauvegardes automatiques activées
- [ ] Logs de sécurité configurés
- [ ] Rate limiting activé
- [ ] CORS configuré correctement
- [ ] Headers de sécurité (HSTS, CSP, etc.)
- [ ] Mise à jour régulière des dépendances

### Configuration Sécurité Django

```python
# settings.py (production)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 31536000
SECURE_REDIRECT_EXEMPT = []
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'
```

Cette configuration garantit un déploiement sécurisé et maintenable de l'application CMDB.